# Deployment Ordering & Dependencies

> Generated: 2026-04-07 | Epic: 1gz.6 | Stack: talos-baremetal

## Overview

This document captures the exact deployment sequence from `pulumi/__main__.py` for reproducing the OpenChoreo environment on a clean cluster. Each step lists hard prerequisites, timeouts, parallelism opportunities, and known gotchas.

**Active feature flags** (talos-baremetal stack):
- `cilium_pre_installed: true` (Talos embeds Cilium — Step 0 skipped, Step 0.5 runs)
- `enable_flux: true`
- `enable_observability: true`
- `enable_openobserve: true`
- `enable_rca: true`
- `enable_demo_app_bootstrap: true`
- `tls_enabled: true`

---

## Timeout Constants

| Constant | Value | Used By |
|---|---|---|
| `TIMEOUT_DEFAULT` | 1200s (20m) | Most Helm charts, Thunder, Odigos |
| `TIMEOUT_OPENSEARCH` | 1800s (30m) | OpenSearch logs/traces charts |
| `TIMEOUT_OBS_PLANE` | 2400s (40m) | Observability Plane core chart |
| `TIMEOUT_WAIT` | 600s (10m) | ClusterSecretStore readiness |
| `TIMEOUT_TLS_WAIT` | 240s (4m) | OpenBao pod readiness |
| `TIMEOUT_FLUX_WAIT` | 1200s (20m) | Flux deployments + Kustomization readiness |
| `SLEEP_AFTER_GATEWAY_API` | 10s | CRD propagation delay |
| `SLEEP_AFTER_OPENBAO` | 15s | OpenBao postStart script completion |
| `SLEEP_AFTER_THUNDER` | 15s | Thunder bootstrap scripts |
| `SLEEP_AFTER_ESO_SYNC` | 15s | ExternalSecret sync propagation |

---

## Deployment Sequence

### Step 0: Cilium CNI + Gateway API CRDs (SKIPPED on talos-baremetal)

**Condition**: `cni_mode == "cilium" AND NOT cilium_pre_installed`

On talos-baremetal, Cilium is pre-installed by the nested Talos project (`talos-cluster-baremetal/`). This step only runs on k3d/Rancher Desktop where Pulumi installs Cilium from scratch.

**What it would do**:
1. Apply Gateway API CRDs from upstream URL
2. Install Cilium Helm chart with Gateway API controller enabled

**Hard prerequisites**: K8s provider configured  
**Timeout**: `TIMEOUT_DEFAULT` (20m)

---

### Step 0.5: Cilium L2 Announcements (standalone)

**Condition**: `cilium_l2_announcements_enabled AND cilium_pre_installed` (✅ active on talos-baremetal)

**Source**: `components/cilium_l2.py`

**Creates**:
1. `CiliumLoadBalancerIPPool` — IP pool from `cilium_l2_ip_pool_cidrs` config
2. `CiliumL2AnnouncementPolicy` — L2 ARP announcements on configured interfaces

**Hard prerequisites**: None (runs independently of everything else)  
**Timeout**: None (simple CR creation)  
**Parallelism**: ✅ Runs in parallel with Step 1 (no dependency chain)

**Gotcha**: Without this step, LoadBalancer Services get no external IP. The CP, DP, OP, and gateway-shared Gateways will all show `<pending>` for their external addresses.

---

### Step 1: Prerequisites

**Source**: `components/prerequisites.py`

**Hard prerequisites**: Step 0 Cilium install (if applicable), otherwise none  
**Total sub-steps**: 10 internal sequential stages

#### Internal Ordering:

```
1. Gateway API CRDs ─────┐  (skipped if Cilium mode — CRDs installed in Step 0)
   sleep 10s              │
                          ▼
2. cert-manager NS ──── cert-manager Helm ──┐
                                             │
3. ESO NS ─────────── ESO Helm ────┐        │
                                    │        │
4. CP Namespace ◄───────────────────┘────────┘  (depends on cert-manager)
   DP Namespace ◄───────────────────┘────────┘  (depends on cert-manager)
                                    │
5. kgateway-crds Helm ──────────────┤
   GatewayClass (Cilium) ──────────┤         (depends on kgateway-crds + Cilium)
                                    │
6. OpenBao NS ──── OpenBao Helm ───┤         (depends on ESO)
   WaitPodReady(openbao-0) ────────┤
   sleep 15s (postStart) ──────────┤
                                    │
7. Push Secrets (conditional):      │
   - push-git-secrets              │         (depends on OpenBao postStart)
   - push-backstage-fork-secrets   │
   - push-openobserve-creds        │
   - push-dev-secrets              │
                                    │
8. ESO ServiceAccount ──────────────┤
   ClusterSecretStore ──────────────┤         (depends on ESO + OpenBao postStart)
   WaitCondition(CSS Ready) ────────┤
                                    │
   PushSecret CRs (4x) ────────────┤         (depends on CSS Ready + source secrets)
   sleep 15s (pushsecret-sync) ─────┘
                                    
9. workflows-default NS                      (independent, depends on Gateway API only)

10. CoreDNS rewrite (if platform requires)   (independent)
```

