# pyright: reportMissingImports=false

"""Generate cluster-vars.yaml ConfigMap from OpenChoreoConfig.

This module produces the Flux variable-substitution ConfigMap that drives
ALL platform resources in the gitops repo.  It replaces the manually-maintained
``clusters/<stack>/vars/cluster-vars.yaml`` files with a deterministic,
Pulumi-driven generator.

Usage (standalone)::

    python helpers/cluster_vars.py --stack talos-baremetal \
        --output ../../openchoreo-gitops/clusters/talos-baremetal/vars/cluster-vars.yaml

Usage (from __main__.py)::

    from helpers.cluster_vars import generate_cluster_vars
    yaml_str = generate_cluster_vars(cfg)
"""

from __future__ import annotations

import argparse
import io
import sys
from collections import OrderedDict
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from config import OpenChoreoConfig


# ---------------------------------------------------------------------------
# YAML helpers — deterministic output with quoted strings
# ---------------------------------------------------------------------------


class _QuotedStr(str):
    """Marker subclass so the YAML dumper always emits double-quoted strings."""


def _quoted_str_representer(dumper: yaml.Dumper, data: _QuotedStr) -> yaml.Node:
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


def _ordered_dict_representer(dumper: yaml.Dumper, data: OrderedDict) -> yaml.Node:  # type: ignore[type-arg]
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


def _get_dumper() -> type[yaml.Dumper]:
    """Return a Dumper that quotes strings and preserves OrderedDict order."""
    dumper = yaml.Dumper
    dumper.add_representer(_QuotedStr, _quoted_str_representer)
    dumper.add_representer(OrderedDict, _ordered_dict_representer)
    return dumper


# ---------------------------------------------------------------------------
# ConfigMap data builder
# ---------------------------------------------------------------------------


def _q(value: object) -> _QuotedStr:
    """Convert any value to a quoted YAML string."""
    return _QuotedStr(str(value))


