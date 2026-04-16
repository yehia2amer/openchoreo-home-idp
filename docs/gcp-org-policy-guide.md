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
- **Current reality**: We use SA key files via GCP Secret Manager + ESO because we cannot self-service WI bindings. Future goal: migrate to WI once bindings can be requested via portal.

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

1. **Current**: SA key files via GCP Secret Manager + ESO
2. **Future**: Migrate to Workload Identity once WI bindings can be requested via Global Cloud Requests portal
3. **Ideal**: Full Workload Identity with automated rotation (no manual keys)
