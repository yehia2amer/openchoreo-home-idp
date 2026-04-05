"""CoreDNS LAN DNS component — hostNetwork pod for *.openchoreo.local resolution.

Deploys a single CoreDNS pod on hostNetwork that binds to the node's LAN IP
on port 53, resolving *.openchoreo.local to the Gateway LB IP and forwarding
all other queries to public DNS.

Only used on talos-baremetal where the node needs to resolve local domains
for containerd image pulls.
"""

from __future__ import annotations

import pulumi
import pulumi_kubernetes as k8s

from values.coredns_lan import get_corefile

COREDNS_IMAGE = "coredns/coredns:1.12.1"
NS = "kube-system"


class CoreDnsLan(pulumi.ComponentResource):
    """Deploy CoreDNS as a LAN DNS server on hostNetwork."""

    def __init__(
        self,
        name: str,
        *,
        cp_ip: str,
        dp_ip: str,
        op_ip: str,
        bind_ip: str,
        k8s_provider: k8s.Provider,
        depends: list[pulumi.Resource] | None = None,
    ) -> None:
        super().__init__("openchoreo:infra:CoreDnsLan", name, None, pulumi.ResourceOptions(parent=None))

        corefile = get_corefile(cp_ip, dp_ip, op_ip, bind_ip=bind_ip)

        sa = k8s.core.v1.ServiceAccount(
            "coredns-lan-sa",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="coredns-lan",
                namespace=NS,
            ),
            opts=self._child_opts(provider=k8s_provider, depends_on=depends),
        )

        cm = k8s.core.v1.ConfigMap(
            "coredns-lan-config",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="coredns-lan",
                namespace=NS,
            ),
            data={"Corefile": corefile},
            opts=self._child_opts(provider=k8s_provider, depends_on=depends),
        )

        self.deployment = k8s.apps.v1.Deployment(
            "coredns-lan",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="coredns-lan",
                namespace=NS,
                labels={"app": "coredns-lan"},
            ),
            spec=k8s.apps.v1.DeploymentSpecArgs(
                replicas=1,
                strategy=k8s.apps.v1.DeploymentStrategyArgs(
                    type="Recreate",
                ),
                selector=k8s.meta.v1.LabelSelectorArgs(
                    match_labels={"app": "coredns-lan"},
                ),
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(
                        labels={"app": "coredns-lan"},
                    ),
                    spec=k8s.core.v1.PodSpecArgs(
                        service_account_name="coredns-lan",
                        host_network=True,
                        dns_policy="Default",
                        priority_class_name="system-node-critical",
                        tolerations=[
                            k8s.core.v1.TolerationArgs(operator="Exists"),
                        ],
                        containers=[
                            k8s.core.v1.ContainerArgs(
                                name="coredns",
                                image=COREDNS_IMAGE,
                                args=["-conf", "/etc/coredns/Corefile"],
                                ports=[
                                    k8s.core.v1.ContainerPortArgs(
                                        name="dns-udp",
                                        container_port=53,
                                        protocol="UDP",
                                    ),
                                    k8s.core.v1.ContainerPortArgs(
                                        name="dns-tcp",
                                        container_port=53,
                                        protocol="TCP",
                                    ),
                                ],
                                readiness_probe=k8s.core.v1.ProbeArgs(
                                    http_get=k8s.core.v1.HTTPGetActionArgs(
                                        path="/ready",
                                        port=8080,
                                    ),
                                    initial_delay_seconds=5,
                                    period_seconds=10,
                                ),
                                liveness_probe=k8s.core.v1.ProbeArgs(
                                    http_get=k8s.core.v1.HTTPGetActionArgs(
                                        path="/health",
                                        port=8081,
                                    ),
                                    initial_delay_seconds=5,
                                    period_seconds=10,
                                ),
                                volume_mounts=[
                                    k8s.core.v1.VolumeMountArgs(
                                        name="config",
                                        mount_path="/etc/coredns",
                                        read_only=True,
                                    ),
                                ],
                                resources=k8s.core.v1.ResourceRequirementsArgs(
                                    requests={"cpu": "50m", "memory": "32Mi"},
                                    limits={"memory": "128Mi"},
                                ),
                            ),
                        ],
                        volumes=[
                            k8s.core.v1.VolumeArgs(
                                name="config",
                                config_map=k8s.core.v1.ConfigMapVolumeSourceArgs(
                                    name="coredns-lan",
                                ),
                            ),
                        ],
                    ),
                ),
            ),
            opts=self._child_opts(provider=k8s_provider, depends_on=[sa, cm]),
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
