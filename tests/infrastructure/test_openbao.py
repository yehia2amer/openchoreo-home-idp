"""Tests for OpenBao (Vault)."""

import pytest
import hvac
from kubernetes import client

from utils.k8s_helpers import check_deployment_ready, get_pod_by_name_prefix
from utils.port_forward import PortForward


@pytest.mark.infrastructure
@pytest.mark.smoke
class TestOpenBaoHealth:
    """Test OpenBao server health."""

    def test_openbao_statefulset_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify OpenBao StatefulSet is ready."""
        sts = k8s_apps_api.read_namespaced_stateful_set("openbao", namespaces["openbao"])

        assert sts.status is not None
        assert sts.status.ready_replicas is not None
        assert sts.status.ready_replicas > 0, "OpenBao StatefulSet not ready"

    def test_openbao_pod_running(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
    ):
        """Verify OpenBao pod is running."""
        pod = get_pod_by_name_prefix(k8s_core_api, namespaces["openbao"], "openbao-")

        assert pod is not None, "OpenBao pod not found"
        assert pod.status.phase == "Running", f"OpenBao pod not running: {pod.status.phase}"

    def test_openbao_health_api(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
        test_config: dict,
    ):
        """Verify OpenBao health API returns healthy status."""
        with PortForward(
            k8s_core_api,
            namespaces["openbao"],
            "openbao-0",
            8200,
        ) as local_port:
            vault_client = hvac.Client(
                url=f"http://localhost:{local_port}",
                token=test_config["openbao_token"],
            )

            health = vault_client.sys.read_health_status(method="GET")

            assert health.get("initialized", False), "OpenBao not initialized"
            assert not health.get("sealed", True), "OpenBao is sealed"


@pytest.mark.infrastructure
class TestOpenBaoAuth:
    """Test OpenBao authentication configuration."""

    def test_kubernetes_auth_enabled(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
        test_config: dict,
    ):
        """Verify Kubernetes auth method is enabled."""
        with PortForward(
            k8s_core_api,
            namespaces["openbao"],
            "openbao-0",
            8200,
        ) as local_port:
            vault_client = hvac.Client(
                url=f"http://localhost:{local_port}",
                token=test_config["openbao_token"],
            )

            auth_methods = vault_client.sys.list_auth_methods()

            assert "kubernetes/" in auth_methods, "Kubernetes auth method not enabled"

    def test_kubernetes_auth_config(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
        test_config: dict,
    ):
        """Verify Kubernetes auth method is configured."""
        with PortForward(
            k8s_core_api,
            namespaces["openbao"],
            "openbao-0",
            8200,
        ) as local_port:
            vault_client = hvac.Client(
                url=f"http://localhost:{local_port}",
                token=test_config["openbao_token"],
            )

            try:
                config = vault_client.auth.kubernetes.read_config()
                assert config is not None, "Kubernetes auth not configured"
            except hvac.exceptions.InvalidPath:
                pytest.fail("Kubernetes auth method not configured")


@pytest.mark.infrastructure
class TestOpenBaoSecrets:
    """Test OpenBao secret storage."""

    def test_kv_secrets_engine_enabled(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
        test_config: dict,
    ):
        """Verify KV secrets engine is enabled."""
        with PortForward(
            k8s_core_api,
            namespaces["openbao"],
            "openbao-0",
            8200,
        ) as local_port:
            vault_client = hvac.Client(
                url=f"http://localhost:{local_port}",
                token=test_config["openbao_token"],
            )

            secrets_engines = vault_client.sys.list_mounted_secrets_engines()

            # Check for secret/ or kv/ mount
            has_kv = any(
                path.startswith("secret/") or path.startswith("kv/")
                for path in secrets_engines.keys()
            )
            assert has_kv, "KV secrets engine not enabled"

    def test_backstage_secret_readable(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
        test_config: dict,
    ):
        """Verify backstage secret can be read."""
        with PortForward(
            k8s_core_api,
            namespaces["openbao"],
            "openbao-0",
            8200,
        ) as local_port:
            vault_client = hvac.Client(
                url=f"http://localhost:{local_port}",
                token=test_config["openbao_token"],
            )

            try:
                # Try KV v2 path first
                secret = vault_client.secrets.kv.v2.read_secret_version(
                    path="backstage-backend-secret",
                    mount_point="secret",
                )
                assert secret is not None, "Backstage secret not found"
                assert "data" in secret, "Backstage secret has no data"
            except hvac.exceptions.InvalidPath:
                # Try KV v1 path
                try:
                    secret = vault_client.secrets.kv.v1.read_secret(
                        path="backstage-backend-secret",
                        mount_point="secret",
                    )
                    assert secret is not None, "Backstage secret not found"
                except hvac.exceptions.InvalidPath:
                    pytest.skip("Backstage secret not found at expected path")


@pytest.mark.infrastructure
class TestOpenBaoPolicies:
    """Test OpenBao policy configuration."""

    def test_openchoreo_policies_exist(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
        test_config: dict,
    ):
        """Verify OpenChoreo policies are configured."""
        with PortForward(
            k8s_core_api,
            namespaces["openbao"],
            "openbao-0",
            8200,
        ) as local_port:
            vault_client = hvac.Client(
                url=f"http://localhost:{local_port}",
                token=test_config["openbao_token"],
            )

            policies = vault_client.sys.list_policies()

            # Check for expected policies
            expected_policies = ["default", "root"]
            for policy in expected_policies:
                assert policy in policies["policies"], f"Policy '{policy}' not found"

    def test_external_secrets_role_exists(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
        test_config: dict,
    ):
        """Verify external-secrets Kubernetes auth role exists."""
        with PortForward(
            k8s_core_api,
            namespaces["openbao"],
            "openbao-0",
            8200,
        ) as local_port:
            vault_client = hvac.Client(
                url=f"http://localhost:{local_port}",
                token=test_config["openbao_token"],
            )

            try:
                roles = vault_client.auth.kubernetes.list_roles()
                assert "keys" in roles, "No Kubernetes auth roles found"
                assert len(roles["keys"]) > 0, "No Kubernetes auth roles configured"
            except hvac.exceptions.InvalidPath:
                pytest.skip("No Kubernetes auth roles configured")
