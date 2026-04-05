"""E2E Tests: CI/CD pipeline (WorkflowRun) health.

Detects failed or never-triggered builds before they cause downstream issues.

THIS would have caught: document-svc and collab-svc had zero WorkflowRuns —
their builds were never triggered, so no ComponentReleases were ever created.
"""

from datetime import datetime, timezone

import pytest
from kubernetes import client

from utils.openchoreo_helpers import (
    get_openchoreo_resource,
    list_openchoreo_resources,
)


OPENCHOREO_NAMESPACE = "default"

# Components that are built via WorkflowRuns (excludes pre-built images like nats, postgres)
BUILDABLE_COMPONENTS = ["frontend", "document-svc", "collab-svc"]


def _parse_iso_time(ts: str) -> datetime | None:
    """Parse an ISO 8601 timestamp string."""
    if not ts:
        return None
    try:
        # Handle various formats
        ts = ts.rstrip("Z") + "+00:00" if ts.endswith("Z") else ts
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def _age_in_minutes(ts: str) -> float:
    """Calculate age in minutes from an ISO 8601 timestamp."""
    parsed = _parse_iso_time(ts)
    if parsed is None:
        return 0
    now = datetime.now(timezone.utc)
    return (now - parsed).total_seconds() / 60


@pytest.mark.e2e
@pytest.mark.workflow
class TestWorkflowTemplateExists:
    """Verify the CI workflow templates are available."""

    def test_docker_gitops_release_workflow_exists(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """The docker-gitops-release Workflow template exists."""
        # Try namespace-scoped first
        workflow = get_openchoreo_resource(
            k8s_custom_api, "workflows", "docker-gitops-release",
            namespace=OPENCHOREO_NAMESPACE,
            group="core.openchoreo.dev", version="v1alpha1",
        )
        if workflow is None:
            # Try cluster-scoped
            try:
                workflow = k8s_custom_api.get_cluster_custom_object(
                    "core.openchoreo.dev", "v1alpha1",
                    "clusterworkflows", "docker-gitops-release",
                )
            except client.ApiException:
                workflow = None

        # Also try the openchoreo.dev group (no core prefix)
        if workflow is None:
            workflow = get_openchoreo_resource(
                k8s_custom_api, "workflows", "docker-gitops-release",
                namespace=OPENCHOREO_NAMESPACE,
                group="openchoreo.dev", version="v1alpha1",
            )

        assert workflow is not None, (
            "docker-gitops-release Workflow/ClusterWorkflow missing. "
            "Check that the OpenChoreo control plane has the CI workflow templates installed."
        )


@pytest.mark.e2e
@pytest.mark.workflow
class TestSuccessfulBuilds:
    """Verify every buildable component has at least one successful WorkflowRun."""

    @pytest.mark.parametrize("component", BUILDABLE_COMPONENTS)
    def test_at_least_one_successful_workflow_run(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        component: str,
    ):
        """Every buildable component has at least one completed WorkflowRun.

        THIS would have caught: document-svc and collab-svc never had builds triggered.
        """
        # Try multiple API group variations
        runs = []
        for group in ["core.openchoreo.dev", "openchoreo.dev"]:
            try:
                runs = list_openchoreo_resources(
                    k8s_custom_api, "workflowruns",
                    namespace=OPENCHOREO_NAMESPACE,
                    label_selector=f"openchoreo.dev/component={component}",
                    group=group, version="v1alpha1",
                )
                if runs:
                    break
            except client.ApiException:
                continue

        assert len(runs) > 0, (
            f"Component '{component}' has ZERO WorkflowRuns — "
            f"no build was ever triggered. "
            f"Create a WorkflowRun for this component to build its container image."
        )

        # Check at least one succeeded
        succeeded = [
            r for r in runs
            if r.get("status", {}).get("phase") == "Succeeded"
            or any(
                c.get("type") == "WorkflowSucceeded" and c.get("status") == "True"
                for c in r.get("status", {}).get("conditions", [])
            )
        ]
        phases = [r.get("status", {}).get("phase", "unknown") for r in runs]
        assert len(succeeded) > 0, (
            f"Component '{component}' has {len(runs)} WorkflowRun(s) but "
            f"NONE succeeded. Phases: {phases}. "
            f"Check Argo Workflow logs for build failures."
        )


@pytest.mark.e2e
@pytest.mark.workflow
class TestNoStuckBuilds:
    """Verify no WorkflowRuns are stuck in Running state."""

    @pytest.mark.parametrize("component", BUILDABLE_COMPONENTS)
    def test_no_stuck_workflow_runs(
        self,
        k8s_custom_api: client.CustomObjectsApi,
        component: str,
    ):
        """No WorkflowRuns stuck in Running state for > 30 minutes."""
        runs = []
        for group in ["core.openchoreo.dev", "openchoreo.dev"]:
            try:
                runs = list_openchoreo_resources(
                    k8s_custom_api, "workflowruns",
                    namespace=OPENCHOREO_NAMESPACE,
                    label_selector=f"openchoreo.dev/component={component}",
                    group=group, version="v1alpha1",
                )
                if runs:
                    break
            except client.ApiException:
                continue

        for run in runs:
            phase = run.get("status", {}).get("phase", "")
            if phase == "Running":
                start = run.get("status", {}).get("startedAt", "")
                if start:
                    age = _age_in_minutes(start)
                    run_name = run.get("metadata", {}).get("name", "unknown")
                    assert age < 30, (
                        f"WorkflowRun '{run_name}' for {component} "
                        f"has been Running for {age:.0f} minutes — likely stuck. "
                        f"Check: kubectl get workflowrun {run_name} -n {OPENCHOREO_NAMESPACE}"
                    )


@pytest.mark.e2e
@pytest.mark.workflow
class TestRecentFailures:
    """Alert on recent build failures."""

    def test_no_failed_workflow_runs_in_last_hour(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """No WorkflowRun failed in the last hour."""
        all_runs = []
        for group in ["core.openchoreo.dev", "openchoreo.dev"]:
            try:
                all_runs = list_openchoreo_resources(
                    k8s_custom_api, "workflowruns",
                    namespace=OPENCHOREO_NAMESPACE,
                    group=group, version="v1alpha1",
                )
                if all_runs:
                    break
            except client.ApiException:
                continue

        recent_failures = []
        for run in all_runs:
            phase = run.get("status", {}).get("phase", "")
            if phase == "Failed":
                finished = run.get("status", {}).get("finishedAt", "")
                if finished and _age_in_minutes(finished) < 60:
                    recent_failures.append(run.get("metadata", {}).get("name", "unknown"))

        assert len(recent_failures) == 0, (
            f"WorkflowRuns failed in last hour: {recent_failures}. "
            f"Check: kubectl get workflowruns -n {OPENCHOREO_NAMESPACE}"
        )
