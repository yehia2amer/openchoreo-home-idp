# GKE Deployment Status & Known Issues

> **Date**: 2026-04-15
> **Cluster**: GKE Standard, `europe-west1-b`, project `pg-ae-n-app-173978`
> **Domain**: `idp.aistudio.consulting` (NOT configured)
> **Status**: Platform running — all pods healthy, zero external access

---

## 1. Deployment Summary

### Phase 1 — GKE Infrastructure (Pulumi)

**Status: ✅ COMPLETE — 71 resources**

| Resource Category | Count | Notes |
|---|---|---|
| GKE cluster (private, Dataplane v2) | 1 | `e2-standard-8` × 3 nodes (1 active) |
| Node pool | 1 | Workload Identity enabled |
| VPC + subnets | 3 | Node/Pod/Service CIDRs |
| Cloud NAT + Router | 2 | Required — org policy blocks external IPs |
| Artifact Registry | 1 | `europe-west1-docker.pkg.dev/pg-ae-n-app-173978/openchoreo` |
| GCP CAS (CA Pool + CA) | 2 | Created but issuer not wired (self-signed in use) |
| GCP Secret Manager | 1 | `backstage-secrets` secret created |
| Service Accounts (ESO + CAS) | 2 | Created, IAM bindings NOT applied (see §3) |
| FluxCD bootstrap | 1 | GitHub source + kustomization pointing to `clusters/gke/` |

### Phase 2 — FluxCD GitOps (6 Waves)

**Status: ✅ COMPLETE — all waves reconciled at rev `cac5049`**

| Wave | Contents | Status |
|---|---|---|
| 00-crds | cert-manager CRDs, ESO CRDs, Argo Workflows CRDs (vendored) | ✅ Applied |
| 01-prerequisites | 4 namespaces, cert-manager HelmRelease, ESO HelmRelease | ✅ Applied |
| 02-tls | Self-signed ClusterIssuer, root CA, platform certificates | ✅ Applied |
| 03-platform | Backstage, OpenChoreo API, kgateway, cluster-gateway, controller-manager, Argo | ✅ Applied |
| 04-registration | 4 registration jobs (data-plane, workflow-plane, observability-plane, default org) | ✅ Applied (all Complete) |
| 05-network | NetworkPolicies (allow-gateway-ingress in data-plane) | ✅ Applied |

### Pod Health (all namespaces)

All 8+ long-running pods pass readiness probes with **zero restarts**:
- `backstage`, `openchoreo-api`, `cluster-gateway`, `controller-manager`, `kgateway` (control-plane)
- `cluster-agent-dataplane` (data-plane)
- `argo-server`, `argo-workflow-controller`, `cluster-agent-workflowplane` (workflow-plane)

---

## 2. NO External Access — Port-Forward Only

**There are zero Gateways, zero HTTPRoutes, and zero Ingresses on the cluster.**

All services are ClusterIP. The only way to access them today:

```bash
# Backstage UI
kubectl port-forward -n openchoreo-control-plane svc/backstage 7007:7007

# OpenChoreo API
kubectl port-forward -n openchoreo-control-plane svc/openchoreo-api 8080:8080

# Argo Server UI
kubectl port-forward -n openchoreo-workflow-plane svc/argo-server 2746:443
```

### What's Missing for External Access

1. **Gateway resource** referencing GatewayClass `gke-l7-rilb` (Internal Load Balancer) or `kgateway`
2. **HTTPRoute resources** for each service
3. **DNS records** pointing `idp.aistudio.consulting` to the load balancer IP
4. **TLS certificates** — either via GCP CAS issuer (deferred) or self-signed certs bound to the Gateway

