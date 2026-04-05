"""Standalone Cilium L2 resources for pre-installed Cilium deployments.

When Cilium is pre-installed (e.g. Talos bare-metal), the main Cilium
component is skipped entirely.  This component creates the L2 IP pool
and announcement policy independently so that LoadBalancer services
receive external IPs via Cilium's L2 announcements.
"""

from __future__ import annotations

import pulumi
import pulumi_kubernetes as k8s

from config import OpenChoreoConfig

NS_CILIUM = "kube-system"


class CiliumL2(pulumi.ComponentResource):
    """Create CiliumLoadBalancerIPPool and CiliumL2AnnouncementPolicy."""

    def __init__(
        self,
        name: str,
        *,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        depends: list[pulumi.Resource] | None = None,
    ) -> None:
        super().__init__("openchoreo:infra:CiliumL2", name, None, pulumi.ResourceOptions(parent=None))

        p = cfg.platform

        blocks: list[dict[str, str]] = []
        for entry in p.cilium_l2_ip_pool_cidrs:
            if "-" in entry:
                start, stop = entry.split("-", 1)
                blocks.append({"start": start.strip(), "stop": stop.strip()})
            elif "/" in entry:
                blocks.append({"cidr": entry.strip()})

        self.ip_pool = k8s.apiextensions.CustomResource(
            "homelab-ip-pool",
            api_version="cilium.io/v2alpha1",
            kind="CiliumLoadBalancerIPPool",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="homelab-ip-pool",
                namespace=NS_CILIUM,
            ),
            spec={
                "blocks": blocks,
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=depends),
        )

        self.l2_policy = k8s.apiextensions.CustomResource(
            "homelab-l2-policy",
            api_version="cilium.io/v2alpha1",
            kind="CiliumL2AnnouncementPolicy",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="homelab-l2-policy",
                namespace=NS_CILIUM,
            ),
            spec={
                "interfaces": [f"^{iface}$" for iface in p.cilium_l2_interfaces],
                "loadBalancerIPs": True,
                "externalIPs": True,
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=depends),
        )

        self.register_outputs({})

    def _child_opts(
        self,
        depends_on: list[pulumi.Resource] | None = None,
        provider: k8s.Provider | None = None,
    ) -> pulumi.ResourceOptions:
        opts_kwargs: dict = {"parent": self}
        if depends_on:
            opts_kwargs["depends_on"] = depends_on
        if provider:
            opts_kwargs["provider"] = provider
        return pulumi.ResourceOptions(**opts_kwargs)
