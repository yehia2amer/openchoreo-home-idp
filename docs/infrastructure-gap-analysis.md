# OpenChoreo Kubernetes/Pulumi Infrastructure Gap Analysis Report

**Date**: 2026-04-04  
**Version**: 1.0  
**Author**: Infrastructure Review  

---

## Executive Summary

This report analyzes the OpenChoreo Pulumi-based Kubernetes installation flow for bare-metal Talos deployments. The current flow has **3 phases**:
1. **Talos Cluster Bootstrap** (`talos-cluster-baremetal`) - OS-level Kubernetes
2. **OpenChoreo Core Installation** (main `pulumi/__main__.py`) - Platform prerequisites + planes
3. **GitOps/Apps** - FluxCD-managed applications

While the implementation is functional, I've identified **15 significant gaps/workarounds** that create technical debt, complexity, or potential failure modes.

---

## Table of Contents

- [Gap Analysis](#gap-analysis)
  - [GAP-1: Certificate/Secret Synchronization Across Namespaces](#gap-1-certificatesecret-synchronization-across-namespaces)
  - [GAP-2: OpenBao Dev Mode in Production](#gap-2-openbao-dev-mode-in-production)
  - [GAP-3: k3d-Specific Workflow Template Hardcoding](#gap-3-k3d-specific-workflow-template-hardcoding)
  - [GAP-4: Two-Phase Cluster Bootstrap Complexity](#gap-4-two-phase-cluster-bootstrap-complexity)
  - [GAP-5: Missing Health Checks Between Components](#gap-5-missing-health-checks-between-components)
  - [GAP-6: Thunder Bootstrap Idempotency Issues](#gap-6-thunder-bootstrap-idempotency-issues)
  - [GAP-7: Port-Forward Dependencies in Dynamic Providers](#gap-7-port-forward-dependencies-in-dynamic-providers)
  - [GAP-8: Missing Network Policies for Multi-Tenant Security](#gap-8-missing-network-policies-for-multi-tenant-security)
  - [GAP-9: Credentials Hardcoded in Pulumi Config](#gap-9-credentials-hardcoded-in-pulumi-config)
  - [GAP-10: Flux GitOps Hardcoded Repository Structure](#gap-10-flux-gitops-hardcoded-repository-structure)
  - [GAP-11: Missing Backup/Restore Strategy](#gap-11-missing-backuprestore-strategy)
  - [GAP-12: Integration Tests Run at Deploy Time](#gap-12-integration-tests-run-at-deploy-time)
  - [GAP-13: Talos Node State Detection is Fragile](#gap-13-talos-node-state-detection-is-fragile)
  - [GAP-14: Missing Resource Limits and Requests](#gap-14-missing-resource-limits-and-requests)
  - [GAP-15: No Observability for the Platform Itself](#gap-15-no-observability-for-the-platform-itself)
- [Priority Matrix](#priority-matrix)
- [Implementation Roadmap](#implementation-roadmap)
- [Appendix: Quick Wins](#appendix-quick-wins)

---

## Gap Analysis

---

### GAP-1: Certificate/Secret Synchronization Across Namespaces

**Location**: `pulumi/helpers/copy_ca.py`, `pulumi/helpers/dynamic_providers.py` (`CopyCA` class)

**Current Workaround**: 
The codebase manually copies `cluster-gateway-ca` TLS secrets from `openchoreo-control-plane` namespace to `openchoreo-data-plane`, `openchoreo-workflow-plane`, and `openchoreo-observability-plane` namespaces using a custom Pulumi dynamic provider.

```python
# copy_ca.py - Current approach
def copy_ca(...) -> CopyCA:
    return CopyCA(
        f"copy-ca-{name}",
        kubeconfig_path=cfg.kubeconfig_path,
        secret_name=SECRET_GATEWAY_CA,
        source_namespace=NS_CONTROL_PLANE,
        configmap_name=SECRET_GATEWAY_CA,
        target_namespace=target_namespace,
        ...
    )
```

**Issues**:
- Manual synchronization doesn't handle certificate rotation
- If source cert is updated, copies become stale
- No reconciliation loop - one-shot copy during `pulumi up`
- Converts TLS Secret to ConfigMap (loses some metadata)

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Kubernetes Reflector** | Deploy [emberstack/kubernetes-reflector](https://github.com/emberstack/kubernetes-reflector) to auto-sync annotated secrets | Real-time sync, handles rotation, widely adopted, minimal config | Additional pod, another dependency |
| **B. External Secrets Operator (ESO)** | Store CA in OpenBao, sync via ClusterSecretStore | Already using ESO, centralized secret management, rotation-aware | Requires restructuring TLS flow, cert-manager integration unclear |
| **C. cert-manager Cross-Namespace SecretStoreRef** | Use cert-manager's `secretTemplate.annotations` with reflection | Native cert-manager, no extra components | Limited to cert-manager-generated certs, complex config |
| **D. Shared ClusterIssuer + Per-NS Certificates** | Each namespace requests own cert from shared ClusterIssuer | No sync needed, proper cert lifecycle | More certificates, slight resource overhead |

**Recommendation**: **Option D (Shared ClusterIssuer)** for new deployments, **Option A (Reflector)** for backward compatibility. The current `openchoreo-ca` ClusterIssuer already exists - each plane should request its own certificate referencing this issuer.

---

### GAP-2: OpenBao Dev Mode in Production

**Location**: `pulumi/values/openbao.py`

**Current Implementation**:
```python
def get_values(...) -> dict[str, Any]:
    return {
        "server": {
            "dev": {
                "enabled": True,  # ← Always dev mode
                "devRootToken": openbao_root_token,
            },
            ...
        },
    }
```

**Issues**:
- Dev mode stores secrets in-memory (lost on restart)
- No encryption at rest
- Root token passed directly (not sealed/unsealed flow)
- `postStart` script runs every pod restart, re-seeding secrets

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. HA OpenBao with Raft** | Deploy 3-node OpenBao with integrated Raft storage | Production-ready, auto-unseal possible, persistent | Complex, requires storage class, 3x resources |
| **B. Single-node OpenBao + PVC** | Non-dev mode with `file` storage backend on PVC | Persistent, simple, minimal change | Single point of failure, manual unseal |
| **C. External Vault/OpenBao** | Point to existing enterprise Vault | Leverages existing infrastructure | External dependency, network concerns |
| **D. Keep Dev Mode + StatefulSet PVC** | Hybrid: dev mode with persistent storage | Simple transition path | Still not production best practice |

**Recommendation**: **Option B** for homelab, **Option A** for production. Add `is_production` flag to config to switch behaviors.

---

### GAP-3: k3d-Specific Workflow Template Hardcoding

**Location**: `pulumi/components/workflow_plane.py`, lines 75-105

**Current Workaround**:
```python
# Complex sed replacement chain for k3d-specific URLs
apply_cmds.append(
    f"curl -sL {url}"
    f" | sed 's|host.k3d.internal:10082|{registry_endpoint}|g'"
    f" | sed 's|host.k3d.internal:8080|{gateway_endpoint}|g'"
    f" | kubectl apply ..."
)
```

**Issues**:
- Fragile string replacement (breaks if upstream format changes)
- Couples Pulumi to specific template file structure
- Different paths for k3d vs bare-metal (`publish-image-k3d.yaml` vs `publish-image.yaml`)

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Helm Chart Values** | Move endpoint configs to OpenChoreo Helm chart values | Clean, declarative, version-controlled | Requires upstream chart changes |
| **B. Kustomize Overlays** | Platform-specific overlays with `replacements` | GitOps-native, no sed | Additional complexity layer |
| **C. ConfigMap + EnvSubst** | Template files reference ConfigMap values | Decoupled, runtime configurable | Requires workflow engine support |
| **D. OpenChoreo CRD Controller** | Controller injects endpoints at reconciliation | Cleanest long-term solution | Development effort |

**Recommendation**: **Option B (Kustomize)** for immediate fix, **Option A** as feature request to upstream.

---

### GAP-4: Two-Phase Cluster Bootstrap Complexity

**Location**: `talos-cluster-baremetal/__main__.py` + main `pulumi/__main__.py`

**Current Flow**:
```
Phase 1 (talos-cluster-baremetal):
  Talos → Cilium → Gateway API CRDs → Longhorn

Phase 2 (main pulumi):
  cert-manager → ESO → OpenBao → kgateway-crds → CP/DP/WP/OP
```

**Issues**:
- Two separate `pulumi up` commands required
- Cilium installed twice (Phase 1 Helm, Phase 2 flags say `cilium_pre_installed=True`)
- Gateway API CRDs installed in Phase 1 (`ConfigFile`) but Phase 2 expects to manage them
- State split across two Pulumi stacks

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Single Stack with Phases** | Merge into one Pulumi program with conditional phases | Single command, unified state | Larger program, slower preview |
| **B. Stack References** | Phase 2 imports Phase 1 outputs via StackReference | Clean separation, shared state | Requires Pulumi organization |
| **C. Micro-Stacks with Orchestrator** | Separate stacks + automation API orchestrator | Maximum modularity | Complex orchestration code |
| **D. Talos Inline Manifests** | Move Cilium/Longhorn to Talos `cluster.inlineManifests` | Bootstrap once, no Phase 1 Pulumi | Limited to static manifests |

**Recommendation**: **Option B (Stack References)** for proper separation, or **Option D (Inline Manifests)** for simpler bootstrap.

---

### GAP-5: Missing Health Checks Between Components

**Location**: Throughout `components/*.py`

**Current Pattern**:
```python
# Only uses depends_on - doesn't verify actual readiness
cp_chart = k8s.helm.v3.Release(
    ...,
    opts=pulumi.ResourceOptions(depends_on=[wait_eso_sync]),
)
```

**Issues**:
- `depends_on` only waits for Pulumi resource creation, not pod readiness
- ExternalSecrets may take 30-60s to sync after creation
- Helm releases return success before pods are healthy

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Dynamic Provider Waits** | Add `WaitForDeployment` between all components | Guarantees readiness | Slower deployments |
| **B. Helm `wait` + `timeout`** | Set `wait=True` on all Helm releases | Built-in, simple | Some charts don't have proper readiness |
| **C. ArgoCD/Flux Sync Waves** | Replace Pulumi with GitOps sync ordering | Production-grade ordering | Major architecture change |
| **D. Health Probes in Integration Tests** | Move readiness checks to test phase | Separates concerns | Doesn't block broken deployments |

**Recommendation**: **Option A** for critical paths (OpenBao → ESO → ClusterSecretStore), **Option B** for Helm releases.

---

### GAP-6: Thunder Bootstrap Idempotency Issues

**Location**: `pulumi/components/control_plane.py`, lines 55-140

**Current Workaround**:
```python
# Separate Job to re-run Thunder bootstrap scripts
thunder_setup_rerun = k8s.batch.v1.Job(
    "thunder-setup-rerun",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        annotations={"openchoreo.dev/bootstrap-checksum": thunder_bootstrap_checksum},
    ),
    ...
)
```

**Issues**:
- Creates new Job on every bootstrap script change
- Old Jobs accumulate (`ttl_seconds_after_finished=3600` only)
- Race condition with Helm post-install hook

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Helm Post-Upgrade Hook** | Move re-run logic to Helm hook with `helm.sh/hook-delete-policy` | Clean lifecycle | Requires chart modification |
| **B. CronJob + ConfigMap Hash** | CronJob that checks hash and exits early | Self-healing | Over-engineering |
| **C. Init Container** | Add init container to Thunder deployment | Runs every pod start | May be too frequent |
| **D. Kubernetes Job Replace** | Use `delete_before_replace` strictly | Simple | Current approach, just needs cleanup |

**Recommendation**: **Option A** (Helm hook) for upstream contribution, **Option D** refined for current state.

---

### GAP-7: Port-Forward Dependencies in Dynamic Providers

**Location**: `pulumi/helpers/dynamic_providers.py`, `pulumi/helpers/k8s_ops.py`

**Current Pattern**:
```python
# OpenBaoSecrets uses subprocess port-forward
pf = subprocess.Popen(
    ["kubectl", "port-forward", ..., f"{port}:8200", ...],
    ...
)
```

**Issues**:
- Requires `kubectl` on PATH (not just Python k8s client)
- Port conflicts if multiple deployments run simultaneously
- Process cleanup on failure is fragile

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. In-Cluster Jobs** | Run secret operations as Kubernetes Jobs | No local kubectl, runs in-cluster | More complex, job cleanup |
| **B. Service NodePort** | Expose OpenBao on NodePort for local access | No port-forward | Security concern, port allocation |
| **C. Python K8s Streaming** | Use kubernetes-client's `portforward` module | Pure Python, no subprocess | Less mature API |
| **D. MCP Server Pattern** | Local server manages connections | Reusable, connection pooling | Additional component |

**Recommendation**: **Option A (In-Cluster Jobs)** for critical secret operations, keep current approach for development/testing.

---

### GAP-8: Missing Network Policies for Multi-Tenant Security

**Location**: Not present in codebase

**Current State**: No NetworkPolicies defined except `allow-gateway-ingress` for Cilium.

**Issues**:
- All pods can communicate with all other pods
- No namespace isolation
- OpenBao accessible from all namespaces

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Deny-All + Explicit Allow** | Default deny per namespace, whitelist | Maximum security | Complex to enumerate |
| **B. Cilium ClusterWide Policies** | Use CiliumNetworkPolicy for L7 rules | Rich features | Cilium-specific |
| **C. OpenChoreo-Aware Policies** | Policies based on OpenChoreo labels | Matches application model | Development effort |
| **D. Service Mesh (Istio/Linkerd)** | mTLS + authorization policies | Zero-trust | Heavy dependency |

**Recommendation**: **Option A** with **Option B** for Cilium environments. Create baseline policies in `components/prerequisites.py`.

---

### GAP-9: Credentials Hardcoded in Pulumi Config

**Location**: `pulumi/Pulumi.talos-baremetal.yaml`, `pulumi/config.py`

**Current Pattern**:
```yaml
# Pulumi.talos-baremetal.yaml
openchoreo:github_pat:
  secure: v1:QerXHFHFjBVf+qHY:K2Z8...  # Encrypted but stored in repo
```

**Issues**:
- PAT encrypted in config, but key rotation requires re-encryption
- `openbao_root_token` defaults to `"root"` in dev
- No integration with external secret managers (1Password, AWS Secrets Manager)

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. ESO + External Provider** | Use ExternalSecret with AWS/GCP/1Password provider | Enterprise-grade, rotation | Additional setup |
| **B. Pulumi ESC** | Use Pulumi Environments, Secrets, and Config | Native Pulumi, OIDC support | Pulumi Cloud dependency |
| **C. SOPS-Encrypted Files** | Encrypt secrets with Mozilla SOPS | Git-friendly, AGE/GPG keys | Manual rotation |
| **D. Environment Variables** | Read secrets from env at runtime | Simple CI/CD integration | Less declarative |

**Recommendation**: **Option B (Pulumi ESC)** for Pulumi users, **Option A (ESO)** for GitOps-native approach.

---

### GAP-10: Flux GitOps Hardcoded Repository Structure

**Location**: `pulumi/components/flux_gitops.py`

**Current Pattern**:
```python
# Hardcoded paths and Kustomization names
kust_namespaces = k8s.apiextensions.CustomResource(
    ...,
    spec={"path": "./namespaces", ...},  # Fixed path
)
kust_platform = k8s.apiextensions.CustomResource(
    ...,
    spec={"path": "./namespaces/default/platform", ...},  # Fixed path
)
```

**Issues**:
- Assumes specific repo structure (`namespaces/`, `platform-shared/`, etc.)
- No support for multi-environment (dev/staging/prod)
- Kustomization names are fixed (`oc-namespaces`, `oc-platform`, etc.)

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Configurable Paths** | Add config keys for each path | Flexible | Many config keys |
| **B. Flux Bootstrap Template** | Generate repo structure from template | Ensures compatibility | Opinionated |
| **C. GitRepository + PathPrefix** | Use Flux `path` as base, relative kustomizations | One config point | Flux-specific |
| **D. Remove Flux from Pulumi** | Let users manually `flux bootstrap` | Separation of concerns | Less integrated |

**Recommendation**: **Option C** - add `gitops_path_prefix` config key, default to `./`.

---

### GAP-11: Missing Backup/Restore Strategy

**Location**: Not present

**Current State**: No backup strategy for:
- OpenBao secrets
- Thunder SQLite database
- Longhorn volumes
- OpenSearch indices

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Velero + Restic** | Cluster-wide backup/restore | Comprehensive, CNCF project | Storage costs, complexity |
| **B. Component-Specific** | OpenBao export, Longhorn snapshots, etc. | Targeted, efficient | Multiple tools to manage |
| **C. GitOps + Sealed Secrets** | Store encrypted secrets in Git | Reconstructable | Doesn't cover data (PVCs) |
| **D. Talos Machine Snapshots** | ZFS/btrfs snapshots at OS level | Fast, atomic | Requires specific storage |

**Recommendation**: **Option B** for homelab (Longhorn snapshots already configured), **Option A** for production.

---

### GAP-12: Integration Tests Run at Deploy Time

**Location**: `pulumi/components/integration_tests.py`

**Current Pattern**:
```python
# Tests run every `pulumi up`
class _IntegrationTestProvider(ResourceProvider):
    def diff(self, _id: str, olds: dict, news: dict) -> DiffResult:
        return DiffResult(changes=True, ...)  # Always re-run
```

**Issues**:
- Slows down deployments (40+ tests)
- Test failures block infrastructure changes
- Can't run tests independently

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Separate Test Stack** | Move tests to `pulumi/tests/` stack | Clean separation | Two commands |
| **B. pytest + Port-Forward** | Standard pytest with k8s fixtures | Familiar, CI-friendly | Requires running cluster |
| **C. Pulumi Policy Packs** | Use `pulumi policy` for validation | Native, can block | Limited to config validation |
| **D. Post-Deploy Hook** | Run tests only after successful deploy | Doesn't block deploy | May deploy broken state |

**Recommendation**: **Option B** - the `tests/` directory already exists with this pattern. Make it the primary test method.

---

### GAP-13: Talos Node State Detection is Fragile

**Location**: `pulumi/talos-cluster-baremetal/check_node_state.py`

**Current Pattern**:
```python
def detect_node_state(...) -> NodeStatus:
    # TCP socket check + talosctl health
    # Falls back to UNREACHABLE if any error
```

**Issues**:
- Program-time detection (runs before Pulumi engine starts)
- If node is rebooting during detection, gets wrong state
- No retry/backoff on transient failures

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Dynamic Provider with Retry** | Move detection to Pulumi resource with exponential backoff | Proper lifecycle | More complex |
| **B. Talos Health Data Source** | Use `talos.cluster.get_health` data source | Native Talos provider | May not exist |
| **C. External State File** | Write state to file, read in next run | Simple state machine | Manual intervention needed |
| **D. Assume Maintenance Mode** | Always run full bootstrap, let Talos handle idempotency | Simple | Slower, more API calls |

**Recommendation**: **Option D** with Talos's `apply_mode="auto"` (current) - Talos is idempotent. Remove the pre-flight complexity.

---

### GAP-14: Missing Resource Limits and Requests

**Location**: Throughout Helm values

**Current State**: No resource limits specified for:
- OpenBao pods
- Thunder pods
- Argo Workflows
- Most observability components

**Issues**:
- Unbounded resource consumption
- No QoS guarantees
- Can't enable LimitRange enforcement

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Per-Chart Values** | Add `resources:` to each Helm values file | Precise control | Maintenance burden |
| **B. LimitRange Defaults** | Create LimitRange per namespace | Automatic for all pods | May be too restrictive |
| **C. VPA** | Deploy Vertical Pod Autoscaler | Auto-tuning | Complexity, requires metrics |
| **D. Platform Presets** | Define resource tiers (small/medium/large) | Configurable | Need profiling first |

**Recommendation**: **Option A** + **Option B** - set reasonable defaults in values, enforce LimitRange.

---

### GAP-15: No Observability for the Platform Itself

**Location**: Observability plane monitors apps, not platform

**Current State**: 
- OpenSearch stores app logs/traces
- Prometheus scrapes app metrics
- No monitoring of: Pulumi deployments, ESO sync failures, cert-manager events

**Options**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A. Self-Hosted Grafana Stack** | Deploy separate Grafana/Loki/Tempo for platform | Full observability | Resource overhead |
| **B. Prometheus Federation** | Platform Prometheus federates to app Prometheus | Unified view | Complex config |
| **C. Alert Rules Only** | Add PrometheusRules for critical platform components | Lightweight | No dashboards |
| **D. External Monitoring** | Push to Datadog/New Relic/Grafana Cloud | Managed, persistent | Cost, external dependency |

**Recommendation**: **Option C** for homelab, **Option A** or **Option D** for production.

---

## Priority Matrix

| Gap | Severity | Effort | Priority |
|-----|----------|--------|----------|
| GAP-2 (OpenBao Dev Mode) | 🔴 High | Medium | **P1** |
| GAP-8 (Network Policies) | 🔴 High | Medium | **P1** |
| GAP-9 (Hardcoded Credentials) | 🔴 High | Low | **P1** |
| GAP-1 (Cert Sync) | 🟡 Medium | Medium | **P2** |
| GAP-5 (Health Checks) | 🟡 Medium | Low | **P2** |
| GAP-14 (Resource Limits) | 🟡 Medium | Low | **P2** |
| GAP-3 (k3d Templates) | 🟡 Medium | Medium | **P2** |
| GAP-4 (Two-Phase Bootstrap) | 🟡 Medium | High | **P3** |
| GAP-7 (Port-Forward) | 🟢 Low | Medium | **P3** |
| GAP-12 (Integration Tests) | 🟢 Low | Medium | **P3** |
| GAP-6 (Thunder Bootstrap) | 🟢 Low | Low | **P3** |
| GAP-10 (Flux Hardcoding) | 🟢 Low | Low | **P3** |
| GAP-11 (Backup/Restore) | 🟡 Medium | High | **P3** |
| GAP-13 (Node State Detection) | 🟢 Low | Low | **P4** |
| GAP-15 (Platform Observability) | 🟢 Low | High | **P4** |

---

## Appendix: Quick Wins

These can be implemented immediately with minimal risk:

1. **Add `helm.wait=True`** to all Helm releases
2. **Create LimitRange** in each namespace
3. **Add `.gitignore`** for `outputs/` directory in talos-cluster-baremetal
4. **Document** the two-phase flow in README
5. **Add** `cleanup_timeout_seconds` to integration test Jobs
