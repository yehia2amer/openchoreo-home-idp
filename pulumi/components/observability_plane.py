"""Observability Plane component: namespace, CA, ExternalSecrets, Helm charts, register."""

from __future__ import annotations

import pulumi
import pulumi_command as command
import pulumi_kubernetes as k8s

from config import (
    CLUSTER_SECRET_STORE_NAME,
    NS_OBSERVABILITY_PLANE,
    SECRET_OBSERVER,
    SECRET_OBSERVER_OPENSEARCH,
    SECRET_OPENSEARCH_ADMIN,
    TIMEOUT_DEFAULT,
    TIMEOUT_OBS_PLANE,
    TIMEOUT_OPENSEARCH,
    OpenChoreoConfig,
)
from helpers.copy_ca import copy_ca
from helpers.dynamic_providers import RegisterPlane
from helpers.register_plane import register_plane
from values.observability_plane import get_values as op_values


class ObservabilityPlaneResult:
    """Outputs from the observability plane component."""

    def __init__(self, register_cmd: RegisterPlane):
        self.register_cmd = register_cmd


def deploy(
    cfg: OpenChoreoConfig,
    k8s_provider: k8s.Provider,
    depends: list[pulumi.Resource],
) -> ObservabilityPlaneResult:
    """Deploy observability plane: namespace, secrets, helm charts, register."""

    # ─── 1. Namespace ───
    ns = k8s.core.v1.Namespace(
        NS_OBSERVABILITY_PLANE,
        metadata=k8s.meta.v1.ObjectMetaArgs(name=NS_OBSERVABILITY_PLANE),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=depends,
        ),
    )

    # ─── 2. Copy CA ───
    ca = copy_ca(
        "obs-plane",
        NS_OBSERVABILITY_PLANE,
        cfg,
        opts=pulumi.ResourceOptions(depends_on=[ns]),
    )

    # ─── 3. ExternalSecrets ───
    opensearch_admin = k8s.apiextensions.CustomResource(
        "opensearch-admin-creds",
        api_version="external-secrets.io/v1",
        kind="ExternalSecret",
        metadata=k8s.meta.v1.ObjectMetaArgs(name=SECRET_OPENSEARCH_ADMIN, namespace=NS_OBSERVABILITY_PLANE),
        spec={
            "refreshInterval": "1h",
            "secretStoreRef": {"kind": "ClusterSecretStore", "name": CLUSTER_SECRET_STORE_NAME},
            "target": {"name": SECRET_OPENSEARCH_ADMIN},
            "data": [
                {"secretKey": "username", "remoteRef": {"key": "opensearch-username", "property": "value"}},
                {"secretKey": "password", "remoteRef": {"key": "opensearch-password", "property": "value"}},
            ],
        },
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[ns]),
    )

    observer_opensearch = k8s.apiextensions.CustomResource(
        "observer-opensearch-creds",
        api_version="external-secrets.io/v1",
        kind="ExternalSecret",
        metadata=k8s.meta.v1.ObjectMetaArgs(name=SECRET_OBSERVER_OPENSEARCH, namespace=NS_OBSERVABILITY_PLANE),
        spec={
            "refreshInterval": "1h",
            "secretStoreRef": {"kind": "ClusterSecretStore", "name": CLUSTER_SECRET_STORE_NAME},
            "target": {"name": SECRET_OBSERVER_OPENSEARCH},
            "data": [
                {"secretKey": "username", "remoteRef": {"key": "opensearch-username", "property": "value"}},
                {"secretKey": "password", "remoteRef": {"key": "opensearch-password", "property": "value"}},
            ],
        },
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[ns]),
    )

    observer_secret = k8s.apiextensions.CustomResource(
        "observer-secret",
        api_version="external-secrets.io/v1",
        kind="ExternalSecret",
        metadata=k8s.meta.v1.ObjectMetaArgs(name=SECRET_OBSERVER, namespace=NS_OBSERVABILITY_PLANE),
        spec={
            "refreshInterval": "1h",
            "secretStoreRef": {"kind": "ClusterSecretStore", "name": CLUSTER_SECRET_STORE_NAME},
            "target": {"name": SECRET_OBSERVER},
            "data": [
                {
                    "secretKey": "OBSERVER_OAUTH_CLIENT_SECRET",
                    "remoteRef": {"key": "observer-oauth-client-secret", "property": "value"},
                },
            ],
        },
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[ns]),
    )

    # ─── 4. Machine-id (k3d only) ───
    if cfg.is_k3d:
        command.local.Command(
            "machine-id",
            create=(
                f"docker exec k3d-{cfg.k3d_cluster_name}-server-0 sh -c"
                " \"cat /proc/sys/kernel/random/uuid | tr -d '-' > /etc/machine-id\""
            ),
            opts=pulumi.ResourceOptions(depends_on=[ns]),
        )

    # ─── 5. Observability Plane core Helm chart ───
    # Use helm.v3.Release (not v4.Chart) because the chart contains
    # cert-manager Certificate resources; v4.Chart does client-side rendering
    # that fails if cert-manager CRDs are not yet installed.
    obs_chart = k8s.helm.v3.Release(
        NS_OBSERVABILITY_PLANE,
        k8s.helm.v3.ReleaseArgs(
            chart=cfg.obs_chart,
            version=cfg.openchoreo_version,
            namespace=NS_OBSERVABILITY_PLANE,
            values=op_values(
                domain_base=cfg.domain_base,
                thunder_url=cfg.thunder_url,
                tls_enabled=cfg.tls_enabled,
                op_http_port=cfg.op_http_port,
                op_https_port=cfg.op_https_port,
            ),
            timeout=TIMEOUT_OBS_PLANE,
        ),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[ca, opensearch_admin, observer_opensearch, observer_secret],
            custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_OBS_PLANE}s"),
        ),
    )

    # ─── 6. Observability modules ───
    k8s.helm.v3.Release(
        "observability-logs-opensearch",
        k8s.helm.v3.ReleaseArgs(
            chart=cfg.logs_chart,
            version=cfg.logs_opensearch_version,
            namespace=NS_OBSERVABILITY_PLANE,
            values={
                "openSearchSetup": {"openSearchSecretName": SECRET_OPENSEARCH_ADMIN},
                "fluent-bit": {"enabled": True},
            },
            timeout=TIMEOUT_OPENSEARCH,
        ),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[obs_chart],
            custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_OPENSEARCH}s"),
        ),
    )

    k8s.helm.v3.Release(
        "observability-traces-opensearch",
        k8s.helm.v3.ReleaseArgs(
            chart=cfg.traces_chart,
            version=cfg.traces_opensearch_version,
            namespace=NS_OBSERVABILITY_PLANE,
            values={
                "openSearch": {"enabled": False},
                "openSearchSetup": {"openSearchSecretName": SECRET_OPENSEARCH_ADMIN},
            },
            timeout=TIMEOUT_OPENSEARCH,
        ),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[obs_chart],
            custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_OPENSEARCH}s"),
        ),
    )

    # Use helm.v3.Release because this chart relies on Helm hooks (Jobs to
    # create TLS secrets) that k8s.helm.v4.Chart does not execute.
    k8s.helm.v3.Release(
        "observability-metrics-prometheus",
        k8s.helm.v3.ReleaseArgs(
            chart=cfg.metrics_chart,
            version=cfg.metrics_prometheus_version,
            namespace=NS_OBSERVABILITY_PLANE,
            values={
                "kube-prometheus-stack": {
                    "prometheusOperator": {
                        "admissionWebhooks": {"enabled": False},
                        "tls": {"enabled": False},
                    },
                },
            },
            timeout=TIMEOUT_DEFAULT,
        ),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[obs_chart],
            custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s"),
        ),
    )

    # ─── 7. Register ClusterObservabilityPlane ───
    register = register_plane(
        name="obs-plane",
        namespace=NS_OBSERVABILITY_PLANE,
        kind="ClusterObservabilityPlane",
        cfg=cfg,
        extra_spec={"observerURL": cfg.observer_url},
        opts=pulumi.ResourceOptions(depends_on=[obs_chart]),
    )

    return ObservabilityPlaneResult(register_cmd=register)
