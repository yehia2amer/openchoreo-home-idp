"""Data Plane Helm values builder."""

from __future__ import annotations

from typing import Any


def get_values() -> dict[str, Any]:
    """Return Helm values for the OpenChoreo Data Plane chart.

    The gateway section was removed as part of the gateway consolidation
    (Phase 3 of sf8). All traffic now routes through the shared gateway
    in openchoreo-gateway namespace. Per-plane gateway-default resources
    are no longer created.
    """
    return {}
