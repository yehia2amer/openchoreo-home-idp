# FluxCD Full Control Migration Report

**Date**: April 9, 2026
**Status**: COMPLETE — All 28 implementation tasks + 4 verification tasks passed
**Beads EPIC**: `openchoreo-home-idp-dbp`

---

## Executive Summary

The OpenChoreo platform has been migrated from a **Pulumi-managed-everything** architecture to a **FluxCD-first GitOps** architecture. Pulumi's scope has been reduced from managing ~30+ infrastructure components to a minimal **Phase 1 bootstrap** of ~10 foundational resources. FluxCD now manages all infrastructure and platform components declaratively from a dedicated gitops repository.

**Before**: 3-phase deployment (Talos → Pulumi installs everything → FluxCD manages apps only)
**After**: 2-phase deployment (Pulumi minimal bootstrap → FluxCD manages all infrastructure + apps)

### Key Outcomes

- **Net deletion of ~2,856 lines** of Pulumi Python code (67 added, 2,923 removed across 21 files)
- **106 new GitOps YAML manifests** (74 base + 32 cluster overlays) totaling ~3,927 lines
- **17 HelmReleases** and **24 Kustomizations** all healthy on the live cluster
- **4 platform overlays** ready for multi-cluster deployment (talos-baremetal, k3d, talos-vm, rancher-desktop)
- **118 E2E tests** (96 passing, 22 skipped for optional components)
- **Zero downtime** — migration was performed on the live production cluster

---

## Architecture: Before vs After

### Before (Pulumi-Managed-Everything)

```
+---------------------------------------------------+
|                 Pulumi Stack                       |
|                                                    |
|  Phase 1: Talos + Cilium                          |
|  Phase 2: OpenBao + Thunder + secrets             |
|           cert-manager, ESO, kgateway             |
|           TLS CA chain, wildcard certs            |
|           CP, DP, WP, OP, Odigos                  |
|           Plane registration, linking             |
|           Docker Registry                         |
|           Cilium L2 configs                       |
|           OpenSearch, OTel Collector              |
|  Phase 3: FluxCD (apps only)                      |
|                                                    |
|  ~5,000+ lines of Python                          |
|  30+ infrastructure components                    |
|  Single point of failure                          |
+---------------------------------------------------+
```

### After (FluxCD-First Architecture)

```
+----------------------+     +------------------------------------------+
|   Pulumi Phase 1     |     |           FluxCD GitOps                  |
|   (Bootstrap Only)   |     |      (openchoreo-gitops repo)            |
|                      |---->|                                          |
|  - Talos cluster     |     |  00-crds: Gateway API CRDs              |
|  - Cilium CNI        |     |  01-prerequisites:                      |
|  - GW API CRDs       |     |    cert-manager, ESO, kgateway,         |
|  - Longhorn storage  |     |    kubernetes-replicator                 |
|  - OpenBao vault     |     |  02-tls:                                |
|  - Thunder OIDC      |     |    CA chain, wildcard certs             |
|  - PushSecrets       |     |  03-platform:                           |
|  - ClusterSecretStore|     |    CP, DP, WP, OP, Odigos,             |
|  - Seed secrets      |     |    Docker Registry, workflow templates  |
|  - Flux bootstrap    |     |  04-registration:                       |
|                      |     |    register-planes Jobs, link-planes Job|
|  ~2,156 lines Python |     |  05-network:                            |
|  ~10 components      |     |    Cilium L2 configs                    |
+----------------------+     |                                          |
                             |  106 YAML files, ~3,927 lines           |
                             |  17 HelmReleases, 24 Kustomizations     |
                             |  4 platform overlays                    |
                             +------------------------------------------+
```

---

## Code Metrics

### Pulumi Changes (Python, excluding tests)

| Metric | Value |
|--------|-------|
| Files changed | 21 |
| Lines added | 67 |
| Lines removed | 2,923 |
| **Net change** | **-2,856 lines** |
| Remaining Pulumi code | ~2,156 lines across 5 core files |

**Remaining Pulumi files:**

| File | Lines | Purpose |
|------|-------|---------|
| `pulumi/__main__.py` | 135 | Phase 1 orchestration |
| `pulumi/config.py` | 380 | Configuration + platform detection |
| `pulumi/components/prerequisites.py` | 615 | OpenBao + secrets + namespaces |
| `pulumi/components/thunder.py` | 406 | Thunder OIDC provider |
| `pulumi/helpers/dynamic_providers.py` | 620 | Custom resource providers |

### GitOps YAML (New)

