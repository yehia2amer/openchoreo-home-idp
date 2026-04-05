"""Tests for External Secrets Operator."""

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
class TestESOController:
    """Test External Secrets Operator controller health."""

    def test_external_secrets_deployment_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify external-secrets deployment is ready."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["external_secrets"], "external-secrets"
        )
        assert is_ready, f"external-secrets deployment not ready: {message}"

    def test_external_secrets_webhook_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify external-secrets-webhook deployment is ready."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["external_secrets"], "external-secrets-webhook"
        )
        assert is_ready, f"external-secrets-webhook not ready: {message}"

    def test_external_secrets_cert_controller_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify external-secrets-cert-controller deployment is ready."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["external_secrets"], "external-secrets-cert-controller"
        )
        assert is_ready, f"external-secrets-cert-controller not ready: {message}"


@pytest.mark.infrastructure
class TestClusterSecretStore:
    """Test ClusterSecretStore configuration."""

    def test_default_cluster_secret_store_ready(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """Verify default ClusterSecretStore is ready and connected to OpenBao."""
        store = get_custom_resource(
            k8s_custom_api,
            group="external-secrets.io",
            version="v1beta1",
            plural="clustersecretstores",
            name="default",
        )

        assert store is not None, "ClusterSecretStore 'default' not found"
        assert check_resource_condition(store, "Ready"), "ClusterSecretStore 'default' not ready"

        # Verify it's configured for Vault/OpenBao
        spec = store.get("spec", {})
        provider = spec.get("provider", {})
        assert "vault" in provider, "ClusterSecretStore not configured for Vault/OpenBao"

    def test_cluster_secret_store_provider_config(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """Verify ClusterSecretStore has correct provider configuration."""
        store = get_custom_resource(
            k8s_custom_api,
            group="external-secrets.io",
            version="v1beta1",
            plural="clustersecretstores",
            name="default",
        )

        if store is None:
            pytest.skip("ClusterSecretStore 'default' not found")

        spec = store.get("spec", {})
        vault_config = spec.get("provider", {}).get("vault", {})

        # Check server URL is configured
        assert vault_config.get("server"), "Vault server URL not configured"

        # Check auth method is configured
        auth = vault_config.get("auth", {})
        assert auth, "Vault auth not configured"


@pytest.mark.infrastructure
class TestExternalSecrets:
    """Test ExternalSecret resources and sync status."""

    @pytest.mark.parametrize(
        "secret_name,namespace_key",
        [
            ("backstage-secrets", "control_plane"),
            ("opensearch-admin-credentials", "observability_plane"),
        ],
    )
    def test_external_secret_synced(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
        secret_name: str,
        namespace_key: str,
    ):
        """Verify ExternalSecrets are synced successfully."""
        es = get_custom_resource(
            k8s_custom_api,
            group="external-secrets.io",
            version="v1beta1",
            plural="externalsecrets",
            name=secret_name,
            namespace=namespaces[namespace_key],
        )

        if es is None:
            pytest.skip(f"ExternalSecret '{secret_name}' not found")

        # Check SecretSynced condition
        conditions = es.get("status", {}).get("conditions", [])
        synced = False
        for condition in conditions:
            if condition.get("type") == "Ready" and condition.get("status") == "True":
                synced = True
                break

        assert synced, f"ExternalSecret '{secret_name}' not synced"

    @pytest.mark.parametrize(
        "secret_name,namespace_key,expected_keys",
        [
            ("backstage-secrets", "control_plane", ["POSTGRES_PASSWORD"]),
        ],
    )
    def test_synced_secret_has_expected_keys(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
        secret_name: str,
        namespace_key: str,
        expected_keys: list[str],
    ):
        """Verify synced secrets contain expected keys."""
        secret_data = get_secret_data(k8s_core_api, namespaces[namespace_key], secret_name)

        if secret_data is None:
            pytest.skip(f"Secret '{secret_name}' not found")

        for key in expected_keys:
            assert key in secret_data, f"Secret '{secret_name}' missing key '{key}'"


@pytest.mark.infrastructure
class TestSecretStoreConnectivity:
    """Test connectivity between ESO and OpenBao."""

    def test_secret_store_can_authenticate(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """Verify ClusterSecretStore can authenticate to OpenBao."""
        store = get_custom_resource(
            k8s_custom_api,
            group="external-secrets.io",
            version="v1beta1",
            plural="clustersecretstores",
            name="default",
        )

        if store is None:
            pytest.skip("ClusterSecretStore 'default' not found")

        status = store.get("status", {})
        conditions = status.get("conditions", [])

        # Look for Ready condition with True status
        for condition in conditions:
            if condition.get("type") == "Ready":
                assert condition.get("status") == "True", (
                    f"ClusterSecretStore authentication failed: {condition.get('message')}"
                )
                return

        pytest.fail("ClusterSecretStore has no Ready condition")
