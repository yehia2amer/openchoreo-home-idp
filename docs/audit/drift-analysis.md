# Drift Analysis: Resources in Cluster but Not in Pulumi/FluxCD

> **Date:** 2026-04-07 · **Cluster:** talos-baremetal
> **Method:** Cross-reference cluster-snapshot.md against pulumi-inventory.md and fluxcd-inventory.md

## Summary

Every resource in the cluster falls into one of four ownership buckets:

| Owner | Count (namespaces) | Status |
|-------|-------------------|--------|
| Kubernetes system | 4 | Expected — `default`, `kube-*` |
| Nested Pulumi (talos-cluster-baremetal) | 2 | Expected — `cilium-secrets`, `longhorn-system` |
| Main Pulumi stack | 11 | Declared in `prerequisites.py`, `flux_gitops.py`, `odigos.py` |
| FluxCD (gitops repo) | 4 | Declared in `oc-namespaces` kustomization |
| **OpenChoreo operators** | **4** | **Runtime-generated — not in any IaC source** |

The 4 operator-created namespaces and their child resources are the primary "drift" — though they're **expected runtime behavior**, not accidental drift.

---

## Category 1: Operator-Generated Resources (Expected Runtime Drift)

These resources are created automatically by OpenChoreo operators when users create Projects, Components, and ReleaseBindings. They are **not** declared in Pulumi or FluxCD and should **not** be codified — they're the product of the platform working correctly.

### Namespaces

| Namespace | Created By | Trigger |
|-----------|-----------|---------|
| `arr-stack` | OpenChoreo controller-manager | `Project/arr-stack` CR in `default` ns |
| `dp-default-arr-stack-development-8dda33b1` | OpenChoreo data-plane agent | `ReleaseBinding/sonarr-development` |
| `dp-default-doclet-development-50ce4d9b` | OpenChoreo data-plane agent | Multiple development ReleaseBindings |
| `dp-default-doclet-staging-cba15825` | OpenChoreo data-plane agent | Staging ReleaseBindings |

### Deployments in `dp-default-*` namespaces

| Namespace | Deployment | Created By |
|-----------|-----------|-----------|
| `dp-default-arr-stack-dev…` | `sonarr-development-*` | Data plane agent (from Workload CR) |
| `dp-default-doclet-dev…` | `collab-svc-development-*` | Data plane agent |
| `dp-default-doclet-dev…` | `document-svc-development-*` | Data plane agent |
| `dp-default-doclet-dev…` | `frontend-development-*` | Data plane agent |
| `dp-default-doclet-dev…` | `nats-development-*` | Data plane agent |
| `dp-default-doclet-dev…` | `postgres-development-*` | Data plane agent |
| `dp-default-doclet-stag…` | `nats-staging-*` | Data plane agent |
| `dp-default-doclet-stag…` | `postgres-staging-*` | Data plane agent |

### HTTPRoutes in `dp-default-*` namespaces

| Namespace | HTTPRoute | Hostname |
|-----------|----------|----------|
| `dp-default-arr-stack-dev…` | `sonarr-endpoint-*` | `endpoint-1-sonarr-development-*.amernas.work` |
| `dp-default-doclet-dev…` | `document-svc-http-*` | `development-default.amernas.work` |
| `dp-default-doclet-dev…` | `frontend-http-*` | `http-frontend-development-*.amernas.work` |

### ExternalSecrets in `workflows-default`

| Name | Created By |
|------|-----------|
| `collab-svc-bootstrap-gitops-git-secret` | Workflow plane agent (for git clone in workflows) |
| `collab-svc-bootstrap-source-git-secret` | Workflow plane agent |
| `document-svc-bootstrap-gitops-git-secret` | Workflow plane agent |
| `document-svc-bootstrap-source-git-secret` | Workflow plane agent |
| `frontend-bootstrap-gitops-git-secret` | Workflow plane agent |
| `frontend-bootstrap-source-git-secret` | Workflow plane agent |

### OpenChoreo CRs in `default` namespace

These are user-created platform objects (via Backstage UI or kubectl):

| Kind | Name | Notes |
|------|------|-------|
| `Project` | `doclet` | Demo app — created by `oc-demo-projects` FluxCD kustomization |
| `Project` | `arr-stack` | Demo app — created by `oc-demo-projects` FluxCD kustomization |
| `Project` | `dfg` | **⚠️ Unknown origin** — created 4h ago, not in gitops repo |
| `Component` | `deep-agent` (arr-stack) | **⚠️ Unknown origin** — type `usecase`, created 6h ago |
| `ComponentType` | `usecase` | **⚠️ Unknown origin** — not in standard demo set |

