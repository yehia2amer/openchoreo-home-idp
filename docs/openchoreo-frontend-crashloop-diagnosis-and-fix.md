# OpenChoreo Frontend CrashLoopBackOff — Diagnosis, Root Cause & Fix Plan

**Date**: 2026-04-05
**Cluster**: Talos Baremetal (`talos-c43-5pl` at `192.168.0.100:6443`)
**Platform**: OpenChoreo + FluxCD + Argo Workflows
**Tutorial being followed**: [GitOps with Flux CD](https://github.com/openchoreo/sample-gitops/blob/main/flux/README.md)

---

## 1. Symptom

The frontend pod in the `dp-default-doclet-development-50ce4d9b` namespace is in **CrashLoopBackOff** with 68+ restarts:

```
frontend-development-def9a783-6858fdd5d9-49p7l   0/1   CrashLoopBackOff   68
```

Container log output:

```
/usr/local/bin/doclet-entrypoint.sh: line 4: DOC_SERVICE_URL: missing DOC_SERVICE_URL
```

The entrypoint requires `DOC_SERVICE_URL` and `COLLAB_SERVICE_URL` environment variables, but the Deployment was rendered with `env: []` (empty).

---

## 2. Root Cause Analysis — Full Resource Chain

### 2.1 OpenChoreo Resource Chain (Bottom-Up)

| # | Resource | Status | Finding |
|---|----------|--------|---------|
| 1 | **Pod** `frontend-development-*` | `CrashLoopBackOff` | Entrypoint exits with code 2: `missing DOC_SERVICE_URL` |
| 2 | **Deployment** `frontend-development-def9a783` | 0/1 Available | Container spec has `env: []` — no env vars injected |
| 3 | **RenderedRelease** `frontend-development` | `Degraded` | Deployment rendered with empty env because connections are unresolved |
| 4 | **ReleaseBinding** `frontend-development` | `ConnectionsPending` | Status: **"2 connections pending, 0 resolved"** |
| 5 | **Workload** `frontend-workload` | Healthy | Declares `dependencies.endpoints` on `document-svc` (→`DOC_SERVICE_URL`) and `collab-svc` (→`COLLAB_SERVICE_URL`) |
| 6 | **ComponentRelease** `frontend-f3a5cd49` | Exists | Immutable snapshot exists, workload has correct dependency declarations |
| 7 | **`document-svc`** — Component + Workload | Exists, **no ComponentRelease** | No release was ever generated → never deployed |
| 8 | **`collab-svc`** — Component + Workload | Exists, **no ComponentRelease** | Image is `temp-image-placeholder` — build never ran |

### 2.2 How OpenChoreo Dependency Resolution Works

Per the [Endpoint Dependencies docs](https://openchoreo.dev/docs/developer-guide/dependencies/endpoints/):

1. The `frontend` Workload declares `dependencies.endpoints` on `document-svc.http` and `collab-svc.http`
2. When the ReleaseBinding controller processes `frontend-development`, it looks for ReleaseBindings of `document-svc` and `collab-svc` in the same environment (`development`)
3. If the target ReleaseBindings exist and have resolved endpoints, the controller injects the connection addresses as env vars (e.g., `DOC_SERVICE_URL=http://document-svc.<ns>.svc.cluster.local:8080`)
4. If the target ReleaseBindings **don't exist**, connections stay "pending" and **no env vars are injected** — the Deployment is rendered with `env: []`

### 2.3 Why the Dependencies Are Missing

Tracing the [Flux CD tutorial](https://github.com/openchoreo/sample-gitops/blob/main/flux/README.md):

| Tutorial Step | Required Action | Was It Done? |
|---|---|---|
| Step 1: Fork repo | Fork `sample-gitops` | ✅ Done (`yehia2amer/openchoreo-gitops`) |
| Step 2: Update URLs | Update GitRepository + Workflow URLs | ✅ Done |
| Step 3: Create secrets | Store PAT in OpenBao (`git-token` + `gitops-token`) | ✅ Done (verified token is valid) |
| Step 4: Deploy Flux | `kubectl apply -f flux/` | ✅ Done (all 4 Kustomizations Ready) |
| Step 5: Verify platform | Check environments, component types, workflows | ✅ Done |
| **Step 6.1: Build `document-svc`** | Create WorkflowRun `document-svc-manual-01` | ❌ **Never done** |
| **Step 6.2: Build `collab-svc`** | Create WorkflowRun `collab-svc-manual-01` | ❌ **Never done** |
| **Step 6.3: Build `frontend`** | Create WorkflowRun `frontend-workflow-manual-01` | ⚠️ `frontend-build-002` ran but **failed** at `generate-gitops-resources` |
| **Step 6.4: Merge PRs** | Merge 3 PRs in gitops repo | ❌ **Can't — 0 PRs exist** (builds never created them) |

**The root cause is that Steps 6.1 and 6.2 were never executed.** The `document-svc` and `collab-svc` WorkflowRuns were never triggered, so:
- No container images were built for these components
- No ComponentReleases were generated
- No ReleaseBindings were created
- The frontend's dependency connections can never resolve

### 2.4 Additional Findings

#### GitOps Repo State

The gitops repo (`yehia2amer/openchoreo-gitops`) shows:

```
components/frontend/       → component.yaml, workload.yaml, releases/, release-bindings/ ✅
components/document-svc/   → component.yaml, workload.yaml (NO releases/ or release-bindings/) ❌
components/collab-svc/     → component.yaml, workload.yaml (NO releases/ or release-bindings/) ❌
components/nats/           → component.yaml, workload.yaml, releases/, release-bindings/ ✅
components/postgres/       → component.yaml, workload.yaml, releases/, release-bindings/ ✅
```

#### Stale Image Reference

The `document-svc` workload in the gitops repo references `host.k3d.internal:10082/` (k3d development DNS). The in-cluster Workload was updated to `registry.openchoreo-workflow-plane.svc.cluster.local:10082/`. This is self-correcting — the `docker-gitops-release` workflow uses `registry-url` parameter from the Workflow's `runTemplate`, which already points to the correct in-cluster registry.

#### `frontend-build-002` Failure

The only WorkflowRun that was ever triggered (`frontend-build-002`) completed steps through `create-feature-branch` but **failed** at `generate-gitops-resources` (exit code 1). The Argo Workflow pods have been garbage-collected, so the exact error message is lost. The `git-commit-push-pr` step never ran, so no PR was created (confirmed: 0 PRs in the repo).

#### CI Pipeline Architecture

The `docker-gitops-release` workflow (per [Build and Release Workflows docs](https://openchoreo.dev/docs/platform-engineer-guide/gitops/automations/build-and-release-workflows/)) follows this pattern:

```
Phase 1 — Build:     Clone Source → Build Image → Push to Registry
Phase 2 — Release:   Clone GitOps Repo → Create Feature Branch →
                      occ workload create → occ componentrelease generate →
                      occ releasebinding generate → Git Commit → Push → Create PR
```

The `occ` CLI runs in **file-system mode** against the cloned gitops repo directory.

---

## 3. Fix Plan

### Phase 1: Execute Tutorial Steps 6.1–6.4 (Immediate Fix)

#### 3.1 Trigger `document-svc` WorkflowRun

```bash
kubectl apply -f - <<EOF
apiVersion: openchoreo.dev/v1alpha1
kind: WorkflowRun
metadata:
  name: document-svc-manual-01
  namespace: default
  labels:
    openchoreo.dev/project: "doclet"
    openchoreo.dev/component: "document-svc"
spec:
  workflow:
    name: docker-gitops-release
    kind: Workflow
    parameters:
      componentName: document-svc
      projectName: doclet
      docker:
        context: /project-doclet-app/service-go-document
        filePath: /project-doclet-app/service-go-document/Dockerfile
      repository:
        appPath: /project-doclet-app/service-go-document
        revision:
          branch: main
          commit: ""
        url: https://github.com/openchoreo/sample-workloads.git
      workloadDescriptorPath: workload.yaml
EOF
```

#### 3.2 Trigger `collab-svc` WorkflowRun

```bash
kubectl apply -f - <<EOF
apiVersion: openchoreo.dev/v1alpha1
kind: WorkflowRun
metadata:
  name: collab-svc-manual-01
  namespace: default
  labels:
    openchoreo.dev/project: "doclet"
    openchoreo.dev/component: "collab-svc"
spec:
  workflow:
    kind: Workflow
    name: docker-gitops-release
    parameters:
      componentName: collab-svc
      projectName: doclet
      docker:
        context: /project-doclet-app/service-go-collab
        filePath: /project-doclet-app/service-go-collab/Dockerfile
      repository:
        appPath: /project-doclet-app/service-go-collab
        revision:
          branch: main
          commit: ""
        url: https://github.com/openchoreo/sample-workloads.git
      workloadDescriptorPath: workload.yaml
EOF
```

#### 3.3 Re-trigger `frontend` WorkflowRun

```bash
kubectl apply -f - <<EOF
apiVersion: openchoreo.dev/v1alpha1
kind: WorkflowRun
metadata:
  name: frontend-manual-01
  namespace: default
  labels:
    openchoreo.dev/project: "doclet"
    openchoreo.dev/component: "frontend"
spec:
  workflow:
    kind: Workflow
    name: docker-gitops-release
    parameters:
      componentName: frontend
      projectName: doclet
      docker:
        context: /project-doclet-app/webapp-react-frontend
        filePath: /project-doclet-app/webapp-react-frontend/Dockerfile
      repository:
        appPath: /project-doclet-app/webapp-react-frontend
        revision:
          branch: main
          commit: ""
        url: https://github.com/openchoreo/sample-workloads.git
      workloadDescriptorPath: workload.yaml
EOF
```

#### 3.4 Monitor builds

```bash
# Watch workflow status
kubectl get workflowruns.openchoreo.dev -w

# Check Argo Workflow pods for logs (if any step fails)
kubectl get pods -n workflows-default
kubectl logs -n workflows-default <pod-name> --tail=50
```

#### 3.5 Merge the 3 PRs

Once all WorkflowRuns succeed, 3 PRs appear on `yehia2amer/openchoreo-gitops`. Each adds:
- Updated `workload.yaml` (with real container image from registry)
- `releases/<component>-<hash>.yaml` (immutable ComponentRelease)
- `release-bindings/<component>-development.yaml` (ReleaseBinding for development env)

Merge all 3 PRs → Flux syncs → OpenChoreo resolves dependencies → frontend gets env vars → CrashLoop resolves.

#### 3.6 Verify

```bash
kubectl get releasebindings                    # Should show all 5 (frontend, document-svc, collab-svc, nats, postgres)
kubectl get pods -A | grep dp-default-doclet   # All pods should be Running
kubectl describe releasebinding frontend-development  # ConnectionsResolved should be True
```

### Phase 2: General Improvements for Pulumi/FluxCD Code

#### 2.1 Add Flux Notifications for Sync/Build Failures

Per [OpenChoreo GitOps monitoring best practices](https://openchoreo.dev/docs/platform-engineer-guide/gitops/overview/#monitoring-and-observability), add Flux Alert + Provider in `pulumi/components/flux_gitops.py`:

```python
flux_alert_provider = k8s.apiextensions.CustomResource(
    "flux-alert-provider",
    api_version="notification.toolkit.fluxcd.io/v1beta3",
    kind="Provider",
    metadata={"name": "webhook-alerts", "namespace": NS_FLUX_SYSTEM},
    spec={"type": "generic", "address": cfg.alert_webhook_url},
)

flux_alert = k8s.apiextensions.CustomResource(
    "flux-alert",
    api_version="notification.toolkit.fluxcd.io/v1beta3",
    kind="Alert",
    metadata={"name": "openchoreo-sync-alerts", "namespace": NS_FLUX_SYSTEM},
    spec={
        "providerRef": {"name": "webhook-alerts"},
        "eventSeverity": "error",
        "eventSources": [
            {"kind": "Kustomization", "name": "*"},
            {"kind": "GitRepository", "name": "*"},
        ],
    },
)
```

#### 2.2 Add OpenBao Secret Validation in Pulumi

Add a post-deploy check that validates `git-token` and `gitops-token` exist in OpenBao before workflows can run. This prevents cryptic `generate-gitops-resources` failures.

#### 2.3 Codify Demo App Bootstrap in Pulumi

Add an optional Pulumi component that triggers the 3 WorkflowRuns after initial FluxCD sync, so the tutorial's Step 6 happens automatically for demo/dev environments.

#### 2.4 Add Flux Health Checks on ReleaseBinding Conditions

Per [OpenChoreo monitoring docs](https://openchoreo.dev/docs/platform-engineer-guide/gitops/overview/#openchoreo-resource-monitoring), ReleaseBindings expose `ConnectionsResolved`, `ReleaseSynced`, and `Ready` conditions. Add Flux `healthChecks`:

```yaml
# In Kustomization spec
healthChecks:
  - apiVersion: openchoreo.dev/v1alpha1
    kind: ReleaseBinding
    name: frontend-development
    namespace: default
timeout: 10m
```

#### 2.5 Document Deployment Order Requirement

The OpenChoreo GitOps model is **PR-based by design** — builds produce PRs for review, not direct commits. Document that for the Doclet demo app:
1. WorkflowRuns must be triggered manually (or via auto-build) for each component
2. PRs must be reviewed and merged
3. Dependency components (`document-svc`, `collab-svc`) must be deployed before the `frontend`

---

## 4. Key OpenChoreo Concepts Referenced

---

## 5. Resolution Summary

**Executed on**: 2026-04-05 ~11:00-11:22 UTC

### What was done:

1. **Triggered `document-svc-manual-01` WorkflowRun** — All 8 steps succeeded (clone → build → push → extract-descriptor → clone-gitops → create-feature-branch → generate-gitops-resources → git-commit-push-pr). PR #2 created on gitops repo.

2. **Triggered `collab-svc-manual-01` WorkflowRun** — All 8 steps succeeded. PR #1 created on gitops repo.

3. **Attempted `frontend-manual-01` WorkflowRun** — Build/push succeeded, but `generate-gitops-resources` failed with:
   ```
   Error: a component release with name "frontend-f3a5cd49" already exists
   ```
   The frontend ComponentRelease was already in the gitops repo from a prior manual commit. **No frontend rebuild was needed** — the existing release was correct.

4. **Merged PR #1 (collab-svc) and PR #2 (document-svc)** via GitHub API.

5. **Triggered Flux reconciliation** — Within 90 seconds:
   - `collab-svc-f3a5cd49` ComponentRelease + `collab-svc-development` ReleaseBinding created
   - `document-svc-f3a5cd49` ComponentRelease + `document-svc-development` ReleaseBinding created
   - `frontend-development` ReleaseBinding transitioned to **"All 2 connections resolved"** + **Ready=True**
   - Frontend Deployment re-rendered with env vars injected
   - New frontend pod started successfully with `DOC_SERVICE_URL` and `COLLAB_SERVICE_URL`

### Final State:

```
$ kubectl get pods -n dp-default-doclet-development-50ce4d9b
collab-svc-development-*     1/1  Running
document-svc-development-*   1/1  Running
frontend-development-*       1/1  Running
nats-development-*           1/1  Running
postgres-development-*       1/1  Running
```

```
$ kubectl exec frontend-pod -- env | grep SERVICE
DOC_SERVICE_URL=http://document-svc.dp-default-doclet-development-50ce4d9b.svc.cluster.local:8080
COLLAB_SERVICE_URL=http://collab-svc.dp-default-doclet-development-50ce4d9b.svc.cluster.local:8090
```

### Key Lessons:

1. **The OpenChoreo Flux CD tutorial Step 6 must be followed in order** — dependency components must be built first
2. **The `generate-gitops-resources` step is idempotent for Workloads but NOT for ComponentReleases** — if a release with the same name exists, it fails. Use a different commit SHA or delete the existing release first.
3. **`workload.yaml` descriptor must exist at the `appPath` in the source repo** — without it, the workload is generated without endpoints/dependencies (warning: "Workload descriptor not found")
4. **The GitOps model is PR-based by design** — builds create PRs for review, PRs must be merged for Flux to sync

---

## 6. Key OpenChoreo Concepts Referenced

| Concept | Doc Reference |
| Dependency resolution via `dependencies.endpoints` | [Endpoint Dependencies](https://openchoreo.dev/docs/developer-guide/dependencies/endpoints/) |
| ComponentRelease → ReleaseBinding → RenderedRelease chain | [Resource Relationships](https://openchoreo.dev/docs/concepts/resource-relationships/) |
| `occ` CLI file-system mode for GitOps | [Build and Release Workflows](https://openchoreo.dev/docs/platform-engineer-guide/gitops/automations/build-and-release-workflows/) |
| Flux CD Kustomization ordering | [Using Flux CD](https://openchoreo.dev/docs/platform-engineer-guide/gitops/using-flux-cd/) |
| Bulk promotion workflow | [Bulk Promote](https://openchoreo.dev/docs/platform-engineer-guide/gitops/automations/bulk-promote/) |
| ReleaseBinding environment overrides | [Environment Overrides](https://openchoreo.dev/docs/developer-guide/deploying-applications/environment-overrides/) |
| Workload descriptor format | [Workload Descriptor](https://openchoreo.dev/docs/developer-guide/workflows/ci/workload-descriptor/) |
| GitOps repo structure (mono-repo) | [GitOps Overview](https://openchoreo.dev/docs/platform-engineer-guide/gitops/overview/) |
