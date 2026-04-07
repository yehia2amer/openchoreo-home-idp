"""Observability Plane Helm values builder."""

from __future__ import annotations

from typing import Any

from config import CERT_OP_GATEWAY_TLS, SECRET_OBSERVER, SECRET_OPENSEARCH_ADMIN, THUNDER_INTERNAL_BASE


def get_values(
    domain_base: str,
    thunder_url: str,
    backstage_url: str,
    tls_enabled: bool,
    op_http_port: int,
    op_https_port: int,
    observer_url: str = "",
    control_plane_api_url: str = "",
    enable_openobserve: bool = False,
    enable_rca: bool = False,
    rca_llm_model: str = "",
    rca_llm_base_url: str = "",
) -> dict[str, Any]:
    """Return Helm values for the OpenChoreo Observability Plane chart."""
    op_scheme = "https" if tls_enabled else "http"
    op_port = op_https_port if tls_enabled else op_http_port
    effective_observer_url = observer_url or f"{op_scheme}://observer.{domain_base}:{op_port}"
    # Internal service URL for control plane API (authz + uid-resolver).
    # Falls back to the internal k8s service name.
    effective_cp_api_url = (
        control_plane_api_url or "http://openchoreo-api.openchoreo-control-plane.svc.cluster.local:8080"
    )
    return {
        "observer": {
            "openSearchSecretName": SECRET_OPENSEARCH_ADMIN,
            "secretName": SECRET_OBSERVER,
            "controlPlaneApiUrl": effective_cp_api_url,
            "authzTlsInsecureSkipVerify": tls_enabled,  # self-signed certs
            "http": {
                "hostnames": [f"observer.{domain_base}"],
            },
            "cors": {
                "allowedOrigins": [backstage_url],
            },
            "extraEnvs": [
                # IMPORTANT: extraEnvs REPLACES (not appends) the chart's default
                # env block, which includes OPENSEARCH_ADDRESS, PROMETHEUS_ADDRESS,
                # PROMETHEUS_TIMEOUT, and AUTHZ_TIMEOUT. We must include all of them
                # here alongside any custom env vars.
                {"name": "OBSERVER_BASE_URL", "value": effective_observer_url},
                {"name": "OPENSEARCH_ADDRESS", "value": "https://opensearch:9200"},
                {"name": "PROMETHEUS_ADDRESS", "value": "http://openchoreo-observability-prometheus:9091"},
                {"name": "PROMETHEUS_TIMEOUT", "value": "30s"},
                {"name": "AUTHZ_TIMEOUT", "value": "30s"},
            ],
            # When OpenObserve is enabled, route logs/traces through adapters
            **(
                {
                    "logsAdapter": {
                        "enabled": True,
                        "url": "http://logs-adapter:9098",
                    },
                    "tracingAdapter": {
                        "enabled": True,
                        "url": "http://tracing-adapter:9100",
                    },
                }
                if enable_openobserve
                else {}
            ),
        },
        "security": {
            "oidc": {
                "jwksUrl": f"{THUNDER_INTERNAL_BASE}/oauth2/jwks",
                "tokenUrl": f"{THUNDER_INTERNAL_BASE}/oauth2/token",
                "authServerBaseUrl": thunder_url,
            },
        },
        "rca": {
            "enabled": enable_rca,
            "replicas": 0,
            "http": {
                "hostnames": [f"rca-agent.{domain_base}"],
            },
            "openchoreoApiUrl": effective_cp_api_url,
            "cors": {
                "allowedOrigins": [backstage_url],
            },
            **(
                {
                    "llm": {"modelName": rca_llm_model},
                    "remedAgent": True,
                    "extraEnvs": [
                        ev
                        for ev in [
                            {"name": "OPENAI_BASE_URL", "value": rca_llm_base_url} if rca_llm_base_url else None,
                            {"name": "TLS_INSECURE_SKIP_VERIFY", "value": "true"} if rca_llm_base_url else None,
                            {"name": "LANGCHAIN_MAX_INPUT_TOKENS", "value": "200000"},
                            {"name": "RCA_STRUCTURED_OUTPUT_STRATEGY", "value": "tool"},
                        ]
                        if ev is not None
                    ],
                }
                if enable_rca and rca_llm_model
                else {}
            ),
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
