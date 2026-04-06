"""Control Plane Helm values builder."""

from __future__ import annotations

from typing import Any

from config import CERT_CP_GATEWAY_TLS, SECRET_BACKSTAGE, THUNDER_INTERNAL_BASE


def get_values(
    domain_base: str,
    scheme: str,
    cp_port: int,
    cp_http_port: int,
    cp_https_port: int,
    tls_enabled: bool,
    thunder_url: str,
) -> dict[str, Any]:
    """Return Helm values for the OpenChoreo Control Plane chart."""
    backstage_base_url = f"{scheme}://{domain_base}:{cp_port}"
    backstage_redirect_url = f"{backstage_base_url}/api/auth/openchoreo-auth/handler/frame"

    return {
        "openchoreoApi": {
            "http": {
                "hostnames": [f"api.{domain_base}"],
            },
            "config": {
                "server": {
                    "publicUrl": f"{scheme}://api.{domain_base}:{cp_port}",
                },
                "mcp": {
                    "enabled": True,
                    "toolsets": [
                        "namespace",
                        "project",
                        "component",
                        "deployment",
                        "build",
                        "pe",
                    ],
                },
            },
        },
        "backstage": {
            "secretName": SECRET_BACKSTAGE,
            "baseUrl": backstage_base_url,
            "http": {
                "hostnames": [domain_base],
            },
            "auth": {
                "redirectUrls": [backstage_redirect_url],
            },
            "features": {
                "auth": {
                    "redirectFlow": {
                        "enabled": True,
                    },
                },
            },
        },
        "security": {
            "oidc": {
                "issuer": thunder_url,
                "jwksUrl": f"{THUNDER_INTERNAL_BASE}/oauth2/jwks",
                "authorizationUrl": f"{thunder_url}/oauth2/authorize",
                "tokenUrl": f"{THUNDER_INTERNAL_BASE}/oauth2/token",
            },
        },
        "gateway": {
            "httpPort": cp_http_port,
            "httpsPort": cp_https_port,
            "tls": {
                "enabled": tls_enabled,
                **(
                    {
                        "hostname": f"*.{domain_base}",
                        "certificateRefs": [{"name": CERT_CP_GATEWAY_TLS}],
                    }
                    if tls_enabled
                    else {}
                ),
            },
        },
    }
