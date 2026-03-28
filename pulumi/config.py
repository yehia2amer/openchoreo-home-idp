"""Typed configuration loader for OpenChoreo Pulumi stack."""

from __future__ import annotations

from dataclasses import dataclass

import pulumi

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

# Thunder in-cluster service URL (used by observability plane for direct service calls)
THUNDER_INTERNAL_BASE = "http://thunder-service.thunder.svc.cluster.local:8090"

# Flux install manifest URL
FLUX_INSTALL_URL = "https://github.com/fluxcd/flux2/releases/latest/download/install.yaml"

# OpenChoreo CRD API group/version
OPENCHOREO_API_VERSION = "openchoreo.dev/v1alpha1"

# Timeouts (seconds) — generous for slow internet / laptop
TIMEOUT_DEFAULT = 1200
TIMEOUT_OPENSEARCH = 1800
TIMEOUT_OBS_PLANE = 2400
TIMEOUT_WAIT = 600
TIMEOUT_TLS_WAIT = 240

# Sleep durations (seconds)
SLEEP_AFTER_GATEWAY_API = 10
SLEEP_AFTER_OPENBAO = 15
SLEEP_AFTER_THUNDER = 15
SLEEP_AFTER_ESO_SYNC = 15


@dataclass
class OpenChoreoConfig:
    """All configuration values for the OpenChoreo stack."""

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
    enable_cilium: bool

    # Cilium-specific (used when kubeProxyReplacement is enabled, i.e. non-k3d)
    cilium_k8s_api_host: str

    # k3d-specific
    is_k3d: bool
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

    # Credentials — plain strings needed by dynamic providers and Command interpolation.
    # Only github_pat is encrypted in Pulumi.dev.yaml via `pulumi config set --secret`;
    # the others use dev-mode defaults and are NOT secret-encrypted.
    openbao_root_token = cfg.get("openbao_root_token") or "root"
    opensearch_username = cfg.get("opensearch_username") or "admin"
    opensearch_password = cfg.get("opensearch_password") or "ThisIsTheOpenSearchPassword1"
    github_pat = cfg.get("github_pat") or ""

    # GitOps
    gitops_repo_url = cfg.get("gitops_repo_url") or ""
    gitops_repo_branch = cfg.get("gitops_repo_branch") or "main"
    enable_flux = cfg.get_bool("enable_flux") or False
    enable_observability = cfg.get_bool("enable_observability") or False
    enable_cilium = cfg.get_bool("enable_cilium") or False

    # Cilium-specific
    cilium_k8s_api_host = cfg.get("cilium_k8s_api_host") or ""

    # k3d-specific
    is_k3d = cfg.get_bool("is_k3d") or False
    k3d_cluster_name = cfg.get("k3d_cluster_name") or "openchoreo"

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
    workflow_templates_urls = [
        f"{wt_base}/workflow-templates/checkout-source.yaml",
        f"{wt_base}/workflow-templates.yaml",
        f"{wt_base}/workflow-templates/publish-image-k3d.yaml",
        f"{wt_base}/workflow-templates/generate-workload-k3d.yaml",
    ]

    return OpenChoreoConfig(
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
        enable_cilium=enable_cilium,
        cilium_k8s_api_host=cilium_k8s_api_host,
        is_k3d=is_k3d,
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
