# PwC GCP Org Policy & IAM Request Guide

> **Purpose**: Reference for all agents and developers working on OpenChoreo GKE deployments within PwC's GCP environment. These constraints are NON-NEGOTIABLE org-level policies.

## Critical Org Policy Constraints

### 1. `constraints/iam.disableServiceAccountKeyCreation`
- **Impact**: You CANNOT create GCP Service Account keys via `gcloud`, Pulumi, Terraform, or any API call.
- **Workaround**: Request key creation through the **Global Cloud Requests** portal (see below).
- **Pulumi flag**: `skip_sa_key_creation: true` in stack config.

### 2. IAM Binding Restrictions
- **Impact**: You CANNOT grant IAM roles to service accounts via `gcloud iam`, Pulumi, or GCP Console.
- **Workaround**: Request IAM bindings through the **Global Cloud Requests** portal.
- **Pulumi flag**: `skip_iam_bindings: true` in stack config.

### 3. Google Managed Keys Preferred
- **Org guidance**: For apps/services running within GCP, use Google managed keys (Workload Identity, metadata server). User-managed keys must be rotated every 90 days.
- **GKE recommendation**: Use Workload Identity to let KSAs act as GSAs without manual keys.
- **Current reality**: All four GCP service accounts now use Workload Identity. Migration from SA key files completed 2026-04-18. See [WI Migration Path](#wi-migration-path) for details.

## How to Request GCP Changes

### Global Cloud Requests Portal
All IAM role grants, SA key creation, and privileged operations must go through PwC's **Global Cloud Requests** custom portal. You CANNOT:
- Run `gcloud iam service-accounts keys create`
- Run `gcloud projects add-iam-policy-binding`
- Run `gcloud artifacts repositories add-iam-policy-binding`
- Use Pulumi/Terraform to create IAM bindings or SA keys
- Use the GCP Console to modify IAM

### What to Request (Template)

When filing a portal request, specify:
1. **Service Account Email**: e.g., `openchoreo-ar-push@pg-ae-n-app-173978.iam.gserviceaccount.com`
2. **Role Needed**: Use the exact `role_value` from `pwc_gcp_roles.json`
3. **Scope**: Project-level (`pg-ae-n-app-173978`) or resource-level (specific AR repo, etc.)
4. **Justification**: Why this role is needed

### Available Roles Reference
The file `pwc_gcp_roles.json` in the IDP repo root contains ALL roles available through the portal, organized by service. Key roles for OpenChoreo:

| Service | Role | Value | Purpose |
|---------|------|-------|---------|
| Artifact Registry | Writer | `roles/artifactregistry.writer` | Push container images |
| Artifact Registry | Reader | `roles/artifactregistry.reader` | Pull container images |
| Artifact Registry | Repo Admin | `roles/artifactregistry.repoAdmin` | Manage AR repos |
| Secret Manager | Accessor | `roles/secretmanager.secretAccessor` | ESO reads secrets |
| Secret Manager | Admin | `roles/secretmanager.admin` | Create/manage secrets |
| IAM | Workload Identity User | `roles/iam.workloadIdentityUser` | WI federation |
| IAM | SA Token Creator | `roles/iam.serviceAccountTokenCreator` | Create OAuth tokens |
| IAM | SA User | `roles/iam.serviceAccountUser` | Run as SA |
| Kubernetes Engine | Admin | `roles/container.admin` | Full GKE access |
| Kubernetes Engine | Developer | `roles/container.developer` | K8s API access |
| Compute Engine | Network Admin | `roles/compute.networkAdmin` | VPC/firewall mgmt |

## OpenChoreo Service Accounts

| SA Email | Purpose | Roles Needed |
|----------|---------|--------------|
| `openchoreo-eso@pg-ae-n-app-173978.iam.gserviceaccount.com` | External Secrets Operator | `roles/secretmanager.secretAccessor` |
| `openchoreo-cas@pg-ae-n-app-173978.iam.gserviceaccount.com` | cert-manager CAS issuer | `roles/privateca.certificateRequester` |
| `openchoreo-dns@pg-ae-n-app-173978.iam.gserviceaccount.com` | ExternalDNS + cert-manager DNS-01 | `roles/dns.admin` (on DNS project `pg-ae-n-app-237049`) |
| `openchoreo-ar-push@pg-ae-n-app-173978.iam.gserviceaccount.com` | Argo Workflows image push | `roles/artifactregistry.writer` |

## SA Key → Secret Manager → ESO Flow

Since we can't use Workload Identity (can't self-service the binding), the auth flow is:

