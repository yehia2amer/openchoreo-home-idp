# pyright: reportMissingImports=false

"""Resolve a platform name from Pulumi config into a ``PlatformProfile``."""

from __future__ import annotations

import pulumi

from platforms.types import PlatformProfile


def _clone_profile(base: PlatformProfile, **overrides: object) -> PlatformProfile:
    payload = {**base.__dict__, **overrides}
    return PlatformProfile(**payload)


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
        from platforms.k3d import K3D

        if enable_cilium:
            # k3d + Cilium: override gateway_mode to cilium but keep k3d quirks
            return _clone_profile(
                K3D,
                gateway_mode="cilium",
                cni_mode="cilium",
            )
        return K3D

    if enable_cilium:
        # Non-k3d + Cilium → treat as Rancher Desktop (current behaviour)
        from platforms.rancher_desktop import rancher_desktop

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
        bootstrap_script="",
        cluster_name_config_key="",
        workflow_template_mode="default",
        local_registry=True,
    )


def _from_name(name: str, cfg: pulumi.Config) -> PlatformProfile:
    """Map an explicit platform name to its profile."""
    name = name.lower().strip()

    if name == "k3d":
        from platforms.k3d import K3D

        return K3D
    if name == "gke":
        from platforms.gke import GKE_PROFILE

        return GKE_PROFILE
    if name in ("rancher-desktop", "rancher_desktop"):
        from platforms.rancher_desktop import rancher_desktop

        k8s_host = cfg.get("cilium_k8s_api_host") or ""
        return rancher_desktop(k8s_service_host=k8s_host)
    if name == "talos":
        from platforms.talos import talos

        return talos()
    if name in ("talos-baremetal", "talos_baremetal"):
        from platforms.talos_baremetal import talos_baremetal

        return talos_baremetal()

    raise ValueError(
        f"Unknown platform '{name}'. Supported values: gke, k3d, rancher-desktop, talos, talos-baremetal"
    )
