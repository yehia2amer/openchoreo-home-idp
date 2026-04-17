# OpenChoreo GKE Deployment — Discoveries Report

## Executive Summary

This report documents 39 discoveries made during the OpenChoreo GKE deployment sessions. The discoveries span six categories: Flux/GitOps behavior, authentication and secrets management, container registry and build pipelines, Kubernetes storage, OpenChoreo platform internals, and GCP-specific constraints. Many discoveries reveal fundamental differences between baremetal and cloud deployments that aren't obvious from documentation alone. The most critical findings involve FluxCD's hook execution model, Thunder's signing key persistence requirement, and Podman 5.x's strict dockerconfigjson format. Together, these discoveries form a practical knowledge base for anyone deploying OpenChoreo on GKE.

---

## Summary Table

| Category | Discoveries | Critical |
|---|---|---|
| Flux/GitOps | 7 | 3 |
| Authentication / Secrets | 7 | 4 |
| Registry / Builds | 9 | 3 |
| Kubernetes / Storage | 4 | 2 |
| OpenChoreo Platform | 7 | 2 |
| GCP-Specific | 2 | 1 |
| **Total** | **39** | **18** |

---

## Category 1: Flux/GitOps

### Discovery 1: FluxCD Doesn't Execute Helm Hooks

**Root Cause**: Flux applies Helm releases via template rendering, skipping hook-only resources. The Thunder bootstrap Job never runs because Flux never invokes the hook lifecycle.

**Fix Applied**: Added an initContainer workaround to the Thunder deployment that runs bootstrap logic before the main container starts.

**Files Modified**: Thunder deployment manifest.

**Lesson Learned**: Any Helm chart relying on hooks needs alternative bootstrap mechanisms when deployed via FluxCD. Hooks are a Helm-native concept that Flux deliberately bypasses.

---

### Discovery 3: Flux `${}` Escaping Breaks Shell Scripts in ConfigMaps

**Root Cause**: Flux envsubst processes ALL string values, including shell scripts embedded in ConfigMaps. Using `${VAR}` in shell scripts conflicts with Flux substitution. The `$${}` escape syntax breaks when the script actually needs shell variable expansion.

**Fix Applied**: Changed shell scripts to use `$VAR` instead of `${VAR}` format to avoid Flux envsubst interference.

**Files Modified**: ConfigMaps containing shell scripts managed by Flux.

**Lesson Learned**: Never use `${VAR}` syntax in shell scripts inside Flux-managed ConfigMaps. Use `$VAR` for shell variables. Flux owns the `${}` namespace.

---

### Discovery 9: Catalog Empty Because `namespaces/` Directory Not Synced by Flux on GKE

**Root Cause**: The GKE cluster was missing the Flux Kustomization that syncs the `namespaces/` directory, so no Components, Projects, or Environments were being applied.

**Fix Applied**: Created `clusters/gke/06-namespaces.yaml` with kustomizations for namespaces, platform-shared, platform, and projects.

**Files Modified**: `clusters/gke/06-namespaces.yaml`

**Lesson Learned**: Each cluster needs explicit Flux kustomization wiring for all directory paths. Don't assume cross-cluster consistency — what's wired on baremetal may not exist on GKE.

---

### Discovery 10: OpenChoreo CEL Expressions Break Flux envsubst

**Root Cause**: OpenChoreo CRDs use `${metadata.name}`, `${environmentConfigs.storageClass}` CEL syntax which conflicts with Flux envsubst's `${}` syntax.

**Fix Applied**: Originally: no `postBuild` on namespace kustomizations. Updated in Discovery 36: CEL expressions use dotted paths (`metadata.name`, `environmentConfigs.X`) which are NOT valid env var names, so `postBuild` with `strict: false` safely ignores them.

**Files Modified**: Namespace kustomization files.

**Lesson Learned**: Flux envsubst with `strict: false` ONLY substitutes patterns matching valid env var names `[A-Za-z_][A-Za-z0-9_]*`. CEL dotted paths are safe because they contain dots, which aren't valid in env var names.

---

