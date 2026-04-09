# OpenChoreo Deployment Guide

> **Scope**: Infrastructure deployment for the OpenChoreo platform using Pulumi (Phase 1) and FluxCD (Phase 2).
>
> **Audience**: Platform engineers deploying and maintaining the OpenChoreo cluster.
>
> **Related**: See [Project Onboarding Guide](project-onboarding-guide.md) for deploying applications on the platform.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Phase 1: Pulumi Bootstrap](#2-phase-1-pulumi-bootstrap)
3. [Phase 2: FluxCD GitOps](#3-phase-2-fluxcd-gitops)
4. [GitOps Repository Structure](#4-gitops-repository-structure)
5. [Rollback Procedures](#5-rollback-procedures)
6. [Adding a New Platform Overlay](#6-adding-a-new-platform-overlay)
7. [Workflow Template Upgrade Process](#7-workflow-template-upgrade-process)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Architecture Overview

OpenChoreo uses a **2-phase deployment model** to bring up the full platform stack:

### Phase 1 — Pulumi Bootstrap

Pulumi handles components that require imperative sequencing or secret seeding that cannot be declaratively expressed in GitOps:

| Component | Why Pulumi? |
|-----------|-------------|
| **Talos + Cilium CNI** | Chicken-and-egg: CNI must exist before any pods can schedule |
| **Gateway API CRDs** | Must precede any Gateway/HTTPRoute resources |
| **Longhorn** | Storage backend required by PVCs before platform deploys |
| **flux-bootstrap** | Installs Flux controllers + creates GitRepository/root Kustomization |
| **OpenBao** | Vault needs imperative `vault kv put` to seed initial secrets |
| **Thunder (OIDC)** | Requires imperative OIDC bootstrap configuration |
| **PushSecrets** | Seeds ESO PushSecret resources that push to OpenBao |
| **ClusterSecretStore** | Bridges ESO to OpenBao; depends on OpenBao being unsealed |
| **Seed secrets** | Initial K8s secrets (git tokens, registry creds) for platform bootstrap |

### Phase 2 — FluxCD GitOps

Once Pulumi completes, FluxCD takes ownership of the remaining platform infrastructure through numbered Kustomization layers:

| Layer | Contents |
|-------|----------|
| **00-crds** | kgateway CRDs |
| **01-prerequisites** | cert-manager, External Secrets Operator, kgateway controller, kubernetes-replicator |
| **02-tls** | Self-signed CA chain, wildcard TLS certificates |
| **03-platform** | Control Plane, Data Plane, Workflow Plane, Observability Plane, Odigos |
| **04-registration** | `register-planes` and `link-planes` Jobs |
| **05-network** | Cilium L2 announcement policies and IP pools |

Each layer depends on the previous via `dependsOn`, ensuring correct deployment ordering.

### Why Two Phases?

- **OpenBao** needs imperative `vault kv put` commands to seed secrets — cannot be done declaratively
- **Thunder** requires OIDC bootstrap that depends on a running OpenBao
- **Cilium** is the CNI — nothing schedules until it's running, including Flux controllers
- **Flux itself** must be installed before it can reconcile anything

Once these bootstrapping concerns are satisfied, FluxCD manages everything else declaratively with drift detection and automatic reconciliation.

---

## 2. Phase 1: Pulumi Bootstrap

### Prerequisites

- Python 3.11+ with `uv` package manager
- Pulumi CLI installed (`curl -fsSL https://get.pulumi.com | sh`)
- Valid kubeconfig for the target cluster
- Access to the Pulumi state backend

### Running Phase 1

```bash
cd pulumi
export PULUMI_CONFIG_PASSPHRASE="<your-passphrase>"  # Required for state encryption
pulumi up -s dev
```

> **Security Note**: Never commit `PULUMI_CONFIG_PASSPHRASE` to version control. Store it in a secure password manager.

### What Phase 1 Creates

The Pulumi orchestration (`pulumi/__main__.py`) runs these steps in order:

1. **Cilium + Gateway API CRDs** (conditional) — CNI and gateway infrastructure
2. **Prerequisites** — Namespaces (`openchoreo-control-plane`, `openchoreo-data-plane`, `openchoreo-workflow-plane`, `workflows-default`), OpenBao, seed K8s secrets, ClusterSecretStore + readiness wait, PushSecret resources
3. **Thunder** — OIDC provider with namespace, bootstrap config, Helm release

The Talos bare-metal nested project (`pulumi/talos-cluster-baremetal/`) additionally bootstraps:
- Flux controller installation from local manifests
- Flux `GitRepository` resources pointing to the gitops repo
- Root Flux `Kustomization` pointing to `./clusters/<platform>/`

### Kubeconfig

After Pulumi completes, the kubeconfig is available at:

```
pulumi/talos-cluster-baremetal/outputs/kubeconfig
```

Context name: `admin@openchoreo`

```bash
export KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig
kubectl get nodes
```

### Pulumi State

After Phase 1, ~35 URNs remain in Pulumi state — purely bootstrap infrastructure (Talos, Cilium, Longhorn, Gateway API CRDs, Flux controllers, OpenBao, Thunder, seed secrets). All platform-layer resources are owned by FluxCD.

---

## 3. Phase 2: FluxCD GitOps

### How It Works

After Pulumi bootstraps Flux, the root Kustomization automatically begins reconciling the cluster entry point at `./clusters/<platform>/`. This triggers the numbered infrastructure layers in dependency order.

### Infrastructure Layers

Each layer is a FluxCD `Kustomization` resource in the `flux-system` namespace:

```
00-crds              → ./infrastructure/base/00-crds
01-prerequisites     → ./infrastructure/base/01-prerequisites
02-tls               → ./infrastructure/base/02-tls
03-platform          → ./infrastructure/base/03-platform
04-registration      → ./infrastructure/base/04-registration
05-network           → ./infrastructure/base/05-network
```

### Dependency Chain

```
00-crds
  └── 01-prerequisites (dependsOn: 00-crds)
        └── 02-tls (dependsOn: 01-prerequisites)
              └── 03-platform (dependsOn: 02-tls)
                    └── 04-registration (dependsOn: 03-platform)
                          └── 05-network (dependsOn: 04-registration)
```

### Reconciliation Intervals

| Setting | Value |
|---------|-------|
| **Reconciliation interval** | `1h` |
| **Retry interval** | `5s` |
| **Infrastructure timeout** | `5m` |
| **Platform timeout** | `10m` |

### Variable Substitution

All numbered Kustomizations use Flux `postBuild.substituteFrom` to inject platform-specific values from `clusters/<platform>/vars/cluster-vars.yaml`. Key variables include:

| Variable | Example (talos-baremetal) | Purpose |
|----------|--------------------------|---------|
| `OPENCHOREO_VERSION` | `1.0.0` | Platform chart version |
| `DOMAIN_BASE` | `amernas.work` | Base domain for all services |
| `API_URL` | `https://api.amernas.work` | Control plane API URL |
| `THUNDER_URL` | `https://thunder.amernas.work` | OIDC provider URL |
| `BACKSTAGE_URL` | `https://backstage.amernas.work` | Developer portal URL |
| `OBSERVER_URL` | `https://observer.amernas.work` | Observability dashboard URL |
| `REGISTRY_ENDPOINT` | `registry...svc.cluster.local:5000` | In-cluster container registry |
| `CERT_MANAGER_VERSION` | `v1.19.4` | cert-manager chart version |
| `EXTERNAL_SECRETS_VERSION` | `2.0.1` | ESO chart version |
| `KGATEWAY_VERSION` | `v2.2.1` | kgateway chart version |

See `clusters/<platform>/vars/cluster-vars.yaml` for the full list.

### What FluxCD Manages

After Phase 2 completes, FluxCD owns:

- **17 HelmReleases** — cert-manager, ESO, kgateway (CRDs + controller), kubernetes-replicator, docker-registry, control plane, data plane, workflow plane, observability plane (core + 3 sub-charts), Odigos
- **24 Kustomizations** — 6 numbered infrastructure layers + sub-kustomizations + 4 app-layer kustomizations
- **TLS certificates** — Self-signed CA chain, wildcard certs for CP, DP, and OP gateways
- **Registration Jobs** — `register-planes` (data, workflow, observability) and `link-planes`
- **Network config** — Cilium L2 announcement policies and LoadBalancer IP pools

---

## 4. GitOps Repository Structure

The gitops repository (`yehia2amer/openchoreo-gitops`) contains both infrastructure and application-layer resources:

```
openchoreo-gitops/
├── clusters/                         # Per-cluster entry points
│   ├── talos-baremetal/              # Production bare-metal
│   │   ├── kustomization.yaml        # Lists numbered files as resources
│   │   ├── 00-crds.yaml             # FluxCD Kustomization → infrastructure/base/00-crds
│   │   ├── 01-prerequisites.yaml    # FluxCD Kustomization → infrastructure/base/01-prerequisites
│   │   ├── 02-tls.yaml             # FluxCD Kustomization → infrastructure/base/02-tls
│   │   ├── 03-platform.yaml        # FluxCD Kustomization → infrastructure/base/03-platform
│   │   ├── 04-registration.yaml    # FluxCD Kustomization → infrastructure/base/04-registration
│   │   ├── 05-network.yaml         # FluxCD Kustomization → infrastructure/base/05-network
│   │   └── vars/
│   │       └── cluster-vars.yaml    # Flux postBuild variable substitution
│   ├── k3d/                         # Local development (k3d)
│   ├── talos-vm/                    # Talos VM development
│   └── rancher-desktop/             # Rancher Desktop development
│
├── infrastructure/
│   ├── base/                        # Shared infrastructure (FluxCD-managed)
│   │   ├── 00-crds/                 # kgateway CRDs
│   │   ├── 01-prerequisites/        # cert-manager, ESO, kgateway, kubernetes-replicator
│   │   ├── 02-tls/                  # CA chain, wildcard certificates
│   │   ├── 03-platform/             # CP, DP, WP, OP, Odigos
│   │   ├── 04-registration/         # register-planes, link-planes Jobs
│   │   └── 05-network/              # Cilium L2 configs
│   │
│   ├── backstage-fork/              # Personal homelab infra (not FluxCD-managed)
│   ├── openchoreo-gateway/
│   ├── cert-manager/
│   ├── external-dns/
│   ├── adguard-home/
│   └── keepalived/
│
├── flux/                             # App-layer FluxCD sync configuration
│   ├── gitrepository.yaml
│   ├── namespaces-kustomization.yaml
│   ├── platform-shared-kustomization.yaml
│   ├── oc-demo-platform-kustomization.yaml
│   └── oc-demo-projects-kustomization.yaml
│
├── namespaces/                       # App namespaces and projects
│   └── default/
│       ├── platform/                 # ComponentTypes, Environments, Workflows, Traits
│       └── projects/                 # Developer project definitions
│
└── platform-shared/                  # Shared platform resources
    └── cluster-workflow-templates/   # Argo ClusterWorkflowTemplates
```

### Key Points

- **`clusters/`** — Each subdirectory is a platform overlay. All share the same `infrastructure/base/` manifests but differ in `vars/cluster-vars.yaml`.
- **`infrastructure/base/`** — Shared infrastructure manifests. Platform-specific differences are handled via Flux variable substitution, not separate files.
- **`infrastructure/` (root-level dirs)** — Personal homelab infrastructure, not managed by the numbered FluxCD layers.
- **`flux/`** — App-layer Kustomizations for namespaces, platform-shared, and demo projects.

### 4 Platform Overlays

| Platform | Use Case | Notable Differences |
|----------|----------|-------------------|
| `talos-baremetal` | Production bare-metal | Real domain, Cilium L2, NodePort registry |
| `talos-vm` | Talos VM development | Dev IP pool, `eth0` interface |
| `k3d` | Local k3d cluster | HTTP registry, no Cilium L2 |
| `rancher-desktop` | Rancher Desktop dev | Similar to k3d |

---

## 5. Rollback Procedures

### Git-Based Rollback (FluxCD)

FluxCD reconciles from Git, so rollback is a Git operation:

```bash
# Revert a specific commit in the gitops repo
cd /tmp/openchoreo-gitops
git revert <commit-hash>
git push origin main
```

FluxCD will automatically reconcile the reverted state within the reconciliation interval (1h) or immediately with a forced sync:

```bash
kubectl annotate gitrepository flux-system -n flux-system \
  "reconcile.fluxcd.io/requestedAt=$(date +%s)" --overwrite
```

### Tagged Checkpoints

Git tags mark known-good states after major deployment waves:

| Tag | State |
|-----|-------|
| `post-wave1` | After Phase 1 (Pulumi) complete |
| `post-wave2` | After FluxCD infrastructure layers healthy |
| `post-wave3` | After full platform including apps |

### Pulumi State Backups

Pulumi state snapshots are stored at:

```
.sisyphus/backups/post-wave{1,2,3}.json
```

To restore Pulumi state:

```bash
cd pulumi
pulumi stack import --file ../.sisyphus/backups/post-wave1.json
```

### HelmRelease Rollback

For individual HelmRelease issues, Flux supports suspend/resume:

```bash
# Suspend reconciliation
flux suspend hr <name> -n <namespace>

# Fix the issue in Git, then resume
flux resume hr <name> -n <namespace>
```

---

## 6. Adding a New Platform Overlay

To support a new cluster or environment:

### Step 1: Create the Cluster Directory

```bash
cd /tmp/openchoreo-gitops
mkdir -p clusters/<new-platform>/vars
```

### Step 2: Copy Numbered Kustomization Files

```bash
cp -f clusters/talos-baremetal/00-crds.yaml clusters/<new-platform>/
cp -f clusters/talos-baremetal/01-prerequisites.yaml clusters/<new-platform>/
cp -f clusters/talos-baremetal/02-tls.yaml clusters/<new-platform>/
cp -f clusters/talos-baremetal/03-platform.yaml clusters/<new-platform>/
cp -f clusters/talos-baremetal/04-registration.yaml clusters/<new-platform>/
cp -f clusters/talos-baremetal/05-network.yaml clusters/<new-platform>/
cp -f clusters/talos-baremetal/kustomization.yaml clusters/<new-platform>/
```

The numbered files are identical across platforms — all differentiation comes from variables.

### Step 3: Create Platform-Specific Variables

Create `clusters/<new-platform>/vars/cluster-vars.yaml` with values appropriate for the new platform:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-vars
  namespace: flux-system
data:
  PLATFORM: "<new-platform>"
  DOMAIN_BASE: "<your-domain>"
  OPENCHOREO_VERSION: "1.0.0"
  # ... see clusters/talos-baremetal/vars/cluster-vars.yaml for full list
```

### Step 4: Create the Master Kustomization

The `kustomization.yaml` should list the vars ConfigMap and all numbered files:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - vars/cluster-vars.yaml
  - 00-crds.yaml
  - 01-prerequisites.yaml
  - 02-tls.yaml
  - 03-platform.yaml
  - 04-registration.yaml
  - 05-network.yaml
```

### Step 5: Update Pulumi Bootstrap

In the Talos bootstrap project, set the `platform_name` config to match:

```bash
cd pulumi/talos-cluster-baremetal
pulumi config set platform_name <new-platform>
```

### Step 6: Commit and Push

```bash
git add clusters/<new-platform>/
git commit -m "Add <new-platform> cluster overlay"
git push origin main
```

---

## 7. Workflow Template Upgrade Process

OpenChoreo workflow templates (Argo WorkflowTemplates) are stored in the gitops repo and use Flux `postBuild` variable substitution for environment-specific values.

### How Variable Substitution Works

Templates in `infrastructure/base/03-platform/workflow-plane/templates/` contain `${VAR}` placeholders. When FluxCD reconciles, it substitutes values from `clusters/<platform>/vars/cluster-vars.yaml`.

Key substituted variables in templates:

| Variable | Used In | Purpose |
|----------|---------|---------|
| `REGISTRY_ENDPOINT` | `publish-image.yaml` | Container registry push target |
| `THUNDER_URL` | `generate-workload.yaml` | OAuth2 token endpoint |
| `API_URL` | `generate-workload.yaml` | Control plane API |
| `GATEWAY_ENDPOINT` | `generate-workload.yaml` | Gateway endpoint for workloads |

### Upgrading OpenChoreo Version

1. **Update the version variable** in each platform's `cluster-vars.yaml`:

   ```yaml
   data:
     OPENCHOREO_VERSION: "1.1.0"
     OPENCHOREO_REF: "release-v1.1"
   ```

2. **Commit and push** to the gitops repo:

   ```bash
   git add clusters/
   git commit -m "Upgrade OpenChoreo to v1.1.0"
   git push origin main
   ```

3. **FluxCD substitutes** the new version into all HelmReleases that reference `${OPENCHOREO_VERSION}` and reconciles the upgrade.

### Updating Individual Component Versions

Each component has its own version variable:

```yaml
CERT_MANAGER_VERSION: "v1.19.4"
EXTERNAL_SECRETS_VERSION: "2.0.1"
KGATEWAY_VERSION: "v2.2.1"
DOCKER_REGISTRY_VERSION: "3.0.0"
ODIGOS_VERSION: "1.23.0"
```

Update the specific version in `cluster-vars.yaml`, commit, and push. FluxCD handles the rolling upgrade.

---

## 8. Troubleshooting

### FluxCD Status Commands

```bash
# Overview of all Kustomizations
flux get kustomizations -A

# Overview of all HelmReleases
flux get helmreleases -A

# Kustomization logs (reconciliation events)
flux logs --kind=Kustomization

# HelmRelease logs (install/upgrade events)
flux logs --kind=HelmRelease

# Detailed status of a specific Kustomization
flux get ks <name> -n flux-system

# Detailed status of a specific HelmRelease
flux get hr <name> -n <namespace>
```

### Suspend and Resume

When debugging, you may need to pause reconciliation:

```bash
# Suspend a HelmRelease
flux suspend hr <name> -n <namespace>

# Resume after fixing
flux resume hr <name> -n <namespace>

# Suspend a Kustomization
flux suspend ks <name> -n flux-system

# Resume a Kustomization
flux resume ks <name> -n flux-system
```

### Force Reconciliation

```bash
# Force reconcile a specific Kustomization
flux reconcile ks <name> -n flux-system

# Force reconcile a specific HelmRelease
flux reconcile hr <name> -n <namespace>

# Force reconcile the root GitRepository
flux reconcile source git flux-system -n flux-system
```

### Common Issues

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Kustomization stuck `False` | Dependency layer not ready | Check previous layer: `flux get ks -A` |
| HelmRelease `install retries exhausted` | Chart values error or missing CRDs | Check logs: `flux logs --kind=HelmRelease` |
| Variable `${VAR}` not substituted | Missing in `cluster-vars.yaml` | Add the variable to the platform's ConfigMap |
| `dependsOn` timeout | Upstream component unhealthy | Check the dependency HelmRelease status |
| Registration Job failed | Plane CR not ready or RBAC issue | Check Job logs: `kubectl logs job/<name> -n openchoreo-system` |
| CRDs not found | 00-crds layer not reconciled | Force reconcile: `flux reconcile ks infra-crds -n flux-system` |

### Checking Variable Substitution

To verify what values Flux will substitute:

```bash
# View the cluster-vars ConfigMap
kubectl get configmap cluster-vars -n flux-system -o yaml

# Check if a Kustomization has substituteFrom configured
kubectl get kustomization <name> -n flux-system -o jsonpath='{.spec.postBuild}'
```

### Drift Detection

By default, HelmRelease drift detection is **not enabled**. Flux checks Helm release storage (secrets), not actual cluster resources. To enable true drift detection on critical releases, add to the HelmRelease spec:

```yaml
spec:
  driftDetection:
    mode: enabled
```

Without drift detection, deleting a Kubernetes resource (e.g., a Deployment) will NOT trigger re-creation until the next Helm release secret is invalidated.

### Viewing All Managed Resources

```bash
# All FluxCD-managed Kustomizations
kubectl get kustomizations.kustomize.toolkit.fluxcd.io -A

# All FluxCD-managed HelmReleases
kubectl get helmreleases.helm.toolkit.fluxcd.io -A

# All FluxCD-managed HelmRepositories
kubectl get helmrepositories.source.toolkit.fluxcd.io -A

# All FluxCD-managed GitRepositories
kubectl get gitrepositories.source.toolkit.fluxcd.io -A
```