**Key outputs consumed downstream**:
- `cluster_secret_store_ready` → Control Plane (Step 2)
- `control_plane_ns` → TLS Setup (Step 1.5), Control Plane (Step 2)
- `data_plane_ns` → TLS Setup (Step 1.5), Data Plane (Step 3)

**Parallelism within Step 1**:
- CP NS and DP NS can be created in parallel (both depend only on cert-manager)
- kgateway-crds is independent of OpenBao chain
- push-git-secrets, push-backstage-fork-secrets, push-openobserve-creds, push-dev-secrets are all parallel (all depend on OpenBao postStart)

**Timeout**: `TIMEOUT_DEFAULT` (20m) for cert-manager, ESO, OpenBao, kgateway-crds Helm charts. `TIMEOUT_TLS_WAIT` (4m) for OpenBao pod readiness. `TIMEOUT_WAIT` (10m) for ClusterSecretStore readiness.

**Gotchas**:
- OpenBao postStart script runs `setup.sh` which seeds the vault. The 15s sleep is a safety margin — if the script takes longer, ClusterSecretStore creation may fail.
- ClusterSecretStore depends on **both** ESO and OpenBao being ready. If either fails, the entire downstream chain (CP, DP, WP) is blocked.
- PushSecret sync is the final gate. All secrets must be in OpenBao before any plane can start.

---

### Step 1.5: TLS Setup (optional)

**Condition**: `tls_enabled: true` (✅ active)

**Source**: `components/tls_setup.py`

**Hard prerequisites**: `control_plane_ns`, `data_plane_ns` (from Step 1)

**Creates** (sequential chain):
1. `ClusterIssuer/selfsigned-bootstrap` — self-signed issuer
2. `Certificate/openchoreo-ca` — CA cert (ECDSA P256) in `cert-manager` NS
3. `ClusterIssuer/openchoreo-ca` — CA-backed issuer
4. **Parallel from here**:
   - `Certificate/cp-gateway-tls` — wildcard cert in CP NS
   - `Certificate/dp-gateway-tls` — wildcard cert in DP NS
   - `Certificate/op-gateway-tls` — wildcard cert in OP NS

**Key outputs consumed downstream**:
- `tls.cp_cert` → Control Plane (Step 2) depends_on
- `tls.dp_cert` → Data Plane (Step 3) depends_on
- `tls.op_cert` → Observability Plane (Step 5) depends_on

**Timeout**: None (cert-manager handles issuance; Pulumi default applies)

**Gotcha**: All three wildcard certs depend on the CA ClusterIssuer, which depends on the CA Certificate. If cert-manager is slow to issue the CA cert, all three plane certs are blocked.

---

### Step 2: Control Plane

**Source**: `components/control_plane.py`

**Hard prerequisites**:
- `cluster_secret_store_ready` (from Step 1 — PushSecret sync complete)
- `control_plane_ns` (from Step 1)
- `tls.cp_cert` (from Step 1.5, if TLS enabled)

**Internal ordering**:
1. Thunder NS → Thunder bootstrap ConfigMap → Thunder Helm Release (v3)
2. `sleep 15s` → Thunder setup-rerun Job (re-runs bootstrap scripts idempotently)
3. Backstage ExternalSecret → `sleep 15s` (ESO sync)
4. Control Plane Helm chart (v3.Release) — depends on Thunder + ESO sync
5. Workflow CRD patching (k3d-patch mode only — not on talos-baremetal)
6. Label CP namespace

**Key outputs**: `cp.helm_chart` — consumed by Steps 3, 4, 5, 6, 6.5, 7, 8

**Timeout**: `TIMEOUT_DEFAULT` (20m) for Thunder and CP chart

