# Reconciliation Report: OpenChoreo Environment Audit

> **Generated:** 2026-04-07 | **Epic:** 1gz | **Cluster:** talos-baremetal (single-node Talos Linux K8s v1.33.0)

## Executive Summary

This report synthesizes findings from the complete Pulumi/FluxCD vs cluster audit. The environment is **well-codified** — all 269 Pulumi resources and all FluxCD-managed resources exist in the cluster. True drift is limited to 2 manual experiment CRs and 20 orphaned PVs. Two FluxCD HelmReleases are failed (non-critical), and two Gateways lack external IPs.

**Verdict:** The environment can be reproduced on a clean cluster by running `pulumi up -s talos-baremetal` after provisioning the nested Talos project. Estimated time: 60-100 minutes.

---

## Audit Inventory

| Audit Document | Content | File |
|---|---|---|
| Pulumi Inventory | 269 resources, 16 Helm charts, 11 namespaces | [pulumi-inventory.md](./pulumi-inventory.md) |
| FluxCD Inventory | 6 controllers, 1 GitRepo, 5 Kustomizations, 3 HelmReleases | [fluxcd-inventory.md](./fluxcd-inventory.md) |
| Cluster Snapshot | 25 namespaces, 65 Deployments, 161 CRDs, 32 PVs | [cluster-snapshot.md](./cluster-snapshot.md) |
| Drift Analysis | 4 operator-created NS, 2 experiment CRs, 20 orphaned PVs | [drift-analysis.md](./drift-analysis.md) |
| Failed/Missing | 2 failed HelmReleases, 2 pending IPs, 1 dead code file | [failed-missing.md](./failed-missing.md) |
| Deployment Ordering | 10 steps, dependency graph, timeout constants, parallelism map | [deployment-ordering.md](./deployment-ordering.md) |

---

## Resource Ownership Matrix

| Owner | Namespaces | Resources | Status |
|---|---|---|---|
| Kubernetes system | 4 (`default`, `kube-system`, `kube-public`, `kube-node-lease`) | Core system | ✅ Expected |
| Nested Pulumi (talos-cluster-baremetal) | 2 (`cilium-secrets`, `longhorn-system`) | Cilium, Longhorn, Gateway API CRDs, snapshot-controller | ✅ Expected |
| Main Pulumi stack | 11 | 269 resources (Helm charts, CRs, Secrets, etc.) | ✅ All present |
| FluxCD (gitops repo) | 4 (`backstage-fork`, `external-dns`, `keepalived`, `openchoreo-gateway`) | HelmReleases, HTTPRoutes, ExternalSecrets, Gateways | ✅ All present (2 failed) |
| OpenChoreo operators (runtime) | 4 (`arr-stack`, `dp-default-*`) | Deployments, HTTPRoutes, ExternalSecrets | ✅ Expected runtime |
| **Manual/unknown** | **0** | **3 CRs** (`dfg`, `deep-agent`, `usecase`) | **⚠️ True drift** |

---

## Actionable Items

### Priority 1: Fix Before Next Production Use

| # | Issue | Impact | Action | Effort |
|---|---|---|---|---|
| 1 | **Failed HelmRelease: external-dns-adguard-k8s** | LAN DNS not auto-registered for k8s AdGuard | Fix AdGuard endpoint/credentials or add `spec.suspend: true` to gitops repo | 30m |
| 2 | **Failed HelmRelease: external-dns-adguard-truenas** | LAN DNS not auto-registered for TrueNAS AdGuard | Fix TrueNAS AdGuard connectivity/credentials or suspend | 30m |

### Priority 2: Clean Up Before Fresh Deployment

| # | Issue | Impact | Action | Effort |
|---|---|---|---|---|
| 3 | **20 Released PVs (~54Gi)** | Wasted storage from completed builds | `kubectl delete pv <name>` for all Released PVs | 10m |
| 4 | **Manual experiment: Project/dfg** | Orphaned project and child namespace | Delete or codify in gitops repo | 5m |
| 5 | **Manual experiment: Component/deep-agent + ComponentType/usecase** | Unknown component type | Delete or codify in gitops repo | 5m |
| 6 | **Dead code: otel_operator.py** | Confusing for new contributors | Delete `pulumi/components/otel_operator.py` | 2m |

### Priority 3: Architecture Decisions Needed

| # | Issue | Impact | Action | Effort |
|---|---|---|---|---|
| 7 | **DP/OP Gateways have no external IP** | No direct external access to DP/OP gateways; traffic routes through gateway-shared | Decide: expand CiliumL2 IP pool, or document gateway-shared as the intentional single ingress point | 15m |
| 8 | **ai-rca-agent scaled to 0** | RCA feature not operational | Scale to 1 and configure LLM API key, or set `enable_rca: false` if not needed | 10m |

---

## Clean Cluster Reproduction Procedure

### Prerequisites

1. Run `talos-cluster-baremetal` nested Pulumi project:
   - Provisions Talos Linux node
   - Installs Cilium CNI, Longhorn, Gateway API CRDs, snapshot-controller
2. Verify kubeconfig:
   ```bash
   export KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig
   kubectl get nodes  # Should show 1 Ready node
   ```
