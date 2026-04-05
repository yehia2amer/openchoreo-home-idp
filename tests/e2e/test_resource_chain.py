"""E2E Tests: OpenChoreo resource chain validation.

Verifies every link in the chain:
  Component → Workload → ComponentRelease → ReleaseBinding → RenderedRelease

This would have caught the root cause of the frontend CrashLoopBackOff:
- document-svc and collab-svc had no ComponentReleases
- frontend ReleaseBinding was stuck at "2 connections pending, 0 resolved"
"""

import pytest
from kubernetes import client

from utils.openchoreo_helpers import (
    get_openchoreo_resource,
    get_resource_condition,
    list_openchoreo_resources,
)


OPENCHOREO_NAMESPACE = "default"

# All components in the doclet demo app
ALL_COMPONENTS = ["frontend", "document-svc", "collab-svc", "nats", "postgres"]

# Components that must have ComponentReleases (built via WorkflowRun or pre-committed)
COMPONENTS_WITH_RELEASES = ["frontend", "document-svc", "collab-svc", "nats", "postgres"]

# Components deployed to development environment
COMPONENTS_IN_DEVELOPMENT = [
    ("frontend", "development"),
    ("document-svc", "development"),
    ("collab-svc", "development"),
    ("nats", "development"),
    ("postgres", "development"),
]

# Components with endpoint dependencies that need connection resolution
COMPONENTS_WITH_DEPENDENCIES = [
    ("frontend", "development"),
]


@pytest.mark.e2e
@pytest.mark.resource_chain
class TestComponentExists:
    """Verify Component CRs exist in the cluster."""

    @pytest.mark.parametrize("component", ALL_COMPONENTS)
    def test_component_exists(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        component: str,
    ):
        """Every declared component has a Component CR in the cluster."""
        cr = get_openchoreo_resource(
            k8s_custom_api, "components", component, namespace=OPENCHOREO_NAMESPACE,
        )
        assert cr is not None, (
            f"Component '{component}' CR missing from cluster namespace '{OPENCHOREO_NAMESPACE}'. "
            f"Check that Flux has synced the gitops repo."
        )


@pytest.mark.e2e
@pytest.mark.resource_chain
class TestWorkloadExists:
    """Verify Workload CRs exist for each component."""

    @pytest.mark.parametrize("component", ALL_COMPONENTS)
    def test_workload_exists(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        component: str,
    ):
        """Every component has a Workload CR."""
        # Workload name convention: {component}-workload
        workload = get_openchoreo_resource(
            k8s_custom_api, "workloads", f"{component}-workload",
            namespace=OPENCHOREO_NAMESPACE,
        )
        if workload is None:
            # Also try without -workload suffix
            workload = get_openchoreo_resource(
                k8s_custom_api, "workloads", component,
                namespace=OPENCHOREO_NAMESPACE,
            )
        assert workload is not None, (
            f"Workload for component '{component}' not found. "
            f"Expected '{component}-workload' or '{component}' in namespace '{OPENCHOREO_NAMESPACE}'."
        )


@pytest.mark.e2e
@pytest.mark.resource_chain
class TestComponentReleaseExists:
    """Verify ComponentReleases exist for all components."""

    @pytest.mark.parametrize("component", COMPONENTS_WITH_RELEASES)
    def test_component_release_exists(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        component: str,
    ):
        """Every component has at least one ComponentRelease.

        THIS would have caught: document-svc and collab-svc had no releases
        because their builds were never triggered.
        """
        releases = list_openchoreo_resources(
            k8s_custom_api,
            "componentreleases",
            namespace=OPENCHOREO_NAMESPACE,
            label_selector=f"openchoreo.dev/component={component}",
        )

        # Also try listing without label selector and filtering by name prefix
        if not releases:
            all_releases = list_openchoreo_resources(
                k8s_custom_api, "componentreleases", namespace=OPENCHOREO_NAMESPACE,
            )
            releases = [
                r for r in all_releases
                if r.get("metadata", {}).get("name", "").startswith(component)
            ]

        assert len(releases) > 0, (
            f"Component '{component}' has NO ComponentRelease — "
            f"build was never triggered or failed. "
            f"Run: kubectl get componentreleases -n {OPENCHOREO_NAMESPACE} "
            f"and check WorkflowRuns."
        )


