"""Typed configuration loader for OpenChoreo Pulumi stack."""

# pyright: reportMissingImports=false

from __future__ import annotations

from pathlib import Path

from dataclasses import dataclass

import pulumi

from platforms import PlatformProfile, resolve_platform

# ──────────────────────────────────────────────────────────────
# Constants — single source of truth for all magic strings
# ──────────────────────────────────────────────────────────────

# Helm chart OCI registries
OPENCHOREO_CHART_REPO = "oci://ghcr.io/openchoreo/helm-charts"
CERT_MANAGER_CHART_REPO = "oci://quay.io/jetstack/charts"
EXTERNAL_SECRETS_CHART_REPO = "oci://ghcr.io/external-secrets/charts"
KGATEWAY_CHART_REPO = "oci://cr.kgateway.dev/kgateway-dev/charts"
OPENBAO_CHART_REPO = "oci://ghcr.io/openbao/charts"
THUNDER_CHART_REPO = "oci://ghcr.io/asgardeo/helm-charts"

# Helm chart HTTP repositories
DOCKER_REGISTRY_HELM_REPO = "https://twuni.github.io/docker-registry.helm"

# Namespace names
NS_CONTROL_PLANE = "openchoreo-control-plane"
NS_DATA_PLANE = "openchoreo-data-plane"
NS_WORKFLOW_PLANE = "openchoreo-workflow-plane"
NS_OBSERVABILITY_PLANE = "openchoreo-observability-plane"
NS_OPENBAO = "openbao"
NS_CERT_MANAGER = "cert-manager"
NS_EXTERNAL_SECRETS = "external-secrets"
NS_THUNDER = "thunder"
NS_FLUX_SYSTEM = "flux-system"

# Well-known Kubernetes resource names
SECRET_GATEWAY_CA = "cluster-gateway-ca"
SECRET_AGENT_TLS = "cluster-agent-tls"
SECRET_BACKSTAGE = "backstage-secrets"
SECRET_OPENSEARCH_ADMIN = "opensearch-admin-credentials"
SECRET_OBSERVER_OPENSEARCH = "observer-opensearch-credentials"
SECRET_OBSERVER = "observer-secret"
SA_ESO_OPENBAO = "external-secrets-openbao"
CLUSTER_SECRET_STORE_NAME = "default"

# TLS CA chain resource names (matches official guide Step 2)
ISSUER_SELFSIGNED_BOOTSTRAP = "selfsigned-bootstrap"
CERT_OPENCHOREO_CA = "openchoreo-ca"
SECRET_OPENCHOREO_CA = "openchoreo-ca-secret"
ISSUER_OPENCHOREO_CA = "openchoreo-ca"
CERT_CP_GATEWAY_TLS = "cp-gateway-tls"
CERT_DP_GATEWAY_TLS = "dp-gateway-tls"
CERT_OP_GATEWAY_TLS = "op-gateway-tls"

# Thunder in-cluster service URL (used by observability plane for direct service calls)
THUNDER_INTERNAL_BASE = "http://thunder-service.thunder.svc.cluster.local:8090"

# Flux install manifest — local copy to avoid gRPC timeout on 377KB remote YAML
# Original: https://github.com/fluxcd/flux2/releases/latest/download/install.yaml
FLUX_INSTALL_URL = str(Path(__file__).parent / "flux-install.yaml")

# OpenChoreo CRD API group/version
OPENCHOREO_API_VERSION = "openchoreo.dev/v1alpha1"

# Timeouts (seconds) — generous for slow internet / laptop
TIMEOUT_DEFAULT = 1200
TIMEOUT_OPENSEARCH = 1800
TIMEOUT_OBS_PLANE = 2400
TIMEOUT_WAIT = 600
TIMEOUT_TLS_WAIT = 240
TIMEOUT_FLUX_WAIT = 1200  # 20 min — bare-metal image pulls are slow

# Sleep durations (seconds)
SLEEP_AFTER_GATEWAY_API = 10
SLEEP_AFTER_OPENBAO = 15
SLEEP_AFTER_THUNDER = 15
SLEEP_AFTER_ESO_SYNC = 15


