"""Flux GitOps component: install Flux, GitRepository, Kustomizations."""

# pyright: reportMissingImports=false

from __future__ import annotations

import pulumi
import pulumi_kubernetes as k8s

from config import FLUX_INSTALL_URL, NS_FLUX_SYSTEM, TIMEOUT_FLUX_WAIT, OpenChoreoConfig
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


class FluxGitOps(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        k8s_provider: k8s.Provider,
        depends: list[pulumi.Resource],
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:FluxGitOps", name, {}, opts)

        # ─── 1. Install Flux CD ───
        install_flux = k8s.yaml.v2.ConfigGroup(
            "install-flux",
            files=[FLUX_INSTALL_URL],
            opts=self._child_opts(provider=k8s_provider, depends_on=depends),
        )

        wait_flux = WaitDeployments(
            "wait-flux",
            kubeconfig_path=cfg.kubeconfig_path,
            context=cfg.kubeconfig_context,
            deployment_names=["source-controller", "kustomize-controller", "helm-controller"],
            namespace=NS_FLUX_SYSTEM,
            timeout=TIMEOUT_FLUX_WAIT,
            opts=self._child_opts(depends_on=[install_flux]),
        )

        # ─── 2a. Git credentials Secret (private repo auth) ───
        git_repo_depends: list[pulumi.Resource] = [wait_flux]
        if cfg.github_pat:
            git_secret = k8s.core.v1.Secret(
                "flux-git-credentials",
                metadata=k8s.meta.v1.ObjectMetaArgs(
                    name="flux-git-credentials",
                    namespace=NS_FLUX_SYSTEM,
                ),
                string_data={
                    "username": "git",
                    "password": cfg.github_pat,
                },
                opts=self._child_opts(provider=k8s_provider, depends_on=[wait_flux]),
            )
            git_repo_depends.append(git_secret)

        # ─── 2b. GitRepository ───
        git_repo_spec: dict = {
            "interval": "1m",
            "url": cfg.gitops_repo_url,
            "ref": {"branch": cfg.gitops_repo_branch},
        }
        if cfg.github_pat:
            git_repo_spec["secretRef"] = {"name": "flux-git-credentials"}

        git_repo = k8s.apiextensions.CustomResource(
            "git-repository",
            api_version="source.toolkit.fluxcd.io/v1",
            kind="GitRepository",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="sample-gitops",
                namespace=NS_FLUX_SYSTEM,
            ),
            spec=git_repo_spec,
            opts=self._child_opts(provider=k8s_provider, depends_on=git_repo_depends),
        )

        # ─── 3. Kustomizations ───
        kust_namespaces = k8s.apiextensions.CustomResource(
            "kustomization-namespaces",
            api_version="kustomize.toolkit.fluxcd.io/v1",
            kind="Kustomization",
            metadata=k8s.meta.v1.ObjectMetaArgs(name="oc-namespaces", namespace=NS_FLUX_SYSTEM),
            spec={
                "interval": "5m",
                "path": "./namespaces",
                "prune": True,
                "sourceRef": {"kind": "GitRepository", "name": "sample-gitops"},
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[git_repo]),
        )

        kust_platform_shared = k8s.apiextensions.CustomResource(
            "kustomization-platform-shared",
            api_version="kustomize.toolkit.fluxcd.io/v1",
            kind="Kustomization",
            metadata=k8s.meta.v1.ObjectMetaArgs(name="oc-platform-shared", namespace=NS_FLUX_SYSTEM),
            spec={
                "interval": "5m",
                "path": "./platform-shared",
                "prune": True,
                "sourceRef": {"kind": "GitRepository", "name": "sample-gitops"},
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[git_repo]),
        )

        kust_platform = k8s.apiextensions.CustomResource(
            "kustomization-platform",
            api_version="kustomize.toolkit.fluxcd.io/v1",
            kind="Kustomization",
            metadata=k8s.meta.v1.ObjectMetaArgs(name="oc-platform", namespace=NS_FLUX_SYSTEM),
            spec={
                "interval": "5m",
                "path": "./namespaces/default/platform",
                "prune": True,
                "targetNamespace": "default",
                "sourceRef": {"kind": "GitRepository", "name": "sample-gitops"},
                "dependsOn": [{"name": "oc-namespaces"}, {"name": "oc-platform-shared"}],
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[kust_namespaces, kust_platform_shared]),
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
                "dependsOn": [{"name": "oc-platform"}],
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[kust_platform]),
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
            timeout=TIMEOUT_FLUX_WAIT,
            opts=self._child_opts(depends_on=[kust_projects]),
        )

        # ─── 5. Flux Notifications (sync/build failure alerts) ───
        # Generic webhook provider — receives JSON payloads from Flux.
        # Replace the address with a real webhook URL (Slack, Discord, etc.)
        # when ready.  The generic provider logs events that can be scraped
        # by any observability stack.
        notif_provider = k8s.apiextensions.CustomResource(
            "flux-notification-provider",
            api_version="notification.toolkit.fluxcd.io/v1beta3",
            kind="Provider",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="openchoreo-alerts",
                namespace=NS_FLUX_SYSTEM,
            ),
            spec={
                "type": "generic",
                # Log to Flux notification-controller stdout (always available).
                # Swap to a real URL when a webhook sink is configured.
                "address": "http://notification-controller.flux-system.svc.cluster.local/",
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[wait_flux]),
        )

        # Alert on any Kustomization or GitRepository failure/warning.
        k8s.apiextensions.CustomResource(
            "flux-alert",
            api_version="notification.toolkit.fluxcd.io/v1beta3",
            kind="Alert",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="openchoreo-sync-alerts",
                namespace=NS_FLUX_SYSTEM,
            ),
            spec={
                "providerRef": {"name": "openchoreo-alerts"},
                "eventSeverity": "error",
                "eventSources": [
                    {
                        "kind": "Kustomization",
                        "name": "*",
                        "namespace": NS_FLUX_SYSTEM,
                    },
                    {
                        "kind": "GitRepository",
                        "name": "*",
                        "namespace": NS_FLUX_SYSTEM,
                    },
                ],
            },
            opts=self._child_opts(provider=k8s_provider, depends_on=[notif_provider]),
        )

        # ─── 6. Health checks on ReleaseBinding conditions ───
        # Add healthChecks to the projects Kustomization so Flux reports
        # unhealthy when OpenChoreo ReleaseBindings have unresolved deps.
        # We patch the existing kust_projects rather than a separate resource
        # to keep the dependency chain clean.
        k8s.apiextensions.CustomResource(
            "kustomization-projects-healthchecks",
            api_version="kustomize.toolkit.fluxcd.io/v1",
            kind="Kustomization",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="oc-demo-projects",
                namespace=NS_FLUX_SYSTEM,
            ),
            spec={
                "interval": "5m",
                "path": "./namespaces/default/projects",
                "prune": True,
                "targetNamespace": "default",
                "sourceRef": {"kind": "GitRepository", "name": "sample-gitops"},
                "dependsOn": [{"name": "oc-platform"}],
                "healthChecks": [
                    {
                        "apiVersion": "openchoreo.dev/v1alpha1",
                        "kind": "ReleaseBinding",
                        "name": "*",
                        "namespace": "default",
                    },
                ],
            },
            opts=self._child_opts(
                provider=k8s_provider,
                depends_on=[kust_ready],
            ),
        )

        self.result = FluxGitOpsResult(
            kustomization_projects=kust_projects,
            kustomizations_ready=kust_ready,
        )
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
) -> FluxGitOpsResult:
    """Install Flux CD, create GitRepository, and Kustomizations."""
    return FluxGitOps(
        "flux-gitops",
        cfg=cfg,
        k8s_provider=k8s_provider,
        depends=depends,
    ).result