### Discovery 13: `observability-cloud` Component Blocks wave-03-platform Reconciliation

**Root Cause**: Odigos CRDs required by the observability-cloud component weren't installed yet when wave-03 tried to reconcile, causing the entire wave to fail.

**Fix Applied**: Split Odigos into wave-03b (actions) and wave-03c (CRs) with proper dependency ordering.

**Files Modified**: Wave ordering configuration files.

**Lesson Learned**: CRD dependencies require careful wave ordering. Components that depend on CRDs from optional operators need their own reconciliation waves to avoid blocking core platform components.

---

### Discovery 20: Flux Cascade Is Healthy (Transient False Readings)

**Root Cause**: Flux kustomization status sometimes shows transient errors during reconciliation cycles. These resolve within 1-2 minutes.

**Fix Applied**: Wait for reconciliation to complete before concluding there's an issue.

**Files Modified**: None.

**Lesson Learned**: Flux status is eventually consistent. Always check status twice with a gap before raising alarms. A single snapshot of Flux status is not reliable.

---

### Discovery 27: `registry-cloud` Component Is GKE-Only

**Root Cause**: The `registry-cloud` component in `infrastructure/components/` is only included by the GKE platform kustomization, not baremetal.

**Fix Applied**: Safe to add GKE-specific resources here without affecting baremetal.

**Files Modified**: `infrastructure/components/registry-cloud/` (new files).

**Lesson Learned**: Use platform-specific component directories for environment-specific resources. The kustomization include/exclude pattern is the right way to handle environment divergence.

---

## Category 2: Authentication / Secrets

### Discovery 2: Thunder OAuth Apps Require Explicit `user_attributes` and `scope_claims`

**Root Cause**: Thunder OAuth application config must include `user_attributes` and `scope_claims` fields or authentication fails silently. There's no error message — the flow just doesn't work.

**Fix Applied**: Added explicit `user_attributes: ["email", "name"]` and `scope_claims: ["openid", "profile", "email"]` to the Thunder OAuth app configuration.

**Files Modified**: Thunder OAuth application configuration.

**Lesson Learned**: Thunder OAuth is strict about attribute/claim declarations. Defaults don't cover common OIDC flows. Always declare these fields explicitly.

---

### Discovery 4: Client Secret Mismatch Between `backstage-secrets` and Thunder

**Root Cause**: The Backstage OAuth client secret in `backstage-secrets` didn't match what Thunder expected, causing authentication failures.

**Fix Applied**: Ensured both secrets reference the same GCP Secret Manager key via ESO ExternalSecrets.

**Files Modified**: ExternalSecret manifests for Backstage and Thunder.

**Lesson Learned**: Shared secrets must come from a single source of truth (GCP Secret Manager) via ESO, not be duplicated. Duplication guarantees eventual drift.

---

### Discovery 6: Backstage Auth Handler Profile Extraction Logic

**Root Cause**: Backstage OIDC auth handler expects specific profile fields from the identity provider. The extraction logic location varies by auth provider module.

**Fix Applied**: Configured Thunder to return the expected profile fields in the OIDC token claims.

**Files Modified**: Thunder OIDC configuration.

**Lesson Learned**: When integrating custom auth providers with Backstage, verify the profile extraction logic matches the identity provider's claim structure. Mismatches produce confusing partial-auth failures.

---

### Discovery 7: Backstage Empty Catalog / 401 When Thunder Restarts

**Root Cause**: Thunder generates new signing keys on restart, invalidating existing JWT tokens. Backstage backend continues using cached tokens which now fail validation.

**Fix Applied**: Ensured Thunder signing keys persist across restarts via persistent storage configuration.

**Files Modified**: Thunder deployment and storage configuration.

**Lesson Learned**: Auth server signing keys MUST be persisted. Ephemeral keys cause cascading auth failures across all dependent services. This is a critical production concern.

---

### Discovery 24: `gitops-token` Secret Was Missing from GCP Secret Manager

**Root Cause**: The `gitops-token` Secret referenced by ExternalSecret didn't exist in GCP Secret Manager.

