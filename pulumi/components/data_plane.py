"""Data Plane component: Namespace, copy CA, DP Helm chart, register ClusterDataPlane."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pulumi
import pulumi_kubernetes as k8s

from config import NS_DATA_PLANE, TIMEOUT_DEFAULT, OpenChoreoConfig
from helpers.copy_ca import copy_ca
from helpers.register_plane import register_plane
from values.data_plane import get_values as dp_values

if TYPE_CHECKING:
    from helpers.dynamic_providers import RegisterPlane


class DataPlaneResult:
    """Outputs from the data plane component."""

    def __init__(self, register_cmd: RegisterPlane):
        self.register_cmd = register_cmd


def _allow_gateway_ingress(
    k8s_provider: k8s.Provider,
    depends: list[pulumi.Resource],
    opts: pulumi.ResourceOptions | None = None,
) -> k8s.apiextensions.CustomResource:
    """Create a CiliumClusterwideNetworkPolicy allowing Cilium Gateway API
    ingress traffic to reach workloads in OpenChoreo data-plane namespaces.

    The Cilium envoy proxy uses the reserved ``ingress`` identity when
    forwarding traffic, which is invisible to standard Kubernetes
    NetworkPolicies.  This policy explicitly permits it.
    """
    return k8s.apiextensions.CustomResource(
        "allow-gateway-ingress",
        api_version="cilium.io/v2",
        kind="CiliumClusterwideNetworkPolicy",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name="allow-gateway-ingress",
        ),
        spec={
            "endpointSelector": {
                "matchExpressions": [
                    {
                        "key": "io.cilium.k8s.namespace.labels.openchoreo.dev/created-by",
                        "operator": "Exists",
                    }
                ],
            },
            "ingress": [
                {
                    "fromEntities": ["ingress"],
                }
            ],
        },
        opts=opts
        or pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=depends,
        ),
    )


class DataPlane(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        depends: list[pulumi.Resource],
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:DataPlane", name, {}, opts)

        ns = k8s.core.v1.Namespace(
            NS_DATA_PLANE,
            metadata=k8s.meta.v1.ObjectMetaArgs(name=NS_DATA_PLANE),
            opts=self._child_opts(provider=k8s_provider, depends_on=depends),
        )

        ca = copy_ca("data-plane", NS_DATA_PLANE, cfg, opts=self._child_opts(depends_on=[ns]))

        # Use helm.v3.Release (not v4.Chart) because the chart contains
        # cert-manager Certificate resources; v4.Chart does client-side rendering
        # that fails if cert-manager CRDs are not yet installed.
        dp_chart = k8s.helm.v3.Release(
            NS_DATA_PLANE,
            k8s.helm.v3.ReleaseArgs(
                chart=cfg.dp_chart,
                version=cfg.openchoreo_version,
                namespace=NS_DATA_PLANE,
                values=dp_values(
                    dp_http_port=cfg.dp_http_port,
                    dp_https_port=cfg.dp_https_port,
                    tls_enabled=cfg.tls_enabled,
                ),
                timeout=TIMEOUT_DEFAULT,
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[ca]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")),
            ),
        )

        extra_spec = {
            "gateway": {
                "ingress": {
                    "external": {
                        "name": "gateway-default",
                        "namespace": NS_DATA_PLANE,
                        "http": {
                            "host": cfg.domain_base,
                            "port": cfg.dp_http_port,
                        },
                        "https": {
                            "host": cfg.domain_base,
                            "port": cfg.dp_https_port,
                        },
                    },
                },
            },
            "secretStoreRef": {"name": "default"},
        }

        # Allow Cilium gateway ingress to data-plane workloads (Cilium-only)
        if cfg.platform.gateway_mode == "cilium":
            _allow_gateway_ingress(
                k8s_provider,
                depends=[dp_chart],
                opts=self._child_opts(provider=k8s_provider, depends_on=[dp_chart]),
            )

        register = register_plane(
            name="data-plane",
            namespace=NS_DATA_PLANE,
            kind="ClusterDataPlane",
            cfg=cfg,
            extra_spec=extra_spec,
            opts=self._child_opts(depends_on=[dp_chart]),
        )

        self.result = DataPlaneResult(register_cmd=register)
        self.register_outputs({})

    def _child_opts(
        self,
        depends_on: list[pulumi.Resource] | None = None,
        provider: k8s.Provider | None = None,
    ) -> pulumi.ResourceOptions:
        opts_kwargs = {
            "parent": self,
            "aliases": [pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)],
        }
        if depends_on:
            opts_kwargs["depends_on"] = depends_on
        if provider:
            opts_kwargs["provider"] = provider
        return pulumi.ResourceOptions(**opts_kwargs)


def deploy(
    cfg: OpenChoreoConfig,
    k8s_provider: k8s.Provider,
    depends: list[pulumi.Resource],
) -> DataPlaneResult:
    """Deploy the data plane namespace, chart, and register ClusterDataPlane."""
    return DataPlane(
        "data-plane",
        cfg=cfg,
        k8s_provider=k8s_provider,
        depends=depends,
    ).result
