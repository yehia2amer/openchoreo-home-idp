# ADR-001: Pulumi/FluxCD Boundary — Bootstrap vs. GitOps

**Status**: Accepted  
**Date**: 2026-04-06  
**Deciders**: Yehia Amer  
**Context**: DNS Epic (sf8) planning revealed architectural tension between Pulumi and FluxCD ownership

---

## Context

The project uses both Pulumi and FluxCD, but with unclear boundaries. Pulumi currently manages ~65% of K8s resources that are purely declarative (Helm charts, HTTPRoutes, ExternalSecrets, Certificates) — work that FluxCD is purpose-built to handle. This means every infrastructure change requires `pulumi up` instead of `git push`, defeating the GitOps model.

### The Problem

| Symptom | Impact |
|---------|--------|
| 14 Helm charts deployed via `pulumi up` | No auto-reconciliation, manual intervention required |
| HTTPRoutes/ExternalSecrets in Pulumi Python code | Changes require Python knowledge + Pulumi CLI access |
| New DNS epic (sf8) would add 5+ more Pulumi components | Deepens the wrong pattern |
| No FluxCD Kustomization for infrastructure | FluxCD only manages OpenChoreo CRDs, not platform infra |

### Current State

```
Pulumi manages:
├── Bootstrap (CNI, CRDs, OpenBao, FluxCD install)     ← Necessary
├── Imperative ops (secret seeding, plane registration) ← Necessary
└── 40+ declarative K8s resources + 14 Helm charts      ← Should be FluxCD

FluxCD manages:
└── OpenChoreo CRDs (Projects, Components, Workloads)   ← Correct but insufficient
```

## Decision

**Adopt a clear boundary: Pulumi bootstraps, FluxCD reconciles.**

All NEW infrastructure resources go into FluxCD as GitOps manifests. Pulumi is restricted to genuinely imperative operations that FluxCD cannot perform.

### Boundary Rules

**Pulumi owns** (run once, bootstrap):
1. Cilium CNI + Gateway API CRDs (chicken-and-egg: pods need CNI to run)
2. cert-manager + ESO + kgateway CRD installation
3. OpenBao Helm chart + secret policy seeding (`kubectl exec` into pod)
4. FluxCD controller installation + initial Kustomization bootstrap
5. Plane registration API calls (HTTP POST to OpenChoreo API)
6. CopyCA cross-namespace secret propagation
7. Talos machine config patches (cloudflared, keepalived if Talos extension)
8. Platform-specific conditional logic (k3d vs Talos vs bare-metal)

**FluxCD owns** (ongoing reconciliation via `git push`):
1. All HelmRelease CRs (new infrastructure Helm charts)
2. All HTTPRoute / Gateway / ReferenceGrant CRs
3. All ExternalSecret CRs (declarative secret sync from OpenBao)
4. All Certificate / ClusterIssuer CRs
5. All Namespace CRs (for new namespaces)
6. Raw K8s workloads (Deployments, ConfigMaps, Services)
7. CiliumL2 / NetworkPolicy CRs
8. OpenChoreo CRDs (existing — Projects, Components, Workloads)

**The test**: If a resource is a static K8s YAML manifest with no imperative logic → FluxCD.  
If it requires `kubectl exec`, API calls, pod-readiness polling, or conditional branching → Pulumi.

### Implementation

Add a 5th FluxCD Kustomization (`oc-infrastructure`) pointing to a new `./infrastructure/` directory in the gitops repo:

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: oc-infrastructure
  namespace: flux-system
spec:
  interval: 5m
  path: ./infrastructure
  prune: true
  sourceRef:
    kind: GitRepository
    name: sample-gitops
```

GitOps repo structure for DNS epic:

```
infrastructure/
├── kustomization.yaml
├── namespaces/
├── cert-manager/
├── openchoreo-gateway/
│   ├── gateway-shared.yaml
│   ├── reference-grants/
│   └── httproutes/
├── external-dns/
│   ├── helmrepository.yaml
│   ├── cloudflare/
│   ├── adguard-truenas/
│   └── adguard-k8s/
├── adguard-home/
└── keepalived/
```

## DNS Epic (sf8) Task Reclassification

| Task | Before | After | Rationale |
|------|--------|-------|-----------|
| sf8.3 ExternalDNS CF | Pulumi component | FluxCD HelmRelease | Helm chart = declarative |
| sf8.4 ExternalDNS AG | Pulumi component | FluxCD HelmRelease x2 | Helm chart = declarative |
| sf8.5 OpenBao secrets | All Pulumi | **SPLIT**: seeding=Pulumi, ExternalSecrets=FluxCD | exec is imperative; CRs are declarative |
| sf8.8 Shared Gateway | Pulumi component | FluxCD manifests | Gateway+ReferenceGrants = YAML |
| sf8.9 Wildcard TLS | Pulumi component | FluxCD manifests | ClusterIssuer+Certificate = YAML |
| sf8.10 AdGuard K8s | Pulumi component | FluxCD manifests | Deployment+ConfigMap = YAML |
| sf8.11 Keepalived | Pulumi/Talos | FluxCD DaemonSet | Start DaemonSet, Talos ext later |
| sf8.12 HTTPRoutes | Pulumi | FluxCD manifests | ~13 HTTPRoutes = canonical GitOps |
| sf8.13 Router DHCP | Manual | No change | Not automatable |
| sf8.14 Argo Tunnel | Talos config | No change | Talos machine config = Pulumi |

## Consequences

### Positive
- Infrastructure changes via `git push` — no Pulumi CLI required
- Auto-reconciliation — FluxCD detects and fixes drift every 5 minutes
- Consistent pattern — all K8s resources managed the same way
- Collaboration — team members can review infra changes in PRs
- DNS epic establishes the pattern for migrating existing Pulumi resources later

### Negative
- Two repos to manage (IDP repo for Pulumi bootstrap + gitops repo for FluxCD manifests)
- Existing Pulumi-managed resources not migrated yet (deferred to future epic)
- Helm values lose Pulumi's dynamic computation (must be static YAML or use Flux variable substitution)

### Risks
- HelmRelease values may be more verbose than Pulumi Python (acceptable trade-off)
- Ordering between FluxCD Kustomizations needs careful `dependsOn` chains
- ExternalSecrets must be synced before HelmReleases that consume them (handled by FluxCD health checks)

## Future Work

- **Migration epic**: Move existing Pulumi-managed declarative resources (14 Helm charts, HTTPRoutes, ExternalSecrets) to FluxCD
- **Evaluate**: Whether Pulumi bootstrap can be further reduced (e.g., CopyCA replaced by cert-manager trust-manager, plane registration by a K8s Job)
- **Reclassify hq6**: OTel config task should use FluxCD HelmRelease values, not Pulumi
- **Reclassify l4a**: GCP epic should provision cluster with Pulumi but deploy OpenChoreo via FluxCD

---

*This ADR supersedes the implicit assumption that all infrastructure is Pulumi-managed. Going forward, Pulumi is the bootstrap tool; FluxCD is the operations tool.*
