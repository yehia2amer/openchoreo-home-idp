"""OpenChoreo v1.0 — Pulumi Python entry point."""

from __future__ import annotations

from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s

from components import (
    control_plane,
    data_plane,
    flux_gitops,
    integration_tests,
    link_planes,
    observability_plane,
    prerequisites,
    workflow_plane,
)
from config import (
    NS_CONTROL_PLANE,
    NS_DATA_PLANE,
    NS_OBSERVABILITY_PLANE,
    NS_WORKFLOW_PLANE,
    load_config,
)


def main() -> None:
    cfg = load_config()

    # ─── Kubernetes Provider ───
    k8s_provider = k8s.Provider(
        "k8s",
        kubeconfig=cfg.kubeconfig_path,
        context=cfg.kubeconfig_context,
    )

    # ─── Step 0: Cilium CNI + Gateway API (optional) ───
    cilium_install = None
    if cfg.platform.cni_mode == "cilium" or cfg.platform.gateway_mode == "cilium":
        from components import cilium

        # Gateway API CRDs must exist before Cilium starts so it can
        # register its Gateway API controller on first boot.
        gateway_api_crds = k8s.yaml.v2.ConfigGroup(
            "gateway-api-crds",
            files=[cfg.gateway_api_crds_url],
            opts=pulumi.ResourceOptions(provider=k8s_provider),
        )
        cilium_install = cilium.deploy(cfg, k8s_provider, depends=[gateway_api_crds])

    # ─── Step 1: Prerequisites ───
    prereqs = prerequisites.deploy(
        cfg,
        k8s_provider,
        extra_depends=[cilium_install] if cilium_install else [],
    )

    # ─── Step 2: Control Plane ───
    cp = control_plane.deploy(
        cfg,
        k8s_provider,
        depends=[prereqs.cluster_secret_store_ready, prereqs.control_plane_ns],
    )

    # ─── Step 3: Data Plane ───
    dp = data_plane.deploy(cfg, k8s_provider, depends=[cp.helm_chart])

    # ─── Step 4: Workflow Plane ───
    wp = workflow_plane.deploy(cfg, k8s_provider, depends=[cp.helm_chart])

    # ─── Step 5: Observability Plane (optional) ───
    obs = None
    if cfg.enable_observability:
        obs = observability_plane.deploy(cfg, k8s_provider, depends=[cp.helm_chart])

    # ─── Step 6: Link Planes (if observability enabled) ───
    if obs is not None:
        link_depends = [dp.register_cmd, wp.register_cmd, obs.register_cmd]
        link_planes.deploy(cfg, depends=link_depends)

    # ─── Step 7: Flux CD & GitOps (optional) ───
    if cfg.enable_flux and cfg.gitops_repo_url:
        flux_gitops.deploy(
            cfg,
            k8s_provider,
            depends=[cp.helm_chart, dp.register_cmd, wp.register_cmd],
        )

    # ─── Step 8: Integration Tests ───
    test_depends: list[pulumi.Resource] = [cp.helm_chart, dp.register_cmd, wp.register_cmd]
    if obs is not None:
        test_depends.append(obs.register_cmd)
    integration_tests.deploy(cfg, depends=test_depends)

    # ─── Outputs: URLs ───
    pulumi.export("backstage_url", cfg.backstage_url)
    pulumi.export("api_url", cfg.api_url)
    pulumi.export("thunder_url", cfg.thunder_url)
    pulumi.export("argo_workflows_url", f"http://localhost:{cfg.wp_argo_port}")
    pulumi.export("observer_url", cfg.observer_url)
    pulumi.export("opensearch_dashboards_url", f"http://localhost:{cfg.opensearch_dashboards_port}")
    pulumi.export("data_plane_gateway_http", cfg.dp_http_url)
    pulumi.export("data_plane_gateway_https", cfg.dp_https_url)

    # ─── Outputs: Credentials (masked — use `pulumi stack output --show-secrets`) ───
    pulumi.export("opensearch_username", cfg.opensearch_username)
    pulumi.export("opensearch_password", pulumi.Output.secret(cfg.opensearch_password))
    pulumi.export("openbao_root_token", pulumi.Output.secret(cfg.openbao_root_token))

    # ─── Outputs: Cluster Info ───
    pulumi.export("kubeconfig_context", cfg.kubeconfig_context)
    pulumi.export("domain_base", cfg.domain_base)
    pulumi.export("openchoreo_version", cfg.openchoreo_version)
    pulumi.export("platform", cfg.platform.name)
    pulumi.export("edition", "cilium" if cfg.platform.gateway_mode == "cilium" else "generic-cni")

    # ─── Outputs: Feature Flags ───
    pulumi.export("cilium_enabled", cfg.platform.gateway_mode == "cilium")
    pulumi.export("flux_enabled", cfg.enable_flux)
    pulumi.export("observability_enabled", cfg.enable_observability)

    # ─── Outputs: Namespaces ───
    pulumi.export(
        "namespaces",
        {
            "control_plane": NS_CONTROL_PLANE,
            "data_plane": NS_DATA_PLANE,
            "workflow_plane": NS_WORKFLOW_PLANE,
            "observability_plane": NS_OBSERVABILITY_PLANE,
        },
    )

    # ─── Write .env file ───
    env_path = Path(__file__).resolve().parent / ".env"
    env_lines: dict[str, str | pulumi.Output[str]] = {
        "BACKSTAGE_URL": cfg.backstage_url,
        "API_URL": cfg.api_url,
        "THUNDER_URL": cfg.thunder_url,
        "ARGO_WORKFLOWS_URL": f"http://localhost:{cfg.wp_argo_port}",
        "OBSERVER_URL": cfg.observer_url,
        "OPENSEARCH_DASHBOARDS_URL": f"http://localhost:{cfg.opensearch_dashboards_port}",
        "DATA_PLANE_GATEWAY_HTTP": cfg.dp_http_url,
        "DATA_PLANE_GATEWAY_HTTPS": cfg.dp_https_url,
        "OPENSEARCH_USERNAME": cfg.opensearch_username,
        "OPENSEARCH_PASSWORD": cfg.opensearch_password,
        "OPENBAO_ROOT_TOKEN": cfg.openbao_root_token,
        "KUBECONFIG_CONTEXT": cfg.kubeconfig_context,
        "DOMAIN_BASE": cfg.domain_base,
        "OPENCHOREO_VERSION": cfg.openchoreo_version,
        "PLATFORM": cfg.platform.name,
        "EDITION": "cilium" if cfg.platform.gateway_mode == "cilium" else "generic-cni",
        "CILIUM_ENABLED": str(cfg.platform.gateway_mode == "cilium").lower(),
        "FLUX_ENABLED": str(cfg.enable_flux).lower(),
        "OBSERVABILITY_ENABLED": str(cfg.enable_observability).lower(),
        "NS_CONTROL_PLANE": NS_CONTROL_PLANE,
        "NS_DATA_PLANE": NS_DATA_PLANE,
        "NS_WORKFLOW_PLANE": NS_WORKFLOW_PLANE,
        "NS_OBSERVABILITY_PLANE": NS_OBSERVABILITY_PLANE,
    }

    def _write_env(pairs: dict[str, str]) -> None:
        lines = [f"{k}={v}" for k, v in sorted(pairs.items())]
        env_path.write_text("\n".join(lines) + "\n")

    # Resolve any Output[str] values before writing
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
