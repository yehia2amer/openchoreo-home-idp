"""Observability Plane component: namespace, CA, ExternalSecrets, Helm charts, register."""

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

import pulumi
import pulumi_command as command
import pulumi_kubernetes as k8s

from config import (
    CLUSTER_SECRET_STORE_NAME,
    NS_OBSERVABILITY_PLANE,
    SECRET_OBSERVER,
    SECRET_OBSERVER_OPENSEARCH,
    SECRET_OPENOBSERVE_ADMIN,
    SECRET_OPENSEARCH_ADMIN,
    SECRET_RCA_AGENT,
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

# ── Fluent Bit dual-ship config (OpenSearch + OpenObserve) ──────────────
# Env vars referenced: OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD,
#                      OPENOBSERVE_USER, OPENOBSERVE_PASSWORD
_FLUENT_BIT_DUAL_SHIP_CONF = textwrap.dedent("""\
    [SERVICE]
        Flush         1
        Daemon        Off
        Log_Level     info
        Parsers_File  parsers.conf
        Plugins_File  plugins.conf
        HTTP_Server   On
        HTTP_Listen   0.0.0.0
        HTTP_Port     2020

    [INPUT]
        Name tail
        Buffer_Chunk_Size 32KB
        Buffer_Max_Size 2MB
        DB /var/lib/fluent-bit/db/tail-container-logs.db
        Exclude_Path /var/log/containers/fluent-bit-*.log
        Inotify_Watcher false
        Mem_Buf_Limit 100MB
        Path /var/log/containers/*.log
        multiline.parser docker, cri
        Read_from_Head On
        Refresh_Interval 5
        Skip_Long_Lines On
        Tag kube.*

    [FILTER]
        Name kubernetes
        Buffer_Size 15MB
        K8S-Logging.Parser On
        K8S-Logging.Exclude On
        Keep_Log On
        Match kube.*
        Merge_Log Off
        tls.verify Off
        Use_Kubelet true

    [OUTPUT]
        Name opensearch
        Host opensearch
        Port 9200
        Generate_ID On
        HTTP_Passwd ${OPENSEARCH_PASSWORD}
        HTTP_User ${OPENSEARCH_USERNAME}
        Logstash_Format On
        Logstash_DateFormat %Y-%m-%d
        Logstash_Prefix container-logs
        Match kube.*
        Replace_Dots On
        Suppress_Type_Name On
        tls On
        tls.verify Off
        tls.vhost opensearch

    [OUTPUT]
        Name http
        Match kube.*
        Host openobserve
        Port 5080
        URI /api/default/default/_json
        Format json
        HTTP_User ${OPENOBSERVE_USER}
        HTTP_Passwd ${OPENOBSERVE_PASSWORD}
        Json_Date_Key _timestamp
        Json_Date_Format iso8601
        compress gzip
""")

_FLUENT_BIT_PARSERS_CONF = textwrap.dedent("""\
    [PARSER]
        Name docker_no_time
        Format json
        Time_Keep Off
        Time_Key time
        Time_Format %Y-%m-%dT%H:%M:%S.%L
""")


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
                    {
                        "secretKey": "OPENSEARCH_USERNAME",
                        "remoteRef": {"key": "opensearch-username", "property": "value"},
                    },
                    {
                        "secretKey": "OPENSEARCH_PASSWORD",
                        "remoteRef": {"key": "opensearch-password", "property": "value"},
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

        # ─── 4b. RCA Agent Secret (LLM API key + OAuth secret) ───
        rca_secret_deps: list[pulumi.Resource] = [ns]
        if cfg.enable_rca:
            rca_secret = k8s.apiextensions.CustomResource(
                "rca-agent-external-secret",
                api_version="external-secrets.io/v1",
                kind="ExternalSecret",
                metadata=k8s.meta.v1.ObjectMetaArgs(
                    name=SECRET_RCA_AGENT,
                    namespace=NS_OBSERVABILITY_PLANE,
                ),
                spec={
                    "refreshInterval": "1h",
                    "secretStoreRef": {"kind": "ClusterSecretStore", "name": CLUSTER_SECRET_STORE_NAME},
                    "target": {"name": SECRET_RCA_AGENT},
                    "data": [
                        {
                            "secretKey": "RCA_LLM_API_KEY",
                            "remoteRef": {"key": "rca-llm-api-key", "property": "value"},
                        },
                        {
                            "secretKey": "OAUTH_CLIENT_SECRET",
                            "remoteRef": {"key": "rca-oauth-client-secret", "property": "value"},
                        },
                    ],
                },
                opts=self._child_opts(provider=k8s_provider, depends_on=[ns]),
            )
            rca_secret_deps.append(rca_secret)

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
                    backstage_url=cfg.backstage_url,
                    tls_enabled=cfg.tls_enabled,
                    op_http_port=cfg.op_http_port,
                    op_https_port=cfg.op_https_port,
                    observer_url=cfg.observer_url,
                    enable_openobserve=cfg.enable_openobserve,
                    enable_rca=cfg.enable_rca,
                    rca_llm_model=cfg.rca_llm_model,
                    rca_llm_base_url=cfg.rca_llm_base_url,
                ),
                timeout=TIMEOUT_OBS_PLANE,
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(
                    provider=k8s_provider,
                    depends_on=[
                        ca,
                        opensearch_admin,
                        observer_opensearch,
                        observer_secret,
                        *rca_secret_deps,
                    ],
                ),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_OBS_PLANE}s")),
            ),
        )

        # ─── 6. Observability modules ───
        openobserve_creds: k8s.apiextensions.CustomResource | None = None
        if cfg.enable_openobserve:
            # ── 6a. OpenObserve credentials ──
            openobserve_creds = k8s.apiextensions.CustomResource(
                "openobserve-admin-creds",
                api_version="external-secrets.io/v1",
                kind="ExternalSecret",
                metadata=k8s.meta.v1.ObjectMetaArgs(
                    name=SECRET_OPENOBSERVE_ADMIN,
                    namespace=NS_OBSERVABILITY_PLANE,
                    annotations={"pulumi.com/patchForce": "true"},
                ),
                spec={
                    "refreshInterval": "1h",
                    "secretStoreRef": {"kind": "ClusterSecretStore", "name": CLUSTER_SECRET_STORE_NAME},
                    "target": {"name": SECRET_OPENOBSERVE_ADMIN},
                    "data": [
                        {
                            "secretKey": "ZO_ROOT_USER_EMAIL",
                            "remoteRef": {"key": "openobserve-admin-credentials", "property": "ZO_ROOT_USER_EMAIL"},
                        },
                        {
                            "secretKey": "ZO_ROOT_USER_PASSWORD",
                            "remoteRef": {
                                "key": "openobserve-admin-credentials",
                                "property": "ZO_ROOT_USER_PASSWORD",
                            },
                        },
                    ],
                },
                opts=self._child_opts(provider=k8s_provider, depends_on=[ns]),
            )

            # ── 6b. Logging module (OpenObserve + logs-adapter) ──
            # Fluent Bit disabled: the OpenSearch logging module already runs one.
            # We'll disable OpenSearch's fluent-bit in Phase 4 when removing OpenSearch.
            logs_oo = k8s.helm.v3.Release(
                "observability-logs-openobserve",
                k8s.helm.v3.ReleaseArgs(
                    chart=cfg.logs_openobserve_chart,
                    version=cfg.logs_openobserve_version,
                    name="observability-logs-openobserve",
                    namespace=NS_OBSERVABILITY_PLANE,
                    values={
                        "fluent-bit": {"enabled": False},
                        "openobserve-standalone": {
                            "persistence": {"size": "10Gi"},
                            "resources": {
                                "requests": {"memory": "500Mi"},
                                "limits": {"cpu": "500m", "memory": "1000Mi"},
                            },
                        },
                    },
                    timeout=TIMEOUT_DEFAULT,
                ),
                opts=pulumi.ResourceOptions.merge(
                    self._child_opts(provider=k8s_provider, depends_on=[obs_chart, openobserve_creds]),
                    pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")),
                ),
            )

            # ── 6c. Tracing module (tracing-adapter, reuses OpenObserve from logging) ──
            k8s.helm.v3.Release(
                "observability-tracing-openobserve",
                k8s.helm.v3.ReleaseArgs(
                    chart=cfg.tracing_openobserve_chart,
                    version=cfg.tracing_openobserve_version,
                    name="observability-tracing-openobserve",
                    namespace=NS_OBSERVABILITY_PLANE,
                    values={
                        "openobserve-standalone": {"enabled": False},
                        "opentelemetry-collector": {"enabled": False},
                    },
                    timeout=TIMEOUT_DEFAULT,
                ),
                opts=pulumi.ResourceOptions.merge(
                    self._child_opts(provider=k8s_provider, depends_on=[logs_oo]),
                    pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")),
                ),
            )

            # ── 6d. OpenObserve UI HTTPRoute ──
            # The Helm chart only creates a route for /api/default/container-logs/_json.
            # This adds a full UI route at openobserve.<domain>.
            oo_hostname = f"openobserve.{cfg.domain_base}"
            k8s.apiextensions.CustomResource(
                "openobserve-ui-httproute",
                api_version="gateway.networking.k8s.io/v1",
                kind="HTTPRoute",
                metadata=k8s.meta.v1.ObjectMetaArgs(
                    name="openobserve-ui",
                    namespace=NS_OBSERVABILITY_PLANE,
                    annotations={"pulumi.com/patchForce": "true"},
                ),
                spec={
                    "hostnames": [oo_hostname],
                    "parentRefs": [
                        {
                            "group": "gateway.networking.k8s.io",
                            "kind": "Gateway",
                            "name": "gateway-default",
                            "namespace": NS_OBSERVABILITY_PLANE,
                            "sectionName": "http",
                        },
                        {
                            "group": "gateway.networking.k8s.io",
                            "kind": "Gateway",
                            "name": "gateway-default",
                            "namespace": NS_OBSERVABILITY_PLANE,
                            "sectionName": "https",
                        },
                    ],
                    "rules": [
                        {
                            "backendRefs": [{"name": "openobserve", "port": 5080}],
                            "matches": [{"path": {"type": "PathPrefix", "value": "/"}}],
                        }
                    ],
                },
                opts=self._child_opts(provider=k8s_provider, depends_on=[logs_oo]),
            )

        # ── 6e. OpenSearch modules (always installed; Phase 4 will disable) ──
        # Fluent Bit env: always include OpenSearch creds.  When OpenObserve is
        # enabled we also inject its credentials so the dual-ship OUTPUT section
        # can reference them via ${OPENOBSERVE_USER} / ${OPENOBSERVE_PASSWORD}.
        fluent_bit_env = [
            {
                "name": "OPENSEARCH_USERNAME",
                "valueFrom": {"secretKeyRef": {"name": SECRET_OPENSEARCH_ADMIN, "key": "username"}},
            },
            {
                "name": "OPENSEARCH_PASSWORD",
                "valueFrom": {"secretKeyRef": {"name": SECRET_OPENSEARCH_ADMIN, "key": "password"}},
            },
        ]
        if cfg.enable_openobserve:
            fluent_bit_env += [
                {
                    "name": "OPENOBSERVE_USER",
                    "valueFrom": {"secretKeyRef": {"name": SECRET_OPENOBSERVE_ADMIN, "key": "ZO_ROOT_USER_EMAIL"}},
                },
                {
                    "name": "OPENOBSERVE_PASSWORD",
                    "valueFrom": {"secretKeyRef": {"name": SECRET_OPENOBSERVE_ADMIN, "key": "ZO_ROOT_USER_PASSWORD"}},
                },
            ]

        logs_opensearch = k8s.helm.v3.Release(
            "observability-logs-opensearch",
            k8s.helm.v3.ReleaseArgs(
                chart=cfg.logs_chart,
                version=cfg.logs_opensearch_version,
                namespace=NS_OBSERVABILITY_PLANE,
                values={
                    "openSearchSetup": {"openSearchSecretName": SECRET_OPENSEARCH_ADMIN},
                    "fluent-bit": {
                        "enabled": True,
                        "env": fluent_bit_env,
                    },
                },
                timeout=TIMEOUT_OPENSEARCH,
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[obs_chart]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_OPENSEARCH}s")),
            ),
        )

        # ── 6f. Fluent Bit dual-ship ConfigMap (OpenSearch + OpenObserve) ──
        # The observability-logs-opensearch chart renders a fluent-bit ConfigMap
        # with only an OpenSearch OUTPUT.  When OpenObserve is enabled we overwrite
        # that ConfigMap with a version containing both outputs.  Credentials are
        # injected via env vars (see fluent_bit_env above).
        # Phase 4: remove the OpenSearch OUTPUT block and this overwrite; switch
        # to the OpenObserve logging module's own Fluent Bit instance instead.
        if cfg.enable_openobserve:
            assert openobserve_creds is not None
            k8s.core.v1.ConfigMap(
                "fluent-bit-dual-ship-config",
                metadata=k8s.meta.v1.ObjectMetaArgs(
                    name="fluent-bit",
                    namespace=NS_OBSERVABILITY_PLANE,
                    # Preserve Helm ownership so the chart can still manage the
                    # resource on upgrade; Pulumi will reconcile on next `up`.
                    annotations={
                        "meta.helm.sh/release-name": "observability-logs-opensearch-ea4e6fa1",
                        "meta.helm.sh/release-namespace": NS_OBSERVABILITY_PLANE,
                        "pulumi.com/patchForce": "true",
                    },
                    labels={"app.kubernetes.io/managed-by": "Helm"},
                ),
                data={
                    "fluent-bit.conf": _FLUENT_BIT_DUAL_SHIP_CONF,
                    "parsers.conf": _FLUENT_BIT_PARSERS_CONF,
                },
                opts=self._child_opts(
                    provider=k8s_provider,
                    depends_on=[logs_opensearch, openobserve_creds],
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
