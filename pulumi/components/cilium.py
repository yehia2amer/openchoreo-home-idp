"""Cilium CNI + Gateway API component — optional, installed before other components.

When enabled (enable_cilium=true), installs Cilium 1.19.2 as both the CNI and
Gateway API controller via the official OCI Helm chart.  This replaces Flannel
(CNI) and kgateway (Gateway API).

Capabilities:
- eBPF-based networking (replaces Flannel)
- eBPF kube-proxy replacement (on non-k3d environments)
- Native Gateway API v1.4.1 controller (replaces kgateway)
- Hubble observability (relay + UI)
- L7 network policies via built-in Envoy

Notes:
  kubeProxyReplacement is automatically set based on the deployment target:
  - k3d:  false — Cilium eBPF on the container's eth0 blocks Docker
    port-forwarded TCP to the API server.  Gateway API requires
    kubeProxyReplacement=true, so on k3d Cilium acts as CNI only
    and kgateway handles Gateway API.
  - Other (e.g. Rancher Desktop, bare-metal):  true — full kube-proxy
    replacement with Gateway API support.

  References:
  - https://docs.cilium.io/en/stable/installation/k3s/
"""

from __future__ import annotations

import pulumi
import pulumi_kubernetes as k8s

from config import OpenChoreoConfig

CILIUM_CHART_OCI = "oci://quay.io/cilium/charts/cilium"
CILIUM_VERSION = "1.19.2"
NS_CILIUM = "kube-system"


def _ensure_bpf_shared_mount(
    k8s_provider: k8s.Provider,
    depends: list[pulumi.Resource] | None = None,
) -> k8s.batch.v1.Job:
    """Run a privileged Job on every node to make /sys/fs/bpf a shared mount.

    Rancher Desktop (Lima) and some bare-metal setups don't mount /sys/fs/bpf
    with shared propagation, which causes Cilium's mount-bpf-fs init container
    to fail with 'not a shared or slave mount'.  This one-shot Job uses
    nsenter to fix the host mount namespace before Cilium starts.
    """
    return k8s.batch.v1.Job(
        "bpf-mount-fix",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name="bpf-mount-fix",
            namespace="kube-system",
        ),
        spec=k8s.batch.v1.JobSpecArgs(
            ttl_seconds_after_finished=60,
            template=k8s.core.v1.PodTemplateSpecArgs(
                spec=k8s.core.v1.PodSpecArgs(
                    host_pid=True,
                    host_network=True,
                    node_selector={"kubernetes.io/os": "linux"},
                    tolerations=[k8s.core.v1.TolerationArgs(operator="Exists")],
                    restart_policy="Never",
                    containers=[
                        k8s.core.v1.ContainerArgs(
                            name="fix",
                            image="busybox:1.37",
                            command=[
                                "nsenter",
                                "-t",
                                "1",
                                "-m",
                                "--",
                                "sh",
                                "-c",
                                "mount --make-rshared / 2>/dev/null; echo 'root mount is now rshared'",
                            ],
                            security_context=k8s.core.v1.SecurityContextArgs(privileged=True),
                        )
                    ],
                ),
            ),
        ),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=depends or [],
            custom_timeouts=pulumi.CustomTimeouts(create="120s"),
        ),
    )


def deploy(
    cfg: OpenChoreoConfig,
    k8s_provider: k8s.Provider,
    depends: list[pulumi.Resource] | None = None,
) -> k8s.helm.v4.Chart:
    """Install Cilium CNI + Gateway API controller via OCI Helm chart."""

    p = cfg.platform  # Platform profile drives all environment-specific tuning
    kpr_enabled = p.enable_kube_proxy_replacement

    # On platforms that need it (e.g. Rancher Desktop), fix BPF mount
    # propagation before Cilium starts.
    extra_depends = list(depends or [])
    if p.requires_bpf_mount_fix:
        bpf_fix = _ensure_bpf_shared_mount(k8s_provider, depends)
        extra_depends.append(bpf_fix)

    values: dict = {
        "kubeProxyReplacement": kpr_enabled,
        # Gateway API controller (requires kubeProxyReplacement=true).
        # hostNetwork.enabled makes envoy bind directly on the node's host
        # ports so Lima/Rancher Desktop's SSH port-forwarder can detect them
        # and forward traffic from macOS.  Without it, Cilium uses BPF-only
        # listeners that are invisible to Lima's guest-agent.
        "gatewayAPI": {
            "enabled": kpr_enabled,
            "hostNetwork": {"enabled": p.cilium_host_network_gateway},
        },
        # IPAM — use Kubernetes pod CIDR allocation (k3s default: 10.42.0.0/16)
        "ipam": {
            "mode": "kubernetes",
            "operator": {"clusterPoolIPv4PodCIDRList": ["10.42.0.0/16"]},
        },
        # BPF/cgroup mount strategy:
        # - k3d: the bootstrap script pre-mounts BPF with shared propagation,
        #   so autoMount must be disabled (Docker mount propagation limitation).
        # - Rancher Desktop / bare-metal: let Cilium auto-mount BPF and cgroup
        #   since the host/VM doesn't pre-configure shared propagation.
        "bpf": {"autoMount": {"enabled": p.cilium_auto_mount_bpf}},
        "cgroup": {
            "autoMount": {"enabled": p.cilium_auto_mount_bpf},
            "hostRoot": "/sys/fs/cgroup",
        },
        # Socket-based load balancing — required alongside kubeProxyReplacement
        # so the cgroup/connect eBPF hook properly translates ClusterIPs.
        "socketLB": {"enabled": kpr_enabled},
        # Hubble observability
        "hubble": {
            "relay": {"enabled": True},
            "ui": {"enabled": True},
        },
        # L7 proxy for application-aware policies
        "l7Proxy": True,
        # Operator
        "operator": {"replicas": 1},
        # Prefer cached images in local dev
        "image": {"pullPolicy": "IfNotPresent"},
        # Label envoy pods so OpenChoreo NetworkPolicies allow gateway ingress
        "envoy": {"podLabels": {"openchoreo.dev/system-component": "gateway"}},
    }

    # When replacing kube-proxy, Cilium must know the API server's direct IP
    if kpr_enabled and p.k8s_service_host:
        values["k8sServiceHost"] = p.k8s_service_host
        values["k8sServicePort"] = 6443

    # Platform-specific CNI binary path override
    if p.cilium_cni_bin_path:
        values["cni"] = {"binPath": p.cilium_cni_bin_path}

    return k8s.helm.v4.Chart(
        "cilium",
        k8s.helm.v4.ChartArgs(
            chart=CILIUM_CHART_OCI,
            version=CILIUM_VERSION,
            namespace=NS_CILIUM,
            values=values,
        ),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=extra_depends,
            custom_timeouts=pulumi.CustomTimeouts(create="600s"),
        ),
    )