**Gotchas**:
- Thunder uses `helm.v3.Release` (not v4.Chart) because it has Helm lifecycle hooks. Using v4 silently drops pre-install/post-install hooks.
- The CP chart also uses `helm.v3.Release` because it contains cert-manager Certificate resources that fail client-side rendering in v4.
- Thunder bootstrap scripts include `60-assign-themes.sh` and `61-backstage-fork-app.sh` (Flux-conditional). The rerun Job ensures these run even on `pulumi up` after initial install.

---

### Step 3: Data Plane

**Source**: `components/data_plane.py`

**Hard prerequisites**:
- `cp.helm_chart` (from Step 2 — CP must be running)
- `data_plane_ns` (from Step 1)
- `tls.dp_cert` (from Step 1.5, if TLS enabled)

**Internal ordering**:
1. Copy CA cert to DP namespace
2. DP Helm chart (v3.Release)
3. `CiliumClusterwideNetworkPolicy/allow-gateway-ingress` (Cilium mode only)
4. Register `ClusterDataPlane/default` via API

**Key outputs**: `dp.register_cmd` — consumed by Steps 6, 7, 8

**Timeout**: `TIMEOUT_DEFAULT` (20m)

**Parallelism**: Steps 3 and 4 can run **in parallel** — both depend on `cp.helm_chart` but not on each other.

---

### Step 4: Workflow Plane

**Source**: `components/workflow_plane.py`

**Hard prerequisites**: `cp.helm_chart` (from Step 2)

**Internal ordering**:
1. WP Namespace (with privileged PodSecurity labels)
2. Docker Registry Helm chart (v4.Chart, HTTP repo)
3. Copy CA cert to WP namespace
4. WP Helm chart (v3.Release)
5. Apply Workflow Templates via `kubectl apply` (curl + sed pipeline)
6. Register `ClusterWorkflowPlane/default` via API

**Key outputs**: `wp.register_cmd` — consumed by Steps 6, 7, 8

**Timeout**: `TIMEOUT_DEFAULT` (20m) for WP chart. Docker registry: 10m.

**Parallelism**: ✅ Steps 3 and 4 run in parallel (both depend only on CP chart).

**Gotchas**:
- Workflow templates are fetched from GitHub URLs and patched inline via `sed` to replace k3d-specific endpoints. Network issues during `curl` will fail this step.
- The WP chart uses `helm.v3.Release` (cert-manager CRDs required).

---

### Step 5: Observability Plane (optional)

**Condition**: `enable_observability: true` (✅ active)

**Source**: `components/observability_plane.py`

**Hard prerequisites**:
- `cp.helm_chart` (from Step 2)
- `tls.op_cert` (from Step 1.5, if TLS enabled)

**Internal ordering**:
1. OP Namespace
2. Copy CA cert
3. ExternalSecrets (parallel): opensearch-admin, observer-opensearch, observer-secret, rca-agent (if `enable_rca`)
4. OP core Helm chart (v3.Release) — **longest step**, `TIMEOUT_OBS_PLANE` = 40m
5. **Parallel from core chart**:
   - OpenSearch logging module (`TIMEOUT_OPENSEARCH` = 30m)
   - OpenSearch tracing module (`TIMEOUT_OPENSEARCH` = 30m)
   - Prometheus metrics module (`TIMEOUT_DEFAULT` = 20m)
   - OpenObserve logging module (if `enable_openobserve`) (`TIMEOUT_DEFAULT` = 20m)
   - OpenObserve tracing module (depends on OO logging)
   - OpenObserve UI HTTPRoute (depends on OO logging)
   - Fluent Bit dual-ship ConfigMap (depends on OO logging + OpenSearch logging)
6. Register `ClusterObservabilityPlane/default` via API

**Key outputs**: `obs.register_cmd` — consumed by Steps 6, 6.5

**Timeout**: Core chart = 40m. Sub-modules = 20-30m each. This is the **slowest step** in the entire pipeline.

**Parallelism**:
- Step 5 runs in parallel with Steps 3 and 4 (all depend only on CP chart + TLS)
- Within Step 5, OpenSearch logs/traces and Prometheus all run in parallel after core chart
- OpenObserve tracing depends on OpenObserve logging (sequential)

**Gotchas**:
- The core OP chart is the longest single Helm install at 40 minutes timeout. On bare-metal with slow disk, it can take 15-25 minutes.
- OpenSearch logging chart also installs Fluent Bit DaemonSet. When OpenObserve is enabled, Pulumi overwrites the Fluent Bit ConfigMap with a dual-ship version (outputs to both OpenSearch and OpenObserve).
- The `rca-agent` ExternalSecret is only created when `enable_rca: true`.

---

### Step 6: Link Planes

**Condition**: Observability Plane was deployed (obs is not None)