**Fix Applied**: User created it in GCP SM. Agent updated to JSON format v2 (`{"git-token": "ghp_..."}`).

**Files Modified**: GCP Secret Manager (manual), ExternalSecret template.

**Lesson Learned**: Verify ALL secrets exist in the external secret store before deploying ExternalSecrets. Missing secrets cause silent failures that are hard to trace.

---

### Discovery 30: `gitops-token` Must Be JSON Format

**Root Cause**: ESO ExternalSecret expects `{"git-token": "ghp_..."}` format in GCP Secret Manager. A plain text value causes extraction failure.

**Fix Applied**: User recreated the secret as version 2 with proper JSON format.

**Files Modified**: GCP Secret Manager (manual).

**Lesson Learned**: Always verify the expected format of secrets in the ExternalSecret template before creating them in the secret store. The format is defined by the `remoteRef.property` field in the ExternalSecret spec.

---

### Discovery 31: Auth Host Key Mismatch

**Root Cause**: The Podman auth config keyed credentials under `ARTIFACT_REGISTRY_URL` (full path including project), but Podman looks up auth by HOST only (`europe-west1-docker.pkg.dev`).

**Fix Applied**: Added `ARTIFACT_REGISTRY_HOST: "europe-west1-docker.pkg.dev"` cluster-var and updated ESO templates to use it as the auth key.

**Files Modified**: Cluster vars, ESO templates for registry auth.

**Lesson Learned**: Container registry auth is keyed by HOST, not full URL. Always use the bare host for dockerconfigjson auth entries. This is a subtle but fatal misconfiguration.

---

## Category 3: Registry / Builds

### Discovery 11: Doclet Services ImagePullBackOff — Registry Architecture Differences

**Root Cause**: Baremetal uses an in-cluster Zot registry (`registry.openchoreo-workflow-plane.svc.cluster.local:5000`). GKE needs Google Artifact Registry (`europe-west1-docker.pkg.dev`). ComponentRelease files had hardcoded Zot URLs from baremetal seed data.

**Fix Applied**: Deleted stale ComponentRelease files, re-triggered builds targeting AR via WorkflowRuns.

**Files Modified**: ComponentRelease files for all doclet components.

**Lesson Learned**: Registry architecture is fundamentally different between baremetal and cloud. Image URLs in ComponentRelease files must match the target registry. Seed data from one environment is not portable.

---

### Discovery 14: Doclet ComponentRelease Files Had Hardcoded Zot Image URLs from Seed Data

**Root Cause**: ComponentRelease files generated from baremetal seed data contained `192.168.0.100:30082/doclet-*` image references that don't exist on GKE.

**Fix Applied**: Deleted stale release files and their ReleaseBindings, triggered fresh builds via WorkflowRuns.

**Files Modified**: ComponentRelease and ReleaseBinding files for doclet components.

**Lesson Learned**: Seed data from one environment must not be blindly applied to another. Registry-specific values need to be regenerated per environment.

---

### Discovery 22: WorkflowRun CR Structure

**Root Cause**: N/A — documentation discovery. Verified the correct structure from baremetal's `frontend-bootstrap` WorkflowRun.

**Fix Applied**: Used the verified structure as a template for GKE WorkflowRun CRs.

**Files Modified**: New WorkflowRun CRs in the gitops repo.

**Lesson Learned**: Always reference working examples from other environments when creating new CRs. Don't guess at CR structure from the CRD spec alone.

---

### Discovery 23: Three Blockers Before WorkflowRuns Can Succeed on GKE

**Root Cause**: Three prerequisites were missing: (1) AR push credentials ExternalSecret, (2) `workflow-sa` ServiceAccount, (3) `gitops-token` Secret.

**Fix Applied**: Created all three resources in the gitops repo under `infrastructure/components/registry-cloud/`.

**Files Modified**: `infrastructure/components/registry-cloud/` (multiple new files).

**Lesson Learned**: Build pipelines have multiple credential dependencies. Map out the full credential chain before triggering builds. Missing any single link causes the entire pipeline to fail.

---

### Discovery 25: CWT Architecture — Shared vs Inline Push