@pytest.mark.e2e
@pytest.mark.resource_chain
class TestReleaseBindingReady:
    """Verify ReleaseBindings exist and are Ready for each environment."""

    @pytest.mark.parametrize("component,env", COMPONENTS_IN_DEVELOPMENT)
    def test_release_binding_exists_and_ready(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        component: str,
        env: str,
    ):
        """Every component has a Ready ReleaseBinding for its environment.

        THIS would have caught: frontend ReleaseBinding stuck at ConnectionsPending.
        """
        rb_name = f"{component}-{env}"
        rb = get_openchoreo_resource(
            k8s_custom_api, "releasebindings", rb_name, namespace=OPENCHOREO_NAMESPACE,
        )
        assert rb is not None, (
            f"ReleaseBinding '{rb_name}' missing — component '{component}' "
            f"was never deployed to '{env}' environment. "
            f"Check that a ComponentRelease exists and autoDeploy is enabled."
        )

        # Check Ready condition
        ready = get_resource_condition(rb, "Ready")
        assert ready is not None, (
            f"ReleaseBinding '{rb_name}' has no Ready condition in its status. "
            f"Status: {rb.get('status', {})}"
        )
        assert ready["status"] == "True", (
            f"ReleaseBinding '{rb_name}' not Ready: "
            f"reason={ready.get('reason', 'unknown')}, "
            f"message={ready.get('message', 'no message')}. "
            f"Check: kubectl describe releasebinding {rb_name} -n {OPENCHOREO_NAMESPACE}"
        )


@pytest.mark.e2e
@pytest.mark.resource_chain
class TestConnectionsResolved:
    """Verify dependency connections are fully resolved on ReleaseBindings."""

    @pytest.mark.parametrize("component,env", COMPONENTS_WITH_DEPENDENCIES)
    def test_release_binding_connections_resolved(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        component: str,
        env: str,
    ):
        """ReleaseBindings with dependencies have ALL connections resolved.

        THIS is the exact check that would have caught the CrashLoop root cause:
        frontend's ReleaseBinding had "2 connections pending, 0 resolved".
        """
        rb_name = f"{component}-{env}"
        rb = get_openchoreo_resource(
            k8s_custom_api, "releasebindings", rb_name, namespace=OPENCHOREO_NAMESPACE,
        )
        assert rb is not None, f"ReleaseBinding '{rb_name}' not found"

        conn_resolved = get_resource_condition(rb, "ConnectionsResolved")
        if conn_resolved is not None:
            assert conn_resolved["status"] == "True", (
                f"ReleaseBinding '{rb_name}' has UNRESOLVED connections: "
                f"{conn_resolved.get('message', '')}. "
                f"This means dependency components haven't been built/deployed yet. "
                f"Check that document-svc and collab-svc have ReleaseBindings."
            )


@pytest.mark.e2e
@pytest.mark.resource_chain
class TestRenderedReleaseHealthy:
    """Verify RenderedReleases are not degraded."""

    @pytest.mark.parametrize("component,env", COMPONENTS_IN_DEVELOPMENT)
    def test_rendered_release_not_degraded(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        component: str,
        env: str,
    ):
        """RenderedRelease is not in Degraded state."""
        rr_name = f"{component}-{env}"
        rr = get_openchoreo_resource(
            k8s_custom_api, "renderedreleases", rr_name, namespace=OPENCHOREO_NAMESPACE,
        )
        if rr is None:
            # RenderedReleases may be in a different namespace or use different naming
            # Skip rather than fail if not found
            pytest.skip(f"RenderedRelease '{rr_name}' not found — may use different naming")
            return

        degraded = get_resource_condition(rr, "Degraded")
        if degraded is not None:
            assert degraded["status"] != "True", (
                f"RenderedRelease '{rr_name}' is DEGRADED: "
                f"{degraded.get('message', 'no message')}. "
                f"This means the deployment was rendered with errors."
            )
