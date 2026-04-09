"""Gateway E2E — shared Gateway resource Programmed condition."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.gateway_e2e


def test_shared_gateway_programmed(kubectl_json):
    """Shared Gateway 'gateway-shared' in openchoreo-gateway ns has Programmed condition."""
    data = kubectl_json(
        "get",
        "gateways.gateway.networking.k8s.io",
        "gateway-shared",
        "-n",
        "openchoreo-gateway",
    )
    conditions = data.get("status", {}).get("conditions", [])
    programmed = any(
        c.get("type") == "Programmed" and c.get("status") == "True" for c in conditions
    )
    assert programmed, f"Gateway gateway-shared not Programmed: {conditions}"


# ── Plane Registration ───────────────────────────────────────────────────


def test_clusterdataplane_exists(kubectl_json):
    """ClusterDataPlane 'default' has Created condition."""
    data = kubectl_json(
        "get",
        "clusterdataplanes.openchoreo.dev",
        "default",
    )
    conditions = data.get("status", {}).get("conditions", [])
    created = any(c.get("type") == "Created" and c.get("status") == "True" for c in conditions)
    assert created, f"ClusterDataPlane 'default' not Created: {conditions}"


def test_clusterworkflowplane_exists(kubectl_json):
    """ClusterWorkflowPlane 'default' has Created condition."""
    data = kubectl_json(
        "get",
        "clusterworkflowplanes.openchoreo.dev",
        "default",
    )
    conditions = data.get("status", {}).get("conditions", [])
    created = any(c.get("type") == "Created" and c.get("status") == "True" for c in conditions)
    assert created, f"ClusterWorkflowPlane 'default' not Created: {conditions}"
