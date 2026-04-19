# ADR-008: Namespace-Scoped Workflows Instead of Canonical ClusterWorkflows

**Status**: Accepted  
**Date**: 2026-04-19  
**Deciders**: Yehia Amer  
**Context**: OpenChoreo canonical samples define 4 `ClusterWorkflow` resources; this deployment uses namespace-scoped `Workflow` resources instead — this is an intentional deviation, not a gap

---

## Context

The OpenChoreo canonical getting-started samples define four `ClusterWorkflow` resources for CI builds:

| Canonical Name | Build Strategy |
|---|---|
| `paketo-buildpacks-builder` | Paketo buildpacks (Cloud Native Buildpacks) |
| `gcp-buildpacks-builder` | Google Cloud Buildpacks |
| `dockerfile-builder` | Docker image build from Dockerfile |
| `ballerina-buildpack-builder` | Ballerina language buildpack |

`ClusterWorkflow` is a cluster-scoped resource — it's visible to all namespaces and requires a `ClusterWorkflowPlane` reference. The canonical samples assume a multi-namespace deployment model where workflows are shared across tenant namespaces.

### This Deployment's Model

This deployment uses a **single-namespace model**: all projects and components live in the `default` namespace. There is no multi-tenancy requirement at the namespace level.

Under this model, `ClusterWorkflow` resources add complexity without benefit:

- A `ClusterWorkflowPlane` must be created and referenced, adding an extra resource layer
- Cluster-scoped resources require cluster-admin RBAC to manage, which is heavier than namespace-scoped RBAC
- The single-namespace model doesn't need cross-namespace workflow sharing
- Namespace-scoped `Workflow` resources are simpler to deploy, audit, and iterate on

---

## Decision

**Use namespace-scoped `Workflow` resources (in the `default` namespace) instead of `ClusterWorkflow` resources.**

The four workflows implemented in `openchoreo-gitops/namespaces/default/platform/workflows/` are:

| Resource Name | File | Equivalent Canonical | Build Strategy |
|---|---|---|---|
| `docker-gitops-release` | `docker-with-gitops-release.yaml` | `dockerfile-builder` | Docker build from Dockerfile |
| `google-cloud-buildpacks-gitops-release` | `google-cloud-buildpacks-gitops-release.yaml` | `gcp-buildpacks-builder` | Google Cloud Buildpacks |
| `react-gitops-release` | `react-gitops-release.yaml` | *(no canonical equivalent)* | Specialized React web app build |
| `bulk-gitops-release` | `bulk-gitops-release.yaml` | *(no canonical equivalent)* | Bulk release for multiple components |

### Canonical Workflows Not Implemented

Two canonical workflows are intentionally absent:

- **`paketo-buildpacks-builder`** — not needed; GCP buildpacks (`google-cloud-buildpacks-gitops-release`) serve the same purpose for this deployment's target infrastructure (GKE)
- **`ballerina-buildpack-builder`** — not needed; no Ballerina workloads exist or are planned

### ComponentType References

`ComponentType` resources (service, webapp, worker, scheduled-task) reference workflows using `kind: Workflow` instead of `kind: ClusterWorkflow`:

```yaml
spec:
  allowedWorkflows:
    - kind: Workflow
      name: docker-gitops-release
```

All four `Workflow` resources carry the `openchoreo.dev/workflow-type: "component"` label for CI governance and controller filtering.

---

## Consequences

### Positive

- **Simpler deployment** — No `ClusterWorkflowPlane` resource required; namespace-scoped RBAC is sufficient
- **Easier iteration** — Namespace-scoped resources can be updated without cluster-admin access
- **Tailored workflow set** — The implemented workflows match actual workload types (Docker, GCP buildpacks, React, bulk release) rather than the generic canonical set
- **Consistent labeling** — `openchoreo.dev/workflow-type: "component"` is applied uniformly across all workflows

### Negative

- **Deviation from canonical samples** — Operators familiar with the canonical getting-started guide won't find the expected `ClusterWorkflow` names; this ADR serves as the reference
- **No cross-namespace sharing** — If multi-namespace support is added later, each namespace would need its own copy of the workflows until they're promoted to `ClusterWorkflow` scope

### Risks

- **Multi-namespace migration** — If the deployment model expands to multiple namespaces, all `Workflow` resources must be promoted to `ClusterWorkflow` scope and `ComponentType` references updated accordingly
- **Canonical drift** — If upstream OpenChoreo adds new canonical workflows, they won't automatically appear here; periodic review against canonical samples is needed

---

## Alternatives Considered

### 1. Implement All 4 Canonical ClusterWorkflows

Create `ClusterWorkflow` resources matching the canonical names exactly.

**Rejected because**:
- Requires a `ClusterWorkflowPlane` resource and cluster-admin RBAC for management
- `paketo-buildpacks-builder` and `ballerina-buildpack-builder` have no corresponding workloads; they'd be dead resources
- The single-namespace model gains nothing from cluster-scoped resources

### 2. Namespace-Scoped Workflows with Canonical Names

Use `kind: Workflow` but keep the canonical names (`dockerfile-builder`, `gcp-buildpacks-builder`, etc.).

**Rejected because**:
- The implemented workflows include GitOps release steps not present in the canonical CI-only samples; the names would be misleading
- Descriptive names (`docker-gitops-release`, `google-cloud-buildpacks-gitops-release`) better communicate the full build-and-release scope of each workflow

---

## Future Work

- **Multi-namespace expansion** — If multi-tenancy is introduced, promote `Workflow` resources to `ClusterWorkflow` scope and update all `ComponentType` `allowedWorkflows` references
- **Paketo buildpacks** — If workloads requiring Paketo buildpacks are added, implement a `paketo-gitops-release` workflow following the same namespace-scoped pattern
- **Ballerina support** — If Ballerina workloads are introduced, implement a `ballerina-gitops-release` workflow
