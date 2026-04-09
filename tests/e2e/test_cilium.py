"""Cilium CNI — operator deployment and agent daemonset."""

from __future__ import annotations

import os

import pytest

pytestmark = [
    pytest.mark.cilium,
    pytest.mark.skipif(
        not os.getenv("ENABLE_CILIUM", ""),
        reason="ENABLE_CILIUM not set — Cilium tests skipped",
    ),
]


def test_cilium_operator_deployment(kubectl_json):
    """Cilium operator deployment is ready in kube-system."""
    data = kubectl_json(
        "get",
        "deployment",
        "cilium-operator",
        "-n",
        "kube-system",
    )
    ready = data.get("status", {}).get("readyReplicas", 0) or 0
    assert ready > 0, "cilium-operator deployment has 0 ready replicas"


def test_cilium_daemonset(kubectl_json):
    """Cilium agent daemonset has ready nodes in kube-system."""
    data = kubectl_json(
        "get",
        "daemonset",
        "cilium",
        "-n",
        "kube-system",
    )
    ready = data.get("status", {}).get("numberReady", 0) or 0
    assert ready > 0, "cilium daemonset has 0 ready nodes"
