from __future__ import annotations

import importlib
import os

from config import NS_CONTROL_PLANE, NS_THUNDER
from helpers.k8s_ops import (
    check_crd_exists,
    check_deployment_ready,
    check_httproute_accepted,
    check_secret_exists,
    check_service_http,
)

pytest = importlib.import_module("pytest")


@pytest.mark.e2e
@pytest.mark.timeout(120)
def test_control_plane_api_deployment_ready(kubeconfig: str, kube_context: str) -> None:
    namespace = os.getenv("E2E_CP_NAMESPACE", NS_CONTROL_PLANE)
    deployment_name = os.getenv("E2E_CP_DEPLOYMENT", "openchoreo-api")
    result = check_deployment_ready(kubeconfig, kube_context, deployment_name, namespace)
    assert result["passed"], result


@pytest.mark.e2e
@pytest.mark.timeout(120)
def test_thunder_httproute_accepted(kubeconfig: str, kube_context: str) -> None:
    route_name = os.getenv("E2E_THUNDER_ROUTE", "thunder-httproute")
    route_namespace = os.getenv("E2E_THUNDER_NAMESPACE", NS_THUNDER)
    result = check_httproute_accepted(kubeconfig, kube_context, route_name, route_namespace)
    assert result["passed"], result


@pytest.mark.e2e
@pytest.mark.timeout(120)
def test_backstage_service_http(kubeconfig: str, kube_context: str) -> None:
    namespace = os.getenv("E2E_BACKSTAGE_NAMESPACE", NS_CONTROL_PLANE)
    service_name = os.getenv("E2E_BACKSTAGE_SERVICE", "backstage")
    service_port = int(os.getenv("E2E_BACKSTAGE_PORT", "7007"))
    result = check_service_http(
        kubeconfig,
        kube_context,
        service_name,
        namespace,
        service_port,
        path="/",
        expected_statuses=[200, 301, 302],
        timeout=60,
    )
    assert result["passed"], result


@pytest.mark.e2e
@pytest.mark.timeout(120)
def test_gateway_httproute_crd_exists(kubeconfig: str, kube_context: str) -> None:
    crd_name = os.getenv("E2E_HTTPROUTE_CRD", "httproutes.gateway.networking.k8s.io")
    result = check_crd_exists(kubeconfig, kube_context, crd_name)
    assert result["passed"], result


@pytest.mark.e2e
@pytest.mark.timeout(120)
def test_backstage_secret_exists(kubeconfig: str, kube_context: str) -> None:
    namespace = os.getenv("E2E_BACKSTAGE_NAMESPACE", NS_CONTROL_PLANE)
    secret_name = os.getenv("E2E_BACKSTAGE_SECRET", "backstage-secrets")
    result = check_secret_exists(
        kubeconfig,
        kube_context,
        secret_name,
        namespace,
        expected_keys=["backend-secret", "client-secret"],
    )
    assert result["passed"], result