3. Set required secrets in Pulumi config or env:
   - `github_pat` — GitHub PAT for workflow builds and PR creation
   - `openbao_root_token` — OpenBao root token
   - `opensearch_password` — OpenSearch admin password
   - `openobserve_admin_password` — OpenObserve admin password
   - `flux_telegram_bot_token` + `flux_telegram_chat_id` (optional, for notifications)

### Deployment

```bash
cd pulumi
pulumi up -s talos-baremetal
```

### Deployment Sequence (automatic)

| Step | Component | Timeout | Depends On |
|---|---|---|---|
| 0.5 | Cilium L2 (IP pool + ARP policy) | — | None |
| 1 | Prerequisites (cert-manager, ESO, OpenBao, kgateway, namespaces) | 20m | — |
| 1.5 | TLS Setup (self-signed CA + wildcard certs) | — | Step 1 |
| 2 | Control Plane (Thunder, Backstage, API, controllers) | 20m | Step 1 + 1.5 |
| 3 | Data Plane (gateway, agent, network policy) | 20m | Step 2 |
| 4 | Workflow Plane (Argo, registry, templates) | 20m | Step 2 |
| 5 | Observability Plane (OpenSearch, Prometheus, OpenObserve, Odigos) | 40m | Step 2 |
| 6 | Link Planes (patch DP/WP with observability ref) | — | Steps 3+4+5 |
| 6.5 | Odigos (eBPF auto-instrumentation) | 20m | Step 5 |
| 7 | Flux CD (controllers, GitRepo, Kustomizations, notifications) | 20m | Steps 2+3+4 |
| 8 | Integration Tests (~35 health checks) | — | Steps 2+3+4+5 |
| 9 | Demo App Bootstrap (build, merge PRs, verify) | 45m | Steps 2+3+4+5 |

**Steps 3, 4, 5 run in parallel.** Step 7 runs in parallel with Step 5.

**Critical path:** Step 1 → 1.5 → 2 → 5 (40m bottleneck) → 9 (45m). Total: ~60-100 minutes.

### Post-Deploy Verification

Integration tests (Step 8) validate automatically. Manual checks:

```bash
# All pods Running
kubectl get pods -A --field-selector=status.phase!=Succeeded | grep -v Running

# All ExternalSecrets synced
kubectl get externalsecrets -A

# All PushSecrets synced
kubectl get pushsecrets -A

# FluxCD kustomizations healthy
flux get kustomizations

# Gateways have IPs
kubectl get gateways -A

# Backstage reachable
curl -k https://backstage.amernas.work/
```

---

## What Will Differ on Clean Cluster

| Present on current cluster | On clean cluster |
|---|---|
| `Project/dfg`, `Component/deep-agent`, `ComponentType/usecase` | ❌ Absent (manual experiments) |
| `dp-default-*` namespaces + their deployments/routes | ❌ Absent until users create ReleaseBindings |
| `arr-stack` namespace | Recreated when `oc-demo-projects` Kustomization syncs |
| 20 Released PVs (~54Gi) | ❌ Absent (no prior builds) |
| Workflow ExternalSecrets in `workflows-default` | ❌ Absent until workflows run |
| `external-dns-adguard-*` HelmReleases | Present but will fail again unless root cause fixed |
| DP/OP Gateway external IPs | Still pending unless IP pool expanded |

---

## Feature Flag Reference

| Flag | Value (talos-baremetal) | Effect |
|---|---|---|
| `cilium_pre_installed` | `true` | Skips Step 0, runs Step 0.5 |
| `tls_enabled` | `true` | Enables Step 1.5 (self-signed CA chain) |
| `enable_flux` | `true` | Enables Step 7 (Flux CD + GitOps) |
| `enable_observability` | `true` | Enables Step 5 (Observability Plane) |
| `enable_openobserve` | `true` | Adds OpenObserve logging/tracing + dual-ship Fluent Bit |
| `enable_rca` | `true` | Creates RCA agent ExternalSecret (agent at 0 replicas) |
| `enable_demo_app_bootstrap` | `true` | Enables Step 9 (build + deploy demo apps) |

---

## Cross-Owner Dependencies (By Design)

The Pulumi ↔ FluxCD boundary is documented in `docs/adr/001-pulumi-fluxcd-boundary.md`:

| Pulumi Creates | FluxCD Consumes |
|---|---|
| `ClusterSecretStore/default` | ExternalSecrets in `backstage-fork`, `external-dns`, `openchoreo-gateway` |
| `ClusterIssuer/openchoreo-ca` | Wildcard certificates via Helm charts |
| PushSecrets → OpenBao seeds | FluxCD-deployed apps pull secrets from OpenBao |
| Control Plane CRDs | Kustomization-applied CRs (`Project`, `Component`, `Environment`, etc.) |

| FluxCD Creates | Operators Consume |
|---|---|
| `Project` CRs | OpenChoreo controller-manager creates namespaces |
| `Component` + `Workload` CRs | Workflow plane triggers builds; data plane creates deployments |
| `ReleaseBinding` CRs | Data plane agent deploys to `dp-default-*` namespaces |
| `Gateway/gateway-shared` | All planes use for external routing |

---

## Conclusion

The OpenChoreo talos-baremetal environment is **production-reproducible**. All infrastructure-as-code declarations (Pulumi + FluxCD) match the cluster state. The actionable items above are cleanup/improvement tasks, not blockers for reproduction. Running `pulumi up` on a fresh cluster with the same config will produce an equivalent environment within ~60-100 minutes.
