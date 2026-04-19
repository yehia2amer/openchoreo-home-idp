"""Dynamic providers for OpenChoreo demo app bootstrap.

Providers:
  - TriggerWorkflowRun: Creates a WorkflowRun CR, polls until completion.
  - MergeGitHubPR: Finds and merges an open PR by branch pattern.
  - ForceFluxReconcile: Annotates a GitRepository to trigger immediate sync.
  - WaitReleaseBindingReady: Waits for a ReleaseBinding to reach Ready=True.
"""

from __future__ import annotations

import json
import logging
import subprocess
import time
from typing import Any

import pulumi
from pulumi.dynamic import CreateResult, DiffResult, ResourceProvider

logger = logging.getLogger(__name__)


def _kubectl(kubeconfig: str, context: str, *args: str, timeout: int = 30) -> str:
    """Run kubectl and return stdout."""
    cmd = ["kubectl", "--kubeconfig", kubeconfig, "--context", context, *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"kubectl failed: {result.stderr.strip()}")
    return result.stdout.strip()


# ──────────────────────────────────────────────────────────────
# TriggerWorkflowRun
# ──────────────────────────────────────────────────────────────


class _TriggerWorkflowRunProvider(ResourceProvider):
    def _check_existing(self, kubeconfig: str, context: str, run_name: str) -> str | None:
        try:
            raw = _kubectl(
                kubeconfig,
                context,
                "get",
                f"workflowruns.openchoreo.dev/{run_name}",
                "-o",
                "jsonpath={.status.conditions[*]}",
            )
            if "WorkflowSucceeded" in raw and '"status":"True"' in raw:
                return "Succeeded"
            if "WorkflowFailed" in raw and '"status":"True"' in raw:
                return "Failed"
            return "Running"
        except RuntimeError:
            return None

    def create(self, inputs: dict[str, Any]) -> CreateResult:
        kubeconfig = inputs["kubeconfig_path"]
        context = inputs["context"]
        manifest = inputs["manifest_json"]
        timeout = inputs.get("timeout", 900)
        poll_interval = inputs.get("poll_interval", 15)
        run_name = inputs["run_name"]

        existing = self._check_existing(kubeconfig, context, run_name)
        if existing == "Succeeded":
            return CreateResult(
                id_=f"workflowrun/{run_name}",
                outs={**inputs, "status": "Succeeded"},
            )

        if existing == "Failed":
            try:
                _kubectl(
                    kubeconfig,
                    context,
                    "delete",
                    f"workflowruns.openchoreo.dev/{run_name}",
                    "--ignore-not-found=true",
                )
                time.sleep(5)
            except RuntimeError:
                pass

        proc = subprocess.run(
            ["kubectl", "--kubeconfig", kubeconfig, "--context", context, "apply", "-f", "-"],
            input=manifest,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Failed to create WorkflowRun: {proc.stderr.strip()}")

        # Poll until completed or timed out
        deadline = time.time() + timeout
        final_status = "Unknown"
        while time.time() < deadline:
            try:
                raw = _kubectl(
                    kubeconfig,
                    context,
                    "get",
                    f"workflowruns.openchoreo.dev/{run_name}",
                    "-o",
                    "jsonpath={.status.conditions[*]}",
                )
                if "WorkflowSucceeded" in raw and '"status":"True"' in raw:
                    final_status = "Succeeded"
                    break
                if "WorkflowFailed" in raw and '"status":"True"' in raw:
                    # Get task details for error message
                    tasks = _kubectl(
                        kubeconfig,
                        context,
                        "get",
                        f"workflowruns.openchoreo.dev/{run_name}",
                        "-o",
                        "jsonpath={range .status.tasks[*]}{.name}: {.phase} {.message}\\n{end}",
                    )
                    raise RuntimeError(f"WorkflowRun {run_name} failed.\nTasks:\n{tasks}")
            except RuntimeError as e:
                if "failed" in str(e).lower():
                    raise
                pass  # kubectl transient errors, retry
            time.sleep(poll_interval)
        else:
            raise TimeoutError(
                f"WorkflowRun {run_name} did not complete within {timeout}s. Last status: {final_status}"
            )

        return CreateResult(
            id_=f"workflowrun/{run_name}",
            outs={**inputs, "status": final_status},
        )

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        diff_keys = ["manifest_json", "run_name", "kubeconfig_path", "context"]
        replaces = [k for k in diff_keys if olds.get(k) != news.get(k)]
        return DiffResult(changes=bool(replaces), replaces=replaces)

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        # Clean up the WorkflowRun on destroy
        try:
            _kubectl(
                props["kubeconfig_path"],
                props["context"],
                "delete",
                f"workflowruns.openchoreo.dev/{props['run_name']}",
                "--ignore-not-found=true",
            )
        except Exception:
            pass


class TriggerWorkflowRun(pulumi.dynamic.Resource):
    """Create a WorkflowRun and wait for it to complete."""

    status: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        kubeconfig_path: str,
        context: str,
        run_name: str,
        manifest_json: str,
        timeout: int = 900,
        poll_interval: int = 15,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _TriggerWorkflowRunProvider(),
            name,
            {
                "kubeconfig_path": kubeconfig_path,
                "context": context,
                "run_name": run_name,
                "manifest_json": manifest_json,
                "timeout": timeout,
                "poll_interval": poll_interval,
                "status": None,
            },
            opts,
        )


