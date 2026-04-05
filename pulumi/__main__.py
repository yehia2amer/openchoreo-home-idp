"""OpenChoreo v1.0 — Pulumi Python entry point."""

# pyright: reportMissingImports=false, reportAttributeAccessIssue=false

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
    tls_setup,
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
    if (
        cfg.platform.cni_mode == "cilium" or cfg.platform.gateway_mode == "cilium"
    ) and not cfg.platform.cilium_pre_installed:
        from components import cilium

        # Gateway API CRDs must exist before Cilium starts so it can
        # register its Gateway API controller on first boot.
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

    # ─── Step 0.5: Cilium L2 (standalone — for pre-installed Cilium) ───
    if cfg.platform.cilium_l2_announcements_enabled and cfg.platform.cilium_pre_installed:
        from components import cilium_l2

        cilium_l2.CiliumL2(
            "cilium-l2",
            cfg=cfg,
            k8s_provider=k8s_provider,
        )

    # ─── Step 1: Prerequisites ───
    prereqs_component = prerequisites.Prerequisites(
        "prerequisites",
        cfg=cfg,
        k8s_provider=k8s_provider,
        extra_depends=[cilium_install] if cilium_install else [],
    )
    prereqs = prereqs_component.result

    # ─── Step 1.5: TLS Setup (optional — bare-metal self-signed CA) ───
    tls = None
    if cfg.tls_enabled:
        tls_component = tls_setup.TlsSetup(
            "tls-setup",
            cfg=cfg,
            k8s_provider=k8s_provider,
            depends=[prereqs.control_plane_ns, prereqs.data_plane_ns],
        )
        tls = tls_component.result

    # ─── Step 2: Control Plane ───
    cp_component = control_plane.ControlPlane(
        "control-plane",
        cfg=cfg,
        k8s_provider=k8s_provider,
        depends=[prereqs.cluster_secret_store_ready, prereqs.control_plane_ns] + ([tls.cp_cert] if tls else []),
    )
    cp = cp_component.result

    # ─── Step 3: Data Plane ───
    dp_component = data_plane.DataPlane(
        "data-plane",
        cfg=cfg,
        k8s_provider=k8s_provider,
        depends=[cp.helm_chart, prereqs.data_plane_ns] + ([tls.dp_cert] if tls else []),
    )
    dp = dp_component.result

    # ─── Step 4: Workflow Plane ───
    wp_component = workflow_plane.WorkflowPlane(
        "workflow-plane",
        cfg=cfg,
        k8s_provider=k8s_provider,
        depends=[cp.helm_chart],
    )
    wp = wp_component.result

    # ─── Step 5: Observability Plane (optional) ───
    obs = None
    if cfg.enable_observability:
        obs_depends: list[pulumi.Resource] = [cp.helm_chart]
        if tls:
            obs_depends.append(tls.op_cert)
        obs_component = observability_plane.ObservabilityPlane(
            "observability-plane",
            cfg=cfg,
            k8s_provider=k8s_provider,
            depends=obs_depends,
        )
        obs = obs_component.result

    # ─── Step 6: Link Planes (if observability enabled) ───
    if obs is not None:
        link_depends: list[pulumi.Resource] = [dp.register_cmd, wp.register_cmd, obs.register_cmd]
        link_planes.LinkPlanesComponent("link-planes", cfg=cfg, depends=link_depends)

    # ─── Step 7: Flux CD & GitOps (optional) ───
    if cfg.enable_flux and cfg.gitops_repo_url:
        flux_gitops.FluxGitOps(
            "flux-gitops",
            cfg=cfg,
            k8s_provider=k8s_provider,
            depends=[cp.helm_chart, dp.register_cmd, wp.register_cmd],
        )

    # ─── Step 7.5: CoreDNS LAN DNS + Gateway IP pinning (bare-metal only) ───
    if cfg.platform.name == "talos-baremetal" and cfg.gateway_pin_ip:
        from components import coredns_lan

        coredns_lan.CoreDnsLan(
            "coredns-lan",
            cp_ip=cfg.gateway_pin_ip,
            dp_ip=cfg.gateway_pin_ip_dp,
            op_ip=cfg.gateway_pin_ip_op,
            bind_ip=cfg.coredns_bind_ip,
            k8s_provider=k8s_provider,
        )

        # Pin each gateway-default Service to its own LB IP.
        # Different namespaces can't share IPs in Cilium 1.17.
        _gw_pins = [
            (NS_CONTROL_PLANE, cfg.gateway_pin_ip),
            (NS_DATA_PLANE, cfg.gateway_pin_ip_dp),
            (NS_OBSERVABILITY_PLANE, cfg.gateway_pin_ip_op),
        ]
        for ns, ip in _gw_pins:
            if ip:
                k8s.core.v1.ServicePatch(
                    f"gateway-pin-ip-{ns}",
                    metadata=k8s.meta.v1.ObjectMetaPatchArgs(
                        name="gateway-default",
                        namespace=ns,
                        annotations={"io.cilium/lb-ipam-ips": ip},
                    ),
                    opts=pulumi.ResourceOptions(provider=k8s_provider),
                )

        # Registry HTTPRoute — expose in-cluster registry via Gateway
        k8s.apiextensions.CustomResource(
            "registry-httproute",
            api_version="gateway.networking.k8s.io/v1",
            kind="HTTPRoute",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="registry",
                namespace=NS_DATA_PLANE,
            ),
            spec={
                "parentRefs": [
                    {
                        "name": "gateway-default",
                        "namespace": NS_DATA_PLANE,
                        "sectionName": "http",
                    },
                ],
                "hostnames": [f"registry.{cfg.domain_base}"],
                "rules": [
                    {
                        "backendRefs": [
                            {
                                "name": "registry",
                                "namespace": NS_WORKFLOW_PLANE,
                                "port": cfg.wp_registry_port,
                            },
                        ],
                    },
                ],
            },
            opts=pulumi.ResourceOptions(provider=k8s_provider),
        )

        # ReferenceGrant — allow data plane HTTPRoute to reference
        # the registry Service in the workflow plane namespace
        k8s.apiextensions.CustomResource(
            "registry-reference-grant",
            api_version="gateway.networking.k8s.io/v1beta1",
            kind="ReferenceGrant",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="allow-dp-to-registry",
                namespace=NS_WORKFLOW_PLANE,
            ),
            spec={
                "from": [
                    {
                        "group": "gateway.networking.k8s.io",
                        "kind": "HTTPRoute",
                        "namespace": NS_DATA_PLANE,
                    },
                ],
                "to": [
                    {
                        "group": "",
                        "kind": "Service",
                        "name": "registry",
                    },
                ],
            },
            opts=pulumi.ResourceOptions(provider=k8s_provider),
        )

    # ─── Step 8: Integration Tests ───
    test_depends: list[pulumi.Resource] = [cp.helm_chart, dp.register_cmd, wp.register_cmd]
    if obs is not None:
        test_depends.append(obs.register_cmd)
    integration_tests.IntegrationTests("integration-tests", cfg=cfg, depends=test_depends)

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
    # cilium_enabled refers to Cilium as Gateway API controller, not CNI.
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
