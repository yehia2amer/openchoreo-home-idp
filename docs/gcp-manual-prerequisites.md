# GCP Manual Prerequisites for OpenChoreo GitOps

> **Purpose**: Every manual step required before FluxCD GitOps reconciliation can succeed on a GCP/GKE cluster. Complete these in order. Pulumi handles infrastructure provisioning; this document covers the IAM, key, and controller steps that Pulumi cannot perform in PwC's restricted GCP environment.

## Overview

GitOps reconciliation depends on four categories of prerequisites:

1. **Portal-requested IAM bindings** — roles Pulumi cannot grant due to org policy
2. **Portal-requested SA key creation** — keys Pulumi cannot create due to org policy
3. **SA key upload to Secret Manager** — developer-performed after portal approval
4. **Pulumi-provisioned resources** — handled automatically by `gke-cluster/`
5. **google-cas-issuer controller** — must be installed separately before cert-manager CAS issuance works

All values below use the actual project: `pg-ae-n-app-173978`, region: `europe-west1`.

---

## 1. Portal-Requested IAM Bindings

File these requests through PwC's **Global Cloud Requests** portal. Pulumi sets `skip_iam_bindings: "true"` and will not attempt these.

Alternatively, if you have `setIamPolicy` permissions (e.g., in a non-PwC GCP project), run `pulumi/gke-cluster/prereqs/iam-setup.sh` directly.

### 1a. ESO SA — Secret Manager Accessor (project-level)

```bash
gcloud projects add-iam-policy-binding pg-ae-n-app-173978 \
    --member="serviceAccount:openchoreo-eso@pg-ae-n-app-173978.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None
```

**Why**: ESO's `ClusterSecretStore` reads secrets from GCP Secret Manager. Without this binding, all `ExternalSecret` syncs fail with `PermissionDenied`.

### 1b. ESO K8s SA — Workload Identity Binding to ESO GSA

```bash
gcloud iam service-accounts add-iam-policy-binding \
    openchoreo-eso@pg-ae-n-app-173978.iam.gserviceaccount.com \
    --project=pg-ae-n-app-173978 \
    --member="serviceAccount:pg-ae-n-app-173978.svc.id.goog[external-secrets/external-secrets]" \
    --role="roles/iam.workloadIdentityUser"
```

**Why**: The ESO controller pod runs as K8s SA `external-secrets/external-secrets`. WI lets it impersonate the `openchoreo-eso` GSA without a key file. Required for the `ClusterSecretStore` `workloadIdentity` auth mode.

### 1c. CAS K8s SA — Workload Identity Binding to CAS GSA

```bash
gcloud iam service-accounts add-iam-policy-binding \
    openchoreo-cas@pg-ae-n-app-173978.iam.gserviceaccount.com \
    --project=pg-ae-n-app-173978 \
    --member="serviceAccount:pg-ae-n-app-173978.svc.id.goog[cert-manager/google-cas-issuer]" \
    --role="roles/iam.workloadIdentityUser"
```

**Why**: The `google-cas-issuer` controller runs as K8s SA `cert-manager/google-cas-issuer`. WI lets it call the GCP Certificate Authority Service API to sign certificates.

### 1d. CAS GSA — Certificate Requester on CA Pool

```bash
gcloud privateca pools add-iam-policy-binding openchoreo-ca-pool \
    --project=pg-ae-n-app-173978 \
    --location=europe-west1 \
    --member="serviceAccount:openchoreo-cas@pg-ae-n-app-173978.iam.gserviceaccount.com" \
    --role="roles/privateca.certificateRequester"
```

**Why**: Even with WI, the CAS GSA needs explicit permission to request certificates from the specific CA pool. Without this, `GoogleCASClusterIssuer` reconciliation fails with `PERMISSION_DENIED` on the CA pool.

### 1e. DNS GSA — DNS Admin on DNS Project