**Source**: `components/link_planes.py`

**Hard prerequisites**: `dp.register_cmd`, `wp.register_cmd`, `obs.register_cmd` (all three plane registrations)

**What it does**: Patches `ClusterDataPlane/default` and `ClusterWorkflowPlane/default` with `observabilityPlaneRef` pointing to `ClusterObservabilityPlane/default`.

**Timeout**: None (dynamic provider, kubectl patch)

---

### Step 6.5: Odigos (optional)

**Condition**: `enable_openobserve AND enable_observability` (✅ active)

**Source**: `components/odigos.py`

**Hard prerequisites**: `obs.register_cmd` (OP registration complete)

**Internal ordering**:
1. odigos-system Namespace (privileged PodSecurity — eBPF requires hostPID)
2. Odigos Helm chart (v3.Release)
3. Action CR: `openchoreo-labels` (extract OpenChoreo pod labels into trace attributes)
4. Destination CR: `openobserve-via-collector` (send traces to OTel Collector → OpenObserve)

**Timeout**: `TIMEOUT_DEFAULT` (20m)

**Gotchas**:
- Odigos odiglet DaemonSet needs privileged pods with hostPID access. On Talos, the namespace must have `pod-security.kubernetes.io/enforce: privileged`.
- Go eBPF instrumentation requires DWARF debug symbols. Stripped binaries (`-ldflags '-s -w'`) will silently fail instrumentation.

---

### Step 7: Flux CD & GitOps (optional)

**Condition**: `enable_flux AND gitops_repo_url` (✅ active)

**Source**: `components/flux_gitops.py`

**Hard prerequisites**: `cp.helm_chart`, `dp.register_cmd`, `wp.register_cmd`

**Internal ordering**:
1. Install Flux CD from local `flux-install.yaml` manifest
2. WaitDeployments: source-controller, kustomize-controller, helm-controller
3. Git credentials Secret (if `github_pat` set)
4. GitRepository: `sample-gitops` → openchoreo-gitops repo
5. Kustomizations (sequential dependency chain):
   - `oc-namespaces` (parallel with oc-platform-shared)
   - `oc-platform-shared` (parallel with oc-namespaces)
   - `oc-infrastructure` (parallel with oc-namespaces, includes backstage-fork health check)
   - `oc-platform` (depends on oc-namespaces + oc-platform-shared)
   - `oc-demo-projects` (depends on oc-platform)
6. WaitCondition: oc-demo-projects Ready
7. Notification Provider (Telegram or generic webhook)
8. Alert CR
9. Patch oc-demo-projects with ReleaseBinding health checks

**Timeout**: `TIMEOUT_FLUX_WAIT` (20m) for controller deployments + Kustomization readiness

**Parallelism**: Step 7 runs in parallel with Steps 5, 6, 6.5 (only needs CP + DP + WP).

**Gotchas**:
- Flux is installed from a **local** `flux-install.yaml` file (8,612 lines), not from the Flux Helm chart. This is applied via `k8s.yaml.v2.ConfigGroup`.
- The Kustomization dependency chain (`oc-namespaces` → `oc-platform` → `oc-demo-projects`) is enforced both by Flux `dependsOn` and by Pulumi `depends_on`. Breaking this order causes Flux reconciliation failures.
- Flux controllers (image-automation, image-reflector, notification) are installed but not all are actively used.

---

### Step 8: Integration Tests

**Source**: `components/integration_tests.py`

**Hard prerequisites**: `cp.helm_chart`, `dp.register_cmd`, `wp.register_cmd`, `obs.register_cmd` (if observability enabled)

**What it does**: Creates ~35 Pulumi dynamic resources that each perform a live health check (deployment readiness, CRD existence, HTTPRoute status, HTTP endpoint checks, ExternalSecret sync, PushSecret sync, ClusterSecretStore readiness, Gateway programmed status).

Tests always re-run on every `pulumi up` (diff returns `changes=True`).

**Timeout**: Individual tests use 60s for HTTP checks. Overall governed by Pulumi provider defaults.

---

### Step 9: Demo App Bootstrap (optional)

**Condition**: `enable_demo_app_bootstrap AND enable_flux AND github_pat` (✅ active)

**Source**: `components/demo_app_bootstrap.py`

**Hard prerequisites**: Same as Step 8 (test_depends)

