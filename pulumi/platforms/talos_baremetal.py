from __future__ import annotations

from platforms.types import PlatformProfile


def talos_baremetal(
    k8s_service_host: str = "localhost",
    l2_ip_pool_cidrs: tuple[str, ...] = ("192.168.0.10-192.168.0.99",),
    l2_interfaces: tuple[str, ...] = ("enp7s0", "enp0s1", "enp0s25"),
) -> PlatformProfile:
    return PlatformProfile(
        name="talos-baremetal",
        gateway_mode="kgateway",
        cni_mode="cilium",
        enable_kube_proxy_replacement=True,
        k8s_service_host=k8s_service_host,
        k8s_service_port=7445,
        requires_coredns_rewrite=False,
        requires_machine_id_fix=False,
        requires_bpf_mount_fix=False,
        cilium_auto_mount_bpf=False,
        cilium_host_network_gateway=False,
        cilium_cni_bin_path="",
        workflow_template_mode="default",
        local_registry=False,
        workflow_template_urls=(
            "workflow-templates/checkout-source.yaml",
            "workflow-templates.yaml",
            "workflow-templates/publish-image.yaml",
            "workflow-templates/generate-workload.yaml",
        ),
        bootstrap_script="bootstrap_talos_baremetal.py",
        cluster_name_config_key="",
        cilium_bpf_host_legacy_routing=True,
        cilium_l2_announcements_enabled=True,
        cilium_l2_ip_pool_cidrs=l2_ip_pool_cidrs,
        cilium_l2_interfaces=l2_interfaces,
        cilium_pre_installed=True,
        gateway_api_crds_pre_installed=True,
    )
