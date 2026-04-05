"""OpenTelemetry Operator component: Helm install + Instrumentation CR."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pulumi
import pulumi_kubernetes as k8s

from config import (
    NS_OBSERVABILITY_PLANE,
    NS_OTEL_OPERATOR,
    OTEL_OPERATOR_CHART_REPO,
    TIMEOUT_DEFAULT,
    OpenChoreoConfig,
)

if TYPE_CHECKING:
    pass

# OTel Collector endpoint in the observability plane (receives traces)
OTEL_COLLECTOR_ENDPOINT = (
    "http://opentelemetry-collector.openchoreo-observability-plane.svc.cluster.local:4317"
)

# Supported auto-instrumentation images (official OTel images)
_AUTOINSTR_IMAGES = {
    "java": "ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-java:latest",
    "python": "ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-python:latest",
    "nodejs": "ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-nodejs:latest",
    "dotnet": "ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-dotnet:latest",
    "go": "ghcr.io/open-telemetry/opentelemetry-go-instrumentation/autoinstrumentation-go:latest",
}

# Annotation keys for each language
LANG_ANNOTATIONS = {
    "go": "instrumentation.opentelemetry.io/inject-go",
    "java": "instrumentation.opentelemetry.io/inject-java",
    "python": "instrumentation.opentelemetry.io/inject-python",
    "nodejs": "instrumentation.opentelemetry.io/inject-nodejs",
    "dotnet": "instrumentation.opentelemetry.io/inject-dotnet",
}


class OtelOperator(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        depends: list[pulumi.Resource],
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:OtelOperator", name, {}, opts)

        # ─── 1. Namespace ───
        ns = k8s.core.v1.Namespace(
            NS_OTEL_OPERATOR,
            metadata=k8s.meta.v1.ObjectMetaArgs(name=NS_OTEL_OPERATOR),
            opts=self._child_opts(provider=k8s_provider, depends_on=depends),
        )

        # ─── 2. OTel Operator Helm release ───
        operator = k8s.helm.v3.Release(
            "opentelemetry-operator",
            k8s.helm.v3.ReleaseArgs(
                chart=f"{OTEL_OPERATOR_CHART_REPO}/opentelemetry-operator",
                version=cfg.otel_operator_version,
                namespace=NS_OTEL_OPERATOR,
                values={
                    "admissionWebhooks": {
                        "certManager": {"enabled": True},
                    },
                    "manager": {
                        "collectorImage": {
                            "repository": "otel/opentelemetry-collector-contrib",
                        },
                        # Enable Go eBPF auto-instrumentation (experimental)
                        "featureGates": "operator.autoinstrumentation.go",
                    },
                },
                timeout=TIMEOUT_DEFAULT,
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[ns]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")),
            ),
        )

        # ─── 3. Instrumentation CR (all languages) ───
        instr_ref = f"{NS_OBSERVABILITY_PLANE}/auto-instrumentation"
        env_block = [{"name": "OTEL_EXPORTER_OTLP_ENDPOINT", "value": OTEL_COLLECTOR_ENDPOINT}]

        k8s.apiextensions.CustomResource(
            "otel-auto-instrumentation",
            api_version="opentelemetry.io/v1alpha1",
            kind="Instrumentation",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="auto-instrumentation",
                namespace=NS_OBSERVABILITY_PLANE,
            ),
            spec={
                "exporter": {"endpoint": OTEL_COLLECTOR_ENDPOINT},
                "propagators": ["tracecontext", "baggage", "b3"],
                "sampler": {
                    "type": "parentbased_traceidratio",
                    "argument": "1",  # 100% in dev; reduce in prod
                },
                "java": {"image": _AUTOINSTR_IMAGES["java"], "env": env_block},
                "python": {"image": _AUTOINSTR_IMAGES["python"], "env": env_block},
                "nodejs": {"image": _AUTOINSTR_IMAGES["nodejs"], "env": env_block},
                "dotnet": {"image": _AUTOINSTR_IMAGES["dotnet"], "env": env_block},
                "go": {
                    "image": _AUTOINSTR_IMAGES["go"],
                    "env": env_block,
                    "resourceRequirements": {
                        "limits": {"cpu": "500m", "memory": "256Mi"},
                        "requests": {"cpu": "50m", "memory": "64Mi"},
                    },
                },
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[operator]),
        )

        # Export the instrumentation reference for namespace annotations
        self.instrumentation_ref = instr_ref
        self.register_outputs({"instrumentation_ref": instr_ref})

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
) -> OtelOperator:
    """Deploy OTel Operator + Instrumentation CR."""
    return OtelOperator(
        "otel-operator",
        cfg=cfg,
        k8s_provider=k8s_provider,
        depends=depends,
    )
