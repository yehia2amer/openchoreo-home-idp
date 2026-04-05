"""Tests for Flux CD."""

import pytest
from kubernetes import client

from utils.k8s_helpers import check_deployment_ready, check_resource_condition, get_custom_resource


@pytest.mark.gitops
@pytest.mark.smoke
class TestFluxControllers:
    """Test Flux CD controller health."""

    def test_source_controller_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify source-controller deployment is ready."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["flux"], "source-controller"
        )
        assert is_ready, f"source-controller not ready: {message}"

    def test_kustomize_controller_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify kustomize-controller deployment is ready."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["flux"], "kustomize-controller"
        )
        assert is_ready, f"kustomize-controller not ready: {message}"

    def test_helm_controller_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify helm-controller deployment is ready."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["flux"], "helm-controller"
        )
        assert is_ready, f"helm-controller not ready: {message}"

    def test_notification_controller_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify notification-controller deployment is ready (if deployed)."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["flux"], "notification-controller"
        )

        if not is_ready and "not found" in message.lower():
            pytest.skip("notification-controller not deployed")

        assert is_ready, f"notification-controller not ready: {message}"


@pytest.mark.gitops
class TestGitRepository:
    """Test GitRepository resources."""

    def test_gitrepositories_exist(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify GitRepository resources exist."""
        repos = k8s_custom_api.list_namespaced_custom_object(
            group="source.toolkit.fluxcd.io",
            version="v1",
            namespace=namespaces["flux"],
            plural="gitrepositories",
        )

        items = repos.get("items", [])
        if not items:
            pytest.skip("No GitRepositories found")

        assert len(items) > 0, "No GitRepositories configured"

    def test_gitrepository_ready(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify GitRepositories are ready."""
        repos = k8s_custom_api.list_namespaced_custom_object(
            group="source.toolkit.fluxcd.io",
            version="v1",
            namespace=namespaces["flux"],
            plural="gitrepositories",
        )

        items = repos.get("items", [])
        if not items:
            pytest.skip("No GitRepositories found")

        for repo in items:
            name = repo.get("metadata", {}).get("name", "unknown")
            assert check_resource_condition(repo, "Ready"), f"GitRepository '{name}' not ready"

    def test_sample_gitops_repository(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify sample-gitops GitRepository is syncing."""
        repo = get_custom_resource(
            k8s_custom_api,
            group="source.toolkit.fluxcd.io",
            version="v1",
            plural="gitrepositories",
            name="sample-gitops",
            namespace=namespaces["flux"],
        )

        if repo is None:
            pytest.skip("sample-gitops GitRepository not found")

        assert check_resource_condition(repo, "Ready"), "sample-gitops GitRepository not ready"


@pytest.mark.gitops
class TestKustomization:
    """Test Kustomization resources."""

    def test_kustomizations_exist(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify Kustomization resources exist."""
        kustomizations = k8s_custom_api.list_namespaced_custom_object(
            group="kustomize.toolkit.fluxcd.io",
            version="v1",
            namespace=namespaces["flux"],
            plural="kustomizations",
        )

        items = kustomizations.get("items", [])
        if not items:
            pytest.skip("No Kustomizations found")

        assert len(items) > 0, "No Kustomizations configured"

    def test_kustomizations_ready(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify Kustomizations are ready."""
        kustomizations = k8s_custom_api.list_namespaced_custom_object(
            group="kustomize.toolkit.fluxcd.io",
            version="v1",
            namespace=namespaces["flux"],
            plural="kustomizations",
        )

        items = kustomizations.get("items", [])
        if not items:
            pytest.skip("No Kustomizations found")

        for ks in items:
            name = ks.get("metadata", {}).get("name", "unknown")
            assert check_resource_condition(ks, "Ready"), f"Kustomization '{name}' not ready"


@pytest.mark.gitops
class TestHelmRelease:
    """Test HelmRelease resources."""

    def test_helmreleases_exist(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify HelmRelease resources exist (if using Helm)."""
        try:
            releases = k8s_custom_api.list_namespaced_custom_object(
                group="helm.toolkit.fluxcd.io",
                version="v2",
                namespace=namespaces["flux"],
                plural="helmreleases",
            )

            items = releases.get("items", [])
            if not items:
                pytest.skip("No HelmReleases found")

            assert len(items) > 0, "No HelmReleases configured"
        except client.ApiException as e:
            if e.status == 404:
                pytest.skip("HelmRelease CRD not installed")
            raise

    def test_helmreleases_ready(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify HelmReleases are ready."""
        try:
            releases = k8s_custom_api.list_namespaced_custom_object(
                group="helm.toolkit.fluxcd.io",
                version="v2",
                namespace=namespaces["flux"],
                plural="helmreleases",
            )

            items = releases.get("items", [])
            if not items:
                pytest.skip("No HelmReleases found")

            for release in items:
                name = release.get("metadata", {}).get("name", "unknown")
                assert check_resource_condition(release, "Ready"), f"HelmRelease '{name}' not ready"
        except client.ApiException as e:
            if e.status == 404:
                pytest.skip("HelmRelease CRD not installed")
            raise


@pytest.mark.gitops
@pytest.mark.slow
class TestFluxReconciliation:
    """Test Flux reconciliation."""

    def test_trigger_reconciliation(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify on-demand reconciliation works."""
        import time

        # Get first GitRepository
        repos = k8s_custom_api.list_namespaced_custom_object(
            group="source.toolkit.fluxcd.io",
            version="v1",
            namespace=namespaces["flux"],
            plural="gitrepositories",
        )

        items = repos.get("items", [])
        if not items:
            pytest.skip("No GitRepositories found")

        repo = items[0]
        name = repo["metadata"]["name"]

        # Get current last handled reconcile time
        status = repo.get("status", {})
        last_handled = status.get("lastHandledReconcileAt", "")

        # Annotate to trigger reconciliation
        annotations = repo.get("metadata", {}).get("annotations", {}) or {}
        annotations["reconcile.fluxcd.io/requestedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")

        k8s_custom_api.patch_namespaced_custom_object(
            group="source.toolkit.fluxcd.io",
            version="v1",
            namespace=namespaces["flux"],
            plural="gitrepositories",
            name=name,
            body={"metadata": {"annotations": annotations}},
        )

        # Wait for reconciliation (max 60 seconds)
        for _ in range(12):
            time.sleep(5)

            updated_repo = k8s_custom_api.get_namespaced_custom_object(
                group="source.toolkit.fluxcd.io",
                version="v1",
                namespace=namespaces["flux"],
                plural="gitrepositories",
                name=name,
            )

            new_handled = updated_repo.get("status", {}).get("lastHandledReconcileAt", "")
            if new_handled != last_handled:
                # Reconciliation happened
                assert check_resource_condition(updated_repo, "Ready"), "Reconciliation failed"
                return

        pytest.fail("Reconciliation did not complete in time")
