"""Workflow Plane Helm values builder."""

from __future__ import annotations

from typing import Any


def get_values(wp_argo_port: int) -> dict[str, Any]:
    """Return Helm values for the OpenChoreo Workflow Plane chart."""
    return {
        "argo-workflows": {
            "server": {
                "enabled": True,
                "serviceType": "LoadBalancer",
                "servicePort": wp_argo_port,
                "authModes": ["server"],
            },
        },
    }