**Root Cause**: N/A — documentation discovery. `docker-with-gitops-release-template.yaml` is the ClusterWorkflowTemplate used by doclet builds. It has distinct build, push, and git-release steps.

**Fix Applied**: Used this CWT as-is for GKE builds.

**Files Modified**: None.

**Lesson Learned**: Understand the CWT architecture before modifying build pipelines. Changes to shared templates affect all components that reference them.

---

### Discovery 26: Workflow CR `resources` Section Creates Per-Run Secrets (ExternalSecrets)

**Root Cause**: Each Workflow CR's `resources` section generates ExternalSecrets that create per-run K8s secrets in the workflow namespace.

**Fix Applied**: Ensured ExternalSecrets reference correct GCP Secret Manager keys.

**Files Modified**: WorkflowRun CR templates.

**Lesson Learned**: OpenChoreo's resource generation creates a dependency chain: GCP SM → ESO → K8s Secret → Workflow Pod. Each link must be verified independently.

---

### Discovery 29: Backward-Compatible Auth Pattern — CWT `push-image` Uses Optional Auth

**Root Cause**: The CWT's push-image step uses `optional: true` for auth file mounting, allowing it to work with or without registry credentials.

**Fix Applied**: No change needed — the pattern is already backward-compatible.

**Files Modified**: None.

**Lesson Learned**: Well-designed shared templates use optional mounts for environment-specific features. This pattern allows the same CWT to work across baremetal (no AR auth) and GKE (AR auth required).

---

### Discovery 32: Podman 5.x Rejects `username`/`password` Format in dockerconfigjson

**Root Cause**: Podman 5.2.5 treats the `username`/`password` format in dockerconfigjson as an "empty credential entry" and falls back to anonymous push. Only the `auth` field format (base64-encoded `_json_key:<sa-key-json>`) works.

**Fix Applied**: Changed ESO template from `"username": "_json_key", "password": ...` to `"auth": "{{ printf "_json_key:%s" .sa_key | b64enc }}"` using ESO's sprig `b64enc` template function.

**Files Modified**: ESO template for AR push credentials.

**Lesson Learned**: Always use the `auth` field (base64-encoded) in dockerconfigjson, never `username`/`password` separately. Podman and Docker handle these differently, and Podman 5.x is strict.

---

### Discovery 34: Test Image Successfully Pushed to AR

**Root Cause**: Confirmed Artifact Registry working end-to-end from inside GKE pods using the SA key.

**Fix Applied**: No fix needed — validation test.

**Files Modified**: None.

**Lesson Learned**: Use test pushes to validate registry auth independently of the build pipeline. Isolating the auth test from the full pipeline makes debugging much faster.

---

### Discovery 35: Uppercase `HEAD` in ComponentRelease Names Violates RFC 1123

**Root Cause**: WorkflowRuns used `commit: HEAD` (literal string), causing generated resource names like `frontend-HEAD`. Kubernetes requires lowercase names per RFC 1123.

**Fix Applied**: Lowercased all `HEAD` → `head` in 6 files (3 ComponentRelease + 3 ReleaseBinding).

**Files Modified**: 3 ComponentRelease files, 3 ReleaseBinding files.

**Lesson Learned**: Always lowercase any user-provided values that become part of Kubernetes resource names. RFC 1123 compliance is non-negotiable and Kubernetes will reject non-compliant names.

---

## Category 4: Kubernetes / Storage

### Discovery 8: Plane Agent CA Distribution

**Root Cause**: Plane agents (data, workflow, observability) had x509 certificate errors because they were using a placeholder CA certificate instead of the actual cluster CA.

**Fix Applied**: Configured CA distribution through the platform's certificate management to propagate the correct CA to all plane agent namespaces.

**Files Modified**: Certificate management configuration.

**Lesson Learned**: Plane agents need the cluster's actual CA certificate, not placeholders. CA distribution must be part of the platform bootstrap sequence.

---

### Discovery 15: Doclet Pods Deploy to Dynamic Namespaces

**Root Cause**: OpenChoreo creates namespaces with a hash suffix (e.g., `dp-default-doclet-development-50ce4d9b`) based on the dataplane, project, and environment combination.

