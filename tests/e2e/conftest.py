"""E2E test fixtures — extends base conftest with OpenChoreo-specific setup."""

import pytest
from kubernetes import client

from utils.openchoreo_helpers import find_data_plane_namespace


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


@pytest.fixture(scope="session")
def dp_namespace(k8s_core_api: client.CoreV1Api) -> str:
    """Discover the data plane namespace for doclet/development.

    Returns the namespace name or skips the test if not found.
    """
    ns = find_data_plane_namespace(k8s_core_api, project="doclet", environment="development")
    if ns is None:
        pytest.skip(
            "Data plane namespace dp-default-doclet-development-* not found — "
            "demo app may not be deployed yet"
        )
    return ns
