"""Workflow Plane component: docker-registry, copy CA, WP Helm chart, templates, register."""

from __future__ import annotations

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
from helpers.dynamic_providers import RegisterPlane
from helpers.register_plane import register_plane
from values.registry import get_values as registry_values
from values.workflow_plane import get_values as wp_values


class WorkflowPlaneResult:
    """Outputs from the workflow plane component."""

    def __init__(self, register_cmd: RegisterPlane):
        self.register_cmd = register_cmd


def deploy(
    cfg: OpenChoreoConfig,
    k8s_provider: k8s.Provider,
    depends: list[pulumi.Resource],
) -> WorkflowPlaneResult:
    """Deploy docker registry, workflow plane chart, templates, and register."""

    # ─── 1. Namespace ───
    ns = k8s.core.v1.Namespace(
        NS_WORKFLOW_PLANE,
        metadata=k8s.meta.v1.ObjectMetaArgs(name=NS_WORKFLOW_PLANE),
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=depends),
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
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[ns],
        ),
    )

    # ─── 3. Copy CA ───
    ca = copy_ca(
        "workflow-plane",
        NS_WORKFLOW_PLANE,
        cfg,
        opts=pulumi.ResourceOptions(depends_on=[registry]),
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
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[registry, ca],
            custom_timeouts=pulumi.CustomTimeouts(create=f"{TIMEOUT_DEFAULT}s"),
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
        "publish-image-k3d.yaml",
        "generate-workload-k3d.yaml",
    }
    apply_cmds = []
    for url in cfg.workflow_templates_urls:
        if any(url.endswith(t) for t in k3d_templates):
            apply_cmds.append(
                f"curl -sL {url}"
                f" | sed 's|host.k3d.internal:10082|{registry_endpoint}|g'"
                f" | sed 's|host.k3d.internal:8080|{gateway_endpoint}|g'"
                f" | kubectl apply --context {cfg.kubeconfig_context} -f -"
            )
        else:
            apply_cmds.append(f"kubectl apply --context {cfg.kubeconfig_context} -f {url}")
    templates = command.local.Command(
        "workflow-templates",
        create=" && ".join(apply_cmds),
        opts=pulumi.ResourceOptions(depends_on=[wp_chart]),
    )

    # ─── 6. Register ClusterWorkflowPlane ───
    register = register_plane(
        name="workflow-plane",
        namespace=NS_WORKFLOW_PLANE,
        kind="ClusterWorkflowPlane",
        cfg=cfg,
        secret_store_ref={"name": "default"},
        opts=pulumi.ResourceOptions(depends_on=[wp_chart, templates]),
    )

    return WorkflowPlaneResult(register_cmd=register)
