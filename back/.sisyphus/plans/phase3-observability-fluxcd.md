# Phase 3: Enable Observability + FluxCD

## Objective
Enable the OpenChoreo observability plane and FluxCD GitOps on the talos-baremetal stack. Both components already exist in code — this phase flips feature flags, fixes the FluxCD private repo auth gap, creates the minimal directory structure FluxCD expects, and fixes test/component name mismatches.

## Scope
- **IN SCOPE**: Enable `enable_observability=true`, enable `enable_flux=true`, fix FluxCD GitRepository auth for private repo, create minimal FluxCD directories, fix Kustomization name mismatches between component and tests
- **OUT OF SCOPE**: Shared internal-gateway, HTTPRoutes for LAN access, CoreDNS, DNS strategy (→ Phase 4), full FluxCD directory layout from reference project

## Prerequisites
- Phase 2 deployed and healthy (51 pods, 31/31 tests)
- User has GitHub PAT ready for private repo auth
- Cluster accessible at 192.168.0.100

## Guardrails
- DO NOT touch k3d.py, rancher_desktop.py, or any non-baremetal platform files
- DO NOT change the logic or behavior of any existing function — only add/modify what's needed
- DO NOT use `create_namespace=True` on Helm releases
- DO NOT use `k8s.helm.v4.Chart` (use `k8s.helm.v3.Release`)
- DO NOT use git commit without `--no-gpg-sign`
- DO NOT forget to `git checkout -- .sisyphus/boulder.json` after subagent returns

---

## Step 1: Fix FluxCD GitRepository Auth for Private Repos

### Problem
`pulumi/components/flux_gitops.py` line 53-66 creates a GitRepository with NO `secretRef`. This works for public repos but fails silently for private repos — Flux source-controller can't clone.

### Changes

**File: `pulumi/components/flux_gitops.py`**

1. After the `wait_flux` block (line 50) and before the GitRepository (line 53), add a Kubernetes Secret containing the GitHub PAT:

```python
# ─── 2a. Git credentials Secret (private repo auth) ───
git_secret_depends: list[pulumi.Resource] = [wait_flux]
git_secret = None
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
    git_secret_depends.append(git_secret)
```

2. Modify the GitRepository spec to include `secretRef` when PAT is provided:

```python
# Build GitRepository spec
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
    opts=self._child_opts(provider=k8s_provider, depends_on=git_secret_depends),
)
```

### Verification
- `lsp_diagnostics` clean on `flux_gitops.py`
- Ruff lint passes

---

## Step 2: Fix Kustomization Name Mismatches

### Problem
The FluxCD component creates Kustomizations with names that don't match what the integration tests expect:

| Component creates | Test expects | Match? |
|---|---|---|
| `namespaces` | `oc-namespaces` | ❌ |
| `platform-shared` | `oc-platform-shared` | ❌ |
| `oc-demo-platform` | `oc-platform` | ❌ |
| `oc-demo-projects` | `oc-demo-projects` | ✅ |

### Decision
Fix the **component** to use names that match the test expectations. The `oc-` prefix is cleaner and avoids potential naming collisions.

### Changes

**File: `pulumi/components/flux_gitops.py`**

Update Kustomization metadata names and `dependsOn` references:

1. `kust_namespaces`: Change `name="namespaces"` → `name="oc-namespaces"`
2. `kust_platform_shared`: Change `name="platform-shared"` → `name="oc-platform-shared"`
3. `kust_platform`: Change `name="oc-demo-platform"` → `name="oc-platform"`
4. Update `dependsOn` in `kust_platform` from `[{"name": "namespaces"}, {"name": "platform-shared"}]` → `[{"name": "oc-namespaces"}, {"name": "oc-platform-shared"}]`
5. Update `dependsOn` in `kust_projects` from `[{"name": "oc-demo-platform"}]` → `[{"name": "oc-platform"}]`
6. Update `WaitCustomResourceCondition` resource_name from `"oc-demo-projects"` → `"oc-demo-projects"` (already correct)

### Verification
- Names in component match names in integration tests exactly
- `lsp_diagnostics` clean on `flux_gitops.py`

---

## Step 3: Create Minimal FluxCD Directory Structure

### Problem
FluxCD Kustomizations point to paths that don't exist in the repo:
- `./namespaces`
- `./platform-shared`
- `./namespaces/default/platform`
- `./namespaces/default/projects`

Without these, Flux reconciliation will fail with "path not found".

### Changes
Create minimal `kustomization.yaml` in each directory so Flux reconciles cleanly:

**File: `namespaces/kustomization.yaml`**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources: []
```

**File: `platform-shared/kustomization.yaml`**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources: []
```

**File: `namespaces/default/platform/kustomization.yaml`**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources: []
```

**File: `namespaces/default/projects/kustomization.yaml`**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources: []
```

### Verification
- All 4 directories exist with valid `kustomization.yaml`
- Files pushed to repo so FluxCD can reconcile

---

## Step 4: Update Stack Config

### Changes

**File: `pulumi/Pulumi.talos-baremetal.yaml`**

Add/modify these config values:
```yaml
config:
  openchoreo:enable_flux: "true"          # was "false"
  openchoreo:enable_observability: "true"  # was absent (defaults false)
  openchoreo:github_pat:
    secure: <encrypted-value>              # User provides PAT, encrypt with pulumi config set --secret
```