@dataclass
class OpenChoreoConfig:
    """All configuration values for the OpenChoreo stack."""

    # Platform profile — first-class platform identity
    platform: PlatformProfile

    # Cluster connection
    kubeconfig_path: str
    kubeconfig_context: str

    # Domain & networking
    domain_base: str
    tls_enabled: bool
    cp_http_port: int
    cp_https_port: int
    dp_http_port: int
    dp_https_port: int
    wp_argo_port: int
    wp_registry_port: int
    registry_node_port: int
    gateway_pin_ip: str
    gateway_pin_ip_dp: str
    gateway_pin_ip_op: str
    coredns_bind_ip: str
    op_http_port: int
    op_https_port: int
    opensearch_dashboards_port: int

    # Versions
    openchoreo_ref: str
    openchoreo_version: str
    thunder_version: str
    gateway_api_version: str
    cert_manager_version: str
    external_secrets_version: str
    kgateway_version: str
    openbao_version: str
    docker_registry_version: str
    logs_opensearch_version: str
    traces_opensearch_version: str
    metrics_prometheus_version: str

    # Credentials
    openbao_root_token: str
    opensearch_username: str
    opensearch_password: str
    github_pat: str

    # GitOps
    gitops_repo_url: str
    gitops_repo_branch: str
    enable_flux: bool
    enable_observability: bool
    enable_demo_app_bootstrap: bool

    # Flux Telegram notifications (optional)
    flux_telegram_bot_token: str
    flux_telegram_chat_id: str

    # k3d-specific (used by observability machine-id fix)
    k3d_cluster_name: str

    # Derived values
    raw_base: str
    scheme: str
    cp_port: int
    dp_port: int
    op_port: int
    backstage_url: str
    api_url: str
    thunder_url: str
    observer_url: str
    dp_http_url: str
    dp_https_url: str

    # Derived URLs
    gateway_api_crds_url: str
    coredns_rewrite_url: str
    thunder_values_url: str
    workflow_templates_urls: list[str]

    @property
    def thunder_chart(self) -> str:
        return f"{THUNDER_CHART_REPO}/thunder"

    @property
    def cp_chart(self) -> str:
        return f"{OPENCHOREO_CHART_REPO}/openchoreo-control-plane"

    @property
    def dp_chart(self) -> str:
        return f"{OPENCHOREO_CHART_REPO}/openchoreo-data-plane"

    @property
    def wp_chart(self) -> str:
        return f"{OPENCHOREO_CHART_REPO}/openchoreo-workflow-plane"

    @property
    def obs_chart(self) -> str:
        return f"{OPENCHOREO_CHART_REPO}/openchoreo-observability-plane"

    @property
    def logs_chart(self) -> str:
        return f"{OPENCHOREO_CHART_REPO}/observability-logs-opensearch"

    @property
    def traces_chart(self) -> str:
        return f"{OPENCHOREO_CHART_REPO}/observability-tracing-opensearch"

    @property
    def metrics_chart(self) -> str:
        return f"{OPENCHOREO_CHART_REPO}/observability-metrics-prometheus"


