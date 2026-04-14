# OpenChoreo on GKE — Deployment Guide

> **Scope**: Deploying OpenChoreo to Google Kubernetes Engine using Pulumi (Phase 1) and FluxCD (Phase 2).
>
> **Audience**: Platform engineers deploying and maintaining GKE-based OpenChoreo clusters.
>
> **Related**: [Deployment Guide](../deployment-guide.md) for general architecture, [ADR-001](../adr/001-pulumi-fluxcd-boundary.md) for the Pulumi/FluxCD boundary contract.

---

## 1. Prerequisites

### Tools

| Tool | Purpose | Install |
|------|---------|---------|
| `gcloud` | GCP CLI | [cloud.google.com/sdk](https://cloud.google.com/sdk/docs/install) |
| `pulumi` | Infrastructure as Code | [pulumi.com/docs/install](https://www.pulumi.com/docs/install/) |
| Python 3.11+ | Pulumi runtime | System package manager |
| `uv` | Python dependency management | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `kubectl` | Kubernetes CLI | `gcloud components install kubectl` |
| `flux` | FluxCD CLI (debugging) | [fluxcd.io/flux/installation](https://fluxcd.io/flux/installation/) |

### GCP Setup

```bash
# Authenticate
gcloud auth login
gcloud auth application-default login

# Enable required APIs
gcloud services enable \
  container.googleapis.com \
  certificateauthority.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  --project=<PROJECT_ID>
```

### Optional

- GitHub PAT — required only if the GitOps repository is private.

---

## 2. Architecture Overview

OpenChoreo on GKE follows the standard 2-phase deployment model:

**Phase 1 — Pulumi Bootstrap** (`pulumi/gke-cluster/`):
- VPC network + subnet with secondary ranges for pods/services
- GKE Standard cluster with Dataplane v2 (eBPF), Gateway API, Workload Identity
- GCP Certificate Authority Service — root + subordinate CA hierarchy
- Artifact Registry for container images
- GCP Service Accounts with Workload Identity bindings (ESO, CAS)
- Secret Manager secrets (git tokens, backstage config)
- Flux CD controllers + GitRepository + root Kustomization

**Phase 2 — FluxCD GitOps** (`clusters/gke/` in the GitOps repo):
- 6 ordered waves (00-crds through 05-network) with `dependsOn` chaining and `wait: true`
- GCP platform overlays activate Kustomize Components: `issuer-gcp-cas`, `secrets-gcp-sm`, `registry-cloud`, `observability-cloud`, `network-k8s-policy`
- Variable substitution via `cluster-vars` ConfigMap populated from Pulumi outputs

**Boundary rule (ADR-001)**: Pulumi bootstraps infrastructure. FluxCD reconciles Kubernetes resources. Never both.

---

## 3. Step-by-Step Deployment

### 3.1 Clone Repositories

```bash
git clone https://github.com/<org>/openchoreo-home-idp.git
git clone https://github.com/<org>/openchoreo-gitops.git
```

### 3.2 Configure Pulumi Stack

```bash
cd openchoreo-home-idp/pulumi/gke-cluster
uv sync   # Install Python dependencies
pulumi stack init gcp

# Required
pulumi config set openchoreo:gcp_project_id <PROJECT_ID>

# Required if using GitOps (recommended)
pulumi config set openchoreo:gitops_repo_url https://github.com/<org>/openchoreo-gitops.git
pulumi config set openchoreo:gitops_repo_branch main
pulumi config set openchoreo:github_pat <PAT> --secret
pulumi config set openchoreo:domain_base gcp.openchoreo.example.com
```

**Optional overrides** (defaults shown):

| Config Key | Default | Description |
|------------|---------|-------------|
| `gcp_region` | `us-central1` | GCP region for all resources |
| `gcp_gke_cluster_name` | `openchoreo-gke` | GKE cluster name |
| `gcp_gke_node_count` | `3` | Max nodes per zone (autoscaling from 1) |
| `gcp_gke_machine_type` | `e2-standard-4` | Node machine type |
| `gcp_cas_pool_name` | `openchoreo-ca-pool` | CAS CA pool name |
| `gcp_cas_tier` | `DEVOPS` | CAS tier (`DEVOPS` or `ENTERPRISE`) |
| `gcp_eso_service_account` | `openchoreo-eso` | GCP SA for External Secrets Operator |
| `gcp_cas_service_account` | `openchoreo-cas` | GCP SA for CAS issuer |
| `artifact_registry_repository_id` | `openchoreo` | Artifact Registry repo name |
| `gcp_gke_master_authorized_cidr` | *(empty — disabled)* | CIDR block for GKE control plane access (e.g. `203.0.113.0/24`). When set, only this range can reach the API server. |
| `gcp_gke_database_encryption_key` | *(empty — disabled)* | Cloud KMS key resource name for GKE application-layer secrets encryption (e.g. `projects/P/locations/R/keyRings/KR/cryptoKeys/K`). |

> **`PULUMI_CONFIG_PASSPHRASE`**: If you use a local Pulumi backend (file state), set this environment variable before running `pulumi stack init` or `pulumi up`. It encrypts secrets in the state file. For Pulumi Cloud backends this is handled automatically.

<details>
<summary><strong>Full example <code>Pulumi.gcp.yaml</code></strong></summary>

```yaml
config:
  openchoreo:platform: gke
  openchoreo:kubeconfig_path: gke-cluster/outputs/kubeconfig
  openchoreo:kubeconfig_context: gke_PROJECT_REGION_CLUSTER
  openchoreo:domain_base: gcp.openchoreo.example.com
  openchoreo:enable_flux: "true"
  openchoreo:enable_observability: "false"
  openchoreo:gcp_project_id: my-gcp-project
  openchoreo:gcp_region: us-central1
  openchoreo:gcp_zone: us-central1-a
  openchoreo:gcp_network_name: openchoreo-vpc
  openchoreo:gcp_gke_cluster_name: openchoreo-gke
  openchoreo:gcp_gke_node_count: "3"
  openchoreo:gcp_gke_machine_type: e2-standard-4
  openchoreo:gcp_cas_pool_name: openchoreo-ca-pool
  openchoreo:gcp_cas_tier: DEVOPS
  openchoreo:gcp_eso_service_account: openchoreo-eso
  openchoreo:gcp_cas_service_account: openchoreo-cas
  openchoreo:artifact_registry_repository_id: openchoreo
  openchoreo:gitops_repo_url: https://github.com/<org>/openchoreo-gitops
  openchoreo:gitops_repo_branch: main
  # openchoreo:github_pat is set via `pulumi config set --secret`
  # openchoreo:gcp_gke_master_authorized_cidr: 203.0.113.0/24
  # openchoreo:gcp_gke_database_encryption_key: projects/P/locations/R/keyRings/KR/cryptoKeys/K
```

</details>

### 3.3 Deploy Infrastructure

```bash
pulumi up -s gcp
```

Review the plan and confirm. This typically takes 5-10 minutes.

### 3.4 Populate GitOps Cluster Variables

After `pulumi up` completes, extract outputs:

```bash
pulumi stack output --json -s gcp
```

Edit `clusters/gke/cluster-vars.yaml` in the GitOps repo. Replace each `PLACEHOLDER` with the corresponding Pulumi output:

| Variable | Pulumi Output |
|----------|---------------|
| `gcp_project_id` | `gcp_project_id` |
| `gcp_region` | `gcp_region` |
| `gcp_gke_cluster_name` | `gcp_gke_cluster_name` |
| `gcp_cas_pool_name` | `gcp_cas_pool_name` |
| `gcp_eso_service_account` | `gcp_eso_service_account` |
| `gcp_cas_service_account` | `gcp_cas_service_account` |
| `artifact_registry_url` | `artifact_registry_url` |

The `gateway_class_name` and `cluster_issuer_name` fields are pre-populated with correct defaults.

```bash
cd openchoreo-gitops
# Edit clusters/gke/cluster-vars.yaml
git add -A && git commit -m "populate GKE cluster variables"
git push
```

Flux will detect the change and begin reconciling the 6 waves automatically.

### 3.5 Verify Deployment

```bash
export KUBECONFIG=openchoreo-home-idp/pulumi/gke-cluster/outputs/kubeconfig

# Flux wave status — all should show "Ready True"
flux get kustomizations

# GKE nodes
kubectl get nodes

# CAS ClusterIssuer
kubectl get clusterissuers

# External Secrets ClusterSecretStore
kubectl get clustersecretstores

# Platform pods
kubectl get pods -A | grep openchoreo
```

---

## 4. Resource Inventory

### GCP Resources (created by Pulumi)

| Resource | Type | Name/Notes |
|----------|------|------------|
| VPC network | `compute.Network` | `openchoreo-vpc`, no auto-subnets |
| Subnet | `compute.Subnetwork` | Nodes `/20`, Pods `/16`, Services `/20` |
| GKE cluster | `container.Cluster` | Regional, Dataplane v2, Gateway API, Workload Identity |
| Node pool | `container.NodePool` | COS_CONTAINERD, shielded VMs, autoscaling 1-N, auto-repair/upgrade |
| ESO service account | `serviceaccount.Account` | `roles/secretmanager.secretAccessor` + WI binding |
| CAS service account | `serviceaccount.Account` | `roles/privateca.certificateRequester` + WI binding |
| CA pool | `certificateauthority.CaPool` | DEVOPS tier, publishes CRL |
| Root CA | `certificateauthority.Authority` | RSA 4096-bit, self-signed |
| Subordinate CA | `certificateauthority.Authority` | RSA 4096-bit, 5-year lifetime |
| Artifact Registry | `artifactregistry.Repository` | Docker format |
| Secret Manager | `secretmanager.Secret` | `git-token`, `backstage-fork-secrets` |

### Kubernetes Resources (created by Pulumi)

| Resource | Notes |
|----------|-------|
| Flux controllers | source-controller, kustomize-controller, helm-controller |
| GitRepository `flux-system` | Points to GitOps repo |
| Kustomization `root-sync` | Reconciles `./clusters/gke/` |
| Secret `flux-git-credentials` | GitHub PAT (if provided) |

### FluxCD Waves (reconciled by Flux)

| Wave | Platform Overlay Path | Components Activated | Purpose |
|------|----------------------|---------------------|---------|
| 00-crds | `gcp/00-crds` | — | Gateway API CRDs |
| 01-prerequisites | `gcp/01-prerequisites` | `secrets-gcp-sm` | cert-manager, ESO, ClusterSecretStore |
| 02-tls | `gcp/02-tls` | `issuer-gcp-cas` | Google CAS ClusterIssuer, certificates |
| 03-platform | `gcp/03-platform` | `observability-cloud`, `registry-cloud` | All OpenChoreo planes |
| 04-registration | `gcp/04-registration` | — | Plane registration jobs |
| 05-network | `gcp/05-network` | `network-k8s-policy` | Network policies |

---

## 5. GKE Cluster Security Configuration

The cluster is deployed with these security hardening measures:

- **Workload Identity** — no static GCP credentials; pods authenticate via Kubernetes SA → GCP SA binding
- **Dataplane v2** — eBPF-based networking with built-in network policy enforcement
- **Shielded nodes** — Secure Boot and Integrity Monitoring enabled
- **COS_CONTAINERD** — container-optimized OS with minimal attack surface
- **Least-privilege OAuth scopes** — 6 specific scopes instead of `cloud-platform`
- **Auto-repair and auto-upgrade** — automatic node maintenance
- **Maintenance window** — Tuesdays 03:00-07:00 UTC
- **Node autoscaling** — scales between 1 and `node_count` per zone
- **Master authorized networks** *(optional)* — set `gcp_gke_master_authorized_cidr` to restrict API server access to a specific CIDR block
- **Application-layer secrets encryption** *(optional)* — set `gcp_gke_database_encryption_key` to encrypt etcd secrets with a Cloud KMS key
- **IAM least-privilege** — ESO SA scoped to `secretmanager.secretAccessor`; CAS SA scoped to `privateca.certificateRequester` at the CA pool level

---

## 6. Teardown

> **Order matters.** Flux-managed resources can block GKE deletion if they hold finalizers or PVCs. Follow this sequence.

### 6.1 Suspend Flux Reconciliation

Stop Flux from re-creating resources while you tear down:

```bash
export KUBECONFIG=openchoreo-home-idp/pulumi/gke-cluster/outputs/kubeconfig

# Suspend all Kustomizations so Flux stops reconciling
flux suspend kustomization --all

# Verify — all should show "Suspended: True"
flux get kustomizations
```

### 6.2 Clean Up Persistent Volumes

Delete PVCs that would otherwise block namespace deletion or leave orphaned GCE persistent disks:

```bash
# List PVCs across all namespaces
kubectl get pvc -A

# Delete PVCs (adjust namespaces as needed)
kubectl delete pvc --all -n openchoreo-control-plane
kubectl delete pvc --all -n openchoreo-observability-plane
kubectl delete pvc --all -n openbao

# Wait for PV reclamation (GCE disks may take ~60s)
kubectl get pv -w
```

### 6.3 Destroy Infrastructure

```bash
cd openchoreo-home-idp/pulumi/gke-cluster
pulumi destroy -s gcp
```

### 6.4 Certificate Authority Grace Period

The GKE cluster Pulumi program sets `skip_grace_period=True` on dev stacks (CAs are deleted immediately). For production environments:

- CA authorities enter a **30-day grace period** before permanent deletion by default.
- During this period you can restore them via `gcloud privateca authorities undelete`.
- If you need immediate deletion, set `gcp_cas_tier: DEVOPS` (DevOps-tier CAs skip the grace period).
- For `ENTERPRISE` tier CAs, you can force-delete after revoking active certificates:
  ```bash
  gcloud privateca subordinates delete <SUB_CA_ID> \
    --pool=<POOL_NAME> --location=<REGION> \
    --ignore-active-certificates --skip-grace-period
  ```

### 6.5 Notes

- All GCP resources have `deletion_protection=False` set for dev/test environments. For production deployments, consider setting `deletion_protection=True` on the GKE cluster and CA authorities.
- Orphaned GCE disks can be checked via `gcloud compute disks list --filter="name~openchoreo"`.
- The `pulumi/gke-cluster/outputs/` directory (kubeconfig) is gitignored and should be deleted locally after teardown.

---

## 7. Troubleshooting

**Flux wave stuck / not progressing**
```bash
flux get kustomizations          # Which wave failed?
flux events --for kustomization/<wave-name>  # Detailed error
kubectl get events -n flux-system --sort-by=.lastTimestamp
```

**CAS ClusterIssuer not ready**
```bash
kubectl get googlecasclusterissuers -A
kubectl logs -n cert-manager deploy/google-cas-issuer
# Common: WI annotation missing on SA, or CAS SA lacks privateca.certificateRequester role
```

**External Secrets not syncing**
```bash
kubectl get externalsecrets -A
kubectl get clustersecretstores
kubectl get sa -n external-secrets external-secrets -o yaml
# Verify: annotation iam.gke.io/gcp-service-account is present
```

**Flux cannot reach GitOps repository**
```bash
kubectl get gitrepositories -n flux-system
kubectl get secret flux-git-credentials -n flux-system
# Verify PAT has repo read access
```

**Node pool issues**
```bash
gcloud container node-pools describe openchoreo-gke-nodes \
  --cluster=openchoreo-gke \
  --region=us-central1 \
  --project=<PROJECT_ID>
```

**Kubeconfig expired / auth plugin missing**
```bash
# Install the auth plugin
gcloud components install gke-gcloud-auth-plugin

# Or regenerate kubeconfig
gcloud container clusters get-credentials openchoreo-gke \
  --region=us-central1 --project=<PROJECT_ID>
```