**Action required for `dfg` and `deep-agent`:**
- These appear to be manual experiments (created via kubectl or Backstage UI)
- If intentional, codify in gitops repo under `oc-demo-projects`
- If experiments, no action needed — they'll be absent on clean rebuild

### PVs (Released/Orphaned)

20 PVs in `Released` state from completed workflow builds and old database claims:

| Category | Count | Total Size | Action |
|----------|-------|-----------|--------|
| Bootstrap workspace PVs | 6 | 12Gi | Safe to delete |
| Build workspace PVs | 6 | 24Gi | Safe to delete |
| Manual run workspace PVs | 2 | 4Gi | Safe to delete |
| Old postgres data PVs | 4 | 4Gi | Verify no data needed, then delete |
| Backstage rebrand PVs | 2 | 10Gi | Safe to delete |

**Total reclaimable: ~54Gi**

These are a byproduct of Longhorn's `Retain` reclaim policy. On a clean cluster they won't exist.

---

## Category 2: Helm Sub-Resources (Expected — Created by Charts)

These resources exist in the cluster because Helm charts create them, but they don't appear in Pulumi state directly. They are **owned by their parent Helm release** and will be recreated automatically.

### Certificates created by Helm charts

| Certificate | Namespace | Created By |
|------------|-----------|-----------|
| `cluster-gateway-ca` | `openchoreo-control-plane` | CP Helm chart |
| `cluster-gateway-tls` | `openchoreo-control-plane` | CP Helm chart |
| `controller-manager-webhook-server-cert` | `openchoreo-control-plane` | CP Helm chart |
| `cluster-agent-dataplane-tls` | `openchoreo-data-plane` | DP Helm chart |
| `openchoreo-data-plane-*-serving-cert` | `openchoreo-data-plane` | DP Helm chart |
| `cluster-agent-observabilityplane-tls` | `openchoreo-observability-plane` | OP Helm chart |
| `cluster-agent-workflowplane-tls` | `openchoreo-workflow-plane` | WP Helm chart |

**No action needed** — these are templated in the Helm charts and recreated on deploy.

### Services, ConfigMaps, RBAC created by Helm charts

All Helm chart sub-resources (Services, ConfigMaps, ServiceAccounts, Roles, etc.) are owned by their parent release and will be recreated automatically on `pulumi up`.

---

## Category 3: True Drift — Resources to Investigate

| Resource | Namespace | Likely Origin | Risk if Removed | Recommendation |
|----------|-----------|--------------|----------------|----------------|
| `Project/dfg` | `default` | Manual/experiment | ✅ Safe | Remove or codify |
| `Component/deep-agent` | `default` | Manual/experiment | ✅ Safe | Remove or codify |
| `ComponentType/usecase` | `default` | Manual/experiment | ⚠️ Check if needed | Keep if `deep-agent` stays |

---

## Category 4: Cross-Owner Interactions (Not Drift)

These resources are in the cluster and appear to be "extra" but are actually created by one IaC owner for consumption by another:

| Resource | Namespace | Declared In | Consumed By |
|----------|-----------|------------|-------------|
| `ClusterSecretStore/default` | (cluster-scoped) | Pulumi (`prerequisites.py`) | FluxCD ExternalSecrets + operator ExternalSecrets |
| `ClusterIssuer/openchoreo-ca` | (cluster-scoped) | Pulumi (`tls_setup.py`) | Helm chart cert requests |
| `ClusterIssuer/letsencrypt-dns01` | (cluster-scoped) | FluxCD (`oc-infrastructure`) | FluxCD wildcard cert |
| PushSecrets in `openbao` | `openbao` | Pulumi (`prerequisites.py`) | FluxCD ExternalSecrets pull from OpenBao |

These cross-references are **by design** — documented in `docs/adr/001-pulumi-fluxcd-boundary.md`.

---

## Clean Cluster Impact

On a fresh cluster rebuild with identical Pulumi + FluxCD config:

| What will exist | What will NOT exist |
|----------------|-------------------|
| All Pulumi resources (269) | `dfg` project and `deep-agent` component |
| All FluxCD resources | `dp-default-*` namespaces (until users create ReleaseBindings) |
| System namespaces | `arr-stack` namespace (until `oc-demo-projects` triggers bootstrap) |
| | 20 orphaned PVs |
| | `usecase` ComponentType (unless added to demo data) |
| | Workflow ExternalSecrets in `workflows-default` (until workflows run) |

**Bottom line:** The environment is well-codified. The only true drift items are `dfg`/`deep-agent` (manual experiments) and orphaned PVs (reclaimable storage).
