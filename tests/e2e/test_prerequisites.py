"""Prerequisite infrastructure: cert-manager, External Secrets Operator, OpenBao."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.prerequisites

# ── Namespace constants ────────────────────────────────────────────────────
NS_CERT_MANAGER = "cert-manager"
NS_EXTERNAL_SECRETS = "external-secrets"
NS_OPENBAO = "openbao"


def test_cert_manager_deployments(kubectl_json):
    """At least one cert-manager deployment is ready (matched by label)."""
    data = kubectl_json(
        "get",
        "deployments",
        "-n",
        NS_CERT_MANAGER,
        "-l",
        "app.kubernetes.io/name=cert-manager",
    )
    items = data.get("items", [])
    assert len(items) >= 1, "No cert-manager deployments found"
    for dep in items:
        ready = dep.get("status", {}).get("readyReplicas", 0) or 0
        name = dep["metadata"]["name"]
        assert ready > 0, f"cert-manager deployment {name} has 0 ready replicas"


def test_external_secrets_deployment(kubectl_json):
    """external-secrets deployment is ready."""
    data = kubectl_json(
        "get",
        "deployment",
        "external-secrets",
        "-n",
        NS_EXTERNAL_SECRETS,
    )
    ready = data.get("status", {}).get("readyReplicas", 0) or 0
    assert ready > 0, "external-secrets deployment has 0 ready replicas"


def test_openbao_statefulset(kubectl_json):
    """OpenBao StatefulSet has at least one ready replica."""
    data = kubectl_json(
        "get",
        "statefulset",
        "openbao",
        "-n",
        NS_OPENBAO,
    )
    ready = data.get("status", {}).get("readyReplicas", 0) or 0
    assert ready > 0, "openbao statefulset has 0 ready replicas"
