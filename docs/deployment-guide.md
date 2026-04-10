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
4. [Component-Based Platform Architecture](#4-component-based-platform-architecture)
5. [GitOps Repository Structure](#5-gitops-repository-structure)
6. [Rollback Procedures](#6-rollback-procedures)
7. [Adding a New Platform Overlay](#7-adding-a-new-platform-overlay)
8. [Adding a New Component](#8-adding-a-new-component)
9. [Workflow Template Upgrade Process](#9-workflow-template-upgrade-process)
10. [Troubleshooting](#10-troubleshooting)

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

Each layer is a FluxCD `Kustomization` resource in the `flux-system` namespace. The `path` points to the **platform overlay** directory (not base directly), which composes base resources with platform-specific components:

```
wave-00-crds         → ./infrastructure/platforms/<platform>/00-crds
wave-01-prerequisites → ./infrastructure/platforms/<platform>/01-prerequisites
wave-02-tls          → ./infrastructure/platforms/<platform>/02-tls
wave-03-platform     → ./infrastructure/platforms/<platform>/03-platform
wave-04-registration → ./infrastructure/platforms/<platform>/04-registration
wave-05-network      → ./infrastructure/platforms/<platform>/05-network
```

Each wave overlay contains a `kustomization.yaml` that references `infrastructure/base/<wave>/` resources plus any Kustomize Components needed for that platform. See [Component-Based Platform Architecture](#4-component-based-platform-architecture) for details.

### Dependency Chain

```
wave-00-crds
  └── wave-01-prerequisites (dependsOn: wave-00-crds)
        └── wave-02-tls (dependsOn: wave-01-prerequisites)
              └── wave-03-platform (dependsOn: wave-02-tls)
                    └── wave-04-registration (dependsOn: wave-03-platform)
                          └── wave-05-network (dependsOn: wave-04-registration)
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

## 4. Component-Based Platform Architecture

The platform uses **Kustomize Components** (`kind: Component`) to toggle platform-specific infrastructure across different deployment targets (baremetal, k3d, GCP, AWS, Azure). This avoids Helm conditionals, Flux `.spec.components` (broken per Flux bug #1506), and per-platform repository duplication.

> **Design Reference**: See [ADR-006: Kustomize Components for Platform Feature Flags](adr/006-kustomize-components-platform-feature-flags.md) for the full decision record.
>
> **Component ↔ Platform Mapping**: See [Component-Platform Mapping](component-platform-mapping.md) for the complete mapping between Pulumi `PlatformProfile` fields and Kustomize Components.

### How It Works

Each FluxCD wave resolves to a **platform overlay** that composes shared base resources with platform-specific components:

```
infrastructure/platforms/<platform>/<wave>/kustomization.yaml
  ├── resources: ../../../base/<wave>/<sub-dir>     ← shared across all platforms
  └── components: ../../../components/<name>         ← platform-specific toggles
```

**Key design constraint**: Components are referenced in the filesystem `kustomization.yaml` using the `components:` field — NOT via Flux's `.spec.components` (which has a known bug, fluxcd/kustomize-controller#1506).

### Components Directory

All Kustomize Components live under `infrastructure/components/`:

| Component | Kind | Used By | What It Does |
|-----------|------|---------|-------------|
| `cilium-l2` | Active | baremetal | L2 announcement policies + LoadBalancer IP pools |
| `issuer-selfsigned` | Active | baremetal, k3d | Self-signed CA ClusterIssuer for TLS |
| `registry-self-hosted` | Active | baremetal, k3d | In-cluster Docker registry (NodePort) |
| `observability-self-hosted` | Active | baremetal, k3d | Self-hosted OpenObserve observability stack |
| `network-cilium-policy` | Active | baremetal, k3d | Cilium NetworkPolicy resources |
| `kubernetes-replicator` | Active | baremetal, k3d | Cross-namespace secret replication |
| `issuer-gcp-cas` | Stub | (planned: GCP) | Google Certificate Authority Service issuer |
| `issuer-letsencrypt` | Stub | (planned) | Let's Encrypt ACME issuer |
| `registry-cloud` | Stub | (planned: GCP/AWS/Azure) | Cloud-managed container registry |
| `observability-cloud` | Stub | (planned: GCP/AWS/Azure) | Cloud-managed observability |
| `secrets-gcp-sm` | Stub | (planned: GCP) | Google Secret Manager integration |
| `secrets-openbao` | Stub | (planned) | OpenBao secrets backend |

Each component directory contains a `kustomization.yaml` with `kind: Component` that patches, adds, or removes resources from the base.

### Platform Overlays

Each platform has 6 wave subdirectories under `infrastructure/platforms/<platform>/`:

```
infrastructure/platforms/
├── baremetal/
│   ├── 00-crds/kustomization.yaml
│   ├── 01-prerequisites/kustomization.yaml
│   ├── 02-tls/kustomization.yaml
│   ├── 03-platform/kustomization.yaml
│   ├── 04-registration/kustomization.yaml
│   └── 05-network/kustomization.yaml
├── k3d/
│   └── (same 6 wave subdirectories)
├── gcp/                              ← stub (directory structure only)
├── aws/                              ← stub (directory structure only)
└── azure/                            ← stub (directory structure only)
```

**Example**: `baremetal/05-network/kustomization.yaml` includes the Cilium L2 component while `k3d/05-network/` does not:

```yaml
# infrastructure/platforms/baremetal/05-network/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../../base/05-network/cilium-configs
components:
  - ../../../components/cilium-l2          # baremetal needs L2 announcements

# infrastructure/platforms/k3d/05-network/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../../base/05-network/cilium-configs
                                            # no cilium-l2 — k3d uses Docker networking
```

### Wave → Component Mapping (Baremetal)

| Wave | Base Resources | Components |
|------|---------------|-----------|
| 00-crds | `base/00-crds` | (none) |
| 01-prerequisites | cert-manager, ESO, kgateway, kubernetes-replicator | `kubernetes-replicator` |
| 02-tls | CA chain, wildcard certs | `issuer-selfsigned` |
| 03-platform | CP, DP, WP, OP, Odigos | `network-cilium-policy`, `observability-self-hosted`, `registry-self-hosted` |
| 04-registration | register-planes, link-planes | (none) |
| 05-network | cilium-configs | `cilium-l2` |

### Resource Removal via `$patch: delete`

When a component needs to **remove** a resource from the base (rather than add or modify), it uses the strategic merge patch `$patch: delete` directive. This is the Kustomize-native way to subtract resources without maintaining separate base variants.

---

## 5. GitOps Repository Structure

The gitops repository (`yehia2amer/openchoreo-gitops`) contains both infrastructure and application-layer resources:

```
openchoreo-gitops/
├── clusters/                         # Per-cluster entry points
│   ├── talos-baremetal/              # Production bare-metal
│   │   ├── kustomization.yaml        # Lists numbered files as resources
│   │   ├── 00-crds.yaml             # FluxCD Kustomization → platforms/<platform>/00-crds
│   │   ├── 01-prerequisites.yaml    # FluxCD Kustomization → platforms/<platform>/01-prerequisites
│   │   ├── 02-tls.yaml             # FluxCD Kustomization → platforms/<platform>/02-tls
│   │   ├── 03-platform.yaml        # FluxCD Kustomization → platforms/<platform>/03-platform
│   │   ├── 04-registration.yaml    # FluxCD Kustomization → platforms/<platform>/04-registration
│   │   ├── 05-network.yaml         # FluxCD Kustomization → platforms/<platform>/05-network
│   │   └── vars/
│   │       └── cluster-vars.yaml    # Flux postBuild variable substitution
│   ├── k3d/                         # Local development (k3d)
│   ├── talos-vm/                    # Talos VM development
│   └── rancher-desktop/             # Rancher Desktop development
│
├── infrastructure/
│   ├── base/                        # Shared infrastructure manifests
│   │   ├── 00-crds/                 # kgateway CRDs
│   │   ├── 01-prerequisites/        # cert-manager, ESO, kgateway, kubernetes-replicator
│   │   ├── 02-tls/                  # CA chain, wildcard certificates
│   │   ├── 03-platform/             # CP, DP, WP, OP, Odigos
│   │   ├── 04-registration/         # register-planes, link-planes Jobs
│   │   └── 05-network/              # Cilium configs
│   │
│   ├── components/                  # Kustomize Components (platform feature toggles)
│   │   ├── cilium-l2/               # L2 announcement policies (baremetal only)
│   │   ├── issuer-selfsigned/       # Self-signed CA issuer
│   │   ├── registry-self-hosted/    # In-cluster Docker registry
│   │   ├── observability-self-hosted/ # Self-hosted observability stack
│   │   ├── network-cilium-policy/   # Cilium NetworkPolicy resources
│   │   ├── kubernetes-replicator/   # Cross-namespace secret replication
│   │   ├── issuer-gcp-cas/          # (stub) GCP Certificate Authority Service
│   │   ├── issuer-letsencrypt/      # (stub) Let's Encrypt ACME issuer
│   │   ├── registry-cloud/          # (stub) Cloud-managed registry
│   │   ├── observability-cloud/     # (stub) Cloud-managed observability
│   │   ├── secrets-gcp-sm/          # (stub) GCP Secret Manager
│   │   └── secrets-openbao/         # (stub) OpenBao secrets backend
│   │
│   ├── platforms/                   # Per-platform wave overlays (base + components)
│   │   ├── baremetal/               # 6 wave subdirs with kustomization.yaml each
│   │   ├── k3d/                     # 6 wave subdirs (no cilium-l2)
│   │   ├── gcp/                     # (stub) directory structure only
│   │   ├── aws/                     # (stub) directory structure only
│   │   └── azure/                   # (stub) directory structure only
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

- **`clusters/`** — Each subdirectory is a cluster entry point. The numbered YAML files define FluxCD Kustomizations whose `path:` points to platform-specific wave overlays under `infrastructure/platforms/<platform>/`.
- **`infrastructure/base/`** — Shared infrastructure manifests used by all platforms. Never referenced directly by FluxCD — always consumed through platform overlays.
- **`infrastructure/components/`** — Kustomize Components (`kind: Component`) that toggle platform-specific features. See [Section 4](#4-component-based-platform-architecture).
- **`infrastructure/platforms/`** — Per-platform wave overlays. Each wave's `kustomization.yaml` composes base resources + components. See [Section 4](#4-component-based-platform-architecture).
- **`infrastructure/` (root-level dirs)** — Personal homelab infrastructure, not managed by the numbered FluxCD layers.
- **`flux/`** — App-layer Kustomizations for namespaces, platform-shared, and demo projects.

### Cluster Entry Points

| Platform | Use Case | Notable Differences |
|----------|----------|-------------------|
| `talos-baremetal` | Production bare-metal | Real domain, Cilium L2, NodePort registry |
| `talos-vm` | Talos VM development | Dev IP pool, `eth0` interface |
| `k3d` | Local k3d cluster | HTTP registry, no Cilium L2 |
| `rancher-desktop` | Rancher Desktop dev | Similar to k3d |

---

## 6. Rollback Procedures

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

## 7. Adding a New Platform Overlay

To support a new deployment target (e.g., a new cloud provider or bare-metal variant):

### Step 1: Create the Cluster Entry Point

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

Update the `path:` in each numbered YAML file to point to `./infrastructure/platforms/<new-platform>/<wave>` instead of the source platform.

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

### Step 4: Create Platform Wave Overlays

Create the 6 wave subdirectories under `infrastructure/platforms/<new-platform>/`. Each wave needs a `kustomization.yaml` that references the shared base resources and the components appropriate for your platform:

```bash
mkdir -p infrastructure/platforms/<new-platform>/{00-crds,01-prerequisites,02-tls,03-platform,04-registration,05-network}
```

For each wave, create a `kustomization.yaml`. Use `baremetal` as a starting point and adjust the `components:` list for your platform:

```yaml
# Example: infrastructure/platforms/<new-platform>/03-platform/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../../base/03-platform/control-plane
  - ../../../base/03-platform/data-plane
  - ../../../base/03-platform/workflow-plane
  - ../../../base/03-platform/observability-plane
  - ../../../base/03-platform/odigos
components:
  # Include only the components your platform needs:
  - ../../../components/network-cilium-policy
  - ../../../components/observability-self-hosted   # or observability-cloud for cloud platforms
  - ../../../components/registry-self-hosted         # or registry-cloud for cloud platforms
```

See [Component-Based Platform Architecture](#4-component-based-platform-architecture) for the full list of available components and [Component-Platform Mapping](component-platform-mapping.md) for which components each platform profile uses.

### Step 5: Create the Master Kustomization

The `clusters/<new-platform>/kustomization.yaml` should list the vars ConfigMap and all numbered files:

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

### Step 6: Update Pulumi Bootstrap

In the Talos bootstrap project, set the `platform_name` config to match:

```bash
cd pulumi/talos-cluster-baremetal
pulumi config set platform_name <new-platform>
```

### Step 7: Commit and Push

```bash
git add clusters/<new-platform>/ infrastructure/platforms/<new-platform>/
git commit -m "Add <new-platform> platform overlay"
git push origin main
```

---

## 8. Adding a New Component

To add a new platform-specific feature as a Kustomize Component:

### Step 1: Create the Component Directory

```bash
mkdir -p infrastructure/components/<component-name>
```

### Step 2: Create the Component Kustomization

Create `infrastructure/components/<component-name>/kustomization.yaml` with `kind: Component`:

```yaml
apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component

# Add new resources:
resources:
  - my-resource.yaml

# Or patch existing base resources:
patches:
  - target:
      kind: HelmRelease
      name: existing-release
    patch: |
      - op: add
        path: /spec/values/newKey
        value: newValue
```

> **Note**: Use `$patch: delete` in strategic merge patches when you need to **remove** a base resource for a specific platform.

### Step 3: Add Resources

Place any additional manifests (YAML files) in the component directory alongside the `kustomization.yaml`.

### Step 4: Wire Into Platform Overlays

Add the component to the appropriate wave's `kustomization.yaml` for each platform that needs it:

```yaml
# infrastructure/platforms/baremetal/<wave>/kustomization.yaml
components:
  - ../../../components/<component-name>
```

### Step 5: Update Documentation

- Add the component to the table in [Component-Platform Mapping](component-platform-mapping.md)
- Update the Pulumi `PlatformProfile` if the component maps to a profile field

---

## 9. Workflow Template Upgrade Process

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

## 10. Troubleshooting

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
