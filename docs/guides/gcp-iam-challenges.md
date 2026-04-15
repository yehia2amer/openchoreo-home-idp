# GCP IAM Challenges — PwC Enterprise Environment

**Last Updated**: 2026-04-15
**Applies To**: GKE deployment in PwC-managed GCP projects

---

## Overview

This project runs in a PwC-managed GCP environment with **restricted IAM policies**. Standard GCP IAM operations that work in personal or startup projects **will not work here**. This document captures every constraint, workaround, and lesson learned so future contributors (human or AI) don't repeat the same discoveries.

---

## The Core Problem

PwC enforces organization-level IAM restrictions that prevent:

1. **Direct IAM binding** — `gcloud projects add-iam-policy-binding` and `gcloud iam service-accounts add-iam-policy-binding` commands fail with `PERMISSION_DENIED` because no role in the approved catalog grants the `setIamPolicy` permission
2. **Arbitrary role assignment** — You cannot grant any GCP role you want. Only roles from an **approved catalog** are available
3. **Service account impersonation** — `--impersonate-service-account` fails even for project members because `iam.serviceAccounts.getAccessToken` is not granted by default

## The PwC Roles Portal

PwC provides a **custom web portal** for managing IAM role assignments. This is the ONLY way to assign roles to service accounts.

### How It Works