| Area | Files | Lines |
|------|-------|-------|
| `infrastructure/base/` (shared manifests) | 74 | 2,175 |
| `clusters/` (4 platform overlays) | 32 | 1,752 |
| **Total GitOps** | **106** | **3,927** |

### E2E Tests

| Metric | Value |
|--------|-------|
| Test files | 18 |
| Total tests | 118 |
| Passing | 96 |
| Skipped | 22 (optional components) |
| Test code | 1,903 lines |

### Infrastructure on Cluster

| Resource Type | Count | Status |
|---------------|-------|--------|
| HelmReleases | 17 | All healthy |
| Kustomizations | 24 | All healthy |
| K8s Jobs (registration) | 3 | All completed |
| K8s Jobs (linking) | 1 | Completed |
| Platform overlays | 4 | All valid |

---

## GitOps Directory Structure

```
openchoreo-gitops/
├── infrastructure/
│   └── base/
│       ├── 00-crds/                      # Gateway API CRDs
│       ├── 01-prerequisites/
│       │   ├── cert-manager/             # HelmRelease + configs
│       │   ├── external-secrets/         # HelmRelease + configs
│       │   ├── kgateway/                 # CRDs + controller HelmReleases
│       │   └── kubernetes-replicator/    # HelmRelease (NEW)
│       ├── 02-tls/
│       │   ├── ca-chain/                 # Bootstrap issuer -> CA cert -> CA issuer
│       │   └── wildcard-certs/           # CP/DP/OP gateway TLS certs
│       ├── 03-platform/
│       │   ├── control-plane/            # HelmRelease + values ConfigMap
│       │   ├── data-plane/               # HelmRelease + Cilium NetworkPolicy
│       │   ├── workflow-plane/           # HelmRelease + Docker Registry + templates
│       │   ├── observability-plane/      # 4 HelmReleases (observer, logs, metrics, tracing)
│       │   └── odigos/                   # HelmRelease + Action + Destination
│       ├── 04-registration/
│       │   ├── register-planes/          # 3 Jobs (DP, WP, OP) + RBAC
│       │   └── link-planes/              # 1 Job + RBAC
│       └── 05-network/
│           └── cilium-configs/           # L2 announcement policy + IP pool
└── clusters/
    ├── talos-baremetal/                   # Production overlay
    │   ├── 00-crds.yaml ... 05-network.yaml  # 6 Flux Kustomizations
    │   ├── kustomization.yaml            # Master entry point
    │   └── vars/cluster-vars.yaml        # Platform-specific variables
    ├── k3d/                              # Dev overlay (same structure)
    ├── talos-vm/                         # VM overlay
    └── rancher-desktop/                  # Desktop overlay
```

---

## GitOps Workarounds and Patterns

### 1. K8s Jobs for Plane Registration (Imperative in Declarative World)

**Problem**: OpenChoreo planes (DP, WP, OP) must register with the Control Plane via its REST API after deployment. This is inherently imperative — FluxCD is declarative.

**Solution**: K8s Jobs with `ttlSecondsAfterFinished: 300`. Each Job:
- Uses `kubectl wait` to ensure the CP is ready before running
- Calls the CP registration API via `curl`
- Has RBAC (ServiceAccount + Role + RoleBinding) for cross-namespace pod discovery
- Uses Flux `postBuild` variable substitution for domain/namespace values

**Files**: `infrastructure/base/04-registration/register-planes/` (3 Job manifests + RBAC)

**Trade-off**: Jobs are "run-once" — if registration needs to re-run, the Job must be deleted first. This is acceptable because plane registration is a one-time bootstrap operation.

### 2. Flux postBuild Variable Substitution with $$ Escaping

**Problem**: Workflow templates contain bash `${VARIABLE}` syntax that Flux's `envsubst` tries to resolve as Flux variables (and fails).

**Solution**: Use `$$` prefix to escape bash variables: `$${VARIABLE}` passes through Flux as `${VARIABLE}` in the actual template.

**Example**: In `workflow-templates.yaml`, `$${workflow.parameters.image_tag}` survives Flux substitution and arrives as `${workflow.parameters.image_tag}` in the Argo workflow.

### 3. ConfigMaps for Helm Values (Variable Substitution)

**Problem**: FluxCD HelmReleases support `valuesFrom` ConfigMaps but don't support `postBuild` substitution inside `spec.values` directly.

**Solution**: Extract Helm values into ConfigMaps, reference them via `valuesFrom` in HelmRelease, and use `postBuild` substitution on the Kustomization that owns the ConfigMap.

