"""Data Plane Helm values builder."""

from __future__ import annotations

from typing import Any

from config import CERT_DP_GATEWAY_TLS


def get_values(
    dp_http_port: int,
    dp_https_port: int,
    tls_enabled: bool,
    domain_base: str,
) -> dict[str, Any]:
    """Return Helm values for the OpenChoreo Data Plane chart."""
    return {
        "gateway": {
            "httpPort": dp_http_port,
            "httpsPort": dp_https_port,
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