**Phases** (strictly sequential):
1. **Build backends** (parallel): trigger WorkflowRun for `document-svc` and `collab-svc` — timeout 20m each
2. **Build frontend** (sequential after backends): trigger WorkflowRun for `frontend` — timeout 20m
3. **Merge PRs** (parallel after all builds): merge release branches for all 3 components — timeout 2m each
4. **Force Flux reconcile**: `flux reconcile source git sample-gitops` — timeout 3m
5. **Wait ReleaseBindings**: verify `document-svc-development`, `collab-svc-development`, `frontend-development` are Ready — timeout 5m each

**Total estimated time**: 30-45 minutes on bare-metal (builds take ~11m each)

**Gotchas**:
- This is the slowest overall step. Bare-metal builds use Podman in privileged pods and are CPU/IO bound.
- The `workflows-default` namespace must already exist with privileged PodSecurity labels (created in Step 1).
- Requires valid `github_pat` for PR creation and merge.

---

## Dependency Graph (Critical Path)

```
Step 0.5 (CiliumL2) ─────────────────────────────────────────────────── (independent)

Step 1 (Prerequisites) ──┬── Step 1.5 (TLS) ──┬── Step 2 (CP) ──┬── Step 3 (DP) ──┐
                         │                     │                 ├── Step 4 (WP) ──┤
                         │                     │                 ├── Step 5 (OP) ──┤
                         │                     │                 │                 │
                         │                     │                 │  Step 6 (Link) ◄┤ (DP+WP+OP)
                         │                     │                 │  Step 6.5 ◄─────┤ (OP)
                         │                     │                 │                 │
                         │                     │                 ├── Step 7 (Flux) │ (CP+DP+WP)
                         │                     │                 │                 │
                         │                     │                 └── Step 8 (Tests)│ (CP+DP+WP+OP)
                         │                     │                     Step 9 (Demo) │ (same as 8)
```

**Critical path** (longest wall-clock time):
```
Step 1 (Prerequisites, ~5-10m)
  → Step 1.5 (TLS, ~1-2m)
    → Step 2 (Control Plane, ~5-10m)
      → Step 5 (Observability Plane, ~15-25m)  ← BOTTLENECK
        → Step 6.5 (Odigos, ~3-5m)
          → Step 9 (Demo Bootstrap, ~30-45m)  ← LONGEST
```

**Estimated total**: 60-100 minutes for a full clean deployment on bare-metal.

---

## Parallelism Opportunities

| Steps | Can Run In Parallel | Reason |
|---|---|---|
| 0.5 + 1 | ✅ | CiliumL2 has no dependencies |
| 3 + 4 | ✅ | Both depend only on CP (Step 2) |
| 3 + 4 + 5 | ✅ | All three depend only on CP + TLS certs |
| 5 sub-modules | ✅ | OpenSearch logs/traces/Prometheus all parallel after OP core chart |
| 7 (Flux) + 5 (OP) | ✅ | Flux needs CP+DP+WP but not OP |
| 8 (Tests) + 9 (Demo) | ❌ | Same depends, but tests are fast; demo runs after |

---

## Clean Cluster Reproduction Checklist

1. **Nested project first**: Run `talos-cluster-baremetal` Pulumi stack to provision Talos + Cilium + Longhorn + Gateway API CRDs + snapshot-controller
2. **Verify prerequisites**: Cilium running, Longhorn ready, Gateway API CRDs installed, kubeconfig accessible
3. **Set secrets**: `github_pat`, `openbao_root_token`, `opensearch_password`, `openobserve_admin_password`, `flux_telegram_bot_token` (optional)
4. **Run `pulumi up -s talos-baremetal`** — the deployment sequence handles everything else
5. **Wait for Demo Bootstrap** (Step 9) — this is the final gate
6. **Verify via Integration Tests** — Step 8 validates all components

---

## Known Issues for Clean Reproduction

| Issue | Impact | Mitigation |
|---|---|---|
| OpenBao postStart timing | CSS may fail if script exceeds 15s sleep | Increase `SLEEP_AFTER_OPENBAO` to 30s for safety |
| Workflow template fetch | Network-dependent curl from GitHub | Pre-download templates or use local files |
| Bare-metal build times | 11+ minutes per component build | Ensure adequate CPU/RAM; reduce parallelism if OOM |
| Orphaned PVs from prior runs | 20+ Released PVs consuming ~54Gi | `kubectl delete pv` Released PVs before redeploy |
| DP/OP Gateway pending IPs | CiliumL2 pool exhaustion or misconfigured interfaces | Verify `cilium_l2_ip_pool_cidrs` covers enough IPs |
| Dead code: otel_operator.py | No impact — never imported | Clean up in next refactor |
