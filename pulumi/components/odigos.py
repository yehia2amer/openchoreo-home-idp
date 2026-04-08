"""Odigos component: automatic language-agnostic distributed tracing via eBPF.

Replaces OTel Operator + Kyverno + manual namespace annotations with a single
tool that auto-detects language runtimes and injects the correct instrumentation.

Supports: Go (eBPF), Java, Python, Node.js, .NET, nginx, and more.

Note: Go eBPF requires DWARF debug symbols in the binary. Stripped Go binaries
(built with -ldflags '-s -w') will fail instrumentation. Rebuild without strip
flags to enable Go tracing.
"""

from __future__ import annotations

import pulumi
import pulumi_kubernetes as k8s

from config import (
    TIMEOUT_DEFAULT,
    OpenChoreoConfig,
)

NS_ODIGOS = "odigos-system"
ODIGOS_CHART_REPO = "https://odigos-io.github.io/odigos/"


class OdigosResult:
    """Outputs from the Odigos component."""

    def __init__(self, namespace: str):
        self.namespace = namespace


class Odigos(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        depends: list[pulumi.Resource],
        otel_collector_endpoint: str = "",
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:Odigos", name, {}, opts)

        effective_endpoint = otel_collector_endpoint or (
            "openobserve.openchoreo-observability-plane.svc.cluster.local:5081"
        )

        # ─── 1. Namespace with privileged PodSecurity ───
        # Odigos odiglet requires hostPID, privileged, hostPath for eBPF
        ns = k8s.core.v1.Namespace(
            NS_ODIGOS,
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=NS_ODIGOS,
                labels={
                    "pod-security.kubernetes.io/enforce": "privileged",
                    "pod-security.kubernetes.io/warn": "privileged",
                },
            ),
            opts=self._child_opts(provider=k8s_provider, depends_on=depends),
        )

        # ─── 2. Odigos Helm release ───
        # Uses the odigos CLI's embedded chart equivalent
        odigos = k8s.helm.v3.Release(
            "odigos",
            k8s.helm.v3.ReleaseArgs(
                chart="odigos",
                repository_opts=k8s.helm.v3.RepositoryOptsArgs(repo=ODIGOS_CHART_REPO),
                version=cfg.odigos_version,
                namespace=NS_ODIGOS,
                values={
                    "collectorGateway": {
                        "minReplicas": 1,
                        "maxReplicas": 2,
                    },
                },
                timeout=TIMEOUT_DEFAULT,
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[ns]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")),
            ),
        )

        # ─── 3. K8sAttributes Action: extract OpenChoreo pod labels into traces ───
        # The tracing-adapter-openobserve queries by openchoreo.dev/* resource
        # attributes (e.g. service_openchoreo_dev_namespace). Odigos only adds
        # standard k8s attributes by default. This Action tells the odiglet's
        # k8sattributes processor to extract pod labels set by OpenChoreo into
        # resource attributes on every trace span.
        # Ref: https://docs.odigos.io/oss/pipeline/actions/attributes/k8sattributes
        _OPENCHOREO_LABELS = [
            "openchoreo.dev/namespace",
            "openchoreo.dev/project",
            "openchoreo.dev/environment",
            "openchoreo.dev/component",
            "openchoreo.dev/component-uid",
            "openchoreo.dev/environment-uid",
            "openchoreo.dev/project-uid",
        ]
        k8s.apiextensions.CustomResource(
            "odigos-action-openchoreo-labels",
            api_version="odigos.io/v1alpha1",
            kind="Action",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="openchoreo-labels",
                namespace=NS_ODIGOS,
            ),
            spec={
                "actionName": "Extract OpenChoreo pod labels",
                "signals": ["TRACES"],
                "k8sAttributes": {
                    "labelsAttributes": [
                        {
                            "labelKey": label,
                            "attributeKey": label,
                            "from": "pod",
                        }
                        for label in _OPENCHOREO_LABELS
                    ],
                },
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[odigos]),
        )

        # ─── 4. Destination: send traces to existing OTel Collector → OpenObserve ───
        k8s.apiextensions.CustomResource(
            "odigos-destination-openobserve",
            api_version="odigos.io/v1alpha1",
            kind="Destination",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="openobserve-via-collector",
                namespace=NS_ODIGOS,
            ),
            spec={
                "type": "otlp",
                "destinationName": "OpenObserve (direct OTLP)",
                "signals": ["TRACES"],
                "data": {
                    "OTLP_GRPC_ENDPOINT": effective_endpoint,
                    "OTLP_GRPC_TLS": "false",
                },
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[odigos]),
        )

        self.result = OdigosResult(namespace=NS_ODIGOS)
        self.register_outputs({"namespace": NS_ODIGOS})

    def _child_opts(
        self,
        depends_on: list[pulumi.Resource] | None = None,
        provider: k8s.Provider | None = None,
    ) -> pulumi.ResourceOptions:
        opts_kwargs: dict = {
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
) -> OdigosResult:
    """Deploy Odigos for automatic distributed tracing."""
    return Odigos(
        "odigos",
        cfg=cfg,
        k8s_provider=k8s_provider,
        depends=depends,
    ).result
