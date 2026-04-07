# ADR-002: UI-to-GitOps Sync Gap — OpenChoreo Resources Not Persisted in Git

**Status**: Proposed  
**Date**: 2026-04-08  
**Deciders**: Yehia Amer  
**Context**: Cluster audit (epic 1gz) revealed resources created via Backstage UI exist only in the cluster, not in the FluxCD gitops repository

---

## Context

When users create Projects, Components, or ComponentTypes via the OpenChoreo Backstage UI, the API writes directly to the Kubernetes API (`s.k8sClient.Create(ctx, resource)`). These resources are invisible to FluxCD and will be **lost on cluster rebuild**.

### The Problem

| Symptom | Impact |
|---------|--------|
| UI-created resources not in git | Lost on cluster reprovisioning |
| No audit trail for UI changes | Cannot track who created what or when |
| FluxCD gitops repo is incomplete | Repo does not represent full cluster state |
| Two operational modes coexist silently | Users don't know their resources aren't durable |

### How Resources Are Created Today

```
Backstage UI → REST API → service.Create() → s.k8sClient.Create(ctx, resource)
                                                       ↓
                                              Kubernetes API (only)
                                                       ↓
                                              ❌ No git commit
```

### Historical Context

- OpenChoreo v0.x had a `GitCommitRequest` CRD for writing files back to git
- Removed in v1.0.0 (PR #2297) with no replacement
- The `occ` CLI writes rendered YAML to local filesystem, intended for manual git commit
- OpenChoreo proposal 0159 considered "GitOps with Secondary Repository" but **rejected** it
- Proposal 0482 (modular architecture) states: "No built-in GitOps (external GitOps can be plugged in)"
- All controllers (project, component, componenttype, releasebinding, renderedrelease) write only to K8s API — none write to git

---

## Options Evaluated

### Option A: Syngit Operator (Adopt External Tool)

[syngit-org/syngit](https://github.com/syngit-org/syngit) — K8s operator that intercepts resource operations via webhook and pushes to git.

**How it works**: A `RemoteSyncer` CRD defines which resources to watch and which git repo to push to. Uses `CommitApply` strategy (push to git, then apply to cluster) or `CommitOnly`.

```yaml
apiVersion: syngit.io/v1beta4
kind: RemoteSyncer
spec:
  remoteRepository: https://github.com/yehia2amer/openchoreo-gitops.git
  defaultBranch: main
  strategy: CommitApply
  rootPath: resources/openchoreo
  scopedResources:
    rules:
    - apiGroups: ["openchoreo.dev"]
      apiVersions: ["v1alpha1"]
      resources: ["projects", "components", "componenttypes"]
      operations: ["CREATE", "UPDATE", "DELETE"]
```

| Pros | Cons |
|------|------|
| Purpose-built for this exact use case | Small community (115 stars), pre-1.0 (v0.6.0) |
| Helm chart install, no custom code | Single-org maintainer risk |
| Webhook-based = real-time sync | Requires cert-manager (already have it) |
| Supports GitHub natively | CNCF Sandbox pending, not yet accepted |
| Configurable per-resource | Webhook adds latency to every matched API call |

**Effort**: ~1 day (Helm install + RemoteSyncer config)  
**Risk**: Medium — dependency on immature project

### Option B: Custom Controller (Build)

Build a K8s controller using controller-runtime + go-git that watches OpenChoreo CRDs and commits sanitized YAML to the gitops repository.

| Pros | Cons |
|------|------|
| Full control over behavior | 2-4 weeks build time |
| No external dependency | Ongoing maintenance burden |
| Tailored YAML sanitization | Must handle git conflicts, auth, retries |
| Can match gitops repo path conventions exactly | Need to build, test, containerize, deploy |

**Effort**: 2-4 weeks  
**Risk**: Low technical risk, high time investment

### Option C: Reverse the Flow — Backstage Writes to Git First

Instead of Backstage→K8s→(missing)→Git, make Backstage→Git→(Flux)→K8s.

Modify Backstage scaffolder templates to write resource YAML to the gitops repo. Flux then applies it to the cluster. This **eliminates the write-back problem entirely**.

| Pros | Cons |
|------|------|
| Standard GitOps pattern | Requires modifying OpenChoreo API (upstream fork) |
| Git is always the source of truth | Loses instant cluster feedback (Flux reconciliation delay) |
| No additional operator needed | Users must wait for Flux sync (~30s-5m) |
| Audit trail built-in | Complex: need git auth in API, branch strategy, merge conflicts |

**Effort**: 2-3 weeks (modify OpenChoreo API service layer)  
**Risk**: High — requires maintaining upstream fork divergence

### Option D: Accept the Gap — Document and Educate

Document that UI-created resources are ephemeral experiments. Git-committed resources (via `occ` CLI or manual YAML) are the durable path. The UI is a convenience tool, not the system of record.

| Pros | Cons |
|------|------|
| Zero implementation effort | Resources still lost on rebuild |
| Matches OpenChoreo's intended model | Users will be surprised when resources vanish |
| No new moving parts | Violates GitOps principle |

**Effort**: ~2 hours (documentation)  
**Risk**: Low technical, high operational (user confusion)

### Option E: Periodic Export CronJob (kube-dump pattern)

CronJob that exports OpenChoreo CRDs to YAML files and commits to git on a schedule (e.g., every 5 minutes).

| Pros | Cons |
|------|------|
| Simple implementation | Not real-time (5min gap = data loss window) |
| No webhook overhead | Misses intermediate states |
| Can use existing `kubectl` + `git` | Noisy git history (commit per interval, not per change) |

**Effort**: ~2 days  
**Risk**: Low, but poor UX

---

## Decision

**Recommended: Option D (Accept) now, with Option A (Syngit) as a follow-up experiment.**

### Rationale

1. **OpenChoreo's design intent is clear**: The UI creates resources directly in K8s. GitOps is a separate, opt-in workflow via `occ` CLI or manual YAML. Proposals 0159 and 0482 both confirm this architecture.

2. **Our actual impact is low**: On a single bare-metal cluster, "lost on rebuild" means "lost on Talos reprovisioning" — which is a planned event where we'd re-bootstrap everything anyway. The demo app (`doclet`) is bootstrapped by Pulumi. Real workloads should use the gitops path.

3. **Syngit is the right tool but too immature today**: At 115 stars and v0.6.0, it's a bet. Worth revisiting when it hits 1.0 or gets CNCF Sandbox acceptance.

4. **Custom controller is overengineered for one bare-metal node**: 2-4 weeks for a problem that affects ~3 test resources.

### Action Items

- [ ] Document the two operational modes (UI = ephemeral, Git = durable) in the platform engineer guide
- [ ] Add a warning to the Backstage UI resource creation flow (if customizable)
- [ ] Revisit Syngit at v1.0 or when scaling to multi-cluster
- [ ] If users frequently lose resources, escalate to Option A

---

## References

- Audit findings: `docs/audit/drift-analysis.md`, `docs/audit/reconciliation-report.md`
- ADR-001 (Pulumi/FluxCD boundary): `docs/adr/001-pulumi-fluxcd-boundary.md`
- OpenChoreo API source: `docs/reference-project-docs/openchoreo/internal/openchoreo-api/`
- OpenChoreo proposal 0159 (CP/DP separation): rejected GitOps secondary repo
- OpenChoreo proposal 0482 (modular architecture): "No built-in GitOps"
- OpenChoreo CHANGELOG v1.0.0: GitCommitRequest CRD removed (PR #2297)
- Syngit: [github.com/syngit-org/syngit](https://github.com/syngit-org/syngit)
- Flux write-back (image tags only): [fluxcd.io/flux/components/image/imageupdateautomations/](https://fluxcd.io/flux/components/image/imageupdateautomations/)