> **GatewayClass `gke-l7-rilb`** is available and Accepted on the cluster. It creates an internal GCE load balancer.
> **GatewayClass `kgateway`** is also available and Accepted (deployed by OpenChoreo's kgateway chart).

---

## 3. IAM Bindings — NOT Applied (Corporate Constraint)

**PwC's GCP org policy restricts all `setIamPolicy` permissions.** No role in their catalog grants this.

The 4 required IAM bindings are:

| Service Account | Role | Purpose |
|---|---|---|
| `openchoreo-eso@...` | `roles/secretmanager.secretAccessor` | ESO reads secrets from GCP Secret Manager |
| `openchoreo-eso@...` | `roles/iam.workloadIdentityUser` | Workload Identity for ESO pods |
| `openchoreo-cas@...` | `roles/privateca.certificateRequester` | cert-manager requests certs from CAS |
| `openchoreo-cas@...` | `roles/iam.workloadIdentityUser` | Workload Identity for cert-manager pods |

### Workaround

- Pulumi config: `skip_iam_bindings: true` — skips all 4 bindings
- Manual admin script: `pulumi/gke-cluster/prereqs/iam-setup.sh` — admin must run this separately
- **Impact**: ExternalSecret for `backstage-secrets` shows `SecretSyncedError` (ESO SA can't read GCP SM). GCP CAS issuer is non-functional.

### To Fix

Ask a GCP org admin to run:
```bash
cd pulumi/gke-cluster/prereqs
bash iam-setup.sh
```

---

## 4. Placeholder Resources on Cluster (NOT in Git)

These were created manually during deployment. They are **NOT tracked in the GitOps repo** and will be **lost on cluster wipe**.

| Resource | Namespace | Purpose | Status |
|---|---|---|---|
| `secret/backstage-secrets` | openchoreo-control-plane | App secrets for Backstage | Dummy values. ESO owns it but can't sync (IAM). |
| `configmap/cluster-gateway-ca` | openchoreo-data-plane | CA cert for cluster-gateway mTLS | Placeholder (52-char `ca.crt`, real is 113 chars) |
| `configmap/cluster-gateway-ca` | openchoreo-workflow-plane | CA cert for cluster-gateway mTLS | Same placeholder |
| `secret/cluster-agent-tls` | openchoreo-observability-plane | TLS cert for cluster-agent | Self-signed placeholder |

### To Make Durable

Option A: Add these as Kustomize resources in the GitOps repo (with SealedSecrets or SOPS for secrets).
Option B: Fix IAM bindings → ESO syncs `backstage-secrets` from GCP SM. For the CA certs, extract the real CA from the self-signed ClusterIssuer and commit the ConfigMaps.

---

## 5. Workarounds Applied During Deployment

### 5.1 Argo Workflows CRDs — Vendored

**Problem**: Argo Workflows Helm chart doesn't install CRDs when deployed via FluxCD's `installCRDs: false` default path, and the chart's CRD hook doesn't fire in GitOps.

**Workaround**: Vendored 8 minimal CRD files from Argo Workflows v3.6.2 into `infrastructure/base/00-crds/argo-workflows/`. These are applied in wave-00 before Argo deploys in wave-03.

**Risk**: CRD version drift if Argo chart is upgraded without updating vendored CRDs.

### 5.2 Kustomize Namespace Transformation

**Problem**: Kustomize's `namespace:` field rewrites ALL resources including `kind: Namespace` definitions, causing Namespace resources to target themselves.

**Workaround**: Namespace resources are in a separate kustomization WITHOUT the `namespace:` field. Wave kustomizations that set `namespace:` explicitly exclude namespace YAML files.

### 5.3 `$patch: delete` Doesn't Work on `dependsOn` Arrays

**Problem**: HelmRelease `dependsOn` arrays have no strategic merge key, so `$patch: delete` inside array items is ignored by Kustomize.

**Workaround**: Use JSON patches (`op: replace` or `op: remove`) in component kustomizations instead.

**Example** (`infrastructure/components/registry-cloud/kustomization.yaml`):
```yaml
patches:
  - target:
      kind: HelmRelease
      name: backstage
    patch: |
      - op: replace
        path: /spec/values/image/registry
        value: "europe-west1-docker.pkg.dev/pg-ae-n-app-173978/openchoreo"
```

### 5.4 Wave-03 Health Check Cascade

**Problem**: Wave-03 with `wait: true` would block indefinitely because HelmRelease readiness depends on all pods being ready, and some pods take >5min.

**Workaround**: Set `wait: false` on wave-03's Flux Kustomization. Added explicit `healthChecks:` listing the 3 platform HelmReleases (backstage, openchoreo-api, argo-workflows) with extended timeout.

### 5.5 HelmRelease Stalled Recovery

**Problem**: When a HelmRelease exceeds its retry count, it enters `Stalled` state and never retries.

**Workaround**: `flux suspend helmrelease <name> && flux resume helmrelease <name>` resets the failure counter.

### 5.6 Private Cluster + Cloud NAT

**Problem**: GCP org policy `constraints/compute.vmExternalIpAccess` with `allValues: DENY` blocks all external IPs on VMs.

**Workaround**: GKE private cluster with Cloud NAT for outbound internet access. Nodes have no external IPs. Master authorized network configured for kubectl access.

### 5.7 External Secrets v1 API Only

**Problem**: ESO v2.0.1 CRDs only serve `external-secrets.io/v1`. The `v1beta1` version is `served=false, storage=false`.

**Workaround**: All ESO resources (ClusterSecretStore, ExternalSecret) use `apiVersion: external-secrets.io/v1`. Any upstream examples using `v1beta1` must be converted.

---

## 6. Component Stubs (Deferred)

| Component | Path | Status | Notes |
|---|---|---|---|
| `issuer-gcp-cas` | `infrastructure/components/issuer-gcp-cas/` | ❄ DEFERRED | `resources: []` stub. Requires IAM fix first. Using self-signed. |
| `observability-cloud` | `infrastructure/components/observability-cloud/` | ❄ DEFERRED | Stub. Using default GCP Cloud Monitoring/Logging. |
| `secrets-gcp-sm` | `infrastructure/components/secrets-gcp-sm/` | ✅ IMPLEMENTED | ClusterSecretStore + ExternalSecret. Blocked by IAM at runtime. |
| `registry-cloud` | `infrastructure/components/registry-cloud/` | ✅ IMPLEMENTED | JSON patch for Artifact Registry URL. |

---

## 7. Remaining Open Work (Beads Issues)

| Issue | Priority | Description |
|---|---|---|
| `p2u` | P1 | Remove 'gcp' from `DEV_STACKS` — cleanup task |
| `dbp` | P1 | FluxCD Full Control Migration epic (ongoing, not GKE-specific) |
| `bvr.3.3` | P1 | Backstage-fork OIDC login fails at Thunder login page |
| `dbp.33` | P2 | Pin kubernetes-replicator HelmRelease chart version |
| `l71` | P2 | Verify log/trace pipeline after OpenSearch removal |
| `1iw` | P2 | Verify observer Helm chart handles missing openSearchSecretName |
| Spikes (`bvr.*`) | P2 | Ephemeral envs, AI agents, Agent Gateway (future work) |
| `dbp.36` | P3 | Evaluate trust-manager vs kubernetes-replicator |
| `dbp.34` | P3 | Enable drift detection on FluxCD resources |
| `k0c` | P3 | Automate cleanup of orphaned postgres PVs |
| `dbp.37` | P4 | Document Pulumi-to-FluxCD state handoff |

---

## 8. Clean-Wipe Reproduction Checklist

To redeploy from scratch on a new GKE cluster:

### Prerequisites
1. GCP project with APIs enabled: GKE, Artifact Registry, Certificate Authority Service, Secret Manager
2. `gcloud` authenticated as `yehia.amer@gcp.pwc.com`
3. Pulumi CLI installed, passphrase: `openchoreo-talos-baremetal`
4. GitHub PAT with repo access (encrypted in Pulumi config)

### Phase 1 — Infrastructure
```bash
cd pulumi/gke-cluster
pulumi up --stack gcp
```
- Deploys 71 resources (VPC, GKE, NAT, CAS, SM, AR, SAs, FluxCD bootstrap)
- If IAM is restricted: set `skip_iam_bindings: true` in `Pulumi.gcp.yaml`
- Ask admin to run `prereqs/iam-setup.sh` separately

### Phase 2 — GitOps
FluxCD auto-reconciles from `clusters/gke/` in the gitops repo. No manual steps.

### Phase 2.5 — Manual Placeholders (until IAM is fixed)
```bash
# Backstage secrets (dummy values — ESO will overwrite once IAM works)
kubectl create secret generic backstage-secrets \
  -n openchoreo-control-plane \
  --from-literal=GITHUB_TOKEN=placeholder \
  --from-literal=AUTH_GITHUB_CLIENT_ID=placeholder \
  --from-literal=AUTH_GITHUB_CLIENT_SECRET=placeholder \
  --from-literal=POSTGRES_PASSWORD=placeholder

# Cluster gateway CA placeholders
kubectl create configmap cluster-gateway-ca \
  -n openchoreo-data-plane \
  --from-literal=ca.crt="placeholder-replace-with-real-ca"
kubectl create configmap cluster-gateway-ca \
  -n openchoreo-workflow-plane \
  --from-literal=ca.crt="placeholder-replace-with-real-ca"

# Observability plane TLS placeholder
kubectl create secret tls cluster-agent-tls \
  -n openchoreo-observability-plane \
  --cert=/dev/null --key=/dev/null  # Replace with real self-signed
```

### Phase 3 — Verify
```bash
# All pods running
kubectl get pods -A | grep -E 'openchoreo|argo'

# All Flux kustomizations reconciled
flux get kustomizations

# All HelmReleases ready
flux get helmreleases -A

# Health check
kubectl port-forward -n openchoreo-control-plane svc/backstage 7007:7007
# Visit http://localhost:7007
```

---

## 9. Architecture Decisions (Locked)

| Decision | Choice | ADR |
|---|---|---|
| IaC boundary | Pulumi = infra, FluxCD = K8s resources | ADR-001 |
| GKE variant | GKE Standard + Dataplane v2 | — |
| TLS | Self-signed (GCP CAS deferred) | — |
| Secrets | GCP Secret Manager + ESO (blocked by IAM) | — |
| Registry | GCP Artifact Registry | — |
| Networking | Private cluster, Cloud NAT, no external IPs | Org policy constraint |
| Observability | GCP Cloud Monitoring/Logging (native) | Deferred |
| Workload Identity | All service accounts | — |
| Pulumi provider | `pulumi-gcp` (NOT `pulumi-gcp-native`) | — |
| GatewayClass | `gke-l7-rilb` (internal LB) available, not yet used | — |

---

## 10. IP Range Layout

| Range | CIDR | Purpose |
|---|---|---|
| Node subnet | `10.10.0.0/20` | GKE nodes |
| Pods | `10.20.0.0/16` | Pod IPs |
| Services | `10.30.0.0/20` | ClusterIP services |
| Master CIDR | `172.16.0.0/28` | GKE control plane |
