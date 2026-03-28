"""Flux GitOps component: install Flux, GitRepository, Kustomizations."""

from __future__ import annotations

import pulumi
import pulumi_kubernetes as k8s

from config import FLUX_INSTALL_URL, NS_FLUX_SYSTEM, TIMEOUT_WAIT, OpenChoreoConfig
from helpers.dynamic_providers import WaitCustomResourceCondition, WaitDeployments


class FluxGitOpsResult:
    """Outputs from the flux gitops component."""

    def __init__(
        self,
        kustomization_projects: k8s.apiextensions.CustomResource,
        kustomizations_ready: WaitCustomResourceCondition,
    ):
        self.kustomization_projects = kustomization_projects
        self.kustomizations_ready = kustomizations_ready


def deploy(
    cfg: OpenChoreoConfig,
    k8s_provider: k8s.Provider,
    depends: list[pulumi.Resource],
) -> FluxGitOpsResult:
    """Install Flux CD, create GitRepository, and Kustomizations."""

    # ─── 1. Install Flux CD ───
    install_flux = k8s.yaml.v2.ConfigGroup(
        "install-flux",
        files=[FLUX_INSTALL_URL],
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=depends),
    )

    wait_flux = WaitDeployments(
        "wait-flux",
        kubeconfig_path=cfg.kubeconfig_path,
        context=cfg.kubeconfig_context,
        deployment_names=["source-controller", "kustomize-controller", "helm-controller"],
        namespace=NS_FLUX_SYSTEM,
        timeout=TIMEOUT_WAIT,
        opts=pulumi.ResourceOptions(depends_on=[install_flux]),
    )

    # ─── 2. GitRepository ───
    git_repo = k8s.apiextensions.CustomResource(
        "git-repository",
        api_version="source.toolkit.fluxcd.io/v1",
        kind="GitRepository",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name="sample-gitops",
            namespace=NS_FLUX_SYSTEM,
        ),
        spec={
            "interval": "1m",
            "url": cfg.gitops_repo_url,
            "ref": {"branch": cfg.gitops_repo_branch},
        },
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[wait_flux]),
    )

    # ─── 3. Kustomizations ───
    kust_namespaces = k8s.apiextensions.CustomResource(
        "kustomization-namespaces",
        api_version="kustomize.toolkit.fluxcd.io/v1",
        kind="Kustomization",
        metadata=k8s.meta.v1.ObjectMetaArgs(name="namespaces", namespace=NS_FLUX_SYSTEM),
        spec={
            "interval": "5m",
            "path": "./namespaces",
            "prune": True,
            "sourceRef": {"kind": "GitRepository", "name": "sample-gitops"},
        },
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[git_repo]),
    )

    kust_platform_shared = k8s.apiextensions.CustomResource(
        "kustomization-platform-shared",
        api_version="kustomize.toolkit.fluxcd.io/v1",
        kind="Kustomization",
        metadata=k8s.meta.v1.ObjectMetaArgs(name="platform-shared", namespace=NS_FLUX_SYSTEM),
        spec={
            "interval": "5m",
            "path": "./platform-shared",
            "prune": True,
            "sourceRef": {"kind": "GitRepository", "name": "sample-gitops"},
        },
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[git_repo]),
    )

    kust_platform = k8s.apiextensions.CustomResource(
        "kustomization-platform",
        api_version="kustomize.toolkit.fluxcd.io/v1",
        kind="Kustomization",
        metadata=k8s.meta.v1.ObjectMetaArgs(name="oc-demo-platform", namespace=NS_FLUX_SYSTEM),
        spec={
            "interval": "5m",
            "path": "./namespaces/default/platform",
            "prune": True,
            "targetNamespace": "default",
            "sourceRef": {"kind": "GitRepository", "name": "sample-gitops"},
            "dependsOn": [{"name": "namespaces"}, {"name": "platform-shared"}],
        },
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[kust_namespaces, kust_platform_shared]),
    )

    kust_projects = k8s.apiextensions.CustomResource(
        "kustomization-projects",
        api_version="kustomize.toolkit.fluxcd.io/v1",
        kind="Kustomization",
        metadata=k8s.meta.v1.ObjectMetaArgs(name="oc-demo-projects", namespace=NS_FLUX_SYSTEM),
        spec={
            "interval": "5m",
            "path": "./namespaces/default/projects",
            "prune": True,
            "targetNamespace": "default",
            "sourceRef": {"kind": "GitRepository", "name": "sample-gitops"},
            "dependsOn": [{"name": "oc-demo-platform"}],
        },
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[kust_platform]),
    )

    # ─── 4. Wait for the final Kustomization to become Ready ───
    kust_ready = WaitCustomResourceCondition(
        "wait-kustomization-projects-ready",
        kubeconfig_path=cfg.kubeconfig_path,
        context=cfg.kubeconfig_context,
        group="kustomize.toolkit.fluxcd.io",
        version="v1",
        plural="kustomizations",
        resource_name="oc-demo-projects",
        namespace=NS_FLUX_SYSTEM,
        condition_type="Ready",
        timeout=TIMEOUT_WAIT,
        opts=pulumi.ResourceOptions(depends_on=[kust_projects]),
    )

    return FluxGitOpsResult(
        kustomization_projects=kust_projects,
        kustomizations_ready=kust_ready,
    )