**Fix Applied**: No fix needed — this is by design. Used `kubectl get pods --all-namespaces | grep doclet` to find resources.

**Files Modified**: None.

**Lesson Learned**: When debugging OpenChoreo workloads, search across all namespaces. Don't assume static namespace names. The hash suffix is deterministic but not human-readable.

---

### Discovery 28: `workflow-sa` ServiceAccount Never Explicitly Created

**Root Cause**: The `workflow-sa` ServiceAccount referenced by WorkflowRuns didn't exist in the workflow namespace. On baremetal, it was presumably created by the Argo controller or another mechanism.

**Fix Applied**: Created explicit `workflow-sa` YAML files in the gitops repo.

**Files Modified**: New ServiceAccount manifests in `infrastructure/components/registry-cloud/`.

**Lesson Learned**: Don't assume ServiceAccounts exist. Explicitly declare them in GitOps. Implicit creation by controllers is not reliable across environments.

---

### Discovery 36: Postgres PVC Requests StorageClass `longhorn` Which Doesn't Exist on GKE

**Root Cause**: PVC `postgres-development-1e5b3b43-data-storage` requests `storageClassName: longhorn`. GKE has `standard-rwo` (default), not longhorn. The value originates from `persistent-volume.yaml` trait and embedded copies in ComponentRelease files.

**Fix Applied**: In progress — templatizing with `${DEFAULT_STORAGE_CLASS}` cluster-var. Requires `postBuild` with `strict: false` on namespace kustomizations, which is safe because CEL expressions use dotted paths that aren't valid env var names.

**Files Modified**: `persistent-volume.yaml` trait, ComponentRelease files, cluster vars.

**Lesson Learned**: Storage provisioner names are environment-specific. Never hardcode them — templatize with cluster-vars. `longhorn` is a baremetal-only storage class.

---

## Category 5: OpenChoreo Platform

### Discovery 16: No WorkflowRuns Triggered Despite `autoBuild: true`

**Root Cause**: The `autoBuild: true` flag on Components was expected to create WorkflowRuns automatically, but no runs were generated.

**Fix Applied**: This was a misunderstanding — see Discovery 21 for the full explanation.

**Files Modified**: None.

**Lesson Learned**: Read the controller source code or docs before assuming behavior from field names. `autoBuild` does not mean what it sounds like in a GitOps context.

---

### Discovery 17: Component CRs DO Exist — Previous Label Query Was Wrong

**Root Cause**: Earlier debugging queried Components with wrong label selectors, leading to the false conclusion that Components weren't synced.

**Fix Applied**: Used correct label selectors and found all Components present.

**Files Modified**: None.

**Lesson Learned**: Always verify query results with multiple approaches before concluding resources are missing. A failed query is not proof of absence.

---

### Discovery 18: ReleaseBindings Still Existed, Blocking WorkflowRun Creation

**Root Cause**: Old ReleaseBinding files from a prior session remained in the gitops repo, which blocked new WorkflowRun creation for the same components.

**Fix Applied**: Deleted stale ReleaseBinding files from the gitops repo.

**Files Modified**: Stale ReleaseBinding files (deleted).

**Lesson Learned**: Old release bindings can interfere with new builds. Clean up stale bindings before triggering new workflows. GitOps repos accumulate state that must be actively managed.

---

### Discovery 19: wave-03b/03c Odigos Split Still Has Issues (Non-Blocking)

**Root Cause**: The Odigos CRD/operator split into separate waves has occasional reconciliation timing issues.

**Fix Applied**: Non-blocking — Odigos is optional for the core platform.

**Files Modified**: None.

**Lesson Learned**: Optional components should have graceful degradation. Don't let optional features block core platform functionality. Mark optional components clearly in the wave ordering.

---

### Discovery 21: `autoBuild: true` Does NOT Trigger WorkflowRuns During Reconciliation

**Root Cause**: The OpenChoreo controller NEVER creates WorkflowRuns from its reconciliation loop. The `-bootstrap` WorkflowRuns on baremetal were created manually via Backstage UI or OpenChoreo API, not automatically.

