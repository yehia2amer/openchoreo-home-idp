# Failed/Missing: Resources Declared but Not in Cluster

> **Date:** 2026-04-07 · **Cluster:** talos-baremetal
> **Method:** Cross-reference Pulumi/FluxCD declarations against actual cluster state

## Summary

| Category | Count | Severity |
|----------|-------|----------|
| Failed HelmReleases (FluxCD) | 2 | ⚠️ Warning |
| Missing external IPs (networking) | 2 | ⚠️ Warning |
| Intentionally disabled/scaled | 1 | ℹ️ Info |
| Dead code (unused Pulumi component) | 1 | ℹ️ Info |
| Skipped Pulumi steps (conditional) | 1 | ✅ By design |

**Overall assessment:** No critical failures. All Pulumi-declared resources exist in the cluster. The only failures are in FluxCD-managed HelmReleases and missing Cilium L2 IP assignments.

---

## 1. Failed FluxCD HelmReleases

### `external-dns-adguard-k8s` (external-dns namespace)

| Field | Value |
|-------|-------|
| **Declared in** | FluxCD gitops repo → `oc-infrastructure` kustomization |
| **Status** | ❌ Stalled — `RetriesExceeded: Failed to install after 1 attempt(s)` |
| **Chart** | `external-dns` (AdGuard provider) |
| **Likely cause** | AdGuard Home on the k8s cluster itself may not be reachable at the configured endpoint, or the AdGuard webhook/API isn't configured correctly |
| **Impact** | DNS records for `*.amernas.work` are NOT auto-registered in the k8s AdGuard instance |
| **Workaround** | `external-dns-cloudflare` is working — public DNS resolution still functions |

### `external-dns-adguard-truenas` (external-dns namespace)

| Field | Value |
|-------|-------|
| **Declared in** | FluxCD gitops repo → `oc-infrastructure` kustomization |
| **Status** | ❌ Stalled — `RetriesExceeded: Failed to install after 1 attempt(s)` |
| **Chart** | `external-dns` (AdGuard provider) |
| **Likely cause** | TrueNAS AdGuard instance not reachable from cluster, or credentials in `adguard-truenas-credentials` ExternalSecret are incorrect |
| **Impact** | DNS records are NOT auto-registered in the TrueNAS AdGuard instance |
| **Workaround** | Same as above — Cloudflare handles public DNS |

**Action items:**
1. Check AdGuard API endpoints in HelmRelease values
2. Verify ExternalSecret credentials are correct in OpenBao
3. Consider `flux resume helmrelease external-dns-adguard-k8s -n external-dns` after fixing
4. If these are intentionally disabled, remove from gitops repo or add `spec.suspend: true`

---

## 2. Missing External IPs (Cilium L2)

### Data Plane gateway — no external IP

| Field | Value |
|-------|-------|
| **Declared in** | Pulumi (`data_plane.py`) — Gateway resource creates a LoadBalancer service |
| **Actual state** | `openchoreo-data-plane/gateway-default` has ClusterIP `10.104.74.83` but NO external IP |
| **Expected** | Should get an IP from `CiliumLoadBalancerIPPool` |
| **Why missing** | The `gateway_pin_ip` config (`192.168.0.14`) only pins the CP gateway. DP gateway has no pin and the IP pool may not have additional IPs, OR the DP gateway doesn't match the L2 announcement policy selector |
| **Impact** | Data plane endpoints (user apps) are only accessible through the shared gateway's wildcard route (`*.amernas.work` → `gateway-shared` at `192.168.0.10`). Direct DP gateway access is not available externally. |

### Observability Plane gateway — no external IP

| Field | Value |
|-------|-------|
| **Declared in** | Pulumi (`observability_plane.py`) — Gateway resource creates a LoadBalancer service |
| **Actual state** | `openchoreo-observability-plane/gateway-default` has ClusterIP `10.108.59.140` but NO external IP |
| **Expected** | Should get an IP from `CiliumLoadBalancerIPPool` |
| **Why missing** | Same as DP — no pinned IP and pool may be exhausted or selector doesn't match |
| **Impact** | Observability endpoints (observer, openobserve) are only accessible through the shared gateway at `192.168.0.10`. Direct OP gateway access is not available externally. |

