"""Talos Linux platform profile.

Talos is an immutable, API-driven Linux OS purpose-built for Kubernetes.
Key differences from Rancher Desktop / k3d:
- Pre-mounts cgroupv2 and bpffs → Cilium must NOT auto-mount
- KubePrism internal API proxy on localhost:7445
- No kernel module loading by workloads → SYS_MODULE dropped from Cilium
- Standard CNI binary path (/opt/cni/bin)
- No SSH/Lima layer → hostNetwork gateway not needed for port forwarding
"""

from __future__ import annotations

from platforms.types import PlatformProfile


def talos(k8s_service_host: str = "localhost") -> PlatformProfile:
    """Return a Talos Linux profile.

    Parameters
    ----------
    k8s_service_host:
        API-server endpoint for Cilium kube-proxy replacement.
        Defaults to ``localhost`` (Talos KubePrism).
    """
    return PlatformProfile(
        name="talos",
        cloud_provider="none",
        # Networking — Cilium as both CNI and Gateway API controller
        gateway_mode="cilium",
        cni_mode="cilium",
        enable_kube_proxy_replacement=True,
        k8s_service_host=k8s_service_host,
        k8s_service_port=7445,  # Talos KubePrism port
        # Node fixes — immutable OS, no container-node hacks needed
        requires_coredns_rewrite=False,
        requires_machine_id_fix=False,
        requires_bpf_mount_fix=False,
        # Cilium tuning — Talos pre-mounts BPF and cgroups
        cilium_auto_mount_bpf=False,
        cilium_host_network_gateway=False,  # No Lima SSH layer to bypass
        cilium_cni_bin_path="",  # Standard /opt/cni/bin
        # Workflow
        workflow_template_mode="default",
        local_registry=True,
        registry_mode="local",
        secrets_backend="openbao",
        tls_issuer_mode="self-signed",
        observability_mode="self-hosted",
        load_balancer_mode="local",
        storage_class="local-path",
        longhorn_enabled=False,
        external_snapshotter_enabled=False,
        # Bootstrap
        bootstrap_script="",
        cluster_name_config_key="",
    )
