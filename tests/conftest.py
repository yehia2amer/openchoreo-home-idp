"""
Pytest configuration and fixtures for OpenChoreo integration tests.
"""

import os
import ssl
from pathlib import Path
from typing import Generator

import hvac
import pytest
import requests
from kubernetes import client, config
from opensearchpy import OpenSearch
from prometheus_api_client import PrometheusConnect

from utils.auth_helpers import get_oauth_token
from utils.port_forward import PortForward


# =============================================================================
# Configuration
# =============================================================================


def get_env(key: str, default: str | None = None) -> str:
    """Get environment variable or raise if not set and no default."""
    value = os.environ.get(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} is required")
    return value


@pytest.fixture(scope="session")
def test_config() -> dict:
    """Test configuration from environment variables."""
    return {
        "kubeconfig": get_env("KUBECONFIG", str(Path.home() / ".kube" / "config")),
        "kube_context": get_env("KUBE_CONTEXT", "admin@openchoreo"),
        "domain_base": get_env("DOMAIN_BASE", "openchoreo.local"),
        "tls_enabled": get_env("TLS_ENABLED", "true").lower() == "true",
        "ca_cert_path": os.environ.get("CA_CERT_PATH", ""),
        "openbao_token": get_env("OPENBAO_TOKEN", "root"),
        "opensearch_user": get_env("OPENSEARCH_USER", "admin"),
        "opensearch_pass": get_env("OPENSEARCH_PASS", "ThisIsTheOpenSearchPassword1"),
        # Ports
        "control_plane_https_port": int(get_env("CP_HTTPS_PORT", "8443")),
        "data_plane_http_port": int(get_env("DP_HTTP_PORT", "19080")),
        "data_plane_https_port": int(get_env("DP_HTTPS_PORT", "19443")),
        "observer_port": int(get_env("OBSERVER_PORT", "11085")),
    }


# =============================================================================
# Kubernetes Client Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def k8s_config(test_config: dict) -> None:
    """Load Kubernetes configuration."""
    config.load_kube_config(
        config_file=test_config["kubeconfig"],
        context=test_config["kube_context"],
    )


@pytest.fixture(scope="session")
def k8s_core_api(k8s_config) -> client.CoreV1Api:
    """Kubernetes Core V1 API client."""
    return client.CoreV1Api()


@pytest.fixture(scope="session")
def k8s_apps_api(k8s_config) -> client.AppsV1Api:
    """Kubernetes Apps V1 API client."""
    return client.AppsV1Api()


@pytest.fixture(scope="session")
def k8s_custom_api(k8s_config) -> client.CustomObjectsApi:
    """Kubernetes Custom Objects API client."""
    return client.CustomObjectsApi()


@pytest.fixture(scope="session")
def k8s_networking_api(k8s_config) -> client.NetworkingV1Api:
    """Kubernetes Networking V1 API client."""
    return client.NetworkingV1Api()


# =============================================================================
# HTTP Session Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def http_session(test_config: dict) -> Generator[requests.Session, None, None]:
    """HTTP session with TLS configuration."""
    session = requests.Session()

    if test_config["tls_enabled"] and test_config["ca_cert_path"]:
        session.verify = test_config["ca_cert_path"]
    elif test_config["tls_enabled"]:
        # Disable SSL verification for self-signed certs (not recommended for production)
        session.verify = False
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    session.timeout = 30
    yield session
    session.close()


@pytest.fixture(scope="session")
def control_plane_base_url(test_config: dict) -> str:
    """Base URL for control plane services."""
    protocol = "https" if test_config["tls_enabled"] else "http"
    port = test_config["control_plane_https_port"]
    return f"{protocol}://{test_config['domain_base']}:{port}"


@pytest.fixture(scope="session")
def thunder_base_url(test_config: dict) -> str:
    """Base URL for Thunder IdP."""
    protocol = "https" if test_config["tls_enabled"] else "http"
    port = test_config["control_plane_https_port"]
    return f"{protocol}://thunder.{test_config['domain_base']}:{port}"


@pytest.fixture(scope="session")
def api_base_url(test_config: dict) -> str:
    """Base URL for OpenChoreo API."""
    protocol = "https" if test_config["tls_enabled"] else "http"
    port = test_config["control_plane_https_port"]
    return f"{protocol}://api.{test_config['domain_base']}:{port}"


