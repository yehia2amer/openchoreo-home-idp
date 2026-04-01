"""Workflow Plane component: docker-registry, copy CA, WP Helm chart, templates, register."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pulumi
import pulumi_command as command
import pulumi_kubernetes as k8s

from config import (
    DOCKER_REGISTRY_HELM_REPO,
    NS_CONTROL_PLANE,
    NS_WORKFLOW_PLANE,
    TIMEOUT_DEFAULT,
    OpenChoreoConfig,
)
from helpers.copy_ca import copy_ca
from helpers.register_plane import register_plane
from values.registry import get_values as registry_values
from values.workflow_plane import get_values as wp_values

if TYPE_CHECKING:
    from helpers.dynamic_providers import RegisterPlane


class WorkflowPlaneResult:
    """Outputs from the workflow plane component."""

    def __init__(self, register_cmd: RegisterPlane):
        self.register_cmd = register_cmd


class WorkflowPlane(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        depends: list[pulumi.Resource],
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:WorkflowPlane", name, {}, opts)

        # ─── 1. Namespace ───
        ns = k8s.core.v1.Namespace(
            NS_WORKFLOW_PLANE,
            metadata=k8s.meta.v1.ObjectMetaArgs(name=NS_WORKFLOW_PLANE),
            opts=self._child_opts(provider=k8s_provider, depends_on=depends),
        )

        # ─── 2. Docker Registry (HTTP repo, NOT OCI) ───
        registry = k8s.helm.v4.Chart(
            "docker-registry",
            k8s.helm.v4.ChartArgs(
                chart="docker-registry",
                version=cfg.docker_registry_version,
                namespace=NS_WORKFLOW_PLANE,
                repository_opts=k8s.helm.v4.RepositoryOptsArgs(
                    repo=DOCKER_REGISTRY_HELM_REPO,
                ),
                values=registry_values(wp_registry_port=cfg.wp_registry_port),
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[ns]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")),
            ),
        )

        # ─── 3. Copy CA ───
        ca = copy_ca(
            "workflow-plane",
            NS_WORKFLOW_PLANE,
            cfg,
            opts=self._child_opts(depends_on=[registry]),
        )

        # ─── 4. Workflow Plane Helm Chart ───
        # Use helm.v3.Release (not v4.Chart) because the chart contains
        # cert-manager Certificate resources; v4.Chart does client-side rendering
        # that fails if cert-manager CRDs are not yet installed.
        wp_chart = k8s.helm.v3.Release(
            NS_WORKFLOW_PLANE,
            k8s.helm.v3.ReleaseArgs(
                chart=cfg.wp_chart,
                version=cfg.openchoreo_version,
                namespace=NS_WORKFLOW_PLANE,
                values=wp_values(wp_argo_port=cfg.wp_argo_port),
                timeout=TIMEOUT_DEFAULT,
            ),
            opts=pulumi.ResourceOptions.merge(
                self._child_opts(provider=k8s_provider, depends_on=[registry, ca]),
                pulumi.ResourceOptions(custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s")),
            ),
        )

        # ─── 5. Workflow Templates ───
        # Applied via kubectl because they reference ClusterWorkflowTemplate CRDs
        # installed by the wp_chart; yaml.v2.ConfigGroup fails at preview time
        # before the CRDs exist.
        registry_endpoint = f"registry.{NS_WORKFLOW_PLANE}.svc.cluster.local:{cfg.wp_registry_port}"
        if cfg.platform.gateway_mode == "cilium":
            gateway_endpoint = f"cilium-gateway-gateway-default.{NS_CONTROL_PLANE}.svc.cluster.local:{cfg.cp_http_port}"
        else:
            gateway_endpoint = f"gateway-default.{NS_CONTROL_PLANE}.svc.cluster.local:{cfg.cp_http_port}"
        # Patching: download → sed replace k3d-specific endpoints → apply.
        # Templates with k3d hostnames are patched inline before apply so the
        # resource never contains host.k3d.internal references.
        k3d_templates = {
            "publish-image-k3d.yaml",  # k3d: registry endpoint
            "generate-workload-k3d.yaml",  # k3d: gateway + thunder
        }
        standard_sed_templates = {
            "generate-workload.yaml",  # standard: gateway + thunder
        }
        thunder_url = f"https://thunder.{cfg.domain_base}/oauth2/token"
        api_url = f"https://api.{cfg.domain_base}"
        apply_cmds = []
        for url in cfg.workflow_templates_urls:
            if any(url.endswith(t) for t in k3d_templates):
                # k3d templates: replace registry + gateway endpoints
                apply_cmds.append(
                    f"curl -sL {url}"
                    f" | sed 's|host.k3d.internal:10082|{registry_endpoint}|g'"
                    f" | sed 's|host.k3d.internal:8080|{gateway_endpoint}|g'"
                    f" | kubectl apply --kubeconfig {cfg.kubeconfig_path} --context {cfg.kubeconfig_context} -f -"
                )
            elif any(url.endswith(t) for t in standard_sed_templates):
                # Standard templates: replace k3d placeholders with real URLs
                apply_cmds.append(
                    f"curl -sL {url}"
                    f" | sed 's|https://host.k3d.internal:8080/oauth2/token|{thunder_url}|g'"
                    f" | sed 's|http://host.k3d.internal:8080|{api_url}|g'"
                    f" | kubectl apply --kubeconfig {cfg.kubeconfig_path} --context {cfg.kubeconfig_context} -f -"
                )
            else:
                apply_cmds.append(
                    f"kubectl apply --kubeconfig {cfg.kubeconfig_path} --context {cfg.kubeconfig_context} -f {url}"
                )
        templates = command.local.Command(
            "workflow-templates",
            create=" && ".join(apply_cmds),
            opts=self._child_opts(depends_on=[wp_chart]),
        )

        # ─── 6. Register ClusterWorkflowPlane ───
        register = register_plane(
            name="workflow-plane",
            namespace=NS_WORKFLOW_PLANE,
            kind="ClusterWorkflowPlane",
            cfg=cfg,
            secret_store_ref={"name": "default"},
            opts=self._child_opts(depends_on=[wp_chart, templates]),
        )

        self.result = WorkflowPlaneResult(register_cmd=register)
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
) -> WorkflowPlaneResult:
    """Deploy docker registry, workflow plane chart, templates, and register."""
    return WorkflowPlane(
        "workflow-plane",
        cfg=cfg,
        k8s_provider=k8s_provider,
        depends=depends,
    ).result
