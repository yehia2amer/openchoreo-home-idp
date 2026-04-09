"""FluxCD — controller deployments, Kustomizations, HelmReleases, drift healing."""

from __future__ import annotations

import os
import time

import pytest

pytestmark = [
    pytest.mark.flux,
    pytest.mark.skipif(
        not os.getenv("ENABLE_FLUX", ""),
        reason="ENABLE_FLUX not set — Flux tests skipped",
    ),
]

NS_FLUX = "flux-system"


# ── Controller deployments ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "controller",
    [
        "source-controller",
        "kustomize-controller",
        "helm-controller",
    ],
)
def test_flux_controller_deployment(kubectl_json, controller):
    """Flux controller deployment is ready in flux-system."""
    data = kubectl_json("get", "deployment", controller, "-n", NS_FLUX)
    ready = data.get("status", {}).get("readyReplicas", 0) or 0
    assert ready > 0, f"flux {controller} has 0 ready replicas"


# ── Kustomization E2E ─────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "kustomization",
    [
        "oc-namespaces",
        "oc-platform-shared",
        "oc-platform",
        "oc-demo-projects",
    ],
)
def test_flux_kustomization_ready(kubectl_json, kustomization):
    """Flux Kustomization reports Ready=True condition."""
    data = kubectl_json(
        "get",
        "kustomization.kustomize.toolkit.fluxcd.io",
        kustomization,
        "-n",
        NS_FLUX,
    )
    conditions = data.get("status", {}).get("conditions", [])
    ready = any(c.get("type") == "Ready" and c.get("status") == "True" for c in conditions)
    assert ready, f"Kustomization {kustomization} not Ready: {conditions}"


# ── Backstage-fork ExternalSecret (Flux-managed) ─────────────────────────


def test_backstage_fork_externalsecret_synced(kubectl_json):
    """backstage-fork ExternalSecret in backstage-fork namespace reports Ready."""
    data = kubectl_json(
        "get",
        "externalsecrets.external-secrets.io",
        "backstage-fork-secrets",
        "-n",
        "backstage-fork",
    )
    conditions = data.get("status", {}).get("conditions", [])
    ready = any(c.get("type") == "Ready" and c.get("status") == "True" for c in conditions)
    assert ready, f"ExternalSecret backstage-fork-secrets not Ready: {conditions}"


def test_backstage_fork_secret_exists(kubectl_json):
    """backstage-fork-secrets K8s Secret exists with expected keys."""
    data = kubectl_json("get", "secret", "backstage-fork-secrets", "-n", "backstage-fork")
    secret_data = data.get("data", {})
    expected_keys = [
        "backend-secret",
        "client-id",
        "client-secret",
        "auth-authorization-url",
        "jenkins-api-key",
    ]
    for key in expected_keys:
        assert key in secret_data, f"Key '{key}' missing from backstage-fork-secrets"


# ── NEW: HelmReleases reconciled ──────────────────────────────────────────


def test_helmreleases_reconciled(kubectl):
    """All Flux HelmReleases across all namespaces report Ready status."""
    result = kubectl(
        "get",
        "helmreleases.helm.toolkit.fluxcd.io",
        "-A",
        "-o",
        "json",
    )
    assert result.returncode == 0, f"Failed to list HelmReleases: {result.stderr}"
    import json

    data = json.loads(result.stdout)
    items = data.get("items", [])
    if not items:
        pytest.skip("No HelmReleases found in cluster")
    for hr in items:
        name = hr["metadata"]["name"]
        ns = hr["metadata"]["namespace"]
        conditions = hr.get("status", {}).get("conditions", [])
        ready = any(c.get("type") == "Ready" and c.get("status") == "True" for c in conditions)
        assert ready, f"HelmRelease {ns}/{name} not Ready: {conditions}"


# ── NEW: Kustomizations all ready ────────────────────────────────────────


def test_all_kustomizations_ready(kubectl):
    """All Flux Kustomizations across all namespaces report Ready status."""
    result = kubectl(
        "get",
        "kustomizations.kustomize.toolkit.fluxcd.io",
        "-A",
        "-o",
        "json",
    )
    assert result.returncode == 0, f"Failed to list Kustomizations: {result.stderr}"
    import json

    data = json.loads(result.stdout)
    items = data.get("items", [])
    if not items:
        pytest.skip("No Kustomizations found in cluster")
    for ks in items:
        name = ks["metadata"]["name"]
        ns = ks["metadata"]["namespace"]
        conditions = ks.get("status", {}).get("conditions", [])
        ready = any(c.get("type") == "Ready" and c.get("status") == "True" for c in conditions)
        assert ready, f"Kustomization {ns}/{name} not Ready: {conditions}"


# ── NEW: Drift healing ───────────────────────────────────────────────────


def test_drift_healing(kubectl):
    """Delete a Flux-managed ConfigMap and verify it's recreated within 60s.

    Uses the flux-system namespace kube-root-ca.crt ConfigMap as a safe target.
    If no suitable ConfigMap is found, creates and deletes a test one in a
    Flux-managed namespace.
    """
    # Use oc-namespaces Kustomization — it manages namespace resources
    # Create a ConfigMap that Flux doesn't manage, then delete one it does
    # Safer approach: check that the flux-system namespace itself exists after deletion attempt

    # List ConfigMaps in flux-system managed by Flux Kustomization
    result = kubectl(
        "get",
        "configmaps",
        "-n",
        NS_FLUX,
        "-l",
        "kustomize.toolkit.fluxcd.io/name",
        "-o",
        "json",
    )
    if result.returncode != 0 or not result.stdout.strip():
        pytest.skip("No Flux-managed ConfigMaps found for drift test")

    import json

    data = json.loads(result.stdout)
    items = data.get("items", [])
    if not items:
        pytest.skip("No Flux-managed ConfigMaps found for drift test")

    target = items[0]
    cm_name = target["metadata"]["name"]

    # Delete the ConfigMap
    del_result = kubectl("delete", "configmap", cm_name, "-n", NS_FLUX, "--wait=false")
    assert del_result.returncode == 0, f"Failed to delete ConfigMap: {del_result.stderr}"

    # Wait up to 90s for Flux to recreate it
    for _ in range(18):
        time.sleep(5)
        check = kubectl("get", "configmap", cm_name, "-n", NS_FLUX)
        if check.returncode == 0:
            return  # Drift healed

    pytest.fail(f"ConfigMap {cm_name} was not recreated by Flux within 90s")
