"""Docker Registry Helm values builder."""

from __future__ import annotations

from typing import Any


def get_values(wp_registry_port: int, registry_node_port: int = 0) -> dict[str, Any]:
    """Return Helm values for the docker-registry chart."""
    service: dict[str, Any] = {
        "port": wp_registry_port,
    }
    if registry_node_port:
        service["type"] = "NodePort"
        service["nodePort"] = registry_node_port
    else:
        service["type"] = "ClusterIP"

    return {
        "fullnameOverride": "registry",
        "persistence": {
            "enabled": True,
        },
        "service": service,
    }
