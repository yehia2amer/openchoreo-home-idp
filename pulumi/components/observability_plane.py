"""Observability Plane component: namespace, CA, ExternalSecrets, Helm charts, register."""

from __future__ import annotations

from typing import TYPE_CHECKING

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
from helpers.register_plane import register_plane
from values.observability_plane import get_values as op_values

if TYPE_CHECKING:
    from helpers.dynamic_providers import RegisterPlane


class ObservabilityPlaneResult:
    """Outputs from the observability plane component."""

    def __init__(self, register_cmd: RegisterPlane):
        self.register_cmd = register_cmd


class ObservabilityPlane(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        depends: list[pulumi.Resource],
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:ObservabilityPlane", name, {}, opts)

        # ─── 1. Namespace ───
        ns = k8s.core.v1.Namespace(
            NS_OBSERVABILITY_PLANE,
            metadata=k8s.meta.v1.ObjectMetaArgs(name=NS_OBSERVABILITY_PLANE),
            opts=self._child_opts(provider=k8s_provider, depends_on=depends),
        )

        # ─── 2. Copy CA ───
        ca = copy_ca(
            "obs-plane",
            NS_OBSERVABILITY_PLANE,
            cfg,
            opts=self._child_opts(depends_on=[ns]),
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
            opts=self._child_opts(provider=k8s_provider, depends_on=[ns]),
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
            opts=self._child_opts(provider=k8s_provider, depends_on=[ns]),
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
            opts=self._child_opts(provider=k8s_provider, depends_on=[ns]),
        )

        # ─── 4. Machine-id (platform-specific) ───
        if cfg.platform.requires_machine_id_fix:
            command.local.Command(
                "machine-id",
                create=(
                    f"docker exec k3d-{cfg.k3d_cluster_name}-server-0 sh -c"
                    " \"cat /proc/sys/kernel/random/uuid | tr -d '-' > /etc/machine-id\""
                ),
                opts=self._child_opts(depends_on=[ns]),
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
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(
                    provider=k8s_provider, depends_on=[ca, opensearch_admin, observer_opensearch, observer_secret]
                ),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_OBS_PLANE}s")),
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
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[obs_chart]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_OPENSEARCH}s")),
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
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[obs_chart]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_OPENSEARCH}s")),
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
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[obs_chart]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")),
            ),
        )

        # ─── 7. Register ClusterObservabilityPlane ───
        register = register_plane(
            name="obs-plane",
            namespace=NS_OBSERVABILITY_PLANE,
            kind="ClusterObservabilityPlane",
            cfg=cfg,
            extra_spec={"observerURL": cfg.observer_url},
            opts=self._child_opts(depends_on=[obs_chart]),
        )

        self.result = ObservabilityPlaneResult(register_cmd=register)
        self.register_outputs({})

    def _child_opts(
        self,
        depends_on: list[pulumi.Resource] | None = None,
        provider: k8s.Provider | None = None,
    ) -> pulumi.ResourceOptions:
        opts_kwargs = {
            "parent": self,
            "aliases": [pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)],
        }
        if depends_on:
            opts_kwargs["depends_on"] = depends_on
        if provider:
            opts_kwargs["provider"] = provider
        return pulumi.ResourceOptions(**opts_kwargs)


def deploy(
    cfg: OpenChoreoConfig,
    k8s_provider: k8s.Provider,
    depends: list[pulumi.Resource],
) -> ObservabilityPlaneResult:
    """Deploy observability plane: namespace, secrets, helm charts, register."""
    return ObservabilityPlane(
        "observability-plane",
        cfg=cfg,
        k8s_provider=k8s_provider,
        depends=depends,
    ).result
