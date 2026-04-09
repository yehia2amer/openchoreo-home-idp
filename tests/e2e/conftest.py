from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

try:
    from kubernetes import client as _k8s_client
    from utils.openchoreo_helpers import find_data_plane_namespace as _find_dp_ns

    _HAS_K8S_CLIENT = True
except ImportError:
    _HAS_K8S_CLIENT = False


# =============================================================================
# kubectl-based Fixtures (zero external dependencies)
# =============================================================================


@pytest.fixture(scope="session")
def kubeconfig() -> str:
    """Path to the kubeconfig file."""
    default = str(
        Path(__file__).resolve().parent.parent.parent
        / "pulumi"
        / "talos-cluster-baremetal"
        / "outputs"
        / "kubeconfig"
    )
    return os.path.expanduser(os.getenv("KUBECONFIG", default))


@pytest.fixture(scope="session")
def kube_context() -> str:
    """Kubernetes context name."""
    return os.getenv("KUBE_CONTEXT", "admin@openchoreo")


@pytest.fixture(scope="session")
def kubectl(kubeconfig: str, kube_context: str):
    """Helper that runs kubectl commands with the correct kubeconfig and context.

    Returns a callable: ``kubectl("get", "pods", "-n", "default")``
    that returns a ``subprocess.CompletedProcess``.
    """

    def _run(*args: str, **kwargs: Any) -> subprocess.CompletedProcess:
        cmd = [
            "kubectl",
            "--kubeconfig",
            kubeconfig,
            "--context",
            kube_context,
            *args,
        ]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120, **kwargs)

    return _run


@pytest.fixture(scope="session")
def kubectl_json(kubectl):
    """Helper that runs kubectl with ``-o json`` and returns parsed dict.

    Raises ``AssertionError`` if the command fails.
    """

    def _run(*args: str) -> dict:
        result = kubectl(*args, "-o", "json")
        assert result.returncode == 0, f"kubectl {' '.join(args)} failed: {result.stderr}"
        return json.loads(result.stdout)

    return _run


# =============================================================================
# Demo App Configuration
# =============================================================================


@pytest.fixture(scope="session")
def demo_app_config() -> dict:
    """Configuration for the Doclet demo application."""
    return {
        "project": "doclet",
        "environment": "development",
        "namespace": "default",
        "components": {
            "frontend": {"port": 80, "has_dependencies": True},
            "document-svc": {"port": 8080, "has_dependencies": False},
            "collab-svc": {"port": 8090, "has_dependencies": False},
            "nats": {"port": 4222, "has_dependencies": False},
            "postgres": {"port": 5432, "has_dependencies": False},
        },
        "buildable_components": ["frontend", "document-svc", "collab-svc"],
        "dependency_map": {
            "frontend": {
                "DOC_SERVICE_URL": "document-svc",
                "COLLAB_SERVICE_URL": "collab-svc",
            },
        },
    }


# =============================================================================
# Data Plane Namespace Discovery
# =============================================================================


if _HAS_K8S_CLIENT:

    @pytest.fixture(scope="session")
    def dp_namespace(k8s_core_api: _k8s_client.CoreV1Api) -> str:  # type: ignore[name-defined]
        ns = _find_dp_ns(k8s_core_api, project="doclet", environment="development")  # type: ignore[possibly-undefined]
        if ns is None:
            pytest.skip(
                "Data plane namespace dp-default-doclet-development-* not found — "
                "demo app may not be deployed yet"
            )
        return ns