def load_config() -> OpenChoreoConfig:
    """Load Pulumi config and compute derived values."""
    cfg = pulumi.Config()

    # Cluster connection
    kubeconfig_path = cfg.get("kubeconfig_path") or "~/.kube/config"
    kubeconfig_context = cfg.get("kubeconfig_context") or ""

    # Domain & networking
    domain_base = cfg.get("domain_base") or "openchoreo.localhost"
    tls_enabled = cfg.get_bool("tls_enabled") or False
    cp_http_port = cfg.get_int("cp_http_port") or 8080
    cp_https_port = cfg.get_int("cp_https_port") or 8443
    dp_http_port = cfg.get_int("dp_http_port") or 19080
    dp_https_port = cfg.get_int("dp_https_port") or 19443
    wp_argo_port = cfg.get_int("wp_argo_port") or 10081
    wp_registry_port = cfg.get_int("wp_registry_port") or 10082
    registry_node_port = cfg.get_int("registry_node_port") or 0
    gateway_pin_ip = cfg.get("gateway_pin_ip") or ""
    gateway_pin_ip_dp = cfg.get("gateway_pin_ip_dp") or ""
    gateway_pin_ip_op = cfg.get("gateway_pin_ip_op") or ""
    coredns_bind_ip = cfg.get("coredns_bind_ip") or ""
    op_http_port = cfg.get_int("op_http_port") or 11080
    op_https_port = cfg.get_int("op_https_port") or 11085
    opensearch_dashboards_port = cfg.get_int("opensearch_dashboards_port") or 11081

    # Versions
    openchoreo_ref = cfg.get("openchoreo_ref") or "release-v1.0"
    openchoreo_version = cfg.get("openchoreo_version") or "1.0.0"
    thunder_version = cfg.get("thunder_version") or "0.28.0"
    gateway_api_version = cfg.get("gateway_api_version") or "v1.4.1"
    cert_manager_version = cfg.get("cert_manager_version") or "v1.19.4"
    external_secrets_version = cfg.get("external_secrets_version") or "2.0.1"
    kgateway_version = cfg.get("kgateway_version") or "v2.2.1"
    openbao_version = cfg.get("openbao_version") or "0.25.6"
    docker_registry_version = cfg.get("docker_registry_version") or "3.0.0"
    logs_opensearch_version = cfg.get("logs_opensearch_version") or "0.3.11"
    traces_opensearch_version = cfg.get("traces_opensearch_version") or "0.3.10"
    metrics_prometheus_version = cfg.get("metrics_prometheus_version") or "0.2.5"

    # Credentials — warn on non-dev stacks when using insecure defaults.
    # Use cfg.get() for plain strings needed by dynamic providers.
    stack_name = pulumi.get_stack()
    is_dev_stack = stack_name in ("dev", "rancher-desktop", "local", "test", "talos", "talos-baremetal")

    openbao_root_token = cfg.get("openbao_root_token")
    if not openbao_root_token:
        if not is_dev_stack:
            raise pulumi.ConfigMissingError("openchoreo:openbao_root_token", secret=True)
        openbao_root_token = "root"

    opensearch_username = cfg.get("opensearch_username") or "admin"

    opensearch_password = cfg.get("opensearch_password")
    if not opensearch_password:
        if not is_dev_stack:
            raise pulumi.ConfigMissingError("openchoreo:opensearch_password", secret=True)
        opensearch_password = "ThisIsTheOpenSearchPassword1"

    github_pat = cfg.get("github_pat") or ""

    # GitOps
    gitops_repo_url = cfg.get("gitops_repo_url") or ""
    gitops_repo_branch = cfg.get("gitops_repo_branch") or "main"
    enable_flux = cfg.get_bool("enable_flux") or False
    enable_observability = cfg.get_bool("enable_observability") or False
    enable_demo_app_bootstrap = cfg.get_bool("enable_demo_app_bootstrap") or False

    # Flux Telegram notifications (optional)
    flux_telegram_bot_token = cfg.get("flux_telegram_bot_token") or ""
    flux_telegram_chat_id = cfg.get("flux_telegram_chat_id") or ""

    # k3d-specific (still needed for docker exec in observability machine-id fix)
    k3d_cluster_name = cfg.get("k3d_cluster_name") or "openchoreo"

    # ── Platform profile resolution ──
    platform = resolve_platform(cfg)

    # Derived values
    raw_base = f"https://raw.githubusercontent.com/openchoreo/openchoreo/{openchoreo_ref}"
    scheme = "https" if tls_enabled else "http"
    cp_port = cp_https_port if tls_enabled else cp_http_port
    dp_port = dp_https_port if tls_enabled else dp_http_port
    op_port = op_https_port if tls_enabled else op_http_port
    backstage_url = f"{scheme}://{domain_base}:{cp_port}"
    api_url = f"{scheme}://api.{domain_base}:{cp_port}"
    thunder_url = f"{scheme}://thunder.{domain_base}:{cp_port}"
    observer_url = f"{scheme}://observer.{domain_base}:{op_port}"
    dp_http_url = f"http://{domain_base}:{dp_http_port}"
    dp_https_url = f"https://{domain_base}:{dp_https_port}"

    # Derived URLs
    gateway_api_crds_url = (
        f"https://github.com/kubernetes-sigs/gateway-api/releases/download"
        f"/{gateway_api_version}/experimental-install.yaml"
    )
    coredns_rewrite_url = f"{raw_base}/install/k3d/common/coredns-custom.yaml"
    thunder_values_url = f"{raw_base}/install/k3d/common/values-thunder.yaml"
    wt_base = f"{raw_base}/samples/getting-started"
    if platform.workflow_template_urls:
        workflow_templates_urls = [f"{wt_base}/{path}" for path in platform.workflow_template_urls]
    else:
        # Default: k3d-specific URLs (backward compatible)
        workflow_templates_urls = [
            f"{wt_base}/workflow-templates/checkout-source.yaml",
            f"{wt_base}/workflow-templates.yaml",
            f"{wt_base}/workflow-templates/publish-image-k3d.yaml",
            f"{wt_base}/workflow-templates/generate-workload-k3d.yaml",
        ]

    return OpenChoreoConfig(
        platform=platform,
        kubeconfig_path=kubeconfig_path,
        kubeconfig_context=kubeconfig_context,
        domain_base=domain_base,
        tls_enabled=tls_enabled,
        cp_http_port=cp_http_port,
        cp_https_port=cp_https_port,
        dp_http_port=dp_http_port,
        dp_https_port=dp_https_port,
        wp_argo_port=wp_argo_port,
        wp_registry_port=wp_registry_port,
        registry_node_port=registry_node_port,
        gateway_pin_ip=gateway_pin_ip,
        gateway_pin_ip_dp=gateway_pin_ip_dp,
        gateway_pin_ip_op=gateway_pin_ip_op,
        coredns_bind_ip=coredns_bind_ip,
        op_http_port=op_http_port,
        op_https_port=op_https_port,
        opensearch_dashboards_port=opensearch_dashboards_port,
        openchoreo_ref=openchoreo_ref,
        openchoreo_version=openchoreo_version,
        thunder_version=thunder_version,
        gateway_api_version=gateway_api_version,
        cert_manager_version=cert_manager_version,
        external_secrets_version=external_secrets_version,
        kgateway_version=kgateway_version,
        openbao_version=openbao_version,
        docker_registry_version=docker_registry_version,
        logs_opensearch_version=logs_opensearch_version,
        traces_opensearch_version=traces_opensearch_version,
        metrics_prometheus_version=metrics_prometheus_version,
        openbao_root_token=openbao_root_token,
        opensearch_username=opensearch_username,
        opensearch_password=opensearch_password,
        github_pat=github_pat,
        gitops_repo_url=gitops_repo_url,
        gitops_repo_branch=gitops_repo_branch,
        enable_flux=enable_flux,
        enable_observability=enable_observability,
        enable_demo_app_bootstrap=enable_demo_app_bootstrap,
        flux_telegram_bot_token=flux_telegram_bot_token,
        flux_telegram_chat_id=flux_telegram_chat_id,
        k3d_cluster_name=k3d_cluster_name,
        raw_base=raw_base,
        scheme=scheme,
        cp_port=cp_port,
        dp_port=dp_port,
        op_port=op_port,
        backstage_url=backstage_url,
        api_url=api_url,
        thunder_url=thunder_url,
        observer_url=observer_url,
        dp_http_url=dp_http_url,
        dp_https_url=dp_https_url,
        gateway_api_crds_url=gateway_api_crds_url,
        coredns_rewrite_url=coredns_rewrite_url,
        thunder_values_url=thunder_values_url,
        workflow_templates_urls=workflow_templates_urls,
    )
