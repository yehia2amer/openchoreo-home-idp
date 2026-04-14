"""GKE platform profile."""

from __future__ import annotations

from platforms.types import PlatformProfile


GKE_PROFILE = PlatformProfile(
    name="gke",
    cloud_provider="gcp",
    gateway_mode="cloud",
    cni_mode="cloud",
    enable_kube_proxy_replacement=False,
    k8s_service_host="",
    k8s_service_port=443,
    requires_coredns_rewrite=False,
    requires_machine_id_fix=False,
    requires_bpf_mount_fix=False,
    cilium_auto_mount_bpf=False,
    cilium_host_network_gateway=False,
    cilium_cni_bin_path="",
    workflow_template_mode="default",
    local_registry=False,
    registry_mode="cloud",
    secrets_backend="gcp-sm",
    tls_issuer_mode="gcp-cas",
    observability_mode="cloud",
    load_balancer_mode="cloud",
    storage_class="premium-rwo",
    longhorn_enabled=False,
    external_snapshotter_enabled=False,
    workflow_template_urls=(
        "workflow-templates/checkout-source.yaml",
        "workflow-templates.yaml",
        "workflow-templates/publish-image.yaml",
        "workflow-templates/generate-workload.yaml",
    ),
    bootstrap_script="",
    cluster_name_config_key="gcp_gke_cluster_name",
    cilium_pre_installed=True,
    gateway_api_crds_pre_installed=True,
)