@pytest.fixture(scope="session")
def data_plane_base_url(test_config: dict) -> str:
    """Base URL for data plane gateway."""
    protocol = "https" if test_config["tls_enabled"] else "http"
    port = (
        test_config["data_plane_https_port"]
        if test_config["tls_enabled"]
        else test_config["data_plane_http_port"]
    )
    return f"{protocol}://{test_config['domain_base']}:{port}"


@pytest.fixture(scope="session")
def observer_base_url(test_config: dict) -> str:
    """Base URL for Observer service."""
    protocol = "https" if test_config["tls_enabled"] else "http"
    port = test_config["observer_port"]
    return f"{protocol}://observer.{test_config['domain_base']}:{port}"


# =============================================================================
# Authentication Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def oauth_token(thunder_base_url: str, http_session: requests.Session) -> str:
    """OAuth2 access token from Thunder."""
    return get_oauth_token(
        token_url=f"{thunder_base_url}/oauth2/token",
        client_id=os.environ.get("OAUTH_CLIENT_ID", "backstage"),
        client_secret=os.environ.get("OAUTH_CLIENT_SECRET", "backstage-secret"),
        session=http_session,
    )


@pytest.fixture(scope="session")
def auth_headers(oauth_token: str) -> dict:
    """Authorization headers with Bearer token."""
    return {"Authorization": f"Bearer {oauth_token}"}


# =============================================================================
# Service Client Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def openbao_client(
    test_config: dict, k8s_core_api: client.CoreV1Api
) -> Generator[hvac.Client, None, None]:
    """OpenBao (Vault) client via port-forward."""
    with PortForward(
        k8s_core_api,
        namespace="openbao",
        pod_name="openbao-0",
        remote_port=8200,
    ) as local_port:
        vault_client = hvac.Client(
            url=f"http://localhost:{local_port}",
            token=test_config["openbao_token"],
        )
        yield vault_client


@pytest.fixture(scope="session")
def opensearch_client(
    test_config: dict, k8s_core_api: client.CoreV1Api
) -> Generator[OpenSearch, None, None]:
    """OpenSearch client via port-forward."""
    with PortForward(
        k8s_core_api,
        namespace="openchoreo-observability-plane",
        pod_name="opensearch-cluster-master-0",
        remote_port=9200,
    ) as local_port:
        os_client = OpenSearch(
            hosts=[{"host": "localhost", "port": local_port}],
            http_auth=(test_config["opensearch_user"], test_config["opensearch_pass"]),
            use_ssl=True,
            verify_certs=False,
            ssl_show_warn=False,
        )
        yield os_client


@pytest.fixture(scope="session")
def prometheus_client(k8s_core_api: client.CoreV1Api) -> Generator[PrometheusConnect, None, None]:
    """Prometheus client via port-forward."""
    with PortForward(
        k8s_core_api,
        namespace="openchoreo-observability-plane",
        pod_name="prometheus-server-0",
        remote_port=9090,
    ) as local_port:
        prom_client = PrometheusConnect(
            url=f"http://localhost:{local_port}",
            disable_ssl=True,
        )
        yield prom_client


# =============================================================================
# Namespace Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def namespaces() -> dict:
    """Namespace mapping for all OpenChoreo components."""
    return {
        "cilium": "kube-system",
        "cert_manager": "cert-manager",
        "external_secrets": "external-secrets",
        "openbao": "openbao",
        "thunder": "thunder",
        "control_plane": "openchoreo-control-plane",
        "data_plane": "openchoreo-data-plane",
        "workflow_plane": "openchoreo-workflow-plane",
        "observability_plane": "openchoreo-observability-plane",
        "flux": "flux-system",
    }


# =============================================================================
# Utility Fixtures
# =============================================================================


@pytest.fixture
def port_forward_factory(k8s_core_api: client.CoreV1Api):
    """Factory for creating port-forward contexts."""

    def _create(namespace: str, pod_name: str, remote_port: int) -> PortForward:
        return PortForward(k8s_core_api, namespace, pod_name, remote_port)

    return _create
