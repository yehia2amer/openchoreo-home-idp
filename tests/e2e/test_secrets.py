"""Secrets E2E — PushSecrets, ClusterSecretStore, ExternalSecrets, K8s Secrets."""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.secrets

NS_OPENBAO = "openbao"
NS_CP = "openchoreo-control-plane"
CLUSTER_SECRET_STORE_NAME = "default"


# ── PushSecret sync (conditional) ────────────────────────────────────────


def _assert_cr_condition_ready(
    kubectl_json, group, version, plural, name, namespace, condition_type="Ready"
):
    args = ["get", f"{plural}.{group}", name]
    if namespace:
        args += ["-n", namespace]
    data = kubectl_json(*args)
    conditions = data.get("status", {}).get("conditions", [])
    ready = any(c.get("type") == condition_type and c.get("status") == "True" for c in conditions)
    assert ready, f"{plural}/{name} condition {condition_type} not True: {conditions}"


@pytest.mark.skipif(not os.getenv("GITHUB_PAT", ""), reason="GITHUB_PAT not set")
def test_pushsecret_git_secrets(kubectl_json):
    """PushSecret git-secrets in openbao namespace reports Ready."""
    _assert_cr_condition_ready(
        kubectl_json,
        "external-secrets.io",
        "v1alpha1",
        "pushsecrets",
        "git-secrets",
        NS_OPENBAO,
    )


@pytest.mark.skipif(not os.getenv("ENABLE_FLUX", ""), reason="ENABLE_FLUX not set")
def test_pushsecret_backstage_fork_secrets(kubectl_json):
    """PushSecret backstage-fork-secrets in openbao namespace reports Ready."""
    _assert_cr_condition_ready(
        kubectl_json,
        "external-secrets.io",
        "v1alpha1",
        "pushsecrets",
        "backstage-fork-secrets",
        NS_OPENBAO,
    )


@pytest.mark.skipif(not os.getenv("ENABLE_OPENOBSERVE", ""), reason="ENABLE_OPENOBSERVE not set")
def test_pushsecret_openobserve_creds(kubectl_json):
    """PushSecret openobserve-creds in openbao namespace reports Ready."""
    _assert_cr_condition_ready(
        kubectl_json,
        "external-secrets.io",
        "v1alpha1",
        "pushsecrets",
        "openobserve-creds",
        NS_OPENBAO,
    )


@pytest.mark.skipif(not os.getenv("IS_DEV_STACK", ""), reason="IS_DEV_STACK not set")
def test_pushsecret_dev_secrets(kubectl_json):
    """PushSecret dev-secrets in openbao namespace reports Ready."""
    _assert_cr_condition_ready(
        kubectl_json,
        "external-secrets.io",
        "v1alpha1",
        "pushsecrets",
        "dev-secrets",
        NS_OPENBAO,
    )


# ── Source secret for git push ───────────────────────────────────────────


@pytest.mark.skipif(not os.getenv("GITHUB_PAT", ""), reason="GITHUB_PAT not set")
def test_push_git_secrets_exist(kubectl_json):
    """K8s Secret push-git-secrets in openbao ns has expected keys."""
    data = kubectl_json("get", "secret", "push-git-secrets", "-n", NS_OPENBAO)
    secret_data = data.get("data", {})
    for key in ("git-token", "gitops-token"):
        assert key in secret_data, f"Key '{key}' missing from push-git-secrets"


# ── ClusterSecretStore ───────────────────────────────────────────────────


def test_clustersecretstore_ready(kubectl_json):
    """ClusterSecretStore 'default' reports Ready — ESO can talk to OpenBao."""
    _assert_cr_condition_ready(
        kubectl_json,
        "external-secrets.io",
        "v1",
        "clustersecretstores",
        CLUSTER_SECRET_STORE_NAME,
        namespace=None,
    )


# ── Backstage ExternalSecret bridge ──────────────────────────────────────


def test_backstage_externalsecret_synced(kubectl_json):
    """backstage-secrets ExternalSecret in control plane ns reports Ready."""
    _assert_cr_condition_ready(
        kubectl_json,
        "external-secrets.io",
        "v1",
        "externalsecrets",
        "backstage-secrets",
        NS_CP,
    )


def test_backstage_secret_exists(kubectl_json):
    """backstage-secrets K8s Secret has expected keys."""
    data = kubectl_json("get", "secret", "backstage-secrets", "-n", NS_CP)
    secret_data = data.get("data", {})
    for key in ("backend-secret", "client-secret"):
        assert key in secret_data, f"Key '{key}' missing from backstage-secrets"