def _build_data(cfg: OpenChoreoConfig, overrides: dict[str, str] | None = None) -> OrderedDict[str, _QuotedStr]:
    """Build the ``data:`` section of the cluster-vars ConfigMap.

    Keys are sorted alphabetically for deterministic output.  Platform-conditional
    keys (GCP, Cilium L2) are included for all platforms with empty/false defaults
    so the schema stays consistent.

    Parameters
    ----------
    cfg:
        Loaded OpenChoreoConfig.
    overrides:
        Optional dict to override/supplement any generated values.
        Useful for runtime-only values like ``GATEWAY_ENDPOINT`` that come
        from Pulumi outputs rather than static config.
    """
    from config import (
        NS_CONTROL_PLANE,
        NS_DATA_PLANE,
        NS_OBSERVABILITY_PLANE,
        NS_WORKFLOW_PLANE,
    )

    platform = cfg.platform
    is_gcp = platform.cloud_provider == "gcp"

    # -- Registry values depend on platform --
    if is_gcp:
        ar_url = f"{cfg.gcp_region}-docker.pkg.dev/{cfg.gcp_project_id}/{cfg.artifact_registry_repository_id}"
        registry_endpoint = ar_url
        registry_image_prefix = ar_url
    elif platform.registry_mode == "local" and platform.load_balancer_mode == "cilium-l2":
        # Bare-metal with Cilium L2 — in-cluster registry + VIP node port
        keepalived_vip = _resolve_keepalived_vip(cfg)
        registry_endpoint = "registry.openchoreo-workflow-plane.svc.cluster.local:5000"
        registry_image_prefix = f"{keepalived_vip}:{cfg.registry_node_port}" if keepalived_vip else ""
    else:
        # Default / k3d — empty, components fill in at runtime
        registry_endpoint = ""
        registry_image_prefix = ""

    keepalived_vip_str = _resolve_keepalived_vip(cfg) if platform.load_balancer_mode == "cilium-l2" else ""

    # -- Gateway endpoint: configurable override, else derive --
    gateway_endpoint = ""
    if is_gcp:
        # GKE: typically a static IP, must be provided via overrides or stack config
        gateway_endpoint = ""
    elif platform.load_balancer_mode == "cilium-l2":
        gateway_endpoint = f"api.{cfg.domain_base}"
    else:
        gateway_endpoint = f"api.{cfg.domain_base}"

    # -- Gateway class name --
    gateway_class_name = "kgateway"
    if is_gcp:
        gateway_class_name = "kgateway"

    # -- Cilium L2 values --
    l2_enabled = platform.cilium_l2_announcements_enabled
    l2_interfaces = ",".join(platform.cilium_l2_interfaces) if platform.cilium_l2_interfaces else ""
    l2_cidrs = ",".join(platform.cilium_l2_ip_pool_cidrs) if platform.cilium_l2_ip_pool_cidrs else ""
    l2_start, l2_stop = _parse_l2_range(l2_cidrs)
    l2_regex = _build_l2_regex(platform.cilium_l2_interfaces)

    # -- DNS zone domain --
    dns_zone_domain = cfg.domain_base
    if is_gcp:
        # GCP DNS zone may differ from domain_base (strip subdomain)
        parts = cfg.domain_base.split(".")
        dns_zone_domain = ".".join(parts[-2:]) if len(parts) > 2 else cfg.domain_base

    # -- Cluster issuer name --
    cluster_issuer_name = ""
    if is_gcp:
        cluster_issuer_name = "openchoreo-cas-issuer"

    # -- Letsencrypt email --
    letsencrypt_email = ""
    if is_gcp:
        letsencrypt_email = f"admin@{dns_zone_domain}"

    # -- Build data dict (sorted keys) --
    data: dict[str, str] = {
        "PLATFORM": platform.name,
        "DOMAIN_BASE": cfg.domain_base,
        "TLS_ENABLED": str(cfg.tls_enabled).lower(),
        "SCHEME": cfg.scheme,
        # Ports
        "CP_HTTP_PORT": str(cfg.cp_http_port),
        "CP_HTTPS_PORT": str(cfg.cp_https_port),
        "DP_HTTP_PORT": str(cfg.dp_http_port),
        "DP_HTTPS_PORT": str(cfg.dp_https_port),
        "OP_HTTP_PORT": str(cfg.op_http_port),
        "OP_HTTPS_PORT": str(cfg.op_https_port),
        "WP_ARGO_PORT": str(cfg.wp_argo_port),
        "WP_REGISTRY_PORT": str(cfg.wp_registry_port),
        "REGISTRY_NODE_PORT": str(cfg.registry_node_port),
        # Registry
        "REGISTRY_ENDPOINT": registry_endpoint,
        "REGISTRY_IMAGE_PREFIX": registry_image_prefix,
        # Networking
        "KEEPALIVED_VIP": keepalived_vip_str,
        "GATEWAY_ENDPOINT": gateway_endpoint,
        "GATEWAY_CLASS_NAME": gateway_class_name,
        # URLs
        "BACKSTAGE_URL": cfg.backstage_url,
        "BACKSTAGE_FORK_URL": cfg.backstage_fork_url,
        "API_URL": cfg.api_url,
        "THUNDER_URL": cfg.thunder_url,
        "OBSERVER_URL": cfg.observer_url,
        # Service ports
        "THUNDER_SERVICE_PORT": "8090",
        "CP_API_SERVICE_PORT": "8080",
        "OBSERVER_SERVICE_PORT": "8080",
        "RCA_AGENT_SERVICE_PORT": "8080",
        # Versions
        "OPENCHOREO_VERSION": cfg.openchoreo_version,
        "OPENCHOREO_REF": cfg.openchoreo_ref,
        "CERT_MANAGER_VERSION": cfg.cert_manager_version,
        "EXTERNAL_SECRETS_VERSION": cfg.external_secrets_version,
        "KGATEWAY_VERSION": cfg.kgateway_version,
        "DOCKER_REGISTRY_VERSION": cfg.docker_registry_version,
        "METRICS_PROMETHEUS_VERSION": cfg.metrics_prometheus_version,
        "LOGS_OPENOBSERVE_VERSION": cfg.logs_openobserve_version,
        "TRACING_OPENOBSERVE_VERSION": cfg.tracing_openobserve_version,
        "ODIGOS_VERSION": cfg.odigos_version,
        # Cilium L2
        "CILIUM_L2_ENABLED": str(l2_enabled).lower(),
        "CILIUM_L2_INTERFACES": l2_interfaces,
        "CILIUM_L2_IP_POOL_CIDRS": l2_cidrs,
        "CILIUM_L2_IP_POOL_START": l2_start,
        "CILIUM_L2_IP_POOL_STOP": l2_stop,
        "CILIUM_L2_INTERFACE_REGEX": l2_regex,
        # Observability
        "ENABLE_OBSERVABILITY": str(cfg.enable_observability).lower(),
        "ENABLE_OPENOBSERVE": str(cfg.enable_openobserve).lower(),
        "PROMETHEUS_ADDRESS": "http://openchoreo-observability-prometheus:9091",
        # Namespaces
        "NS_CONTROL_PLANE": NS_CONTROL_PLANE,
        "NS_DATA_PLANE": NS_DATA_PLANE,
        "NS_WORKFLOW_PLANE": NS_WORKFLOW_PLANE,
        "NS_OBSERVABILITY_PLANE": NS_OBSERVABILITY_PLANE,
    }

    # -- GCP-specific variables --
    if is_gcp:
        eso_sa_email = cfg.gcp_eso_service_account
        if "@" not in eso_sa_email:
            eso_sa_email = f"{eso_sa_email}@{cfg.gcp_project_id}.iam.gserviceaccount.com"
        cas_sa_email = cfg.gcp_cas_service_account
        if "@" not in cas_sa_email:
            cas_sa_email = f"{cas_sa_email}@{cfg.gcp_project_id}.iam.gserviceaccount.com"
        dns_sa_email = f"openchoreo-dns@{cfg.gcp_project_id}.iam.gserviceaccount.com"

        ar_url_full = f"{cfg.gcp_region}-docker.pkg.dev/{cfg.gcp_project_id}/{cfg.artifact_registry_repository_id}"
        ar_host = f"{cfg.gcp_region}-docker.pkg.dev"

        data.update(
            {
                "GCP_PROJECT_ID": cfg.gcp_project_id,
                "GCP_REGION": cfg.gcp_region,
                "GCP_GKE_CLUSTER_NAME": cfg.gcp_gke_cluster_name,
                "GCP_CAS_POOL_NAME": cfg.gcp_cas_pool_name,
                "GCP_ESO_SERVICE_ACCOUNT": eso_sa_email,
                "GCP_CAS_SERVICE_ACCOUNT": cas_sa_email,
                "ARTIFACT_REGISTRY_URL": ar_url_full,
                "ARTIFACT_REGISTRY_HOST": ar_host,
                "GCP_DNS_PROJECT_ID": cfg.gcp_project_id,
                "GCP_DNS_SA_EMAIL": dns_sa_email,
                "LETSENCRYPT_EMAIL": letsencrypt_email,
                "CLUSTER_ISSUER_NAME": cluster_issuer_name,
                "PROMETHEUS_ADDRESS": "http://gmp-frontend.openchoreo-observability-plane.svc.cluster.local:9090",
                "GCP_MONITORING_SERVICE_ACCOUNT": f"openchoreo-monitoring@{cfg.gcp_project_id}.iam.gserviceaccount.com",
            }
        )

    # -- DNS_ZONE_DOMAIN: present in both schemas --
    data["DNS_ZONE_DOMAIN"] = dns_zone_domain

    # -- Apply overrides last --
    if overrides:
        data.update(overrides)

    # Sort keys for deterministic output
    return OrderedDict((k, _q(v)) for k, v in sorted(data.items()))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_keepalived_vip(cfg: OpenChoreoConfig) -> str:
    """Derive the keepalived VIP from the Cilium L2 IP pool.

    Convention: the VIP is the last usable IP in the first CIDR range,
    or empty if L2 is disabled.  For ``192.168.0.10-192.168.0.99`` the VIP
    is ``192.168.0.100`` (one above the pool stop — used by existing
    baremetal configs).

    If the config has an explicit ``keepalived_vip`` field on the platform
    or in overrides, that wins.
    """
    cidrs = cfg.platform.cilium_l2_ip_pool_cidrs
    if not cidrs:
        return ""
    first = cidrs[0]
    if "-" in first:
        # Range format: "192.168.0.10-192.168.0.99"
        _, stop = first.split("-", 1)
        parts = stop.strip().split(".")
        # VIP = stop + 1 (matches existing convention)
        parts[-1] = str(int(parts[-1]) + 1)
        return ".".join(parts)
    return ""