**Fix Applied**: Created WorkflowRun CRs manually in the gitops repo for each doclet component.

**Files Modified**: New WorkflowRun CRs for all doclet components.

**Lesson Learned**: `autoBuild` is likely for future implementation or requires the API/UI trigger. Don't rely on it for GitOps-only deployments. Manual WorkflowRun CRs are the correct GitOps approach.

---

### Discovery 33: IAM Confirmed — `roles/artifactregistry.repoAdmin` Present

**Root Cause**: Verified that SA `openchoreo-ar-push@pg-ae-n-app-173978.iam.gserviceaccount.com` has `roles/artifactregistry.repoAdmin` at project level.

**Fix Applied**: No fix needed — confirmed correct permissions.

**Files Modified**: None.

**Lesson Learned**: Always verify IAM bindings independently before debugging application-level auth issues. Confirming IAM early eliminates an entire class of potential problems.

---

## Category 6: GCP-Specific

### Discovery 5: Playwright `type=password` Not a Textbox

**Root Cause**: `page.getByRole("textbox")` doesn't match `<input type="password">` in Playwright. Password fields have role "textbox" only if explicitly set.

**Fix Applied**: Used `page.locator("#password")` CSS selector instead of role-based selector.

**Files Modified**: Playwright test files.

**Lesson Learned**: For password fields in Playwright, use CSS selectors or `getByLabel()` — not `getByRole("textbox")`. The ARIA role for password inputs is not "textbox" by default.

---

### Discovery 12: PwC GCP Org Policy Blocks SA Key Creation and IAM Bindings

**Root Cause**: GCP organization policies `constraints/iam.disableServiceAccountKeyCreation` prevent creating SA keys via API/CLI. IAM role grants are also restricted.

**Fix Applied**: Added `skip_sa_key_creation: true` and `skip_iam_bindings: true` to Pulumi stack config. Created comprehensive guide at `docs/gcp-org-policy-guide.md`.

**Files Modified**: Pulumi stack config, `docs/gcp-org-policy-guide.md` (new).

**Lesson Learned**: Enterprise GCP environments often have org policies that block common automation. Always check org policies BEFORE designing the IAM strategy. Discovering this late causes significant rework.

---

### Discovery 37: CEL Curly Braces Break Flux envsubst — EVERYWHERE

**Category**: Architecture / Flux

**Severity**: CRITICAL

**Impact**: ALL OpenChoreo resources

**Root Cause**: Flux `postBuild` envsubst is FUNDAMENTALLY INCOMPATIBLE with ALL OpenChoreo resources. CEL expressions containing curly braces `{}` inside `${...}` break Flux envsubst even with `strict: false`. This affects ComponentType files (e.g., `database.yaml` with `${envConfig.envs.transformMapEntry(index, env, {env.name: env.value})}`), and ALL ComponentRelease files which contain CEL like `${oc_merge(metadata.labels, {"openchoreo.dev/endpoint-name": endpoint})}`. Simple dotted paths like `${metadata.name}` are safe since Flux ignores them.

**Architecture Rule**: `postBuild` with `substituteFrom` MUST NEVER be added to any Flux Kustomization that applies OpenChoreo CRD resources (ComponentTypes, ComponentReleases, etc.). Use cluster-specific file paths instead.

**Lesson Learned**: CEL and Flux envsubst both use `${...}` syntax. Flux tries to substitute CEL expressions and fails. There is no workaround — the two systems are fundamentally incompatible when CEL expressions contain curly braces.

---

### Discovery 38: Cluster-Specific Project Paths Architecture

**Category**: Architecture / Multi-Cluster

**Severity**: HIGH

**Impact**: Multi-cluster GitOps pattern

**Root Cause**: Generated OpenChoreo release artifacts (ComponentRelease, ReleaseBinding) should be treated as cluster-specific, not shared. They already differ by cluster (registry URLs, storage classes, resource limits).