```
[Portal creates SA key] → [Upload to GCP Secret Manager] → [ESO ExternalSecret syncs to K8s] → [Pod mounts secret]
```

### Manual Steps After Portal Approval
```bash
# Upload SA key to Secret Manager (this CAN be done by developer)
gcloud secrets versions add <secret-name> \
  --project=pg-ae-n-app-173978 \
  --data-file=/path/to/downloaded-key.json

# Verify ESO synced it
kubectl get externalsecret -A | grep <secret-name>
kubectl get secret <k8s-secret-name> -n <namespace> -o jsonpath='{.data}'
```

### Pulumi Config for PwC Environments
```yaml
# Pulumi.<stack>.yaml — required for PwC GCP projects
config:
  openchoreo:skip_iam_bindings: "true"
  openchoreo:skip_sa_key_creation: "true"
```

These flags make Pulumi create the SA and Secret Manager shell, but skip key generation and IAM bindings (which must go through the portal).

## Long-Term Roadmap

1. **Completed**: All four GSAs use Workload Identity — ESO, CAS, DNS, AR-push
2. **Retired**: SA key file path (secretRef + ESO) removed from ExternalDNS and registry-cloud components
3. **Ideal**: Full Workload Identity with no manual keys — ✅ ACHIEVED

---

## WI Migration Path

This section documents the migration from the secretRef exception state to full Workload Identity for all four OpenChoreo GCP service accounts. **Migration completed 2026-04-18.**

### Validation Evidence

- **Date**: 2026-04-18
- **Validated**: ExternalDNS (Cloud DNS cross-project), cert-manager (Cloud DNS cross-project), AR-push (Artifact Registry)
- **Method**: Manual `kubectl run` test pods with WI-annotated service accounts, then `gcloud` API calls from inside each pod to confirm token exchange and API access
- **Result**: All three consumers confirmed working via Workload Identity with no SA key files mounted

### 1. Current State — COMPLETED (2026-04-18)

All four GSAs now use Workload Identity. The SA key file exception path for DNS and AR-push has been retired. Pulumi creates WI bindings in the `if not skip_iam_bindings:` block; SA keys are only created in the `if skip_iam_bindings:` fallback block for restricted environments.

| GSA | Auth Method | K8s Secret | Status |
|---|---|---|---|
| `openchoreo-eso@pg-ae-n-app-173978.iam.gserviceaccount.com` | Workload Identity | none (WI, no key) | ✅ WI active |
| `openchoreo-cas@pg-ae-n-app-173978.iam.gserviceaccount.com` | Workload Identity | none (WI, no key) | ✅ WI active |
| `openchoreo-dns@pg-ae-n-app-173978.iam.gserviceaccount.com` | Workload Identity | none (WI, no key) | ✅ WI active (migrated 2026-04-18) |
| `openchoreo-ar-push@pg-ae-n-app-173978.iam.gserviceaccount.com` | Workload Identity | none (WI, no key) | ✅ WI active (migrated 2026-04-18) |

The secretRef path has been retired. All four GSAs now authenticate via the GKE metadata server.

### 2. Target State — ACHIEVED

All four GSAs use Workload Identity. No SA key files exist in the active system.

| GSA | Target KSA | Namespace | WI Binding Command |
|---|---|---|---|
| `openchoreo-eso@...` | `external-secrets` | `external-secrets` | see section 3 |
| `openchoreo-cas@...` | `google-cas-issuer` | `cert-manager` | see section 3 |
| `openchoreo-dns@...` | ExternalDNS SA + cert-manager SA | `kube-system` / `cert-manager` | see section 3 |
| `openchoreo-ar-push@...` | Argo Workflow execution SA | `workflows-default` | see section 3 |

All four GSAs are in target state. WI bindings for DNS and AR-push were created by Pulumi and confirmed via live cluster validation on 2026-04-18.

### 3. What to Request via Portal

File these requests through the Global Cloud Requests portal. Include the exact `gcloud` command as justification so the portal team can verify the scope.

