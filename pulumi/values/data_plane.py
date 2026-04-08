"""Data Plane Helm values builder."""

from __future__ import annotations

from typing import Any

from config import CERT_DP_GATEWAY_TLS


def get_values(
    tls_enabled: bool,
    domain_base: str,
) -> dict[str, Any]:
    """Return Helm values for the OpenChoreo Data Plane chart.

    The per-plane gateway Service was removed as part of the gateway
    consolidation (Phase 3 of sf8). All traffic now routes through the
    shared gateway in openchoreo-gateway namespace. Only the TLS config
    remains so the chart knows which hostname and certificate to use for
    HTTPRoutes.
    """
    return {
        "gateway": {
            "tls": {
                "enabled": tls_enabled,
                **(
                    {
                        "hostname": f"*.{domain_base}",
                        "certificateRefs": [{"name": CERT_DP_GATEWAY_TLS}],
                    }
                    if tls_enabled
                    else {}
                ),
            },
        },
    }
