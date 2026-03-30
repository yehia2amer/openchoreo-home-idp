"""Resolve a platform name from Pulumi config into a ``PlatformProfile``."""

from __future__ import annotations

import pulumi

from platforms.k3d import K3D
from platforms.rancher_desktop import rancher_desktop
from platforms.talos import talos
from platforms.talos_baremetal import talos_baremetal
from platforms.types import PlatformProfile


def resolve_platform(cfg: pulumi.Config) -> PlatformProfile:
    """Read ``platform`` from stack config and return the matching profile.

    Falls back to legacy fields (``is_k3d``, ``enable_cilium``) when
    ``platform`` is not set, so existing stacks keep working.
    """
    platform = cfg.get("platform") or ""

    if platform:
        return _from_name(platform, cfg)

    # ── Legacy fallback ──
    is_k3d = cfg.get_bool("is_k3d") or False
    enable_cilium = cfg.get_bool("enable_cilium") or False

    if is_k3d:
        if enable_cilium:
            # k3d + Cilium: override gateway_mode to cilium but keep k3d quirks
            return PlatformProfile(
                name="k3d",
                gateway_mode="cilium",
                cni_mode="cilium",
                enable_kube_proxy_replacement=False,
                k8s_service_host="",
                k8s_service_port=6443,
                requires_coredns_rewrite=True,
                requires_machine_id_fix=True,
                requires_bpf_mount_fix=False,
                cilium_auto_mount_bpf=False,
                cilium_host_network_gateway=False,
                cilium_cni_bin_path="",
                workflow_template_mode="k3d-patch",
                local_registry=True,
                bootstrap_script="bootstrap_k3d.py",
                cluster_name_config_key="k3d_cluster_name",
            )
        return K3D

    if enable_cilium:
        # Non-k3d + Cilium → treat as Rancher Desktop (current behaviour)
        k8s_host = cfg.get("cilium_k8s_api_host") or ""
        return rancher_desktop(k8s_service_host=k8s_host)

    # Non-k3d, no Cilium → minimal profile (kgateway, no special fixes)
    return PlatformProfile(
        name="generic",
        gateway_mode="kgateway",
        cni_mode="default",
        enable_kube_proxy_replacement=False,
        k8s_service_host="",
        k8s_service_port=6443,
        requires_coredns_rewrite=False,
        requires_machine_id_fix=False,
        requires_bpf_mount_fix=False,
        cilium_auto_mount_bpf=False,
        cilium_host_network_gateway=False,
        cilium_cni_bin_path="",
        workflow_template_mode="default",
        local_registry=True,
        bootstrap_script="",
        cluster_name_config_key="",
    )


def _from_name(name: str, cfg: pulumi.Config) -> PlatformProfile:
    """Map an explicit platform name to its profile."""
    name = name.lower().strip()

    if name == "k3d":
        return K3D
    if name in ("rancher-desktop", "rancher_desktop"):
        k8s_host = cfg.get("cilium_k8s_api_host") or ""
        return rancher_desktop(k8s_service_host=k8s_host)
    if name == "talos":
        return talos()
    if name in ("talos-baremetal", "talos_baremetal"):
        return talos_baremetal()

    raise ValueError(f"Unknown platform '{name}'. Supported values: k3d, rancher-desktop, talos, talos-baremetal")