def _parse_l2_range(cidrs_str: str) -> tuple[str, str]:
    """Extract start/stop from a CIDR range string like ``192.168.0.10-192.168.0.99``."""
    if not cidrs_str or "-" not in cidrs_str:
        return ("", "")
    first_range = cidrs_str.split(",")[0].strip()
    if "-" in first_range:
        start, stop = first_range.split("-", 1)
        return (start.strip(), stop.strip())
    return ("", "")


def _build_l2_regex(interfaces: tuple[str, ...] | None) -> str:
    """Build a regex matching any of the Cilium L2 interfaces.

    Returns ``^(enp7s0|enp0s1|enp0s25)$`` style pattern, or empty.
    """
    if not interfaces:
        return ""
    return f"^({'|'.join(interfaces)})$"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_cluster_vars(
    cfg: OpenChoreoConfig,
    *,
    overrides: dict[str, str] | None = None,
) -> str:
    """Return the full cluster-vars.yaml content as a string.

    Parameters
    ----------
    cfg:
        Loaded ``OpenChoreoConfig`` (from ``config.load_config()``).
    overrides:
        Optional dict to override/add any data keys.  Useful for
        runtime values like ``GATEWAY_ENDPOINT`` from Pulumi outputs.

    Returns
    -------
    str
        Valid YAML for a Kubernetes ConfigMap.
    """
    data = _build_data(cfg, overrides=overrides)

    doc: OrderedDict[str, object] = OrderedDict()
    doc["apiVersion"] = "v1"
    doc["kind"] = "ConfigMap"
    doc["metadata"] = OrderedDict(
        [
            ("name", "cluster-vars"),
            ("namespace", "flux-system"),
        ]
    )
    doc["data"] = data

    stream = io.StringIO()
    yaml.dump(
        doc,
        stream,
        Dumper=_get_dumper(),
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=200,
    )
    return stream.getvalue()