**DNS GSA — WI binding for ExternalDNS:**
```bash
gcloud iam service-accounts add-iam-policy-binding \
    openchoreo-dns@pg-ae-n-app-173978.iam.gserviceaccount.com \
    --project=pg-ae-n-app-173978 \
    --member="serviceAccount:pg-ae-n-app-173978.svc.id.goog[kube-system/external-dns]" \
    --role="roles/iam.workloadIdentityUser"
```

**DNS GSA — WI binding for cert-manager DNS-01 solver:**
```bash
gcloud iam service-accounts add-iam-policy-binding \
    openchoreo-dns@pg-ae-n-app-173978.iam.gserviceaccount.com \
    --project=pg-ae-n-app-173978 \
    --member="serviceAccount:pg-ae-n-app-173978.svc.id.goog[cert-manager/cert-manager]" \
    --role="roles/iam.workloadIdentityUser"
```

**AR Push GSA — WI binding for Argo Workflow execution SA:**
```bash
gcloud iam service-accounts add-iam-policy-binding \
    openchoreo-ar-push@pg-ae-n-app-173978.iam.gserviceaccount.com \
    --project=pg-ae-n-app-173978 \
    --member="serviceAccount:pg-ae-n-app-173978.svc.id.goog[workflows-default/workflow-executor]" \
    --role="roles/iam.workloadIdentityUser"
```

### 4. How to Switch After Portal Approval

Complete these steps in order after the WI bindings are confirmed active.

**Step 1 — Annotate the KSAs:**
```bash
# ExternalDNS SA
kubectl annotate serviceaccount external-dns \
    -n kube-system \
    iam.gke.io/gcp-service-account=openchoreo-dns@pg-ae-n-app-173978.iam.gserviceaccount.com

# cert-manager SA (for DNS-01 solver)
kubectl annotate serviceaccount cert-manager \
    -n cert-manager \
    iam.gke.io/gcp-service-account=openchoreo-dns@pg-ae-n-app-173978.iam.gserviceaccount.com

# Argo Workflow execution SA
kubectl annotate serviceaccount workflow-executor \
    -n workflows-default \
    iam.gke.io/gcp-service-account=openchoreo-ar-push@pg-ae-n-app-173978.iam.gserviceaccount.com
```

**Step 2 — Update ExternalDNS Helm values** to remove `--google-project` credential flag and rely on WI instead of the mounted key secret.

**Step 3 — Update cert-manager DNS-01 solver** in the `Certificate` or `ClusterIssuer` resource to remove `serviceAccountSecretRef` and use the annotated SA.

**Step 4 — Update registry-cloud ExternalSecrets** to remove the `openchoreo-ar-push-key` secret sync. Update Argo Workflow templates to use WI-based registry auth instead of the dockerconfigjson secret.

**Step 5 — Switch ClusterSecretStore** for DNS and AR-push from `secretRef` to `workloadIdentity` auth (if separate stores exist for those). If they share the default store, no change needed there.

**Step 6 — Verify** all workloads function correctly for 30 days before removing the key-based secrets.

### 5. Retirement Criteria — PARTIALLY MET

The secretRef exception path is fully retired when ALL of the following are true:

1. WI bindings for `openchoreo-dns` and `openchoreo-ar-push` are active and confirmed via `gcloud iam service-accounts get-iam-policy`
2. ExternalDNS, cert-manager DNS-01 solver, and Argo Workflow execution SA are all annotated with `iam.gke.io/gcp-service-account`
3. No `ExternalSecret` resources reference `openchoreo-dns-key` or `openchoreo-ar-push-key`
4. GCP Secret Manager secrets `openchoreo-dns-key` and `openchoreo-ar-push-key` are disabled (not deleted — keep for 30-day rollback window). **These can be deleted after 2026-05-18 if no auth failures are observed.**
5. 30 days pass with no ESO sync errors and no auth failures in ExternalDNS, cert-manager, or Argo Workflow logs
6. After the 30-day window: delete the GCP SM secret versions and the K8s secrets, then remove the `clustersecretstore-secretref-fallback.yaml` break-glass file

---

## Investigation Results (2026-04-18)

A four-track investigation was conducted to find the best path from SA key files to Workload Identity. The full reports are in `.sisyphus/drafts/wi-investigation/`. The synthesis is in `.sisyphus/drafts/wi-investigation/synthesis-recommendation.md`.

