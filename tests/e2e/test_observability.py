"""Observability Plane — CRD and ExternalSecret."""

from __future__ import annotations

import os

import pytest

pytestmark = [
    pytest.mark.observability,
    pytest.mark.skipif(
        not os.getenv("ENABLE_OBSERVABILITY", ""),
        reason="ENABLE_OBSERVABILITY not set — observability tests skipped",
    ),
]

NS_OBS = "openchoreo-observability-plane"


def test_crd_clusterobservabilityplanes(kubectl):
    """ClusterObservabilityPlane CRD exists."""
    result = kubectl("get", "crd", "clusterobservabilityplanes.openchoreo.dev")
    assert result.returncode == 0, f"CRD not found: {result.stderr}"


def test_clusterobservabilityplane_exists(kubectl_json):
    """ClusterObservabilityPlane 'default' CR has Created condition."""
    data = kubectl_json(
        "get",
        "clusterobservabilityplanes.openchoreo.dev",
        "default",
    )
    conditions = data.get("status", {}).get("conditions", [])
    created = any(c.get("type") == "Created" and c.get("status") == "True" for c in conditions)
    assert created, f"ClusterObservabilityPlane 'default' not Created: {conditions}"


def test_observer_externalsecret_synced(kubectl_json):
    """observer-secret ExternalSecret reports Ready in observability namespace."""
    data = kubectl_json(
        "get",
        "externalsecrets.external-secrets.io",
        "observer-secret",
        "-n",
        NS_OBS,
    )
    conditions = data.get("status", {}).get("conditions", [])
    ready = any(c.get("type") == "Ready" and c.get("status") == "True" for c in conditions)
    assert ready, f"ExternalSecret observer-secret not Ready: {conditions}"