**Action items:**
1. Check `CiliumLoadBalancerIPPool` — does it have enough IPs for all 4 gateways?
2. Check if the L2 announcement policy `homelab-l2-policy` selector matches DP/OP gateway services
3. Decide: Are DP/OP gateways intentionally ClusterIP-only (since `gateway-shared` handles routing)?
   - If yes → document this as intentional architecture
   - If no → expand the IP pool or add pin IPs for DP/OP

---

## 3. Intentionally Disabled/Scaled Resources

### `ai-rca-agent` — scaled to 0 replicas

| Field | Value |
|-------|-------|
| **Declared in** | Pulumi (`observability_plane.py`) via OP Helm chart |
| **Actual state** | Deployment exists with `0/0` replicas |
| **Flag** | `enable_rca: true` in stack config |
| **Why 0 replicas** | Likely the Helm chart defaults to 0 replicas and scales up only when the RCA agent is fully configured (LLM API key, base URL). The `rca-agent-secret` ExternalSecret exists and is synced, but the agent may need explicit scaling. |
| **PVC** | `ai-rca-agent-data` (128Mi) — bound and allocated |
| **Impact** | RCA (Root Cause Analysis) AI feature is not operational |

**Action item:** If RCA is wanted, scale to 1: `kubectl scale deploy ai-rca-agent -n openchoreo-observability-plane --replicas=1` and verify the LLM credentials are correct.

---

## 4. Dead Code (Not Deployed)

### `otel_operator.py` — never imported

| Field | Value |
|-------|-------|
| **File** | `pulumi/components/otel_operator.py` |
| **Status** | File exists but is never imported from `__main__.py` |
| **Superseded by** | `odigos.py` (Odigos auto-instrumentation) |
| **In cluster?** | No OpenTelemetry Operator resources exist (no `opentelemetry-operator-system` namespace) |
| **Impact** | None — this is dead code only |

**Action item:** Delete `pulumi/components/otel_operator.py` to avoid confusion.

---

## 5. Conditionally Skipped (By Design)

### Step 0: Cilium CNI + Gateway API CRDs

| Field | Value |
|-------|-------|
| **Declared in** | `pulumi/components/cilium.py` |
| **Condition** | `cilium_pre_installed=false` |
| **Actual** | `cilium_pre_installed=true` on `talos-baremetal` |
| **Result** | Step 0 is skipped. Cilium is installed by the nested `talos-cluster-baremetal` project instead. Step 0.5 (CiliumL2) runs for L2 policies. |
| **Status** | ✅ Working as designed |

---

## Pulumi State vs Cluster Reconciliation

All 269 Pulumi state resources have corresponding cluster objects:

| Check | Result |
|-------|--------|
| 11 Namespaces | ✅ All present |
| 16 Helm releases | ✅ All deployed (Pulumi-managed ones — FluxCD HelmReleases are separate) |
| CRDs | ✅ 161 in cluster ≥ 45 from Pulumi (extras from Cilium, Longhorn, FluxCD) |
| ClusterSecretStore | ✅ `default` present |
| ExternalSecrets (Pulumi) | ✅ All 6 present and synced |
| PushSecrets (Pulumi) | ✅ All 4 present and synced |
| Certificates (Pulumi TLS) | ✅ All 4 present and Ready (openchoreo-ca, cp-gateway-tls, dp-gateway-tls, op-gateway-tls) |
| ClusterIssuers (Pulumi) | ✅ Both present (selfsigned-bootstrap, openchoreo-ca) |
| CiliumL2AnnouncementPolicy | ✅ `homelab-l2-policy` present |
| FluxCD GitRepository | ✅ `sample-gitops` present |
| FluxCD Kustomizations | ✅ All 5 present and Applied |
| FluxCD notifications | ✅ Provider + Alert present |

**No Pulumi-declared resources are missing from the cluster.**