**Pattern used for**: CP, DP, WP, OP values that need cluster-specific variables (domain, IPs, etc.)

### 4. Ordered Wave Execution via Kustomization Dependencies

**Problem**: Infrastructure must deploy in order (CRDs -> prerequisites -> TLS -> platform -> registration -> network).

**Solution**: Each cluster overlay has 6 Kustomizations (`00-crds` through `05-network`) with explicit `dependsOn` chains. FluxCD respects these dependencies and deploys waves sequentially while allowing parallelism within each wave.

### 5. kubernetes-replicator for CA Certificate Distribution

**Problem**: The internal CA certificate must be available in every namespace that needs TLS. cert-manager only issues certs in one namespace.

**Solution**: Added `kubernetes-replicator` as a NEW component (not migrated from Pulumi — it didn't exist before). Annotations on the CA Secret trigger automatic replication to all namespaces that need it.

**Future consideration**: `trust-manager` (from cert-manager team) could replace this with a more native approach.

---

## What Pulumi Still Manages (Phase 1 Only)

| Component | Why Still in Pulumi |
|-----------|-------------------|
| Talos cluster | Machine-level config, not K8s resources |
| Cilium CNI | Must be installed before any K8s resources exist |
| Gateway API CRDs | Required before FluxCD Kustomizations can reference them |
| Longhorn storage | Storage backend needed before PVCs work |
| OpenBao (vault) | Secrets store — FluxCD needs secrets FROM OpenBao |
| Thunder (OIDC) | Authentication provider — app registrations are imperative |
| PushSecrets | Push initial secrets from OpenBao to K8s |
| ClusterSecretStore | ESO needs this to connect to OpenBao |
| Seed secrets | Bootstrap secrets that must exist before anything else |
| Flux bootstrap | GitRepository + root Kustomization that starts FluxCD |

**Principle**: Pulumi handles the "chicken-and-egg" resources that must exist before FluxCD can operate. Everything else is in GitOps.

---

## What Was Removed from Pulumi

| Component | Migrated To |
|-----------|-------------|
| cert-manager | FluxCD HelmRelease (`01-prerequisites/cert-manager/`) |
| External Secrets Operator | FluxCD HelmRelease (`01-prerequisites/external-secrets/`) |
| kgateway (CRDs + controller) | FluxCD HelmReleases (`01-prerequisites/kgateway/`) |
| TLS CA chain | FluxCD manifests (`02-tls/ca-chain/`) |
| Wildcard TLS certificates | FluxCD manifests (`02-tls/wildcard-certs/`) |
| Control Plane Helm chart | FluxCD HelmRelease (`03-platform/control-plane/`) |
| Data Plane Helm chart | FluxCD HelmRelease (`03-platform/data-plane/`) |
| Workflow Plane Helm chart | FluxCD HelmRelease (`03-platform/workflow-plane/`) |
| Observability Plane | FluxCD HelmReleases (`03-platform/observability-plane/`) |
| Odigos | FluxCD HelmRelease (`03-platform/odigos/`) |
| Docker Registry | FluxCD HelmRelease (`03-platform/workflow-plane/`) |
| Workflow templates | FluxCD manifests (`03-platform/workflow-plane/templates/`) |
| Plane registration | FluxCD Jobs (`04-registration/register-planes/`) |
| Plane linking | FluxCD Job (`04-registration/link-planes/`) |
| Cilium L2 configs | FluxCD manifests (`05-network/cilium-configs/`) |
| OpenSearch | **Removed entirely** (replaced by OpenObserve) |
| OTel Collector | **Removed entirely** (replaced by Odigos) |

---

## Verification Results (Final Review)

All 4 independent review agents approved:

### F1: Plan Compliance Audit (Oracle)
- **Must Have**: 9/9
- **Must NOT Have**: 10/10 (no dual-managed resources, no hardcoded values, etc.)
- **Tasks**: 28/28 completed
- **Verdict**: **APPROVE**

### F2: Code Quality Review
- **Flux Validate**: PASS (all 106 YAML files valid)
- **Pulumi Code**: PASS (no `as any`, no empty catches, no console.log)
- **YAML Lint**: 106/106 clean
- **Advisory** (non-blocking):
  - kubernetes-replicator HelmRelease missing explicit `spec.chart.spec.version` (LOW)
  - Dev-stack placeholder secrets gated behind `_is_dev_stack` flag (LOW)
  - Empty `resources: []` in cert-manager/ESO configs kustomizations (INFO — placeholders for future use)
- **Verdict**: **APPROVE**

### F3: Real Manual QA
- **E2E Tests**: 96/96 pass (22 skip)
- **HelmReleases**: 17/17 healthy
- **Kustomizations**: 24/24 ready
- **Registration Jobs**: 3/3 completed
- **Link Planes Job**: 1/1 completed
- **Verdict**: **APPROVE**

### F4: Scope Fidelity Check
- **Waves**: 3/3 implemented as specified
- **Git Tags**: 3/3 present (post-wave1, post-wave2, post-wave3)
- **Platform Overlays**: 4/4 valid
- **Verdict**: **APPROVE** (initial REJECT was false positive — agent exported wrong Pulumi stack)

---

## Code Clarity and Maintainability Assessment

### Strengths

1. **Clear separation of concerns**: Pulumi handles bootstrap, FluxCD handles everything else. No overlap.
2. **Numbered wave ordering** (`00-crds` through `05-network`) makes dependency chain obvious.
3. **Base/overlay pattern** enables multi-cluster deployment without duplication.
4. **ConfigMap-based values** allow per-cluster customization via `cluster-vars.yaml`.
5. **E2E test suite** provides confidence for future changes (96 passing tests).
6. **Comprehensive documentation**: New `docs/deployment-guide.md` (558 lines) covers the full deployment flow.

### Areas for Improvement

1. **kubernetes-replicator missing chart version pin**: Could cause unexpected upgrades on reconciliation.
2. **Drift detection not enabled**: HelmReleases don't set `driftDetection.mode: enabled` — manual kubectl changes won't be auto-corrected.
3. **Stale `dev` Pulumi stack**: 200 resources, 2 weeks old — should be cleaned up or destroyed.
4. **Job re-execution**: Registration Jobs need manual deletion + re-apply if they need to re-run. No automatic retry mechanism.
5. **Variable substitution complexity**: The `$$` escaping pattern for Flux `postBuild` + bash variables requires careful documentation for new contributors.

---

## Migration Commits (Chronological)

| Hash | Description |
|------|-------------|
| `d08b6d8` | feat(gitops): add FluxCD infrastructure layer directories, cluster entry points, and platform vars |
| `5abc8e9` | feat(fluxcd): add Flux bootstrap to Phase 1 and fluxcd_manages_infra feature flag |
| `f363980` | test: extract integration tests to standalone pytest E2E suite |
| `dbedc81` | feat(gitops): add Wave 1 prerequisites HelmReleases + Cilium L2 configs |
| `cf54827` | feat: Wave 2 - TLS CA chain, platform Helm charts (CP, DP, WP, Registry) |
| `fd437ff` | feat(gitops): add Wave 3 - OP, Odigos, plane registration/linking, workflow templates |
| `9ce0c17` | feat: remove OpenSearch, OTel Collector, route traces/logs to OpenObserve |
| `8bb738c` | fix: suppress per-plane gateway-default resources |
| `b90aa7d` | fix(tests): correct OpenChoreo API group and HTTPRoute assertions |
| `e795a76` | refactor(pulumi): strip FluxCD-migrated components, Phase 1 only |
| `0a3c03d` | docs: update README and deployment guide for FluxCD-first architecture |

---

## Future Work (Tracked as Beads Issues)

| Priority | Issue | Task | Rationale |
|----------|-------|------|-----------|
| P2 | dbp.33 | Pin kubernetes-replicator chart version | Prevent uncontrolled upgrades |
| P3 | dbp.34 | Enable drift detection on HelmReleases | Auto-correct manual kubectl changes |
| P3 | dbp.35 | Clean up stale dev Pulumi stack | 200 orphaned resources |
| P3 | dbp.36 | Evaluate trust-manager alternative | More native cert-manager integration |
| P4 | dbp.37 | Document state handoff procedure | Knowledge preservation |
| P4 | dbp.38 | Add Slack/Teams notification channel | Broader team visibility |

---

## Conclusion

The FluxCD Full Control migration is **complete and verified**. The platform now follows a true GitOps pattern where:

- **Git is the source of truth** for all infrastructure configuration
- **Pulumi handles only what FluxCD cannot** (pre-K8s resources, secrets bootstrap, OIDC registration)
- **Changes flow through PRs** to the gitops repo, not through `pulumi up` commands
- **Multi-cluster deployment** is enabled through the base/overlay pattern
- **Drift healing** is possible (though not yet enabled by default)

The migration reduced operational complexity significantly — instead of a monolithic Pulumi stack managing 30+ components with complex Python logic, the platform now uses declarative YAML manifests that are easier to understand, review, and modify.
