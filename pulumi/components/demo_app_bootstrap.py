"""Demo App Bootstrap: automate OpenChoreo Flux CD tutorial Step 6.

After FluxCD syncs the gitops repo (Components + Workloads are in the cluster),
this component triggers WorkflowRuns for each component, merges the resulting
PRs, forces Flux reconciliation, and verifies all ReleaseBindings are Ready.

Gated behind ``enable_demo_app_bootstrap`` config flag.
"""

from __future__ import annotations

import json
import re

import pulumi
import pulumi_kubernetes as k8s

from config import OpenChoreoConfig
from helpers.bootstrap_providers import (
    ForceFluxReconcile,
    MergeGitHubPR,
    TriggerWorkflowRun,
    WaitReleaseBindingReady,
)


def _workflowrun_manifest(
    run_name: str,
    project: str,
    component: str,
    docker_context: str,
    dockerfile_path: str,
    app_path: str,
    source_repo: str = "https://github.com/openchoreo/sample-workloads.git",
    branch: str = "main",
) -> str:
    """Generate a WorkflowRun manifest as YAML string."""
    return json.dumps({
        "apiVersion": "openchoreo.dev/v1alpha1",
        "kind": "WorkflowRun",
        "metadata": {
            "name": run_name,
            "namespace": "default",
            "labels": {
                "openchoreo.dev/project": project,
                "openchoreo.dev/component": component,
            },
        },
        "spec": {
            "workflow": {
                "kind": "Workflow",
                "name": "docker-gitops-release",
                "parameters": {
                    "componentName": component,
                    "projectName": project,
                    "docker": {
                        "context": docker_context,
                        "filePath": dockerfile_path,
                    },
                    "repository": {
                        "appPath": app_path,
                        "revision": {"branch": branch, "commit": ""},
                        "url": source_repo,
                    },
                    "workloadDescriptorPath": "workload.yaml",
                },
            },
        },
    })


def _extract_github_repo(url: str) -> str:
    """Extract 'owner/repo' from a GitHub URL."""
    m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
    if not m:
        raise ValueError(f"Cannot extract owner/repo from URL: {url}")
    return m.group(1)


class DemoAppBootstrapResult:
    """Outputs from the demo app bootstrap."""

    def __init__(self, all_ready: list[WaitReleaseBindingReady]):
        self.all_ready = all_ready


class DemoAppBootstrap(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        cfg: OpenChoreoConfig,
        depends: list[pulumi.Resource],
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("openchoreo:components:DemoAppBootstrap", name, {}, opts)

        gitops_repo = _extract_github_repo(cfg.gitops_repo_url)
        build_timeout = 900  # 15 min per build
        pr_timeout = 120     # 2 min to find PR after build
        flux_timeout = 180   # 3 min for Flux sync
        rb_timeout = 300     # 5 min for ReleaseBindings to be Ready

        # ─── Phase 1: Trigger backend builds (parallel) ───────────

        doclet_components = [
            {
                "name": "document-svc",
                "run_name": "document-svc-bootstrap",
                "docker_context": "/project-doclet-app/service-go-document",
                "dockerfile": "/project-doclet-app/service-go-document/Dockerfile",
                "app_path": "/project-doclet-app/service-go-document",
            },
            {
                "name": "collab-svc",
                "run_name": "collab-svc-bootstrap",
                "docker_context": "/project-doclet-app/service-go-collab",
                "dockerfile": "/project-doclet-app/service-go-collab/Dockerfile",
                "app_path": "/project-doclet-app/service-go-collab",
            },
        ]

        backend_builds: list[TriggerWorkflowRun] = []
        for comp in doclet_components:
            build = TriggerWorkflowRun(
                f"build-{comp['name']}",
                kubeconfig_path=cfg.kubeconfig_path,
                context=cfg.kubeconfig_context,
                run_name=comp["run_name"],
                manifest_json=_workflowrun_manifest(
                    run_name=comp["run_name"],
                    project="doclet",
                    component=comp["name"],
                    docker_context=comp["docker_context"],
                    dockerfile_path=comp["dockerfile"],
                    app_path=comp["app_path"],
                ),
                timeout=build_timeout,
                opts=self._child_opts(depends_on=depends),
            )
            backend_builds.append(build)

        # ─── Phase 2: Trigger frontend build (after backends) ─────

        frontend_build = TriggerWorkflowRun(
            "build-frontend",
            kubeconfig_path=cfg.kubeconfig_path,
            context=cfg.kubeconfig_context,
            run_name="frontend-bootstrap",
            manifest_json=_workflowrun_manifest(
                run_name="frontend-bootstrap",
                project="doclet",
                component="frontend",
                docker_context="/project-doclet-app/webapp-react-frontend",
                dockerfile_path="/project-doclet-app/webapp-react-frontend/Dockerfile",
                app_path="/project-doclet-app/webapp-react-frontend",
            ),
            timeout=build_timeout,
            opts=self._child_opts(depends_on=backend_builds),
        )

        all_builds = backend_builds + [frontend_build]

        # ─── Phase 3: Merge PRs ──────────────────────────────────

        pr_merges: list[MergeGitHubPR] = []
        for comp_name in ["document-svc", "collab-svc", "frontend"]:
            merge = MergeGitHubPR(
                f"merge-pr-{comp_name}",
                github_token=cfg.github_pat,
                repo=gitops_repo,
                branch_prefix=f"release/{comp_name}-",
                timeout=pr_timeout,
                opts=self._child_opts(depends_on=all_builds),
            )
            pr_merges.append(merge)

        # ─── Phase 4: Force Flux reconciliation ──────────────────

        flux_sync = ForceFluxReconcile(
            "flux-reconcile-after-merges",
            kubeconfig_path=cfg.kubeconfig_path,
            context=cfg.kubeconfig_context,
            git_repo_name="sample-gitops",
            timeout=flux_timeout,
            opts=self._child_opts(depends_on=pr_merges),
        )

        # ─── Phase 5: Wait for all ReleaseBindings to be Ready ───

        release_bindings_to_check = [
            "document-svc-development",
            "collab-svc-development",
            "frontend-development",
        ]

        all_ready: list[WaitReleaseBindingReady] = []
        for rb_name in release_bindings_to_check:
            wait = WaitReleaseBindingReady(
                f"wait-rb-{rb_name}",
                kubeconfig_path=cfg.kubeconfig_path,
                context=cfg.kubeconfig_context,
                binding_name=rb_name,
                timeout=rb_timeout,
                opts=self._child_opts(depends_on=[flux_sync]),
            )
            all_ready.append(wait)

        self.result = DemoAppBootstrapResult(all_ready=all_ready)
        self.register_outputs({})

    def _child_opts(
        self,
        depends_on: list[pulumi.Resource] | None = None,
    ) -> pulumi.ResourceOptions:
        return pulumi.ResourceOptions(
            parent=self,
            depends_on=depends_on or [],
            aliases=[pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)],
        )
