"""Data Plane — agent deployment and CRD."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.data_plane

NS_DP = "openchoreo-data-plane"


def test_data_plane_agent_deployment(kubectl_json):
    """cluster-agent-dataplane deployment is ready."""
    data = kubectl_json("get", "deployment", "cluster-agent-dataplane", "-n", NS_DP)
    ready = data.get("status", {}).get("readyReplicas", 0) or 0
    assert ready > 0, "cluster-agent-dataplane has 0 ready replicas"


def test_crd_clusterdataplanes(kubectl):
    """ClusterDataPlane CRD exists."""
    result = kubectl("get", "crd", "clusterdataplanes.openchoreo.dev")
    assert result.returncode == 0, f"CRD not found: {result.stderr}"