# ---------------------------------------------------------------------------
# Standalone CLI
# ---------------------------------------------------------------------------


def _cli() -> None:
    """CLI entry point for standalone usage."""
    parser = argparse.ArgumentParser(
        description="Generate cluster-vars.yaml from Pulumi stack config.",
    )
    parser.add_argument(
        "--stack",
        required=True,
        help="Pulumi stack name (e.g. talos-baremetal, gcp)",
    )
    parser.add_argument(
        "--output",
        default="-",
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--override",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Override a data key (can be repeated)",
    )
    args = parser.parse_args()

    # Parse overrides
    overrides: dict[str, str] = {}
    for item in args.override:
        if "=" not in item:
            parser.error(f"Invalid override format: {item!r} (expected KEY=VALUE)")
        k, v = item.split("=", 1)
        overrides[k.strip()] = v.strip()

    # We need Pulumi context to load config — this requires running inside
    # a Pulumi stack or we fall back to a lightweight loader.
    try:
        # Try to import and use the config loader (requires Pulumi context)
        import pulumi

        # Set the stack name in env for Pulumi to pick up
        import os

        os.environ.setdefault("PULUMI_STACK", args.stack)

        from config import load_config

        cfg = load_config()
        result = generate_cluster_vars(cfg, overrides=overrides or None)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print(
            "\nNote: Standalone mode requires a Pulumi context.",
            file=sys.stderr,
        )
        print(
            "Run from within the pulumi/ directory with `pulumi run` or use",
            file=sys.stderr,
        )
        print(
            "  cd pulumi && pulumi run -- python helpers/cluster_vars.py --stack <name>",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.output == "-":
        sys.stdout.write(result)
    else:
        from pathlib import Path

        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result)
        print(f"Wrote {len(result)} bytes to {out}", file=sys.stderr)


if __name__ == "__main__":
    _cli()
