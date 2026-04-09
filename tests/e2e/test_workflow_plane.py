"""Workflow Plane — Argo server, WP agent, CRD."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.workflow_plane

NS_WP = "openchoreo-workflow-plane"


def test_argo_server_deployment(kubectl_json):
    """argo-server deployment is ready."""
    data = kubectl_json("get", "deployment", "argo-server", "-n", NS_WP)
    ready = data.get("status", {}).get("readyReplicas", 0) or 0
    assert ready > 0, "argo-server has 0 ready replicas"


def test_workflow_plane_agent_deployment(kubectl_json):
    """cluster-agent-workflowplane deployment is ready."""
    data = kubectl_json("get", "deployment", "cluster-agent-workflowplane", "-n", NS_WP)
    ready = data.get("status", {}).get("readyReplicas", 0) or 0
    assert ready > 0, "cluster-agent-workflowplane has 0 ready replicas"


def test_crd_clusterworkflowplanes(kubectl):
    """ClusterWorkflowPlane CRD exists."""
    result = kubectl("get", "crd", "clusterworkflowplanes.openchoreo.dev")
    assert result.returncode == 0, f"CRD not found: {result.stderr}"
