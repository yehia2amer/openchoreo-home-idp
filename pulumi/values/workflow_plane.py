"""Workflow Plane Helm values builder."""

from __future__ import annotations


def get_values(wp_argo_port: int) -> dict:
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