```bash
gcloud projects add-iam-policy-binding pg-ae-n-app-237049 \
    --member="serviceAccount:openchoreo-dns@pg-ae-n-app-173978.iam.gserviceaccount.com" \
    --role="roles/dns.admin"
```

**Why**: ExternalDNS and cert-manager's DNS-01 solver both need to create/update DNS records in the `pg-ae-n-app-237049` project (the DNS project, separate from the app project). Note the different project ID.

### 1f. Monitoring GSA — Monitoring Viewer (for GMP Frontend)

```bash
gcloud projects add-iam-policy-binding pg-ae-n-app-173978 \
    --member="serviceAccount:openchoreo-monitoring@pg-ae-n-app-173978.iam.gserviceaccount.com" \
    --role="roles/monitoring.viewer" \
    --condition=None
```

**Why**: The GMP Frontend pod queries Google Cloud Monitoring (Managed Prometheus) via the Prometheus-compatible API. Without `monitoring.viewer`, it returns `PERMISSION_DENIED` for all metric queries. The Observer API depends on this endpoint for CPU/memory metrics.

### 1g. AR Push GSA — Artifact Registry Writer

```bash
gcloud artifacts repositories add-iam-policy-binding openchoreo \
    --project=pg-ae-n-app-173978 \
    --location=europe-west1 \
    --member="serviceAccount:openchoreo-ar-push@pg-ae-n-app-173978.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"
```

**Why**: Argo Workflow pods push built container images to the `europe-west1-docker.pkg.dev/pg-ae-n-app-173978/openchoreo` registry. Without this, image push steps fail with `PERMISSION_DENIED`.

---

## 2. Portal-Requested SA Key Creation

These are needed only if Workload Identity bindings for DNS and AR-push are **not yet available** (the `skip_iam_bindings=True` fallback path). See `docs/gcp-org-policy-guide.md#wi-migration-path` for the WI migration path.

> **Note**: DNS and AR-push SA keys are **NO LONGER required** when `skip_iam_bindings=False` (the default). Pulumi creates WI bindings automatically in that case. The steps below are **FALLBACK ONLY** for `skip_iam_bindings=True` environments where IAM bindings must go through the portal.

### 2a. DNS SA Key

Request creation of a key for `openchoreo-dns@pg-ae-n-app-173978.iam.gserviceaccount.com` through the Global Cloud Requests portal. Download the JSON key file after approval.

### 2b. AR Push SA Key

Request creation of a key for `openchoreo-ar-push@pg-ae-n-app-173978.iam.gserviceaccount.com` through the Global Cloud Requests portal. Download the JSON key file after approval.

---

## 2c. Workload Identity Bindings (created by Pulumi)

When `skip_iam_bindings=False` (default), Pulumi creates these three WI bindings automatically during `pulumi up`:

| KSA | Namespace | GSA |
|---|---|---|
| `external-dns-google` | `external-dns` | `openchoreo-dns@pg-ae-n-app-173978.iam.gserviceaccount.com` |
| `cert-manager` | `cert-manager` | `openchoreo-dns@pg-ae-n-app-173978.iam.gserviceaccount.com` |
| `workflow-sa` | `workflows-default` | `openchoreo-ar-push@pg-ae-n-app-173978.iam.gserviceaccount.com` |
| `gmp-frontend` | `openchoreo-observability-plane` | `openchoreo-monitoring@pg-ae-n-app-173978.iam.gserviceaccount.com` |

These bindings grant `roles/iam.workloadIdentityUser` on the respective GSAs. No SA key creation or Secret Manager upload is needed when these bindings are active.
---

## 3. Upload SA Keys to Secret Manager

After the portal approves key creation and you download the JSON files, upload them to GCP Secret Manager. ESO will sync them into Kubernetes secrets automatically.

