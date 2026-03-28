"""Link Planes component: patch DP/WP with observability plane reference."""

from __future__ import annotations

import pulumi

from config import OpenChoreoConfig
from helpers.dynamic_providers import LinkPlanes


def deploy(cfg: OpenChoreoConfig, depends: list[pulumi.Resource]) -> LinkPlanes:
    """Patch ClusterDataPlane and ClusterWorkflowPlane with observability ref."""
    return LinkPlanes(
        "link-planes",
        kubeconfig_path=cfg.kubeconfig_path,
        context=cfg.kubeconfig_context,
        opts=pulumi.ResourceOptions(depends_on=depends),
    )
