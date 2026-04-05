"""E2E Tests: GitOps repo ↔ cluster consistency.

Verifies that Flux is syncing correctly and that all expected
resources from the gitops repo are present in the cluster.

THIS would have caught: document-svc and collab-svc had no releases/
directory in the gitops repo, meaning Flux never synced their releases.
"""

import pytest
from kubernetes import client

from utils.k8s_helpers import check_resource_condition, get_custom_resource
from utils.openchoreo_helpers import list_openchoreo_resources


OPENCHOREO_NAMESPACE = "default"
FLUX_NAMESPACE = "flux-system"

# All components that should have at least one ComponentRelease synced to cluster
COMPONENTS_WITH_RELEASES = ["frontend", "document-svc", "collab-svc", "nats", "postgres"]


@pytest.mark.e2e
@pytest.mark.gitops_consistency
class TestFluxGitRepositorySynced:
    """Verify Flux GitRepository is synced and healthy."""

    def test_gitrepository_ready(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """Flux GitRepository 'sample-gitops' is synced and not stale."""
        gr = get_custom_resource(
            k8s_custom_api,
            group="source.toolkit.fluxcd.io",
            version="v1",
            plural="gitrepositories",
            name="sample-gitops",
            namespace=FLUX_NAMESPACE,
        )
        if gr is None:
            pytest.skip("GitRepository 'sample-gitops' not found — Flux GitOps not configured")

        assert check_resource_condition(gr, "Ready"), (
            f"GitRepository 'sample-gitops' not Ready. "
            f"Conditions: {gr.get('status', {}).get('conditions', [])}. "
            f"Check: kubectl describe gitrepository sample-gitops -n {FLUX_NAMESPACE}"
        )


@pytest.mark.e2e
@pytest.mark.gitops_consistency
class TestAllKustomizationsReady:
    """Verify all Flux Kustomizations are reconciling successfully."""

    def test_all_kustomizations_ready(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """All Flux Kustomizations are Ready (no stuck reconciliation)."""
        try:
            kustomizations = k8s_custom_api.list_namespaced_custom_object(
                group="kustomize.toolkit.fluxcd.io",
                version="v1",
                namespace=FLUX_NAMESPACE,
                plural="kustomizations",
            )
        except client.ApiException as e:
            if e.status == 404:
                pytest.skip("Kustomization CRD not found")
            raise

        items = kustomizations.get("items", [])
        if not items:
            pytest.skip("No Kustomizations found")

        errors = []
        for ks in items:
            name = ks["metadata"]["name"]
            if not check_resource_condition(ks, "Ready"):
                conditions = ks.get("status", {}).get("conditions", [])
                ready = next((c for c in conditions if c.get("type") == "Ready"), {})
                errors.append(
                    f"{name}: {ready.get('reason', 'unknown')} — "
                    f"{ready.get('message', 'no message')}"
                )

        assert len(errors) == 0, (
            f"Kustomizations not Ready:\n" + "\n".join(f"  - {e}" for e in errors) +
            f"\nThis means Flux can't sync changes from the gitops repo."
        )


@pytest.mark.e2e
@pytest.mark.gitops_consistency
class TestComponentReleasesInCluster:
    """Verify ComponentReleases are synced from gitops repo to cluster."""

    @pytest.mark.parametrize("component", COMPONENTS_WITH_RELEASES)
    def test_component_has_release_in_cluster(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        component: str,
    ):
        """Every expected component has a ComponentRelease synced to the cluster.

        THIS would have caught: document-svc/collab-svc had no releases/ in gitops repo,
        so Flux never synced ComponentReleases for them.
        """
        # Try with label selector first
        releases = list_openchoreo_resources(
            k8s_custom_api,
            "componentreleases",
            namespace=OPENCHOREO_NAMESPACE,
            label_selector=f"openchoreo.dev/component={component}",
        )

        # Fall back to name prefix matching
        if not releases:
            all_releases = list_openchoreo_resources(
                k8s_custom_api, "componentreleases", namespace=OPENCHOREO_NAMESPACE,
            )
            releases = [
                r for r in all_releases
                if r.get("metadata", {}).get("name", "").startswith(component)
            ]

        assert len(releases) > 0, (
            f"Component '{component}' has no ComponentRelease in cluster. "
            f"Either the gitops repo is missing releases/{component}-*.yaml "
            f"or Flux hasn't synced it yet. "
            f"Check: kubectl get componentreleases -n {OPENCHOREO_NAMESPACE}"
        )