### Procedure
1. `cd pulumi && pulumi config set --stack talos-baremetal enable_observability true`
2. `cd pulumi && pulumi config set --stack talos-baremetal enable_flux true`
3. `cd pulumi && pulumi config set --stack talos-baremetal --secret github_pat <USER_PAT>`

### Verification
- `pulumi config --stack talos-baremetal` shows both flags true and github_pat as secret

---

## Step 5: Deploy via Pulumi

### Pre-flight Checks
1. Verify cluster health: `kubectl --context admin@openchoreo get pods -A` — expect 50 Running + 1 Completed
2. Verify existing tests still pass: all 31 current tests green

### Deploy Command
```bash
cd pulumi
PATH="/opt/homebrew/bin:$PATH" PULUMI_CONFIG_PASSPHRASE="openchoreo-talos-baremetal" \
  pulumi up --stack talos-baremetal --yes
```

### What This Deploys (net new resources)
1. **Observability Plane** (from `__main__.py` line 112-119):
   - Namespace: `openchoreo-observability-plane`
   - CA cert copy into OP namespace
   - 3 ExternalSecrets (opensearch-admin, observer-opensearch, observer-secret)
   - Helm release: `openchoreo-observability-plane` (Observer, controller-manager, cluster-agent, Gateway)
   - Helm release: `observability-logs-opensearch` (OpenSearch + Fluent Bit)
   - Helm release: `observability-traces-opensearch` (tracing)
   - Helm release: `observability-metrics-prometheus` (kube-prometheus-stack)
   - RegisterPlane: `ClusterObservabilityPlane`

2. **Link Planes** (from `__main__.py` line 122-124):
   - Patches ClusterDataPlane and ClusterWorkflowPlane with observability reference

3. **FluxCD** (from `__main__.py` line 127-133):
   - Flux controllers (source, kustomize, helm)
   - Git credentials Secret (with PAT)
   - GitRepository (with secretRef)
   - 4 Kustomizations pointing to repo directories

### Expected Deployment Time
- Observability: 20-40 minutes (OpenSearch is heavy)
- FluxCD: 3-5 minutes
- Total: ~25-45 minutes

### Expected Post-Deploy State
- ~70-80 pods total (observability adds ~20-30 pods)
- Integration test count: ~40+ (observability adds CRD + E2E tests, flux adds deployment + E2E tests)

---

## Step 6: Verify Deployment

### Automated (via integration tests)
The integration tests component already has conditional tests for observability and flux. With both flags enabled, these NEW tests will run:

**Flux tests:**
- `flux-source-controller` (deployment exists)
- `flux-kustomize-controller` (deployment exists)
- `flux-helm-controller` (deployment exists)
- `e2e-flux-kustomization-oc-namespaces` (Ready condition)
- `e2e-flux-kustomization-oc-platform-shared` (Ready condition)
- `e2e-flux-kustomization-oc-platform` (Ready condition)
- `e2e-flux-kustomization-oc-demo-projects` (Ready condition)

**Observability tests:**
- `crd-clusterobservabilityplanes` (CRD exists)
- `e2e-clusterobservabilityplane-exists` (Created condition)
- `e2e-obs-externalsecret-opensearch-admin-credentials` (Ready condition)
- `e2e-obs-externalsecret-observer-opensearch-credentials` (Ready condition)
- `e2e-obs-externalsecret-observer-secret` (Ready condition)

### Manual Checks
1. `kubectl --context admin@openchoreo get pods -n openchoreo-observability-plane` — all Running
2. `kubectl --context admin@openchoreo get pods -n flux-system` — 3 controllers Running
3. `kubectl --context admin@openchoreo get gitrepositories -n flux-system` — Ready=True
4. `kubectl --context admin@openchoreo get kustomizations -n flux-system` — all Ready=True

---

## Known Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| R1: OpenSearch takes 20+ min to start | Slow deploy, possible timeout | TIMEOUT_OPENSEARCH=1800s and TIMEOUT_OBS_PLANE=2400s already configured |
| R2: ExternalSecret API version mismatch (component uses `v1`, test checks `v1beta1`) | Test might fail | Kubernetes serves both versions — should work. If not, fix test to use `v1` |
| R3: FluxCD directories not pushed to remote before `pulumi up` | Flux reconciliation fails with "path not found" | Step 3 (create dirs) + commit/push MUST happen before Step 5 (deploy) |
| R4: OpenBao `observer-oauth-client-secret` not accessible | Observer ExternalSecret fails to sync | Already seeded by `values/openbao.py` — verified in codebase |
| R5: Single-node Talos may lack resources for full observability stack | Pods stuck Pending on memory/CPU | Monitor with `kubectl top nodes`. Can reduce OpenSearch replicas if needed |

---

## Execution Order

```
Step 1: Fix FluxCD GitRepository auth     (code change)
Step 2: Fix Kustomization name mismatches  (code change)
Step 3: Create FluxCD directories          (repo structure)
   ↓ commit + push Steps 1-3 to remote
Step 4: Update stack config                (pulumi config)
Step 5: Deploy via pulumi up               (deploy)
Step 6: Verify deployment                  (validation)
```

**Critical ordering**: Steps 1-3 must be committed and pushed to remote BEFORE Step 5, because FluxCD will try to clone the repo and read those directories immediately.
