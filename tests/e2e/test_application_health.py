"""E2E Tests: Application pod health — CrashLoop detection and restart monitoring.

This is the highest-value E2E test layer. It would have caught the frontend
CrashLoopBackOff incident (68+ restarts) immediately.

Tests verify that deployed application pods are:
- Actually Running (not just that Deployments exist)
- Not in CrashLoopBackOff
- Not restarting excessively
- Have all containers in Ready state
"""

import pytest
from kubernetes import client

from utils.openchoreo_helpers import find_data_plane_namespace


# Maximum acceptable restart count before we flag a problem
MAX_RESTART_COUNT = 5


@pytest.mark.e2e
@pytest.mark.app_health
class TestDataPlaneNamespace:
    """Verify the data plane namespace exists for the demo app."""

    def test_data_plane_namespace_exists(self, k8s_core_api: client.CoreV1Api):
        """Data plane namespace for doclet project exists."""
        ns = find_data_plane_namespace(k8s_core_api)
        assert ns is not None, (
            "No namespace matching dp-default-doclet-development-* found. "
            "The project may not have been deployed yet. "
            "Run the WorkflowRuns for document-svc, collab-svc, and frontend first."
        )


@pytest.mark.e2e
@pytest.mark.app_health
class TestPodRunning:
    """Verify each component has at least one Running pod."""

    @pytest.mark.parametrize(
        "pod_prefix",
        ["frontend-development", "document-svc-development", "collab-svc-development",
         "nats-development", "postgres-development"],
    )
    def test_pod_is_running(
        self,
        k8s_core_api: client.CoreV1Api,
        dp_namespace: str,
        pod_prefix: str,
    ):
        """Each component has at least one pod in Running phase."""
        pods = k8s_core_api.list_namespaced_pod(dp_namespace)
        component = pod_prefix.replace("-development", "")

        matching = [
            p for p in pods.items
            if component in p.metadata.name
        ]

        assert len(matching) > 0, (
            f"No pods found for '{component}' in namespace {dp_namespace}. "
            f"Available pods: {[p.metadata.name for p in pods.items]}"
        )

        running = [p for p in matching if p.status.phase == "Running"]
        assert len(running) >= 1, (
            f"Expected >= 1 Running pod for '{component}', "
            f"found {len(running)} Running out of {len(matching)} total. "
            f"Pod statuses: {[(p.metadata.name, p.status.phase) for p in matching]}"
        )


@pytest.mark.e2e
@pytest.mark.app_health
class TestNoCrashLoop:
    """Verify no pods are in CrashLoopBackOff — the exact symptom from the incident."""

    @pytest.mark.parametrize(
        "component",
        ["frontend", "document-svc", "collab-svc", "nats", "postgres"],
    )
    def test_no_crashloop(
        self,
        k8s_core_api: client.CoreV1Api,
        dp_namespace: str,
        component: str,
    ):
        """No pods for this component are in CrashLoopBackOff."""
        pods = k8s_core_api.list_namespaced_pod(dp_namespace)

        for pod in pods.items:
            if component not in pod.metadata.name:
                continue
            for cs in pod.status.container_statuses or []:
                waiting = cs.state.waiting if cs.state else None
                if waiting and waiting.reason == "CrashLoopBackOff":
                    pytest.fail(
                        f"Pod '{pod.metadata.name}' is in CrashLoopBackOff! "
                        f"Restart count: {cs.restart_count}. "
                        f"Last termination: {cs.last_state.terminated if cs.last_state else 'unknown'}. "
                        f"Check: kubectl logs -n {dp_namespace} {pod.metadata.name}"
                    )


@pytest.mark.e2e
@pytest.mark.app_health
class TestRestartCount:
    """Verify pods haven't restarted excessively."""

    @pytest.mark.parametrize(
        "component",
        ["frontend", "document-svc", "collab-svc", "nats", "postgres"],
    )
    def test_low_restart_count(
        self,
        k8s_core_api: client.CoreV1Api,
        dp_namespace: str,
        component: str,
    ):
        """Pods haven't restarted more than MAX_RESTART_COUNT times."""
        pods = k8s_core_api.list_namespaced_pod(dp_namespace)

        for pod in pods.items:
            if component not in pod.metadata.name:
                continue
            for cs in pod.status.container_statuses or []:
                assert cs.restart_count < MAX_RESTART_COUNT, (
                    f"Pod '{pod.metadata.name}' container '{cs.name}' "
                    f"has {cs.restart_count} restarts (threshold: {MAX_RESTART_COUNT}). "
                    f"Something is causing repeated crashes. "
                    f"Check: kubectl logs -n {dp_namespace} {pod.metadata.name} --previous"
                )


@pytest.mark.e2e
@pytest.mark.app_health
class TestContainersReady:
    """Verify all containers in running pods report ready=True."""

    @pytest.mark.parametrize(
        "component",
        ["frontend", "document-svc", "collab-svc", "nats", "postgres"],
    )
    def test_all_containers_ready(
        self,
        k8s_core_api: client.CoreV1Api,
        dp_namespace: str,
        component: str,
    ):
        """All containers in matching Running pods report ready."""
        pods = k8s_core_api.list_namespaced_pod(dp_namespace)

        for pod in pods.items:
            if component not in pod.metadata.name:
                continue
            if pod.status.phase != "Running":
                continue
            for cs in pod.status.container_statuses or []:
                assert cs.ready, (
                    f"Container '{cs.name}' in pod '{pod.metadata.name}' is not ready. "
                    f"State: {cs.state}"
                )