**Fix Applied**: The correct multi-cluster pattern is to use cluster-specific project directories: GKE uses `clusters/gke/projects/` containing only GKE-deployed projects, while baremetal uses `namespaces/default/projects/` containing all projects. Each cluster's `oc-demo-projects` Kustomization points to its own path.

**Files Modified**: Cluster-specific project directory structure.

**Lesson Learned**: This avoids the impossible envsubst problem (Discovery 37) and cleanly separates cluster concerns. Don't try to share OpenChoreo release artifacts across clusters — generate them per cluster.

---

### Discovery 39: RenderedRelease Caching on ComponentRelease Trait Changes

**Category**: OpenChoreo Controller / Debugging

**Severity**: HIGH

**Impact**: Any ComponentRelease trait change (e.g., storageClass)

**Root Cause**: When a ComponentRelease with immutable `spec.traits` is deleted and recreated with different trait values (e.g., changing storageClass default from `longhorn` to `standard-rwo`), the OpenChoreo controller's RenderedRelease is NOT automatically re-rendered. The stale RenderedRelease continues to use old values, causing PVCs to be created with the old storageClass. Additionally, there's a race condition: if the PVC and ComponentRelease are deleted simultaneously, the controller may recreate the PVC from the stale RenderedRelease BEFORE Flux recreates the ComponentRelease.

**Fix Applied**: Delete the stale RenderedRelease (and any PVCs it created), then the controller re-renders from the updated ComponentRelease with correct values.

**Files Modified**: None (operational fix).

**Lesson Learned**: `spec.traits` on ComponentRelease CRDs is immutable — you cannot patch it, you must delete and recreate. After recreating, also delete the stale RenderedRelease to force re-rendering. Watch for the race condition where the controller recreates resources from stale state before Flux applies the updated manifests.

---

## Recommendations

### For New GKE Deployments

1. **Audit org policies first.** Before writing any Pulumi or Terraform, run `gcloud org-policies list` and identify constraints on SA key creation, IAM bindings, and network policies. Design around them from the start.

2. **Never copy seed data between environments.** ComponentRelease files, ReleaseBindings, and any resource containing image URLs or storage class names must be regenerated per environment. Baremetal seed data will break GKE deployments.

3. **Persist auth server signing keys.** Thunder (and any OIDC provider) must have persistent storage for signing keys. Ephemeral keys cause cascading failures that are hard to diagnose.

4. **Map the full credential chain before triggering builds.** For each build pipeline, trace: GCP SM secret → ESO ExternalSecret → K8s Secret → Pod mount. Verify each link exists before triggering a WorkflowRun.

5. **Use `auth` field in dockerconfigjson, not `username`/`password`.** Podman 5.x silently falls back to anonymous push with the split format. Always base64-encode `_json_key:<sa-key-json>` into the `auth` field.

### For Flux/GitOps Management

6. **Never use `${VAR}` in shell scripts inside ConfigMaps.** Use `$VAR` instead. Flux owns the `${}` namespace.

7. **Use `strict: false` on namespace kustomizations.** CEL expressions with dotted paths are safe from envsubst substitution. This allows cluster-var templating to work alongside OpenChoreo CRDs.

8. **Wire all directory paths explicitly per cluster.** Don't assume a Flux kustomization exists because it exists on another cluster. Each cluster's `clusters/<name>/` directory must explicitly wire every path it needs.

### For OpenChoreo Operations

9. **Create WorkflowRun CRs manually in GitOps.** `autoBuild: true` does not trigger builds during reconciliation. Treat WorkflowRuns as first-class GitOps resources.

10. **Search all namespaces when debugging workloads.** OpenChoreo generates namespaces with hash suffixes. `kubectl get pods --all-namespaces | grep <component>` is the reliable way to find resources.

11. **Lowercase all values that become resource names.** RFC 1123 requires lowercase. `HEAD`, environment names, and any user-provided strings that flow into resource names must be lowercased explicitly.

12. **Templatize storage class names with cluster-vars.** `longhorn` is baremetal-only. Use `${DEFAULT_STORAGE_CLASS}` and set it per cluster.

---

*Report generated from 39 discoveries across OpenChoreo GKE deployment sessions. Last updated: April 2026.*