1. You provide the **service account email** (e.g., `openchoreo-dns@pg-ae-n-app-173978.iam.gserviceaccount.com`)
2. You select roles from the **approved catalog** — a curated subset of GCP predefined roles
3. The portal performs the IAM binding on your behalf (it has the `setIamPolicy` permission that you don't)

### The Approved Roles Catalog

The complete list of roles available in the PwC portal is captured in:

```
pwc_gcp_roles.json    # Root of IDP repo — 1011 lines, ~150 roles
```

**This file is critical.** Before planning any GCP integration that needs IAM permissions, check this file first. If the role you need isn't listed, you cannot use it without requesting an exception through PwC governance.

### What's In the Catalog (relevant subset)

| Role | Available | Needed For |
|------|-----------|------------|
| `roles/iam.workloadIdentityUser` | ✅ Yes | Workload Identity bindings for all K8s↔GCP SA mappings |
| `roles/iam.workloadIdentityPoolAdmin` | ✅ Yes | Managing Workload Identity pools |
| `roles/iam.serviceAccountUser` | ✅ Yes | Running operations as a service account |
| `roles/iam.serviceAccountTokenCreator` | ✅ Yes | Creating OAuth2 tokens, signing JWTs |
| `roles/secretmanager.secretAccessor` | ✅ Yes | External Secrets Operator reading from GCP Secret Manager |
| `roles/secretmanager.admin` | ✅ Yes | Full Secret Manager access |
| `roles/container.admin` | ✅ Yes | GKE cluster management |
| `roles/editor` | ✅ Yes | Broad project-level permissions (basic role) |

### What's NOT in the Catalog (discovered blockers)

| Role | Available | Impact |
|------|-----------|--------|
| `roles/dns.admin` | ❌ **No** | Cannot automate DNS record management via standard IAM |
| `roles/privateca.certificateRequester` | ❌ **No** | Cannot use GCP Certificate Authority Service (CAS) |

**Workaround for missing roles:** Use the PwC portal to assign permissions directly. Even though `roles/dns.admin` isn't in the catalog, PwC admins were able to grant equivalent DNS permissions through the portal when asked. Always try the portal first.

---

## Multi-Project Architecture

This deployment spans **two GCP projects**:

| Project | Project ID | Purpose |
|---------|-----------|---------|
| **Workload** | `pg-ae-n-app-173978` | GKE cluster, service accounts, secrets, CAS |
| **DNS** | `pg-ae-n-app-237049` | Cloud DNS zone `aistudio-consulting`, domain `aistudio.consulting` |

### Cross-Project Implications

- Service accounts are created in the **workload project** by Pulumi
- DNS permissions must be granted in the **DNS project** — this is a separate IAM binding
- The PwC Roles Portal may have **different permission catalogs per project** — test each project separately
- ExternalDNS and cert-manager both need the `--google-project=pg-ae-n-app-237049` flag to operate cross-project

---

## Service Account Inventory

Every GCP service account used by OpenChoreo and the permissions it needs:

| Service Account | Created By | Purpose | Roles Needed | Binding Target |
|---|---|---|---|---|
| `openchoreo-eso@pg-ae-n-app-173978.iam` | Pulumi | External Secrets Operator | `roles/secretmanager.secretAccessor` (workload project) | Project-level IAM |
| `openchoreo-eso@pg-ae-n-app-173978.iam` | Pulumi | ESO Workload Identity | `roles/iam.workloadIdentityUser` (on self) | SA-level IAM, member: `serviceAccount:pg-ae-n-app-173978.svc.id.goog[external-secrets/external-secrets]` |
| `openchoreo-cas@pg-ae-n-app-173978.iam` | Pulumi | cert-manager CAS issuer | `roles/privateca.certificateRequester` (workload project) | CA Pool-level IAM |
| `openchoreo-cas@pg-ae-n-app-173978.iam` | Pulumi | CAS Workload Identity | `roles/iam.workloadIdentityUser` (on self) | SA-level IAM, member: `serviceAccount:pg-ae-n-app-173978.svc.id.goog[cert-manager/google-cas-issuer]` |
| `openchoreo-dns@pg-ae-n-app-173978.iam` | Pulumi | ExternalDNS + cert-manager DNS-01 | `roles/dns.admin` (DNS project) | Project-level IAM on `pg-ae-n-app-237049` |
| `openchoreo-dns@pg-ae-n-app-173978.iam` | Pulumi | DNS Workload Identity (ExternalDNS) | `roles/iam.workloadIdentityUser` (on self) | SA-level IAM, member: `serviceAccount:pg-ae-n-app-173978.svc.id.goog[external-dns/external-dns]` |
| `openchoreo-dns@pg-ae-n-app-173978.iam` | Pulumi | DNS Workload Identity (cert-manager) | `roles/iam.workloadIdentityUser` (on self) | SA-level IAM, member: `serviceAccount:pg-ae-n-app-173978.svc.id.goog[cert-manager/cert-manager]` |

---

## The `skip_iam_bindings` Guard

Because Pulumi cannot perform IAM bindings in this environment, all IAM-related Pulumi resources are **guarded** behind a config flag:

```yaml
# Pulumi.gcp.yaml
openchoreo:skip_iam_bindings: "true"
```

When `true`:
- Pulumi **creates the service accounts** (GSAs) but **skips all IAM bindings**
- Bindings must be done **manually** via the PwC Roles Portal + the prereqs script
- This is the permanent state for PwC environments — it will never be `false`

When `false` (non-PwC environments):
- Pulumi manages both service accounts AND their IAM bindings
- Fully automated, no manual steps needed

**Code location**: `pulumi/gke-cluster/__main__.py`, search for `skip_iam_bindings`

---

## Manual IAM Setup Process

### Step 1: Pulumi Creates Service Accounts

Run `pulumi up` — this creates the GCP service accounts but skips IAM bindings.

### Step 2: Run the Prerequisites Script

```bash
cd pulumi/gke-cluster
chmod +x prereqs/iam-setup.sh
./prereqs/iam-setup.sh
```

**This script will fail** in PwC environments because it uses `gcloud ... add-iam-policy-binding` commands. It exists as documentation of what bindings are needed. The actual bindings must be done through the PwC Roles Portal.

### Step 3: Use the PwC Roles Portal

For each service account in the inventory above:

1. Go to the PwC Roles Portal
2. Enter the service account email
3. Select the required role from the catalog
4. Apply

### Step 4: Verify Bindings Work

Test each service account's permissions:

```bash
# Create a temporary key (delete after testing)
gcloud iam service-accounts keys create /tmp/test-key.json \
  --iam-account=<SA_EMAIL>

# Activate the SA
gcloud auth activate-service-account --key-file=/tmp/test-key.json

# Test the specific permission
# For DNS:
gcloud dns record-sets list --zone=aistudio-consulting --project=pg-ae-n-app-237049

# For Secret Manager:
gcloud secrets list --project=pg-ae-n-app-173978

# Clean up
gcloud config set account <YOUR_EMAIL>
rm -f /tmp/test-key.json
```

**Important:** Delete the SA key after testing. In production, Workload Identity is used — no keys should exist.

---

## Org Policy Constraints

PwC enforces additional organization-level policies:

| Constraint | Value | Impact |
|------------|-------|--------|
| `constraints/compute.vmExternalIpAccess` | `allValues: DENY` | No external IPs on any VM. GKE must use private cluster + Cloud NAT |

This means:
- GKE cluster is **private** — nodes have no public IPs
- Internet access is via **Cloud NAT** (deployed by Pulumi)
- `kubectl` access requires either authorized networks or Cloud Shell

---

## Lessons Learned

### 1. Always Check `pwc_gcp_roles.json` First

Before designing any GCP integration, grep the roles file:
```bash
cat pwc_gcp_roles.json | jq '.roles | to_entries[] | .value[] | select(.role_value | test("dns|privateca|certificate"))'
```
If the role isn't there, plan a workaround or request it through governance.

### 2. `gcloud` Commands ≠ Portal Permissions

You may have broad personal access via `gcloud` (your user account), but that doesn't mean you can grant those same permissions to service accounts. The PwC Portal is the only way to assign roles to SAs.

### 3. Cross-Project IAM May Have Different Rules

The DNS project (`pg-ae-n-app-237049`) may have a different permission catalog than the workload project (`pg-ae-n-app-173978`). Test each project's IAM independently.

### 4. Test with SA Keys, Deploy with Workload Identity

During development, create temporary SA keys to verify permissions work. In production, always use Workload Identity (no keys). Delete test keys immediately after verification.

### 5. The Portal Can Sometimes Do What the Catalog Says It Can't

Even when a role isn't listed in `pwc_gcp_roles.json`, the PwC admin portal was sometimes able to assign equivalent permissions. When stuck, always try the portal before giving up.

### 6. `--impersonate-service-account` Won't Work

Service account impersonation requires `iam.serviceAccounts.getAccessToken`, which is not available in this environment. Use SA keys for testing instead.

---

## Quick Reference: Adding a New Service Account

When a new GCP integration requires a new service account:

1. **Add the GSA to Pulumi** — `pulumi/gke-cluster/__main__.py`, guarded by `skip_iam_bindings`
2. **Add the IAM bindings to `prereqs/iam-setup.sh`** — as documentation (script won't run, but documents what's needed)
3. **Update this document** — add the SA to the inventory table above
4. **Coordinate with PwC admin** — provide SA email + required roles
5. **Test with a temporary key** — verify permissions before deploying workloads
6. **Add WI annotation in GitOps repo** — K8s ServiceAccount annotation `iam.gke.io/gcp-service-account: <GSA_EMAIL>`

---

## Related Files

| File | Purpose |
|------|---------|
| `pwc_gcp_roles.json` | Complete PwC approved IAM roles catalog |
| `pulumi/gke-cluster/__main__.py` | Pulumi code with `skip_iam_bindings` guard |
| `pulumi/gke-cluster/Pulumi.gcp.yaml` | Stack config with `skip_iam_bindings: true` |
| `pulumi/gke-cluster/prereqs/iam-setup.sh` | IAM binding commands (documentation, not runnable in PwC) |
| `docs/gke-deployment-status.md` | Overall GKE deployment status and known issues |
