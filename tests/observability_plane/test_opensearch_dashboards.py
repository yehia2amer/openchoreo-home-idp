"""Tests for OpenSearch Dashboards."""

import pytest
import requests
from kubernetes import client

from utils.k8s_helpers import check_deployment_ready
from utils.port_forward import PortForward


@pytest.mark.observability
@pytest.mark.smoke
class TestOpenSearchDashboardsHealth:
    """Test OpenSearch Dashboards health."""

    def test_dashboards_deployment_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify OpenSearch Dashboards deployment is ready."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["observability_plane"], "opensearch-dashboards"
        )

        assert is_ready, f"OpenSearch Dashboards not ready: {message}"

    def test_dashboards_status_api(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
    ):
        """Verify Dashboards status API responds."""
        with PortForward(
            k8s_core_api,
            namespaces["observability_plane"],
            "opensearch-dashboards",
            5601,
        ) as local_port:
            response = requests.get(
                f"http://localhost:{local_port}/api/status",
                timeout=30,
            )

            # May require auth, but should respond
            assert response.status_code in [200, 401, 403], (
                f"Dashboards status failed: {response.status_code}"
            )


@pytest.mark.observability
class TestOpenSearchDashboardsConnectivity:
    """Test OpenSearch Dashboards connectivity."""

    def test_dashboards_opensearch_connection(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
        test_config: dict,
    ):
        """Verify Dashboards can connect to OpenSearch."""
        with PortForward(
            k8s_core_api,
            namespaces["observability_plane"],
            "opensearch-dashboards",
            5601,
        ) as local_port:
            # Try to get status which includes OpenSearch connection info
            response = requests.get(
                f"http://localhost:{local_port}/api/status",
                auth=(test_config["opensearch_user"], test_config["opensearch_pass"]),
                timeout=30,
            )

            if response.status_code == 200:
                status = response.json()
                # Check overall status
                overall = status.get("status", {}).get("overall", {})
                state = overall.get("state", "unknown")
                assert state in ["green", "yellow", "available"], f"Dashboards status: {state}"

    def test_dashboards_ui_accessible(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
    ):
        """Verify Dashboards UI is accessible."""
        with PortForward(
            k8s_core_api,
            namespaces["observability_plane"],
            "opensearch-dashboards",
            5601,
        ) as local_port:
            response = requests.get(
                f"http://localhost:{local_port}/app/home",
                timeout=30,
                allow_redirects=True,
            )

            # Should return HTML or redirect to login
            assert response.status_code in [200, 302, 401], (
                f"Dashboards UI failed: {response.status_code}"
            )
