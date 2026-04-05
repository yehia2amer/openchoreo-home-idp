"""Tests for cert-manager."""

import pytest
from kubernetes import client

from utils.k8s_helpers import (
    check_deployment_ready,
    check_resource_condition,
    get_custom_resource,
    get_secret_data,
)


@pytest.mark.infrastructure
@pytest.mark.smoke
class TestCertManagerController:
    """Test cert-manager controller health."""

    def test_cert_manager_deployment_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify cert-manager deployment is ready."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["cert_manager"], "cert-manager"
        )
        assert is_ready, f"cert-manager deployment not ready: {message}"

    def test_cert_manager_cainjector_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify cert-manager-cainjector deployment is ready."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["cert_manager"], "cert-manager-cainjector"
        )
        assert is_ready, f"cert-manager-cainjector not ready: {message}"

    def test_cert_manager_webhook_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify cert-manager-webhook deployment is ready."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["cert_manager"], "cert-manager-webhook"
        )
        assert is_ready, f"cert-manager-webhook not ready: {message}"


@pytest.mark.infrastructure
class TestClusterIssuer:
    """Test ClusterIssuer configuration."""

    def test_openchoreo_ca_issuer_ready(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """Verify openchoreo-ca ClusterIssuer is ready."""
        issuer = get_custom_resource(
            k8s_custom_api,
            group="cert-manager.io",
            version="v1",
            plural="clusterissuers",
            name="openchoreo-ca",
        )

        assert issuer is not None, "ClusterIssuer 'openchoreo-ca' not found"
        assert check_resource_condition(issuer, "Ready"), "ClusterIssuer 'openchoreo-ca' not ready"

    def test_selfsigned_issuer_ready(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """Verify selfsigned ClusterIssuer is ready (if exists)."""
        issuer = get_custom_resource(
            k8s_custom_api,
            group="cert-manager.io",
            version="v1",
            plural="clusterissuers",
            name="selfsigned",
        )

        if issuer is None:
            pytest.skip("Selfsigned ClusterIssuer not deployed")

        assert check_resource_condition(issuer, "Ready"), "ClusterIssuer 'selfsigned' not ready"


@pytest.mark.infrastructure
class TestCertificates:
    """Test TLS certificate issuance."""

    @pytest.mark.parametrize(
        "cert_name,namespace_key",
        [
            ("cp-gateway-tls", "control_plane"),
            ("dp-gateway-tls", "data_plane"),
            ("op-gateway-tls", "observability_plane"),
        ],
    )
    def test_gateway_certificate_ready(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
        cert_name: str,
        namespace_key: str,
    ):
        """Verify gateway TLS certificates are issued."""
        cert = get_custom_resource(
            k8s_custom_api,
            group="cert-manager.io",
            version="v1",
            plural="certificates",
            name=cert_name,
            namespace=namespaces[namespace_key],
        )

        if cert is None:
            pytest.skip(f"Certificate '{cert_name}' not found in {namespaces[namespace_key]}")

        assert check_resource_condition(cert, "Ready"), f"Certificate '{cert_name}' not ready"

    @pytest.mark.parametrize(
        "cert_name,namespace_key",
        [
            ("cp-gateway-tls", "control_plane"),
            ("dp-gateway-tls", "data_plane"),
            ("op-gateway-tls", "observability_plane"),
        ],
    )
    def test_certificate_secret_exists(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
        cert_name: str,
        namespace_key: str,
    ):
        """Verify TLS secrets exist with expected keys."""
        secret_data = get_secret_data(k8s_core_api, namespaces[namespace_key], cert_name)

        if secret_data is None:
            pytest.skip(f"Secret '{cert_name}' not found")

        assert "tls.crt" in secret_data, f"Secret '{cert_name}' missing tls.crt"
        assert "tls.key" in secret_data, f"Secret '{cert_name}' missing tls.key"

    def test_ca_certificate_exists(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
    ):
        """Verify CA certificate secret exists."""
        # Try common CA secret names
        ca_secret_names = ["openchoreo-ca", "ca-key-pair", "root-ca"]

        for name in ca_secret_names:
            secret_data = get_secret_data(k8s_core_api, namespaces["cert_manager"], name)
            if secret_data is not None:
                assert "tls.crt" in secret_data or "ca.crt" in secret_data, (
                    f"CA secret '{name}' missing certificate"
                )
                return

        pytest.skip("CA certificate secret not found with expected names")