```bash
# Upload DNS SA key
gcloud secrets versions add openchoreo-dns-key \
    --project=pg-ae-n-app-173978 \
    --data-file=/path/to/openchoreo-dns-key.json

# Upload AR push SA key
gcloud secrets versions add openchoreo-ar-push-key \
    --project=pg-ae-n-app-173978 \
    --data-file=/path/to/openchoreo-ar-push-key.json
```

**Verify the secrets exist:**

```bash
gcloud secrets list --project=pg-ae-n-app-173978 \
    --filter="name:(openchoreo-dns-key OR openchoreo-ar-push-key)"
```

**Verify ESO synced them into Kubernetes:**

```bash
kubectl get externalsecret -A | grep -E "dns|ar-push"
kubectl get secret openchoreo-dns-key -n cert-manager -o jsonpath='{.data}' | base64 -d | head -c 50
```

---

## 4. Pulumi-Provisioned Resources

These are handled automatically by `pulumi up -s gcp` from the `gke-cluster/` directory. Listed here so you know what Pulumi creates and what it skips.

### 4a. Created by Pulumi

| Resource | Details |
|---|---|
| GCP Service Accounts | `openchoreo-eso`, `openchoreo-cas`, `openchoreo-dns`, `openchoreo-ar-push`, `openchoreo-monitoring` |
| VPC + Subnets | `openchoreo-vpc` in `europe-west1` |
| GKE Cluster | `openchoreo-gke` in `europe-west1` |
| Artifact Registry | `europe-west1-docker.pkg.dev/pg-ae-n-app-173978/openchoreo` |
| CAS Pool | `openchoreo-ca-pool` in `europe-west1` |
| CAS Root CA | Managed by CAS pool |
| CAS Subordinate CA | Managed by CAS pool |
| Secret Manager secrets (shells) | `git-token`, `backstage-fork-secrets`, `openobserve-admin-credentials`, `observer-oauth-client-secret` |

### 4b. Skipped by Pulumi (PwC org policy)

Pulumi reads `skip_iam_bindings: "true"` and `skip_sa_key_creation: "true"` from `Pulumi.gcp.yaml` and skips:

- All `gcloud projects add-iam-policy-binding` calls
- All `gcloud iam service-accounts add-iam-policy-binding` calls
- All `gcloud iam service-accounts keys create` calls

These must be done via the portal (sections 1 and 2 above).

---

## 5. google-cas-issuer Controller

The `google-cas-issuer` controller is a cert-manager plugin from Jetstack. It is **not bundled with cert-manager** and must be installed separately before the `GoogleCASClusterIssuer` resource can reconcile.

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm install google-cas-issuer jetstack/google-cas-issuer \
    --namespace cert-manager \
    --create-namespace \
    --set replicaCount=1
```

**Verify the controller is running:**

```bash
kubectl get pods -n cert-manager -l app=google-cas-issuer
# Expected: 1/1 Running

kubectl get crd googlecasclusterissuers.cas-issuer.jetstack.io
# Expected: NAME ... ESTABLISHED
```

**Verify the issuer reconciles after Flux deploys it:**

```bash
kubectl get googlecasclusterissuer openchoreo-cas-issuer -o jsonpath='{.status.conditions}'
# Expected: type=Ready, status=True
```

---

## Verification Checklist

Run these after completing all prerequisites and before triggering Flux reconciliation.

### IAM Bindings

```bash
# ESO SA — Secret Manager accessor
gcloud projects get-iam-policy pg-ae-n-app-173978 \
    --flatten="bindings[].members" \
    --filter="bindings.members:openchoreo-eso AND bindings.role:roles/secretmanager.secretAccessor" \
    --format="table(bindings.role)"

# ESO WI binding
gcloud iam service-accounts get-iam-policy \
    openchoreo-eso@pg-ae-n-app-173978.iam.gserviceaccount.com \
    --project=pg-ae-n-app-173978

# CAS WI binding
gcloud iam service-accounts get-iam-policy \
    openchoreo-cas@pg-ae-n-app-173978.iam.gserviceaccount.com \
    --project=pg-ae-n-app-173978

