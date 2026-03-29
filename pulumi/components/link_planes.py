"""Link Planes component: patch DP/WP with observability plane reference."""

from __future__ import annotations

import pulumi

from config import OpenChoreoConfig
from helpers.dynamic_providers import LinkPlanes


class LinkPlanesComponent(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        depends: list[pulumi.Resource],
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:LinkPlanes", name, {}, opts)

        link_result = LinkPlanes(
            "link-planes",
            kubeconfig_path=cfg.kubeconfig_path,
            context=cfg.kubeconfig_context,
            opts=self._child_opts(depends_on=depends),
        )

        self.result = link_result
        self.register_outputs({})

    def _child_opts(
        self,
        depends_on: list[pulumi.Resource] | None = None,
    ) -> pulumi.ResourceOptions:
        opts_kwargs = {
            "parent": self,
            "aliases": [pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)],
        }
        if depends_on:
            opts_kwargs["depends_on"] = depends_on
        return pulumi.ResourceOptions(**opts_kwargs)


def deploy(cfg: OpenChoreoConfig, depends: list[pulumi.Resource]) -> LinkPlanes:
    """Patch ClusterDataPlane and ClusterWorkflowPlane with observability ref."""
    return LinkPlanesComponent("link-planes", cfg=cfg, depends=depends).result
