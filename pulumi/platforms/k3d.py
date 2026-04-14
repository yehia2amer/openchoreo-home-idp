"""k3d platform profile."""

from __future__ import annotations

from platforms.types import PlatformProfile

K3D = PlatformProfile(
    name="k3d",
    cloud_provider="none",
    # Networking
    gateway_mode="kgateway",
    cni_mode="flannel",
    enable_kube_proxy_replacement=False,
    k8s_service_host="",
    k8s_service_port=6443,
    # Node fixes
    requires_coredns_rewrite=True,
    requires_machine_id_fix=True,
    requires_bpf_mount_fix=False,
    # Cilium tuning (only relevant if user force-enables Cilium on k3d)
    cilium_auto_mount_bpf=False,
    cilium_host_network_gateway=False,
    cilium_cni_bin_path="",
    # Workflow
    workflow_template_mode="k3d-patch",
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
    bootstrap_script="bootstrap_k3d.py",
    cluster_name_config_key="k3d_cluster_name",
)
