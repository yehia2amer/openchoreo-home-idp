"""Thunder IdP — deployment, HTTPRoute, JWKS endpoint."""

from __future__ import annotations

import json
import subprocess
import time

import pytest

pytestmark = pytest.mark.thunder

NS_THUNDER = "thunder"


def test_thunder_deployment(kubectl_json):
    """Thunder deployment is ready."""
    data = kubectl_json(
        "get",
        "deployment",
        "thunder-deployment",
        "-n",
        NS_THUNDER,
    )
    ready = data.get("status", {}).get("readyReplicas", 0) or 0
    assert ready > 0, "thunder-deployment has 0 ready replicas"


def test_thunder_httproute_status(kubectl_json):
    """Thunder HTTPRoute is accepted by the gateway controller."""
    data = kubectl_json(
        "get",
        "httproute",
        "thunder-httproute",
        "-n",
        NS_THUNDER,
    )
    parents = data.get("status", {}).get("parents", [])
    assert len(parents) > 0, "HTTPRoute has no parent status"
    for parent in parents:
        conditions = parent.get("conditions", [])
        accepted = any(
            c.get("type") == "Accepted" and c.get("status") == "True" for c in conditions
        )
        assert accepted, f"HTTPRoute parent not accepted: {conditions}"


def test_thunder_jwks_http(kubectl, kubeconfig, kube_context):
    """Thunder JWKS endpoint responds via port-forward to the service."""
    pf_cmd = [
        "kubectl",
        "--kubeconfig",
        kubeconfig,
        "--context",
        kube_context,
        "port-forward",
        "svc/thunder-service",
        "0:8090",
        "-n",
        NS_THUNDER,
    ]
    pf = subprocess.Popen(pf_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        time.sleep(3)
        # Read the assigned local port from stderr
        import select

        local_port = 8090  # fallback
        if pf.stderr and select.select([pf.stderr], [], [], 2)[0]:
            line = pf.stderr.readline()
            if "Forwarding from" in line:
                # "Forwarding from 127.0.0.1:XXXXX -> 8090"
                local_port = int(line.split(":")[1].split(" ")[0])

        result = subprocess.run(
            ["curl", "-sf", "--max-time", "10", f"http://127.0.0.1:{local_port}/oauth2/jwks"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0, f"JWKS request failed: {result.stderr}"
        jwks = json.loads(result.stdout)
        assert "keys" in jwks, "JWKS response missing 'keys' field"
    finally:
        pf.terminate()
        pf.wait(timeout=5)
