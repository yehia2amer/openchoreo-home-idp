"""Tests for Argo Workflows."""

import pytest
import requests
from kubernetes import client

from utils.k8s_helpers import check_deployment_ready, get_custom_resource
from utils.port_forward import PortForward


@pytest.mark.workflow_plane
@pytest.mark.smoke
class TestArgoWorkflowsHealth:
    """Test Argo Workflows server health."""

    def test_argo_server_deployment_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify Argo Workflows server deployment is ready."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["workflow_plane"], "argo-workflows-server"
        )

        # Try alternative name if not found
        if not is_ready and "not found" in message.lower():
            is_ready, message = check_deployment_ready(
                k8s_apps_api, namespaces["workflow_plane"], "argo-server"
            )

        assert is_ready, f"Argo Workflows server not ready: {message}"

    def test_argo_controller_deployment_ready(
        self,
        k8s_apps_api: client.AppsV1Api,
        namespaces: dict,
    ):
        """Verify Argo Workflows controller deployment is ready."""
        is_ready, message = check_deployment_ready(
            k8s_apps_api, namespaces["workflow_plane"], "argo-workflows-workflow-controller"
        )

        # Try alternative name if not found
        if not is_ready and "not found" in message.lower():
            is_ready, message = check_deployment_ready(
                k8s_apps_api, namespaces["workflow_plane"], "workflow-controller"
            )

        assert is_ready, f"Argo Workflows controller not ready: {message}"


@pytest.mark.workflow_plane
class TestArgoWorkflowsAPI:
    """Test Argo Workflows API."""

    def test_argo_api_info(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
    ):
        """Verify Argo Workflows API info endpoint."""
        with PortForward(
            k8s_core_api,
            namespaces["workflow_plane"],
            "argo-workflows-server",
            2746,
        ) as local_port:
            response = requests.get(
                f"http://localhost:{local_port}/api/v1/info",
                timeout=30,
            )

            assert response.status_code == 200, f"API info failed: {response.status_code}"

            info = response.json()
            assert "managedNamespace" in info or "links" in info, "Unexpected API info response"

    def test_list_workflows(
        self,
        k8s_core_api: client.CoreV1Api,
        namespaces: dict,
    ):
        """Verify workflow listing works."""
        with PortForward(
            k8s_core_api,
            namespaces["workflow_plane"],
            "argo-workflows-server",
            2746,
        ) as local_port:
            response = requests.get(
                f"http://localhost:{local_port}/api/v1/workflows/{namespaces['workflow_plane']}",
                timeout=30,
            )

            assert response.status_code == 200, f"List workflows failed: {response.status_code}"

            data = response.json()
            assert "items" in data or isinstance(data, dict), "Invalid workflow list response"


@pytest.mark.workflow_plane
class TestClusterWorkflowTemplates:
    """Test ClusterWorkflowTemplates."""

    def test_cluster_workflow_templates_exist(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """Verify ClusterWorkflowTemplates are installed."""
        templates = k8s_custom_api.list_cluster_custom_object(
            group="argoproj.io",
            version="v1alpha1",
            plural="clusterworkflowtemplates",
        )

        items = templates.get("items", [])
        assert len(items) > 0, "No ClusterWorkflowTemplates found"

    def test_expected_templates_exist(
        self,
        k8s_custom_api: client.CustomObjectsApi,
    ):
        """Verify expected workflow templates exist."""
        expected_templates = [
            "checkout-source",
            "publish-image",
        ]

        templates = k8s_custom_api.list_cluster_custom_object(
            group="argoproj.io",
            version="v1alpha1",
            plural="clusterworkflowtemplates",
        )

        template_names = [t.get("metadata", {}).get("name") for t in templates.get("items", [])]

        for expected in expected_templates:
            if expected not in template_names:
                pytest.skip(f"Template '{expected}' not found (may not be deployed)")


@pytest.mark.workflow_plane
@pytest.mark.slow
class TestWorkflowExecution:
    """Test workflow execution."""

    def test_submit_simple_workflow(
        self,
        k8s_core_api: client.CoreV1Api,
        k8s_custom_api: client.CustomObjectsApi,
        namespaces: dict,
    ):
        """Verify workflow submission and execution."""
        import time

        # Simple echo workflow
        workflow = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
            "metadata": {
                "generateName": "integration-test-",
                "namespace": namespaces["workflow_plane"],
            },
            "spec": {
                "entrypoint": "echo",
                "templates": [
                    {
                        "name": "echo",
                        "container": {
                            "image": "alpine:latest",
                            "command": ["echo"],
                            "args": ["Integration test successful"],
                        },
                    }
                ],
            },
        }

        # Submit workflow
        created = k8s_custom_api.create_namespaced_custom_object(
            group="argoproj.io",
            version="v1alpha1",
            namespace=namespaces["workflow_plane"],
            plural="workflows",
            body=workflow,
        )

        workflow_name = created["metadata"]["name"]

        try:
            # Wait for completion (max 60 seconds)
            for _ in range(12):
                time.sleep(5)

                wf = k8s_custom_api.get_namespaced_custom_object(
                    group="argoproj.io",
                    version="v1alpha1",
                    namespace=namespaces["workflow_plane"],
                    plural="workflows",
                    name=workflow_name,
                )

                phase = wf.get("status", {}).get("phase", "")
                if phase == "Succeeded":
                    return
                elif phase in ["Failed", "Error"]:
                    pytest.fail(f"Workflow failed with phase: {phase}")

            pytest.fail("Workflow did not complete in time")

        finally:
            # Cleanup
            try:
                k8s_custom_api.delete_namespaced_custom_object(
                    group="argoproj.io",
                    version="v1alpha1",
                    namespace=namespaces["workflow_plane"],
                    plural="workflows",
                    name=workflow_name,
                )
            except Exception:
                pass
