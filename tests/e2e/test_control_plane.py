"""Control Plane — API server, Backstage, controller-manager, cluster-gateway, CRDs."""

from __future__ import annotations

import json
import subprocess
import time

import pytest

pytestmark = pytest.mark.control_plane

NS_CP = "openchoreo-control-plane"


# ── Deployments ───────────────────────────────────────────────────────────


def test_openchoreo_api_deployment(kubectl_json):
    """openchoreo-api deployment is ready."""
    data = kubectl_json("get", "deployment", "openchoreo-api", "-n", NS_CP)
    ready = data.get("status", {}).get("readyReplicas", 0) or 0
    assert ready > 0, "openchoreo-api has 0 ready replicas"


def test_backstage_deployment(kubectl_json):
    """backstage deployment is ready."""
    data = kubectl_json("get", "deployment", "backstage", "-n", NS_CP)
    ready = data.get("status", {}).get("readyReplicas", 0) or 0
    assert ready > 0, "backstage has 0 ready replicas"


def test_controller_manager_deployment(kubectl_json):
    """controller-manager deployment is ready."""
    data = kubectl_json("get", "deployment", "controller-manager", "-n", NS_CP)
    ready = data.get("status", {}).get("readyReplicas", 0) or 0
    assert ready > 0, "controller-manager has 0 ready replicas"


def test_cluster_gateway_deployment(kubectl_json):
    """cluster-gateway deployment is ready."""
    data = kubectl_json("get", "deployment", "cluster-gateway", "-n", NS_CP)
    ready = data.get("status", {}).get("readyReplicas", 0) or 0
    assert ready > 0, "cluster-gateway has 0 ready replicas"


# ── HTTPRoutes ────────────────────────────────────────────────────────────


def _assert_httproute_accepted(kubectl_json, name: str, namespace: str):
    data = kubectl_json("get", "httproute", name, "-n", namespace)
    parents = data.get("status", {}).get("parents", [])
    assert len(parents) > 0, f"HTTPRoute {name} has no parent status"
    for parent in parents:
        conditions = parent.get("conditions", [])
        accepted = any(
            c.get("type") == "Accepted" and c.get("status") == "True" for c in conditions
        )
        assert accepted, f"HTTPRoute {name} not accepted: {conditions}"


def test_openchoreo_api_httproute_status(kubectl_json):
    """openchoreo-api HTTPRoute is accepted."""
    _assert_httproute_accepted(kubectl_json, "openchoreo-api", NS_CP)


def test_backstage_httproute_status(kubectl_json):
    """backstage HTTPRoute is accepted."""
    _assert_httproute_accepted(kubectl_json, "backstage", NS_CP)


# ── Service HTTP checks ──────────────────────────────────────────────────


def _port_forward_http_check(
    kubeconfig: str,
    kube_context: str,
    service: str,
    namespace: str,
    port: int,
    path: str,
    expected_statuses: list[int],
):
    pf_cmd = [
        "kubectl",
        "--kubeconfig",
        kubeconfig,
        "--context",
        kube_context,
        "port-forward",
        f"svc/{service}",
        f"0:{port}",
        "-n",
        namespace,
    ]
    pf = subprocess.Popen(pf_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        time.sleep(3)
        local_port = port
        import select

        if pf.stderr and select.select([pf.stderr], [], [], 2)[0]:
            line = pf.stderr.readline()
            if "Forwarding from" in line:
                local_port = int(line.split(":")[1].split(" ")[0])

        result = subprocess.run(
            [
                "curl",
                "-s",
                "-o",
                "/dev/null",
                "-w",
                "%{http_code}",
                "--max-time",
                "10",
                f"http://127.0.0.1:{local_port}{path}",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        status_code = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        assert status_code in expected_statuses, (
            f"svc/{service} returned {status_code}, expected one of {expected_statuses}"
        )
    finally:
        pf.terminate()
        pf.wait(timeout=5)


def test_openchoreo_api_http(kubeconfig, kube_context):
    """openchoreo-api service responds to HTTP (200 or 404 proves it's up)."""
    _port_forward_http_check(
        kubeconfig, kube_context, "openchoreo-api", NS_CP, 8080, "/", [200, 404]
    )


def test_backstage_http(kubeconfig, kube_context):
    """backstage service responds to HTTP."""
    _port_forward_http_check(
        kubeconfig, kube_context, "backstage", NS_CP, 7007, "/", [200, 301, 302]
    )


# ── CRDs ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "crd_name",
    [
        "components.openchoreo.dev",
        "projects.openchoreo.dev",
        "environments.openchoreo.dev",
    ],
)
def test_control_plane_crds(kubectl, crd_name):
    """Control plane CRD exists in the cluster."""
    result = kubectl("get", "crd", crd_name)
    assert result.returncode == 0, f"CRD {crd_name} not found: {result.stderr}"