# CAS pool binding
gcloud privateca pools get-iam-policy openchoreo-ca-pool \
    --project=pg-ae-n-app-173978 \
    --location=europe-west1

# DNS SA binding (note: DNS project)
gcloud projects get-iam-policy pg-ae-n-app-237049 \
    --flatten="bindings[].members" \
    --filter="bindings.members:openchoreo-dns AND bindings.role:roles/dns.admin" \
    --format="table(bindings.role)"

# AR push SA binding
gcloud artifacts repositories get-iam-policy openchoreo \
    --project=pg-ae-n-app-173978 \
    --location=europe-west1
```

### CAS Pool

```bash
gcloud privateca pools describe openchoreo-ca-pool \
    --project=pg-ae-n-app-173978 \
    --location=europe-west1
# Expected: state: ENABLED
```

### ESO Sync

```bash
kubectl get externalsecret -A
# Expected: all READY=True, SYNCED=True

kubectl get clustersecretstore default -o jsonpath='{.status.conditions}'
# Expected: type=Ready, status=True
```

### Certificates

```bash
kubectl get certificate -A
# Expected: READY=True for all certs

kubectl get googlecasclusterissuer openchoreo-cas-issuer \
    -o jsonpath='{.status.conditions[0].type}'
# Expected: Ready
```

---

## Troubleshooting

### WI Binding Missing

**Symptom**: ESO `ClusterSecretStore` shows `READY=False` with error `iam.workloadIdentityUser binding not found` or `UNAUTHENTICATED`.

**Check**:
```bash
gcloud iam service-accounts get-iam-policy \
    openchoreo-eso@pg-ae-n-app-173978.iam.gserviceaccount.com \
    --project=pg-ae-n-app-173978
```

**Fix**: File a portal request for the WI binding (section 1b). As a temporary workaround, use the secretRef fallback documented in `secrets-gcp-sm/clustersecretstore-secretref-fallback.yaml`.

### ESO Sync Failure

**Symptom**: `ExternalSecret` shows `READY=False` with `SecretSyncedError` or `PermissionDenied`.

**Check**:
```bash
kubectl describe externalsecret <name> -n <namespace>
kubectl logs -n external-secrets -l app.kubernetes.io/name=external-secrets --tail=50
```

**Common causes**:
- Secret Manager secret doesn't exist yet (section 3 not done)
- ESO SA lacks `secretmanager.secretAccessor` (section 1a not done)
- WI binding missing (section 1b not done)
- Secret version is disabled or destroyed

### CAS Issuer Not Reconciling

**Symptom**: `GoogleCASClusterIssuer` shows `Ready=False` or `Certificate` stays in `Pending`.

**Check**:
```bash
kubectl describe googlecasclusterissuer openchoreo-cas-issuer
kubectl logs -n cert-manager -l app=google-cas-issuer --tail=50
```

**Common causes**:
- `google-cas-issuer` controller not installed (section 5 not done)
- CAS pool binding missing (section 1d not done)
- CAS WI binding missing (section 1c not done)
- CA pool not in `ENABLED` state (Pulumi may not have run yet)

### Artifact Registry Push Failure

**Symptom**: Argo Workflow image-push step fails with `PERMISSION_DENIED` or `unauthorized`.

**Check**:
```bash
gcloud artifacts repositories get-iam-policy openchoreo \
    --project=pg-ae-n-app-173978 \
    --location=europe-west1
kubectl get secret registry-push-secret -n openchoreo-workflow-plane
kubectl get externalsecret -n openchoreo-workflow-plane | grep ar-push
```

**Common causes**:
- AR push SA binding missing (section 1f not done)
- `openchoreo-ar-push-key` secret not uploaded to Secret Manager (section 3 not done)
- ESO `ExternalSecret` for AR push key not synced
