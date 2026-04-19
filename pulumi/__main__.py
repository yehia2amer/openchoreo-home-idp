# pyright: reportMissingImports=false, reportAttributeAccessIssue=false

from __future__ import annotations

from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s

from components import prerequisites, thunder
from config import NS_CONTROL_PLANE, NS_DATA_PLANE, NS_OBSERVABILITY_PLANE, NS_WORKFLOW_PLANE, load_config


def main() -> None:
    cfg = load_config()

    k8s_provider = k8s.Provider(
        "k8s",
        kubeconfig=cfg.kubeconfig_path,
        context=cfg.kubeconfig_context,
    )

    cilium_install = None
    if (
        cfg.platform.cni_mode == "cilium" or cfg.platform.gateway_mode == "cilium"
    ) and not cfg.platform.cilium_pre_installed:
        from components import cilium

        gateway_api_crds = k8s.yaml.v2.ConfigGroup(
            "gateway-api-crds",
            files=[cfg.gateway_api_crds_url],
            opts=pulumi.ResourceOptions(provider=k8s_provider),
        )
        cilium_install = cilium.Cilium(
            "cilium",
            cfg=cfg,
            k8s_provider=k8s_provider,
            depends=[gateway_api_crds],
        ).result

    prereqs_component = prerequisites.Prerequisites(
        "prerequisites",
        cfg=cfg,
        k8s_provider=k8s_provider,
        extra_depends=[cilium_install] if cilium_install else [],
    )
    prereqs_result = prereqs_component.result

    thunder_component = thunder.Thunder(
        "thunder",
        cfg=cfg,
        k8s_provider=k8s_provider,
        depends=[prereqs_result.cluster_secret_store_ready],
    )
    thunder_component.result

    backstage_infra = None
    if cfg.enable_backstage_infra and cfg.platform.cloud_provider == "gcp":
        from components.backstage_infra import BackstageInfra

        backstage_infra = BackstageInfra(
            "backstage-infra",
            cfg=cfg,
            k8s_provider=k8s_provider,
            depends=[prereqs_result.cluster_secret_store_ready],
        )

    observer_infra = None
    if cfg.enable_backstage_infra and cfg.platform.cloud_provider == "gcp" and backstage_infra is not None:
        from components.observer_infra import ObserverInfra

        observer_infra = ObserverInfra(
            "observer-infra",
            cfg=cfg,
            pg_instance_name=backstage_infra.pg_instance_name,
            pg_instance_private_ip=backstage_infra.pg_instance_private_ip,
            depends=[backstage_infra],
        )

    thunder_infra = None
    if cfg.enable_backstage_infra and cfg.platform.cloud_provider == "gcp" and backstage_infra is not None:
        from components.thunder_infra import ThunderInfra

        thunder_infra = ThunderInfra(
            "thunder-infra",
            cfg=cfg,
            pg_instance_name=backstage_infra.pg_instance_name,
            pg_instance_private_ip=backstage_infra.pg_instance_private_ip,
            depends=[backstage_infra] + ([observer_infra] if observer_infra else []),
        )
    pulumi.export("backstage_url", cfg.backstage_url)
    pulumi.export("api_url", cfg.api_url)
    pulumi.export("thunder_url", cfg.thunder_url)
    pulumi.export("argo_workflows_url", f"http://localhost:{cfg.wp_argo_port}")
    pulumi.export("observer_url", cfg.observer_url)
    pulumi.export("data_plane_gateway_http", cfg.dp_http_url)
    pulumi.export("data_plane_gateway_https", cfg.dp_https_url)

    if cfg.platform.secrets_backend == "openbao":
        pulumi.export("openbao_root_token", pulumi.Output.secret(cfg.openbao_root_token))

    pulumi.export("kubeconfig_context", cfg.kubeconfig_context)
    pulumi.export("domain_base", cfg.domain_base)
    pulumi.export("openchoreo_version", cfg.openchoreo_version)
    pulumi.export("platform", cfg.platform.name)
    pulumi.export("edition", "cilium" if cfg.platform.gateway_mode == "cilium" else "generic-cni")

    pulumi.export("cilium_enabled", cfg.platform.gateway_mode == "cilium")
    pulumi.export("flux_enabled", cfg.enable_flux)
    pulumi.export("observability_enabled", cfg.enable_observability)
    pulumi.export("observability_mode", cfg.platform.observability_mode)
    pulumi.export("demo_app_bootstrap_enabled", cfg.enable_demo_app_bootstrap)

    if cfg.enable_backstage_infra and backstage_infra is not None:
        pulumi.export("backstage_pg_instance_name", backstage_infra.pg_instance_name)
        pulumi.export("backstage_techdocs_bucket_name", backstage_infra.techdocs_bucket_name)

    pulumi.export(
        "namespaces",
        {
            "control_plane": NS_CONTROL_PLANE,
            "data_plane": NS_DATA_PLANE,
            "workflow_plane": NS_WORKFLOW_PLANE,
            "observability_plane": NS_OBSERVABILITY_PLANE,
        },
    )

    env_path = Path(__file__).resolve().parent / ".env"
    env_lines: dict[str, str | pulumi.Output[str]] = {
        "BACKSTAGE_URL": cfg.backstage_url,
        "API_URL": cfg.api_url,
        "THUNDER_URL": cfg.thunder_url,
        "ARGO_WORKFLOWS_URL": f"http://localhost:{cfg.wp_argo_port}",
        "OBSERVER_URL": cfg.observer_url,
        "DATA_PLANE_GATEWAY_HTTP": cfg.dp_http_url,
        "DATA_PLANE_GATEWAY_HTTPS": cfg.dp_https_url,
        "KUBECONFIG_CONTEXT": cfg.kubeconfig_context,
        "DOMAIN_BASE": cfg.domain_base,
        "OPENCHOREO_VERSION": cfg.openchoreo_version,
        "PLATFORM": cfg.platform.name,
        "EDITION": "cilium" if cfg.platform.gateway_mode == "cilium" else "generic-cni",
        "CILIUM_ENABLED": str(cfg.platform.gateway_mode == "cilium").lower(),
        "FLUX_ENABLED": str(cfg.enable_flux).lower(),
        "OBSERVABILITY_ENABLED": str(cfg.enable_observability).lower(),
        "OBSERVABILITY_MODE": cfg.platform.observability_mode,
        "NS_CONTROL_PLANE": NS_CONTROL_PLANE,
        "NS_DATA_PLANE": NS_DATA_PLANE,
        "NS_WORKFLOW_PLANE": NS_WORKFLOW_PLANE,
        "NS_OBSERVABILITY_PLANE": NS_OBSERVABILITY_PLANE,
    }
    if cfg.platform.secrets_backend == "openbao":
        env_lines["OPENBAO_ROOT_TOKEN"] = cfg.openbao_root_token

    def _write_env(pairs: dict[str, str]) -> None:
        lines = [f"{k}={v}" for k, v in sorted(pairs.items())]
        env_path.write_text("\n".join(lines) + "\n")

    plain: dict[str, str] = {}
    outputs: dict[str, pulumi.Output] = {}
    for k, v in env_lines.items():
        if isinstance(v, pulumi.Output):
            outputs[k] = v
        else:
            plain[k] = str(v)

    if outputs:

        def _resolve_and_write(resolved: list[str]) -> None:
            merged = {**plain, **dict(zip(outputs.keys(), resolved))}
            _write_env(merged)

        pulumi.Output.all(*outputs.values()).apply(_resolve_and_write)
    else:
        _write_env(plain)


main()
