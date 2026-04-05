"""E2E Tests: Cross-component dependency resolution.

Verifies that components with declared dependencies actually receive
their environment variables injected by the OpenChoreo controller.

THIS would have caught the frontend CrashLoop mechanism:
the Deployment was rendered with `env: []` instead of
DOC_SERVICE_URL and COLLAB_SERVICE_URL.
"""

import pytest
from kubernetes import client

from utils.openchoreo_helpers import (
    extract_env_vars,
    find_data_plane_namespace,
    find_deployment_by_prefix,
)


@pytest.mark.e2e
@pytest.mark.dependencies
class TestFrontendDependencies:
    """Verify frontend has its dependency env vars injected."""

    def test_frontend_has_doc_service_url(
        self,
        k8s_core_api: client.CoreV1Api,
        k8s_apps_api: client.AppsV1Api,
        dp_namespace: str,
    ):
        """Frontend Deployment has DOC_SERVICE_URL env var injected.

        THIS would have caught: env: [] in the Deployment spec.
        """
        deployment = find_deployment_by_prefix(k8s_apps_api, dp_namespace, "frontend-development")
        if deployment is None:
            # Try broader match
            deployment = find_deployment_by_prefix(k8s_apps_api, dp_namespace, "frontend")
        assert deployment is not None, (
            f"Frontend deployment not found in {dp_namespace}. "
            f"Check that the frontend ReleaseBinding exists and is Ready."
        )

        env_vars = extract_env_vars(deployment)
        assert "DOC_SERVICE_URL" in env_vars, (
            f"Frontend deployment missing DOC_SERVICE_URL. "
            f"Current env vars: {sorted(env_vars.keys())}. "
            f"This means document-svc ReleaseBinding doesn't exist "
            f"or connections are pending."
        )
        assert "document-svc" in env_vars["DOC_SERVICE_URL"], (
            f"DOC_SERVICE_URL doesn't point to document-svc: "
            f"{env_vars['DOC_SERVICE_URL']}"
        )

    def test_frontend_has_collab_service_url(
        self,
        k8s_core_api: client.CoreV1Api,
        k8s_apps_api: client.AppsV1Api,
        dp_namespace: str,
    ):
        """Frontend Deployment has COLLAB_SERVICE_URL env var injected."""
        deployment = find_deployment_by_prefix(k8s_apps_api, dp_namespace, "frontend-development")
        if deployment is None:
            deployment = find_deployment_by_prefix(k8s_apps_api, dp_namespace, "frontend")
        assert deployment is not None, f"Frontend deployment not found in {dp_namespace}"

        env_vars = extract_env_vars(deployment)
        assert "COLLAB_SERVICE_URL" in env_vars, (
            f"Frontend deployment missing COLLAB_SERVICE_URL. "
            f"Current env vars: {sorted(env_vars.keys())}. "
            f"This means collab-svc ReleaseBinding doesn't exist "
            f"or connections are pending."
        )
        assert "collab-svc" in env_vars["COLLAB_SERVICE_URL"], (
            f"COLLAB_SERVICE_URL doesn't point to collab-svc: "
            f"{env_vars['COLLAB_SERVICE_URL']}"
        )

    def test_frontend_env_vars_are_complete_urls(
        self,
        k8s_apps_api: client.AppsV1Api,
        dp_namespace: str,
    ):
        """Dependency URLs are well-formed (http://service.namespace.svc.cluster.local:port)."""
        deployment = find_deployment_by_prefix(k8s_apps_api, dp_namespace, "frontend-development")
        if deployment is None:
            deployment = find_deployment_by_prefix(k8s_apps_api, dp_namespace, "frontend")
        if deployment is None:
            pytest.skip("Frontend deployment not found")

        env_vars = extract_env_vars(deployment)

        for var_name in ["DOC_SERVICE_URL", "COLLAB_SERVICE_URL"]:
            if var_name not in env_vars:
                continue  # Other tests catch missing vars
            url = env_vars[var_name]
            assert url.startswith("http"), (
                f"{var_name} is not a valid HTTP URL: {url}"
            )
            assert ".svc.cluster.local" in url or dp_namespace in url, (
                f"{var_name} doesn't look like a cluster-internal URL: {url}"
            )


@pytest.mark.e2e
@pytest.mark.dependencies
class TestAllDependenciesResolved:
    """Comprehensive dependency check across all components."""

    # Map of component -> expected env vars -> service they should reference
    EXPECTED_DEPENDENCIES = {
        "frontend": {
            "DOC_SERVICE_URL": "document-svc",
            "COLLAB_SERVICE_URL": "collab-svc",
        },
    }

    def test_all_declared_dependencies_injected(
        self,
        k8s_apps_api: client.AppsV1Api,
        dp_namespace: str,
    ):
        """Every component's declared dependencies are present as env vars."""
        failures = []

        for component, deps in self.EXPECTED_DEPENDENCIES.items():
            deployment = find_deployment_by_prefix(
                k8s_apps_api, dp_namespace, f"{component}-development",
            )
            if deployment is None:
                deployment = find_deployment_by_prefix(
                    k8s_apps_api, dp_namespace, component,
                )
            if deployment is None:
                failures.append(f"{component}: deployment not found in {dp_namespace}")
                continue

            env_vars = extract_env_vars(deployment)
            for env_name, expected_svc in deps.items():
                if env_name not in env_vars:
                    failures.append(
                        f"{component}: missing {env_name} (depends on {expected_svc})"
                    )
                elif expected_svc not in env_vars[env_name]:
                    failures.append(
                        f"{component}: {env_name}={env_vars[env_name]} "
                        f"doesn't reference {expected_svc}"
                    )

        assert len(failures) == 0, (
            f"Dependency resolution failures:\n" + "\n".join(f"  - {f}" for f in failures)
        )
