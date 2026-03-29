"""Docker Registry Helm values builder."""

from __future__ import annotations

from typing import Any


def get_values(wp_registry_port: int) -> dict[str, Any]:
    """Return Helm values for the docker-registry chart."""
    return {
        "fullnameOverride": "registry",
        "persistence": {
            "enabled": True,
        },
        "service": {
            "type": "LoadBalancer",
            "port": wp_registry_port,
        },
    }
