"""Observability Plane Helm values builder."""

from __future__ import annotations

from typing import Any

from config import CERT_OP_GATEWAY_TLS, SECRET_OBSERVER, SECRET_OPENSEARCH_ADMIN, THUNDER_INTERNAL_BASE


def get_values(
    domain_base: str,
    thunder_url: str,
    tls_enabled: bool,
    op_http_port: int,
    op_https_port: int,
) -> dict[str, Any]:
    """Return Helm values for the OpenChoreo Observability Plane chart."""
    return {
        "observer": {
            "openSearchSecretName": SECRET_OPENSEARCH_ADMIN,
            "secretName": SECRET_OBSERVER,
            "http": {
                "hostnames": [f"observer.{domain_base}"],
            },
        },
        "security": {
            "oidc": {
                "jwksUrl": f"{THUNDER_INTERNAL_BASE}/oauth2/jwks",
                "tokenUrl": f"{THUNDER_INTERNAL_BASE}/oauth2/token",
                "authServerBaseUrl": thunder_url,
            },
        },
        "rca": {
            "http": {
                "hostnames": [f"rca-agent.{domain_base}"],
            },
        },
        "gateway": {
            "httpPort": op_http_port,
            "httpsPort": op_https_port,
            "tls": {
                "enabled": tls_enabled,
                **(
                    {
                        "hostname": f"*.{domain_base}",
                        "certificateRefs": [{"name": CERT_OP_GATEWAY_TLS}],
                    }
                    if tls_enabled
                    else {}
                ),
            },
        },
    }
