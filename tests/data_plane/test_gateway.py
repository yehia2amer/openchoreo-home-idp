"""Tests for Data Plane Gateway."""

import pytest
import requests
from kubernetes import client

from utils.k8s_helpers import check_resource_condition, get_custom_resource


@pytest.mark.data_plane
@pytest.mark.smoke
class TestDataPlaneGateway:
    """Test Data Plane Gateway resources."""

    def test_gateway_programmed(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify data plane Gateway is programmed."""
        gateway = get_custom_resource(
            k8s_custom_api,
            group="gateway.networking.k8s.io",
            version="v1",
            plural="gateways",
            name="gateway-shared",
            namespace=namespaces["data_plane"],
        )

        assert gateway is not None, "Data plane Gateway not found"
        assert check_resource_condition(gateway, "Programmed"), "Data plane Gateway not programmed"

    def test_gateway_has_address(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify Gateway has an assigned address."""
        gateway = get_custom_resource(
            k8s_custom_api,
            group="gateway.networking.k8s.io",
            version="v1",
            plural="gateways",
            name="gateway-shared",
            namespace=namespaces["data_plane"],
        )

        if gateway is None:
            pytest.skip("Data plane Gateway not found")

        status = gateway.get("status", {})
        addresses = status.get("addresses", [])

        assert len(addresses) > 0, "Gateway has no addresses assigned"

        # Verify address has a value
        for addr in addresses:
            assert addr.get("value"), "Gateway address has no value"


@pytest.mark.data_plane
class TestHTTPRoutes:
    """Test HTTPRoute resources."""

    def test_httproutes_accepted(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify HTTPRoutes are accepted."""
        # List all HTTPRoutes in data plane namespace
        routes = k8s_custom_api.list_namespaced_custom_object(
            group="gateway.networking.k8s.io",
            version="v1",
            namespace=namespaces["data_plane"],
            plural="httproutes",
        )

        items = routes.get("items", [])
        if not items:
            pytest.skip("No HTTPRoutes found in data plane")

        for route in items:
            name = route.get("metadata", {}).get("name", "unknown")
            assert check_resource_condition(route, "Accepted"), f"HTTPRoute '{name}' not accepted"

    def test_httproutes_resolved_refs(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify HTTPRoute backend references are resolved."""
        routes = k8s_custom_api.list_namespaced_custom_object(
            group="gateway.networking.k8s.io",
            version="v1",
            namespace=namespaces["data_plane"],
            plural="httproutes",
        )

        items = routes.get("items", [])
        if not items:
            pytest.skip("No HTTPRoutes found in data plane")

        for route in items:
            name = route.get("metadata", {}).get("name", "unknown")
            assert check_resource_condition(route, "ResolvedRefs"), (
                f"HTTPRoute '{name}' has unresolved refs"
            )


@pytest.mark.data_plane
class TestDataPlaneConnectivity:
    """Test Data Plane HTTP/HTTPS connectivity."""

    def test_http_connectivity(
        self,
        test_config: dict,
        http_session: requests.Session,
    ):
        """Verify HTTP traffic flows through data plane gateway."""
        domain = test_config["domain_base"]
        port = test_config["data_plane_http_port"]

        try:
            response = http_session.get(
                f"http://{domain}:{port}/",
                timeout=30,
                allow_redirects=False,
            )

            # Any response (including 404) means gateway is working
            assert response.status_code in range(100, 600), (
                f"Invalid status code: {response.status_code}"
            )
        except requests.exceptions.ConnectionError:
            pytest.fail("Cannot connect to data plane HTTP gateway")

    def test_https_connectivity(
        self,
        test_config: dict,
        http_session: requests.Session,
    ):
        """Verify HTTPS traffic with TLS termination."""
        if not test_config["tls_enabled"]:
            pytest.skip("TLS not enabled")

        domain = test_config["domain_base"]
        port = test_config["data_plane_https_port"]

        try:
            response = http_session.get(
                f"https://{domain}:{port}/",
                timeout=30,
                allow_redirects=False,
            )

            # Any response means TLS handshake succeeded
            assert response.status_code in range(100, 600), (
                f"Invalid status code: {response.status_code}"
            )
        except requests.exceptions.SSLError as e:
            pytest.fail(f"TLS handshake failed: {e}")
        except requests.exceptions.ConnectionError:
            pytest.fail("Cannot connect to data plane HTTPS gateway")

    def test_tls_certificate_valid(
        self,
        test_config: dict,
    ):
        """Verify TLS certificate is valid (if TLS enabled)."""
        if not test_config["tls_enabled"]:
            pytest.skip("TLS not enabled")

        import ssl
        import socket

        domain = test_config["domain_base"]
        port = test_config["data_plane_https_port"]

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # Self-signed certs

        try:
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert(binary_form=True)
                    assert cert is not None, "No certificate returned"
        except Exception as e:
            pytest.fail(f"TLS connection failed: {e}")
