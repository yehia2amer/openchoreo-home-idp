"""Talos platform profile — placeholder for future implementation."""

from __future__ import annotations

from platforms.types import PlatformProfile

TALOS = PlatformProfile(
    name="talos",
    # Networking — TBD; default to Cilium since Talos ships with Cilium support
    gateway_mode="cilium",
    cni_mode="cilium",
    enable_kube_proxy_replacement=True,
    k8s_service_host="",
    # Node fixes — immutable OS, no container-node hacks needed
    requires_coredns_rewrite=False,
    requires_machine_id_fix=False,
    requires_bpf_mount_fix=False,
    # Cilium tuning
    cilium_auto_mount_bpf=True,
    cilium_host_network_gateway=False,
    cilium_cni_bin_path="",
    # Workflow
    workflow_template_mode="default",
    local_registry=True,
    # Bootstrap
    bootstrap_script="",
    cluster_name_config_key="",
)