# ──────────────────────────────────────────────────────────────
# MergeGitHubPR
# ──────────────────────────────────────────────────────────────


class _MergeGitHubPRProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        import urllib.error
        import urllib.request

        token = inputs["github_token"]
        repo = inputs["repo"]  # "owner/repo"
        branch_prefix = inputs["branch_prefix"]  # e.g. "release/document-svc-"
        timeout = inputs.get("timeout", 300)
        poll_interval = inputs.get("poll_interval", 10)

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "pulumi-openchoreo",
        }

        # ── Idempotency: check if a PR was already merged ──
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{repo}/pulls?state=closed&sort=updated&direction=desc&per_page=30",
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                closed_prs = json.loads(resp.read())

            for pr in closed_prs:
                if pr["head"]["ref"].startswith(branch_prefix) and pr.get("merged_at"):
                    pulumi.log.info(f"PR #{pr['number']} already merged for {branch_prefix} — skipping")
                    return CreateResult(
                        id_=f"pr/{repo}/{pr['number']}",
                        outs={**inputs, "pr_number": pr["number"], "pr_url": pr["html_url"], "merged": True},
                    )
        except Exception:
            pass

        pr_number = None
        pr_url = None
        deadline = time.time() + timeout
        while time.time() < deadline:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{repo}/pulls?state=open&per_page=30",
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                prs = json.loads(resp.read())

            for pr in prs:
                if pr["head"]["ref"].startswith(branch_prefix):
                    pr_number = pr["number"]
                    pr_url = pr["html_url"]
                    break
            if pr_number:
                break
            time.sleep(poll_interval)
        else:
            raise TimeoutError(f"No PR found with branch prefix '{branch_prefix}' in {repo} within {timeout}s")

        # Merge the PR
        merge_data = json.dumps(
            {
                "merge_method": "merge",
                "commit_title": f"Auto-merge: {branch_prefix.rstrip('-')}",
            }
        ).encode()
        merge_req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/pulls/{pr_number}/merge",
            data=merge_data,
            headers={**headers, "Content-Type": "application/json"},
            method="PUT",
        )
        merge_result: dict[str, Any] | None = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(merge_req, timeout=30) as resp:
                    merge_result = json.loads(resp.read())
                break
            except urllib.error.HTTPError as e:
                if attempt < 2 and e.code in (502, 503, 504):
                    time.sleep(2 ** attempt)
                    continue
                raise

        if merge_result is None:
            raise RuntimeError(f"Failed to merge PR #{pr_number}: no response from GitHub")

        if not merge_result.get("merged"):
            raise RuntimeError(f"Failed to merge PR #{pr_number}: {merge_result.get('message', 'unknown error')}")

        return CreateResult(
            id_=f"pr/{repo}/{pr_number}",
            outs={**inputs, "pr_number": pr_number, "pr_url": pr_url, "merged": True},
        )

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        diff_keys = ["repo", "branch_prefix", "github_token"]
        replaces = [k for k in diff_keys if olds.get(k) != news.get(k)]
        return DiffResult(changes=bool(replaces), replaces=replaces)

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        pass


class MergeGitHubPR(pulumi.dynamic.Resource):
    """Find and merge a GitHub PR matching a branch prefix."""

    pr_number: pulumi.Output[int]
    pr_url: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        github_token: str,
        repo: str,
        branch_prefix: str,
        timeout: int = 300,
        poll_interval: int = 10,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _MergeGitHubPRProvider(),
            name,
            {
                "github_token": github_token,
                "repo": repo,
                "branch_prefix": branch_prefix,
                "timeout": timeout,
                "poll_interval": poll_interval,
                "pr_number": None,
                "pr_url": None,
            },
            opts,
        )


# ──────────────────────────────────────────────────────────────
# ForceFluxReconcile
# ──────────────────────────────────────────────────────────────