### Track Summary

| Track | Approach | Verdict |
|---|---|---|
| Track 1 | Classic WI (GSA impersonation via `workloadIdentityUser` binding) | ✅ Viable — simplest fallback, draft manifests ready |
| Track 2 | GKE WI Federation (principal-based direct access, no GSA) | ✅ **Recommended primary path** |
| Track 3 | SA Impersonation via `serviceAccountTokenCreator` | ⚠️ AR-push only — ExternalDNS and cert-manager lack native support |
| Track 4 | Cloudflare DNS01 delegation for cert-manager | ✅ Recommended complement — eliminates cert-manager's GCP DNS dependency |

### Comparison Matrix

| Approach | Portal Requests | Implementation Effort | Eliminates GSAs? | Viable? |
|---|---|---|---|---|
| Classic WI (Track 1) | 3 (one per consumer) | Low | No | ✅ YES |
| WI Federation (Track 2) | 2-3 (principal-based bindings) | Low — no cluster changes | Yes | ✅ YES — **RECOMMENDED** |
| SA Impersonation (Track 3) | 2 (TokenCreator bindings) | Medium-High | No | ⚠️ AR-push only |
| Cloudflare Delegation (Track 4) | 0 for cert-manager | Low | N/A (cert-manager only) | ✅ YES (cert-manager only) |
| **Hybrid: WI Federation + Cloudflare** | 1-2 | Low | Yes | ✅ **BEST** |

### Updated Target State

The target state from Section 2 is updated to reflect the investigation findings. Two paths exist depending on whether the portal accepts `principal://` member format:

**Path A — WI Federation (preferred):**

| Consumer | Auth Method | IAM Binding Type | GSA Needed? |
|---|---|---|---|
| ExternalDNS | ADC via GKE metadata server | `principal://` on DNS project | No |
| cert-manager | ADC via GKE metadata server | `principal://` on DNS project | No |
| AR-push | ADC via GKE metadata server | `principal://` on AR repo | No |

**Path B — Classic WI + Cloudflare (fallback if portal rejects `principal://`):**

| Consumer | Auth Method | IAM Binding Type | GSA Needed? |
|---|---|---|---|
| ExternalDNS | WI via GSA impersonation | `workloadIdentityUser` on GSA | Yes (`openchoreo-dns`) |
| cert-manager | Cloudflare API token (CNAME delegation) | None (token in GCP SM) | No |
| AR-push | WI via GSA impersonation | `workloadIdentityUser` on GSA | Yes (`openchoreo-ar-push`) |

### Implementation Decision Tree

```
Phase 0: Look up project number
  gcloud projects describe pg-ae-n-app-173978 --format='value(projectNumber)'

Phase 1: Submit ExternalDNS portal request using principal:// format
  If approved and working → proceed with Track 2 for cert-manager + AR-push
  If rejected (portal doesn't accept principal://) → fall back to Track 1 + Track 4

Phase 2A (Track 2 works): Add cert-manager + AR-push principal bindings
Phase 2B (Track 2 fails): Classic WI for ExternalDNS + AR-push, Cloudflare for cert-manager

Phase 3: Remove SA key ExternalSecrets once all consumers confirmed on WI/Cloudflare
```

### Key Findings

- **No cluster changes needed.** The existing `workload_identity_config` in Pulumi supports both classic WI and WI Federation. Migration is purely IAM-side.
- **ExternalDNS KSA name is `external-dns-google`**, not `external-dns` — set by `fullnameOverride` in the HelmRelease. Portal requests must use this exact name.
- **cert-manager KSA name is `cert-manager`** — default from the Helm chart.
- **AR-push KSA name is `workflow-sa`** in namespace `workflows-default`.
- **Cloudflare delegation** uses `cnameStrategy: Follow` in the ClusterIssuer. The baremetal pattern already works; this is a port of that config to GCP with a GCP SM ExternalSecret instead of OpenBao.
- **Track 3 (SA Impersonation)** is not recommended as a primary path. ExternalDNS and cert-manager have no native impersonation support. The portal burden is similar to WI, with more operational complexity.

For full portal request templates, rollback procedures, and config diffs, see `.sisyphus/drafts/wi-investigation/synthesis-recommendation.md`.
