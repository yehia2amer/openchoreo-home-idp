"""Gateway API — CRDs for gateways and httproutes."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.gateway_api


@pytest.mark.parametrize(
    "crd_name",
    [
        "gateways.gateway.networking.k8s.io",
        "httproutes.gateway.networking.k8s.io",
    ],
)
def test_gateway_api_crds(kubectl, crd_name):
    """Gateway API CRD exists in the cluster."""
    result = kubectl("get", "crd", crd_name)
    assert result.returncode == 0, f"CRD {crd_name} not found: {result.stderr}"