class _ForceFluxReconcileProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        kubeconfig = inputs["kubeconfig_path"]
        context = inputs["context"]
        git_repo_name = inputs["git_repo_name"]
        namespace = inputs.get("namespace", "flux-system")

        # Annotate the GitRepository to force reconciliation
        _kubectl(
            kubeconfig,
            context,
            "annotate",
            "gitrepository",
            git_repo_name,
            "-n",
            namespace,
            f"reconcile.fluxcd.io/requestedAt={int(time.time())}",
            "--overwrite",
        )

        # Wait for the kustomization to pick up the new revision
        wait_timeout = inputs.get("timeout", 180)
        time.sleep(5)  # Give Flux a moment to detect the annotation
        deadline = time.time() + wait_timeout
        ready = None
        while time.time() < deadline:
            try:
                ready = _kubectl(
                    kubeconfig,
                    context,
                    "get",
                    "kustomizations",
                    "-n",
                    namespace,
                    "-o",
                    "jsonpath={range .items[*]}{.metadata.name}={.status.conditions[0].status} {end}",
                )
                # Check all kustomizations are True
                parts = ready.split()
                if parts and all("=True" in p for p in parts):
                    break
            except Exception:
                pass
            time.sleep(10)
        else:
            not_ready = []
            if ready:
                not_ready = [p.split("=")[0] for p in ready.split() if "=True" not in p]
            raise TimeoutError(
                f"Flux reconciliation timed out after {wait_timeout}s. "
                f"Not ready: {not_ready}"
            )

        return CreateResult(id_=f"flux-reconcile/{git_repo_name}", outs=inputs)

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        diff_keys = ["kubeconfig_path", "context", "git_repo_name", "namespace"]
        replaces = [k for k in diff_keys if olds.get(k) != news.get(k)]
        return DiffResult(changes=bool(replaces), replaces=replaces)

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        pass


class ForceFluxReconcile(pulumi.dynamic.Resource):
    """Force Flux to reconcile a GitRepository immediately."""

    def __init__(
        self,
        name: str,
        kubeconfig_path: str,
        context: str,
        git_repo_name: str = "sample-gitops",
        namespace: str = "flux-system",
        timeout: int = 180,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _ForceFluxReconcileProvider(),
            name,
            {
                "kubeconfig_path": kubeconfig_path,
                "context": context,
                "git_repo_name": git_repo_name,
                "namespace": namespace,
                "timeout": timeout,
            },
            opts,
        )


# ──────────────────────────────────────────────────────────────
# WaitReleaseBindingReady
# ──────────────────────────────────────────────────────────────


class _WaitReleaseBindingReadyProvider(ResourceProvider):
    def create(self, inputs: dict[str, Any]) -> CreateResult:
        kubeconfig = inputs["kubeconfig_path"]
        context = inputs["context"]
        binding_name = inputs["binding_name"]
        namespace = inputs.get("namespace", "default")
        timeout = inputs.get("timeout", 300)
        poll_interval = inputs.get("poll_interval", 10)

        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                raw = _kubectl(
                    kubeconfig,
                    context,
                    "get",
                    f"releasebindings.openchoreo.dev/{binding_name}",
                    "-n",
                    namespace,
                    "-o",
                    "json",
                )
                rb = json.loads(raw)
                conditions = rb.get("status", {}).get("conditions", [])
                ready = any(c.get("type") == "Ready" and c.get("status") == "True" for c in conditions)
                if ready:
                    return CreateResult(
                        id_=f"releasebinding/{namespace}/{binding_name}",
                        outs={**inputs, "ready": True},
                    )
            except Exception:
                pass
            time.sleep(poll_interval)

        raise TimeoutError(f"ReleaseBinding {binding_name} did not reach Ready=True within {timeout}s")

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        diff_keys = ["kubeconfig_path", "context", "binding_name", "namespace"]
        replaces = [k for k in diff_keys if olds.get(k) != news.get(k)]
        return DiffResult(changes=bool(replaces), replaces=replaces)

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        pass


class WaitReleaseBindingReady(pulumi.dynamic.Resource):
    """Wait for a ReleaseBinding to reach Ready=True."""

    ready: pulumi.Output[bool]

    def __init__(
        self,
        name: str,
        kubeconfig_path: str,
        context: str,
        binding_name: str,
        namespace: str = "default",
        timeout: int = 300,
        poll_interval: int = 10,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__(
            _WaitReleaseBindingReadyProvider(),
            name,
            {
                "kubeconfig_path": kubeconfig_path,
                "context": context,
                "binding_name": binding_name,
                "namespace": namespace,
                "timeout": timeout,
                "poll_interval": poll_interval,
                "ready": None,
            },
            opts,
        )
