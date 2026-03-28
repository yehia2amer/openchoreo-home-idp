"""Rancher Desktop platform profile."""

from __future__ import annotations

from platforms.types import PlatformProfile


def rancher_desktop(k8s_service_host: str = "") -> PlatformProfile:
    """Return a Rancher Desktop profile.

    Parameters
    ----------
    k8s_service_host:
        Direct API-server IP for Cilium kube-proxy replacement.
        Required when Cilium is the CNI.
    """
    return PlatformProfile(
        name="rancher-desktop",
        # Networking — Cilium replaces both CNI and gateway controller
        gateway_mode="cilium",
        cni_mode="cilium",
        enable_kube_proxy_replacement=True,
        k8s_service_host=k8s_service_host,
        # Node fixes
        requires_coredns_rewrite=False,
        requires_machine_id_fix=False,
        requires_bpf_mount_fix=True,
        # Cilium tuning
        cilium_auto_mount_bpf=True,
        cilium_host_network_gateway=True,
        cilium_cni_bin_path="/usr/libexec/cni",
        # Workflow
        workflow_template_mode="default",
        local_registry=True,
        # Bootstrap
        bootstrap_script="",
        cluster_name_config_key="",
    )
