# OpenChoreo Project Onboarding Guide

> **Scope**: Everything you need to deploy, promote, troubleshoot, and manage projects on our OpenChoreo bare-metal Talos cluster using GitOps.
>
> **Audience**: Developers deploying applications and platform engineers managing the platform.
>
> **Cluster**: Talos Baremetal (`192.168.0.100:6443`) — domain `amernas.work`

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Platform Configuration](#2-platform-configuration)
3. [GitOps Repository Structure](#3-gitops-repository-structure)
4. [Option A: Pre-Built Docker Images (No CI)](#4-option-a-pre-built-docker-images-no-ci)
5. [Option B: Source Code with CI/CD Pipeline](#5-option-b-source-code-with-cicd-pipeline)
6. [autoDeploy vs autoBuild](#6-autodeploy-vs-autobuild)
7. [Environment Overrides and Promotion](#7-environment-overrides-and-promotion)
8. [Secrets Management](#8-secrets-management)
9. [Verification and Monitoring](#9-verification-and-monitoring)
10. [Troubleshooting](#10-troubleshooting)
11. [Cluster-Specific Reference](#11-cluster-specific-reference)
12. [Appendix A: CRD Quick Reference](#appendix-a-crd-quick-reference)
13. [Appendix B: Available Workflows](#appendix-b-available-workflows)
14. [Appendix C: k3d vs Talos Divergences](#appendix-c-k3d-vs-talos-divergences)

---

## 1. Architecture Overview

> **Infrastructure Deployment**: The platform uses a 2-phase deployment model. Phase 1 (Pulumi) bootstraps the cluster with Talos, Cilium, OpenBao, and Thunder. Phase 2 (FluxCD) manages all remaining infrastructure — cert-manager, external-secrets, kgateway, TLS, and the OpenChoreo platform planes. See [Deployment Guide](deployment-guide.md) for full details.

### End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Developer Workflow                           │
│                                                                      │
│  Source Repo                         GitOps Repo                     │
│  (sample-workloads)                  (openchoreo-gitops)             │
│       │                                    ▲                         │
│       │ clone                              │ push PR / merge         │
│       ▼                                    │                         │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │              Argo Workflows (Workflow Plane)                │      │
│  │                                                            │      │
│  │  WorkflowRun ──► 8-step pipeline:                         │      │
│  │    1. clone-source                                         │      │
│  │    2. resolve-refs                                         │      │
│  │    3. build-push (Podman → in-cluster registry)            │      │
│  │    4. clone-gitops-repo                                    │      │
│  │    5. generate-gitops-resources (occ CLI)                  │      │
│  │    6. commit-changes                                       │      │
│  │    7. push-to-remote                                       │      │
│  │    8. create-pull-request (GitHub API)                     │      │
│  └───────────────────────────────────────────────────────────┘      │
│       │                                    │                         │
│       │ image                              │ PR merged               │
│       ▼                                    ▼                         │
│  ┌──────────┐                   ┌──────────────────────┐            │
│  │ Registry │                   │      Flux CD          │            │
│  │(in-clust)│                   │   (flux-system)       │            │
│  └──────────┘                   │                       │            │
│                                 │  GitRepository        │            │
│                                 │    └► Kustomizations:  │            │
│                                 │      oc-namespaces     │            │
│                                 │        └► oc-platform-shared       │
│                                 │          └► oc-demo-platform       │
│                                 │            └► oc-demo-projects     │
│                                 └──────────────────────┘            │
│                                          │                           │
│                                          │ sync                      │
│                                          ▼                           │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │              OpenChoreo Control Plane                       │      │
│  │                                                            │      │
│  │  Component ──► ComponentRelease ──► ReleaseBinding         │      │
│  │                                         │                  │      │
│  │  Workload + ComponentType               │                  │      │
│  │    └► runtime config + env injection    │                  │      │
│  └─────────────────────────────────────────┼──────────────────┘      │
│                                            │ reconcile               │
│                                            ▼                         │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │              Data Plane (namespace per project+env)         │      │
│  │                                                            │      │
│  │  dp-default-doclet-development-4cc7110c                    │      │
│  │    ├─ postgres (Deployment + PVC)                          │      │
│  │    ├─ nats (Deployment)                                    │      │
│  │    ├─ document-svc (Deployment + Service + HTTPRoute)      │      │
│  │    ├─ collab-svc (Deployment + Service + HTTPRoute)        │      │
│  │    └─ frontend (Deployment + Service + HTTPRoute)          │      │
│  └───────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

### The Four Planes

| Plane | Namespace | Purpose |
|-------|-----------|---------|
| **Control** | `openchoreo-control-plane` | API server, controllers, Backstage, OpenBao |
| **Data** | `openchoreo-data-plane` + `dp-*` per project/env | Runs actual workloads |
| **Workflow** | `workflows-default` | Argo Workflows executes CI builds |
| **Observability** | `openchoreo-observability-plane` | OpenObserve, logs, metrics, traces |

### Resource Hierarchy

```
Project
  └── Component (what to deploy — metadata + build config)
        ├── Workload (how to run it — image, env vars, ports, dependencies)
        └── ComponentRelease (immutable snapshot of Component + Workload + ComponentType)
              └── ReleaseBinding (binds a release to an Environment)
                    └── RenderedRelease (controller materializes actual K8s resources)
                          └── Deployment + Service + HTTPRoute + PVC + NetworkPolicy + ...
```

**Key rules:**

- **Component** = declaration of intent ("I have a Go API called collab-svc")
- **Workload** = runtime spec ("use this image, expose port 8090, connect to nats")
- **ComponentRelease** = immutable snapshot. Once created, never modified. New builds create new releases.
- **ReleaseBinding** = "deploy release X to environment Y". Change the `releaseName` to roll forward/back.
- **ComponentType** = platform-level template defining what K8s resources get created (Deployment, Service, HTTPRoute, etc.). Platform engineers manage these — developers reference them.
- **RenderedRelease** = auto-generated by the controller. Never create manually.

**Two paths to get a ComponentRelease:**

| Path | When to Use | How It Works |
|------|-------------|-------------|
| **Manual** (Option A) | Pre-built images (databases, caches, infra) | Generate with `occ` CLI or copy from existing release |
| **CI Pipeline** (Option B) | App code that needs building | WorkflowRun triggers Argo → builds image → generates release → opens PR |

### FluxCD Sync Chain

Flux watches the gitops repo through 4 Kustomizations with explicit dependency ordering:

```
GitRepository(sample-gitops)
  ├── Kustomization(oc-namespaces)       → ./namespaces
  ├── Kustomization(oc-platform-shared)  → ./platform-shared
  │
  ├── Kustomization(oc-demo-platform)    → ./namespaces/default/platform
  │     dependsOn: [oc-namespaces, oc-platform-shared]
  │
  └── Kustomization(oc-demo-projects)    → ./namespaces/default/projects
        dependsOn: [oc-demo-platform]
```

This ensures: namespaces exist before platform resources, and platform resources (ComponentTypes, Environments, Pipelines) exist before projects reference them.

> **Note**: In addition to the app-layer Kustomizations above, the platform infrastructure is managed by a separate set of numbered FluxCD Kustomizations (00-crds through 05-network) in the `clusters/` directory. These handle cert-manager, external-secrets, kgateway, TLS, platform planes, registration, and network configuration. See [Deployment Guide](deployment-guide.md) for details.

---

## 2. Platform Configuration

These resources are already deployed on the cluster. Developers reference them — platform engineers manage them.

### ComponentTypes (5)

| Name | Reference in Component | Creates | Allowed Traits | Allowed Workflows |
|------|----------------------|---------|---------------|-------------------|
| `service` | `deployment/service` | Deployment + Service + HTTPRoute | api-configuration, observability-alert-rule | docker-gitops-release |
| `web-application` | `deployment/web-application` | Deployment + Service + HTTPRoute | api-configuration, observability-alert-rule | docker-gitops-release |
| `database` | `deployment/database` | Deployment + Service | persistent-volume | (none) |
| `message-broker` | `deployment/message-broker` | Deployment + Service | (none) | (none) |
| `usecase` | `deployment/usecase` | Deployment (minimal) | (none) | (none) |

The reference format in Component YAML is `deployment/<type-name>`. The `deployment` prefix indicates the workload type, and the suffix is the ComponentType name.

**Validation rules:**
- `service`: Must have at least 1 endpoint defined in Workload
- `web-application`: Must have at least 1 HTTP endpoint in Workload

### Environments (3)

| Name | isProduction | DataPlane | Status |
|------|-------------|-----------|--------|
| `development` | false | ClusterDataPlane/default | Ready |
| `staging` | false | ClusterDataPlane/default | Ready |
| `production` | true | ClusterDataPlane/default | Ready |

All environments share the same data plane (single-node cluster). In a multi-cluster setup, staging and production would reference different DataPlanes.

### Deployment Pipeline

The `standard` pipeline defines the promotion path:

```
development ──► staging ──► production
```

All projects reference this pipeline via `deploymentPipelineRef.name: standard`.

### Workflows (4)

| Workflow | Use Case | Key Parameters |
|----------|----------|---------------|
| `docker-gitops-release` | Build from Dockerfile + GitOps release | repository (url, branch, appPath), docker (context, filePath) |
| `react-gitops-release` | React app build (Node 16/18/20/22) | Same + nodeVersion |
| `google-cloud-buildpacks-gitops-release` | GCP Buildpacks + GitOps release | repository, buildpacks config |
| `bulk-gitops-release` | Bulk promotion across components | targetEnv, usePipeline |

### Traits (3)

| Trait | What It Does | Parameters |
|-------|-------------|-----------|
| `persistent-volume` | Creates PVC, patches Deployment with volume + volumeMount | volumeName, mountPath, containerName; envConfig: size (default 10Gi), storageClass (default longhorn) |
| `api-configuration` | Creates Backend + RestApi resources, patches HTTPRoute for API gateway routing | (advanced, for API management) |
| `observability-alert-rule` | Creates ObservabilityAlertRule on observability plane | Alert config (log/metric based) |

### CI Governance

ComponentTypes restrict which workflows developers can use via `allowedWorkflows`. For example, `service` only allows `docker-gitops-release`. Attempting to use a different workflow on a service component will fail validation.

---

## 3. GitOps Repository Structure

The gitops repo (`yehia2amer/openchoreo-gitops`) follows this layout:

```
openchoreo-gitops/
├── flux/                                          # Flux CD sync configuration
│   ├── gitrepository.yaml                         # Points to this repo
│   ├── namespaces-kustomization.yaml              # Syncs ./namespaces
│   ├── platform-shared-kustomization.yaml         # Syncs ./platform-shared
│   ├── oc-demo-platform-kustomization.yaml        # Syncs ./namespaces/default/platform
│   └── oc-demo-projects-kustomization.yaml        # Syncs ./namespaces/default/projects
│
├── platform-shared/                               # Cluster-scoped resources
│   └── cluster-workflow-templates/
│       └── argo/                                  # Argo ClusterWorkflowTemplates
│           ├── docker-with-gitops-release-template.yaml
│           ├── react-gitops-release-template.yaml
│           ├── google-cloud-buildpacks-gitops-release-template.yaml
│           └── bulk-gitops-release-template.yaml
│
├── namespaces/                                    # Namespace-scoped resources
│   ├── kustomization.yaml
│   └── default/
│       ├── namespace.yaml                         # labels: openchoreo.dev/control-plane: "true"
│       ├── platform/                              # Platform team manages this
│       │   ├── infra/
│       │   │   ├── deployment-pipelines/
│       │   │   │   └── standard.yaml
│       │   │   └── environments/
│       │   │       ├── development.yaml
│       │   │       ├── staging.yaml
│       │   │       └── production.yaml
│       │   ├── component-types/
│       │   │   ├── service.yaml
│       │   │   ├── webapp.yaml
│       │   │   ├── database.yaml
│       │   │   └── message-broker.yaml
│       │   ├── traits/
│       │   │   ├── persistent-volume.yaml
│       │   │   ├── api-management.yaml
│       │   │   └── observability-alert-rule.yaml
│       │   └── workflows/
│       │       ├── docker-with-gitops-release.yaml
│       │       ├── react-gitops-release.yaml
│       │       ├── google-cloud-buildpacks-gitops-release.yaml
│       │       └── bulk-gitops-release.yaml
│       └── projects/                              # Developers add projects here
│           └── doclet/                            # Example: the Doclet project
│               ├── project.yaml
│               └── components/
│                   ├── collab-svc/
│                   │   ├── component.yaml
│                   │   ├── workload.yaml
│                   │   ├── releases/
│                   │   │   └── collab-svc-f3a5cd49.yaml
│                   │   └── release-bindings/
│                   │       └── collab-svc-development.yaml
│                   ├── document-svc/
│                   │   └── (same structure)
│                   ├── frontend/
│                   │   └── (same structure)
│                   ├── nats/
│                   │   ├── component.yaml
│                   │   ├── workload.yaml
│                   │   ├── releases/
│                   │   │   └── nats-20260223-1.yaml
│                   │   └── release-bindings/
│                   │       ├── nats-development.yaml
│                   │       └── nats-staging.yaml
│                   └── postgres/
│                       └── (same as nats, with staging binding too)
│
└── infrastructure/                                # Personal homelab infra
    ├── kustomization.yaml                         # NOT synced by OpenChoreo Flux
    ├── openchoreo-gateway/                        # Shared gateway + HTTPRoutes
    ├── adguard-home/                              # DNS server
    ├── keepalived/                                # DNS HA (VIP)
    ├── external-dns/                              # Cloudflare + AdGuard sync
    ├── cert-manager/                              # TLS certificates
    └── backstage-fork/                            # Custom Backstage
```

**Key points:**
- All OpenChoreo resources go under `namespaces/default/projects/<project-name>/`
- Flux picks up changes recursively — just add files and commit
- The `infrastructure/` directory is personal homelab infra, not part of the OpenChoreo platform layer
- Release naming: CI-produced = `<component>-<commit-hash>`, manual = `<component>-<date>-<seq>`

---

## 4. Option A: Pre-Built Docker Images (No CI)

Use this for databases, caches, message brokers, and any component where you already have a container image.

### Step 1: Create the Project

```yaml
# namespaces/default/projects/taskboard/project.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Project
metadata:
  annotations:
    openchoreo.dev/description: "Task Board — collaborative task management"
    openchoreo.dev/display-name: Task Board
  labels:
    openchoreo.dev/name: taskboard
  name: taskboard
  namespace: default
spec:
  deploymentPipelineRef:
    name: standard
```

**Real example** (deployed on our cluster):

```yaml
# namespaces/default/projects/doclet/project.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Project
metadata:
  annotations:
    openchoreo.dev/description: "Doclet — Anonymous Real-time Collaborative Editor"
    openchoreo.dev/display-name: Doclet
  labels:
    openchoreo.dev/name: doclet
  name: doclet
  namespace: default
spec:
  deploymentPipelineRef:
    name: standard
```

### Step 2: Create a Component

Components declare WHAT you're deploying. The `componentType` determines what K8s resources get created.

**Database example** (real, from our cluster):

```yaml
# namespaces/default/projects/doclet/components/postgres/component.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: postgres
  namespace: default
spec:
  owner:
    projectName: doclet
  componentType:
    name: deployment/database
    kind: ComponentType
  parameters:
    replicas: 1
    port: 5432
  traits:
    - name: persistent-volume
      kind: Trait
      instanceName: data-storage
      parameters:
        volumeName: pg-data
        mountPath: /var/lib/postgresql/data
        containerName: main
```

The `persistent-volume` trait creates a PVC and mounts it into the container. Storage class defaults to `longhorn`, size defaults to `10Gi` (configurable per-environment via ReleaseBinding overrides).

**Message broker example** (real, from our cluster):

```yaml
# namespaces/default/projects/doclet/components/nats/component.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: nats
  namespace: default
spec:
  owner:
    projectName: doclet
  componentType:
    name: deployment/message-broker
    kind: ComponentType
  parameters:
    replicas: 1
    port: 4222
```

No `workflow` section — these components don't need CI/CD builds.

### Step 3: Create Workloads

Workloads define HOW the container runs: image, env vars, ports, and inter-component dependencies.

**Postgres workload** (real):

```yaml
# namespaces/default/projects/doclet/components/postgres/workload.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Workload
metadata:
  name: postgres
  namespace: default
spec:
  owner:
    componentName: postgres
    projectName: doclet
  container:
    image: postgres:16-alpine
    env:
      - key: POSTGRES_USER
        value: "doclet"
      - key: POSTGRES_PASSWORD
        value: "doclet-dev"
      - key: POSTGRES_DB
        value: "doclet"
      - key: PGDATA
        value: "/var/lib/postgresql/data/pgdata"
  endpoints:
    tcp:
      type: TCP
      port: 5432
```

**NATS workload** (real):

```yaml
# namespaces/default/projects/doclet/components/nats/workload.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Workload
metadata:
  name: nats
  namespace: default
spec:
  owner:
    componentName: nats
    projectName: doclet
  container:
    image: nats:2.10-alpine
    args:
      - "--jetstream"
  endpoints:
    tcp:
      type: TCP
      port: 4222
```

**Endpoint visibility options:** `project` (default, implicit), `namespace`, `internal`, `external`. Use `external` for HTTP endpoints that need ingress via the gateway.

### Step 4: Generate ComponentRelease

ComponentReleases are immutable snapshots. For pre-built images, generate them with the `occ` CLI:

```bash
# Clone the gitops repo
git clone https://github.com/yehia2amer/openchoreo-gitops.git
cd openchoreo-gitops

# Generate ComponentRelease
occ componentrelease generate \
  --mode file-system \
  --namespace default \
  --project doclet \
  --component postgres \
  --name postgres-20260407-1
```

This reads the Component + Workload + ComponentType YAMLs and produces an immutable snapshot at:
`namespaces/default/projects/doclet/components/postgres/releases/postgres-20260407-1.yaml`

**If `occ` is not installed** (as on our local machine currently), you can copy an existing release file and adapt it. The release is a frozen snapshot of the component, workload, and component type at release time. Look at `namespaces/default/projects/doclet/components/nats/releases/nats-20260223-1.yaml` for an example to copy.

### Step 5: Create ReleaseBinding

ReleaseBindings connect a release to an environment:

```yaml
# namespaces/default/projects/doclet/components/postgres/release-bindings/postgres-development.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: ReleaseBinding
metadata:
  name: postgres-development
  namespace: default
spec:
  environment: development
  owner:
    componentName: postgres
    projectName: doclet
  releaseName: postgres-20260407-1
```

To deploy to staging, create another binding:

```yaml
# namespaces/default/projects/doclet/components/postgres/release-bindings/postgres-staging.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: ReleaseBinding
metadata:
  name: postgres-staging
  namespace: default
spec:
  environment: staging
  owner:
    componentName: postgres
    projectName: doclet
  releaseName: postgres-20260407-1
```

### Step 6: Commit, Push, Verify

```bash
git add namespaces/default/projects/doclet/
git commit -m "Add doclet postgres component"
git push origin main
```

Flux detects the change within its reconciliation interval (default 5 minutes). Force immediate sync:

```bash
export KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig

kubectl annotate gitrepository sample-gitops -n flux-system \
  "reconcile.fluxcd.io/requestedAt=$(date +%s)" --overwrite
```

Watch the deployment:

```bash
# Flux sync status
kubectl get kustomization -n flux-system -w

# OpenChoreo resources
kubectl get componentreleases.openchoreo.dev -n default
kubectl get releasebindings.openchoreo.dev -n default
kubectl get renderedrelease -n default

# Actual pods (namespace is auto-generated)
kubectl get pods -A -l openchoreo.dev/project=doclet
```

The data plane namespace follows the pattern: `dp-<namespace>-<project>-<environment>-<hash>`

### Minimum Files for Pre-Built Deployment

```
project.yaml                              # Project definition
components/<name>/component.yaml          # Component metadata
components/<name>/workload.yaml           # Container spec
components/<name>/releases/<name>.yaml    # ComponentRelease (immutable)
components/<name>/release-bindings/<name>.yaml  # Environment binding
```

---

## 5. Option B: Source Code with CI/CD Pipeline

Use this when you have source code that needs building into a Docker image. The CI pipeline handles: clone -> build -> push -> generate ComponentRelease -> commit -> open PR.

### Step 1: Create Project

Same as Option A.

### Step 2: Create Component WITH Workflow Config

The key difference: components that need CI/CD include a `workflow` section and `autoBuild: true`.

**Real example** (collab-svc from our cluster):

```yaml
# namespaces/default/projects/doclet/components/collab-svc/component.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: collab-svc
  namespace: default
spec:
  owner:
    projectName: doclet
  componentType:
    name: deployment/service
    kind: ComponentType
  autoBuild: true
  workflow:
    name: docker-gitops-release
    kind: Workflow
    parameters:
      componentName: "collab-svc"
      projectName: "doclet"
      repository:
        url: "https://github.com/openchoreo/sample-workloads.git"
        revision:
          branch: "main"
        appPath: "/project-doclet-app/service-go-collab"
      docker:
        context: "/project-doclet-app/service-go-collab"
        filePath: "/project-doclet-app/service-go-collab/Dockerfile"
      workloadDescriptorPath: "workload.yaml"
  parameters:
    exposed: true
    replicas: 1
    port: 8090
```

### Step 3: Create Workload with Dependencies

Workloads reference other components via the `dependencies` section. OpenChoreo resolves these at deploy time and injects connection URLs as environment variables.

**Real example** (collab-svc depends on nats):

```yaml
# namespaces/default/projects/doclet/components/collab-svc/workload.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Workload
metadata:
  name: collab-svc-workload
  namespace: default
spec:
  owner:
    componentName: collab-svc
    projectName: doclet
  container:
    env:
      - key: DOCLET_COLLAB_ADDR
        value: ":8090"
    image: registry.openchoreo-workflow-plane.svc.cluster.local:10082/doclet-collab-svc-image:v1-f3a5cd49
  dependencies:
    endpoints:
      - component: nats
        name: tcp
        visibility: project
        envBindings:
          address: DOCLET_NATS_URL
  endpoints:
    http:
      port: 8090
      type: HTTP
```

**Dependency resolution:** The controller resolves `nats`'s TCP endpoint within the same project and injects `DOCLET_NATS_URL` pointing to the nats service in the data plane. Dependencies must be deployed and Ready before the dependent component gets correct env vars.

**The `image` field:** For CI-built components, this field gets overwritten by the pipeline with the actual built image tag. For the initial commit, use any placeholder or the last known good image.

### Step 4: Commit Component + Workload

```bash
git add namespaces/default/projects/doclet/
git commit -m "Add doclet collab-svc component and workload"
git push origin main
```

At this point Flux syncs the Component and Workload to the cluster. Nothing deploys yet — there are no ComponentReleases or ReleaseBindings.

### Step 5: Trigger the Build Pipeline

Create a WorkflowRun CR. This is **imperative** — apply it directly to the cluster, **NOT** in the gitops repo.

```yaml
# Apply directly: kubectl apply -f collab-svc-build.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: WorkflowRun
metadata:
  name: collab-svc-build-001
  namespace: default
  labels:
    openchoreo.dev/project: doclet
    openchoreo.dev/component: collab-svc
spec:
  workflow:
    kind: Workflow
    name: docker-gitops-release
    parameters:
      componentName: collab-svc
      projectName: doclet
      docker:
        context: /project-doclet-app/service-go-collab
        filePath: /project-doclet-app/service-go-collab/Dockerfile
      repository:
        appPath: /project-doclet-app/service-go-collab
        revision:
          branch: main
          commit: ""
        url: https://github.com/openchoreo/sample-workloads.git
      workloadDescriptorPath: workload.yaml
```

```bash
kubectl apply -f collab-svc-build.yaml
```

Or via the `occ` CLI:

```bash
occ component workflow run collab-svc
```

### The 8-Step Pipeline

| Step | Name | What It Does | Duration |
|------|------|-------------|----------|
| 1 | `clone-source` | Clones source repo at specified branch/commit | ~10s |
| 2 | `resolve-refs` | Resolves component references | ~5s |
| 3 | `build-push` | Builds container image with Podman, pushes to in-cluster registry | 3-8 min |
| 4 | `clone-gitops-repo` | Clones `yehia2amer/openchoreo-gitops` with GitHub PAT from OpenBao | ~10s |
| 5 | `generate-gitops-resources` | Runs `occ` CLI to generate release manifests | ~5s |
| 6 | `commit-changes` | Git commit of generated manifests to feature branch | ~5s |
| 7 | `push-to-remote` | Git push to `release/<component>-<hash>` branch | ~10s |
| 8 | `create-pull-request` | Creates PR on GitHub via API | ~5s |

**What `generate-gitops-resources` runs internally:**

```bash
# 1. Create/update Workload with real image tag
occ workload create \
  --mode file-system \
  --root-dir /workspace/gitops \
  --project doclet \
  --component collab-svc \
  --image registry.openchoreo-workflow-plane.svc.cluster.local:10082/doclet-collab-svc-image:v1-f3a5cd49 \
  --descriptor /workspace/source/workload.yaml

# 2. Generate immutable ComponentRelease
occ componentrelease generate \
  --mode file-system \
  --root-dir /workspace/gitops \
  --project doclet \
  --component collab-svc \
  --name collab-svc-f3a5cd49

# 3. Generate ReleaseBinding for first environment
occ releasebinding generate \
  --mode file-system \
  --root-dir /workspace/gitops \
  --project doclet \
  --component collab-svc \
  --component-release collab-svc-f3a5cd49
```

### Step 6: Merge the PR

After the pipeline completes, a PR appears in the gitops repo:

```bash
gh pr list --repo yehia2amer/openchoreo-gitops
gh pr merge <PR_NUMBER> --repo yehia2amer/openchoreo-gitops --merge
```

### Step 7: Force Flux Reconciliation and Verify

```bash
kubectl annotate gitrepository sample-gitops -n flux-system \
  "reconcile.fluxcd.io/requestedAt=$(date +%s)" --overwrite

# Watch deployment
kubectl get releasebindings.openchoreo.dev -n default -w
kubectl get pods -A -l openchoreo.dev/project=doclet -w
```

### Minimum Files for CI/CD Deployment

```
project.yaml                              # Project definition
components/<name>/component.yaml          # Component metadata (with workflow section)
components/<name>/workload.yaml           # Container spec (image overwritten by CI)
+ kubectl apply WorkflowRun CR            # Triggers the pipeline (imperative)
```

The pipeline automatically generates: ComponentRelease, updated Workload, ReleaseBinding — all committed via PR.

### Important Caveats

- **`occ componentrelease generate` is NOT idempotent**: If a release with the same name exists in the gitops repo, it fails. Must delete existing or use a different commit SHA.
- **Parallel builds are slower**: On a single-node cluster, 2+ simultaneous builds cause ~1.5x slowdown due to CPU contention.
- **Build pods need privileged access**: Podman requires `pod-security.kubernetes.io/enforce: privileged` on the `workflows-default` namespace.
- **Dependencies must deploy first**: If component A depends on component B, B must have a Ready ReleaseBinding before A gets correct dependency env vars.

---

## 6. autoDeploy vs autoBuild

| Flag | Effect | Use Case |
|------|--------|----------|
| `autoDeploy: true` | When a ComponentRelease is created, automatically creates a ReleaseBinding for the first environment in the deployment pipeline | Pre-built images where you want instant deployment after release creation |
| `autoBuild: true` | Triggers CI build automatically on git push via webhook (requires webhook setup) | Source code repos where every push should trigger a build |

**Combining both:**

```yaml
spec:
  autoBuild: true
  autoDeploy: true
```

Push code → auto-build triggered → image built → ComponentRelease generated → PR merged → auto-deploy creates ReleaseBinding for `development` → pods running.

**Current state on our cluster:**
- `collab-svc`, `document-svc`, `frontend`: `autoBuild: true` (auto-deploy not set)
- `postgres`, `nats`: Neither flag (manual releases)
- `sonarr`: `autoDeploy: true` (pre-built image, auto-deploys on release)

**Webhook setup for autoBuild** (platform engineer task):

```bash
# Create webhook secret
WEBHOOK_SECRET=$(openssl rand -hex 32)
kubectl create secret generic git-webhook-secrets \
  -n openchoreo-control-plane \
  --from-literal=github-secret="$WEBHOOK_SECRET"

# Configure webhook in GitHub repo settings:
# Payload URL: https://api.amernas.work/api/v1alpha1/autobuild
# Content type: application/json
# Secret: $WEBHOOK_SECRET
# Events: Push only
```

---

## 7. Environment Overrides and Promotion

### Promoting to Another Environment

To promote a release from development to staging, create a new ReleaseBinding pointing to the same release:

```yaml
# namespaces/default/projects/doclet/components/nats/release-bindings/nats-staging.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: ReleaseBinding
metadata:
  name: nats-staging
  namespace: default
spec:
  environment: staging
  owner:
    componentName: nats
    projectName: doclet
  releaseName: nats-20260223-1
```

Or via `occ` CLI:

```bash
occ component deploy nats --to staging
```

### Environment Overrides

ReleaseBindings support three types of overrides:

**1. ComponentType environment configs** (replicas, resources):

```yaml
spec:
  componentTypeEnvironmentConfigs:
    replicas: 3
    resources:
      requests:
        cpu: "500m"
        memory: "512Mi"
```

**2. Trait environment configs** (storage size, alert thresholds):

```yaml
spec:
  traitEnvironmentConfigs:
    data-storage:           # matches trait instanceName
      size: "50Gi"
      storageClass: "longhorn-ssd"
```

**3. Workload overrides** (env vars, config files):

```yaml
spec:
  workloadOverrides:
    container:
      env:
        - key: LOG_LEVEL
          value: "warn"
        - key: DB_PASSWORD
          secretKeyRef:
            name: prod-db-creds
            key: password
```

**Override priority**: ComponentType defaults < Component parameters < ReleaseBinding overrides

### Full Production ReleaseBinding Example

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: ReleaseBinding
metadata:
  name: postgres-production
  namespace: default
spec:
  environment: production
  owner:
    componentName: postgres
    projectName: doclet
  releaseName: postgres-20260223-1
  componentTypeEnvironmentConfigs:
    replicas: 2
  traitEnvironmentConfigs:
    data-storage:
      size: "100Gi"
      storageClass: "longhorn-ssd"
  workloadOverrides:
    container:
      env:
        - key: POSTGRES_PASSWORD
          secretKeyRef:
            name: prod-pg-creds
            key: password
```

### Bulk Promotion

Promote all components in a project (or all projects) at once:

```bash
# Promote all components across all projects to staging
occ releasebinding generate --all \
  --mode file-system \
  --root-dir /path/to/openchoreo-gitops \
  --target-env staging \
  --use-pipeline standard

# Promote specific project
occ releasebinding generate --project doclet \
  --mode file-system \
  --root-dir /path/to/openchoreo-gitops \
  --target-env production \
  --use-pipeline standard
```

### Rollback

Change the `releaseName` in the ReleaseBinding to point to a previous release, commit, and push:

```yaml
spec:
  releaseName: collab-svc-a1b2c3d4  # previous known-good release
```

Or via CLI:

```bash
occ component deploy collab-svc --release collab-svc-a1b2c3d4
```

List available releases:

```bash
occ componentrelease list --namespace default --project doclet --component collab-svc
# or
kubectl get componentreleases.openchoreo.dev -n default -l openchoreo.dev/component=collab-svc
```

---

## 8. Secrets Management

### Architecture

OpenChoreo uses External Secrets Operator (ESO) with OpenBao as the secret store. The flow:

```
OpenBao (secret/*)  ──►  ESO ClusterSecretStore  ──►  SecretReference CRD  ──►  K8s Secret
```

### Required CI Secrets

The build pipeline needs two secrets in OpenBao to clone source repos and push to the gitops repo:

```bash
export KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig

# Verify secrets exist
kubectl exec -n openchoreo-control-plane openbao-0 -- \
  vault kv list -mount=secret /

# Check specific secrets
kubectl exec -n openchoreo-control-plane openbao-0 -- \
  vault kv get -mount=secret git-token
kubectl exec -n openchoreo-control-plane openbao-0 -- \
  vault kv get -mount=secret gitops-token

# If missing, create them
kubectl exec -n openchoreo-control-plane openbao-0 -- \
  vault kv put -mount=secret git-token git-token="ghp_YOUR_GITHUB_TOKEN"
kubectl exec -n openchoreo-control-plane openbao-0 -- \
  vault kv put -mount=secret gitops-token git-token="ghp_YOUR_GITHUB_TOKEN"
```

### SecretReference CRD

For application secrets (database passwords, API keys), use SecretReference to pull from OpenBao into K8s Secrets:

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: SecretReference
metadata:
  name: prod-db-creds
  namespace: default
spec:
  refreshInterval: 1h
  template:
    type: Opaque
  data:
    - secretKey: password
      remoteRef:
        key: prod/postgres
        property: password
```

Then reference in Workload or ReleaseBinding overrides:

```yaml
spec:
  workloadOverrides:
    container:
      env:
        - key: DB_PASSWORD
          secretKeyRef:
            name: prod-db-creds
            key: password
```

### Private Git Repositories

For building from private repos, create a SecretReference for Git credentials and reference it in the Component:

```yaml
# SecretReference for Git auth
apiVersion: openchoreo.dev/v1alpha1
kind: SecretReference
metadata:
  name: private-repo-creds
  namespace: default
spec:
  data:
    - secretKey: username
      remoteRef:
        key: git-credentials
        property: username
    - secretKey: password
      remoteRef:
        key: git-credentials
        property: token
```

```yaml
# Component referencing private repo
spec:
  workflow:
    parameters:
      repository:
        url: "https://github.com/yehia2amer/private-app.git"
        secretRef: "private-repo-creds"
```

---

## 9. Verification and Monitoring

### Check the Full Resource Chain

```bash
export KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig

# 1. Components registered
kubectl get components.openchoreo.dev -n default -l openchoreo.dev/project=doclet

# 2. Workloads present
kubectl get workloads.openchoreo.dev -n default -l openchoreo.dev/project=doclet

# 3. Releases created
kubectl get componentreleases.openchoreo.dev -n default -l openchoreo.dev/project=doclet

# 4. Release bindings ready
kubectl get releasebindings.openchoreo.dev -n default \
  -o custom-columns='NAME:.metadata.name,COMPONENT:.spec.owner.componentName,ENV:.spec.environment,RELEASE:.spec.releaseName,READY:.status.conditions[?(@.type=="Ready")].status'

# 5. Rendered releases applied
kubectl get renderedreleases.openchoreo.dev -n default

# 6. Actual workloads running
kubectl get deployments -A -l openchoreo.dev/project=doclet
kubectl get pods -A -l openchoreo.dev/project=doclet
kubectl get svc -A -l openchoreo.dev/project=doclet
```

### Check Dependency Resolution

For components with dependencies, verify the resolved connections:

```bash
kubectl get releasebinding collab-svc-development -n default \
  -o jsonpath='{.status.resolvedConnections}' | python3 -m json.tool
```

### Check External URLs

```bash
kubectl get releasebinding -n default \
  -o jsonpath='{range .items[*]}{.metadata.name}: {.status.externalURL}{"\n"}{end}'
```

Currently deployed external URLs:
- document-svc: `https://development-default.amernas.work/document-svc-http`
- frontend: `https://http-frontend-development-default-4cc7110c.amernas.work`
- sonarr: `https://endpoint-1-sonarr-development-default-36191239.amernas.work`

### Check Flux Sync Status

```bash
kubectl get kustomization -n flux-system
kubectl get gitrepository -n flux-system
```

All should show `Ready=True`. If not:

```bash
kubectl describe kustomization <name> -n flux-system

# Force reconciliation
kubectl annotate gitrepository sample-gitops -n flux-system \
  "reconcile.fluxcd.io/requestedAt=$(date +%s)" --overwrite
```

### Check WorkflowRun Status

```bash
kubectl get workflowruns.openchoreo.dev -n default
kubectl describe workflowrun <name> -n default

# Check Argo Workflow pods
kubectl get pods -n workflows-default
kubectl logs <pod-name> -n workflows-default -c main
```

### ReleaseBinding Conditions

| Condition | Meaning |
|-----------|---------|
| `Ready=True` | Deployment is fully up and healthy |
| `Deployed=True` | Resources created in data plane |
| `Synced=True` | In sync with component definition |

---

## 10. Troubleshooting

### Common Failure Patterns

| Symptom | Cause | Fix |
|---------|-------|-----|
| Pod `CrashLoopBackOff` with missing env vars | Dependency components have no Ready ReleaseBinding | Build & deploy dependencies first |
| WorkflowRun stuck at `build-push` | PodSecurity blocking privileged containers | Check `workflows-default` ns labels: `pod-security.kubernetes.io/enforce: privileged` |
| `generate-gitops-resources` fails "already exists" | ComponentRelease name collision | Delete existing release in gitops repo or use different commit SHA |
| Flux `ReconciliationFailed` | Bad YAML in gitops repo or merge conflict | Check gitops repo, fix manifests, push |
| WorkflowRun `clone-gitops-repo` fails | GitHub PAT expired or missing | Check OpenBao: `vault kv get -mount=secret gitops-token` |
| Pods `ImagePullBackOff` | Registry unreachable or image not built | Check registry NodePort (`192.168.0.100:30082`), verify image tag |
| ReleaseBinding stuck `Deployed=False` | RenderedRelease cannot create resources | Check events: `kubectl describe renderedrelease <name> -n default` |
| Component `WorkloadNotFound` | No matching Workload in namespace | Create workload.yaml with matching `owner.componentName` |

### Debugging Workflow

```bash
# 1. Start from the top: Is Flux in sync?
kubectl get kustomization -n flux-system

# 2. Are OpenChoreo resources created?
kubectl get components,workloads,componentreleases,releasebindings -n default

# 3. Are rendered releases healthy?
kubectl get renderedreleases -n default -o wide

# 4. Find the data plane namespace
kubectl get ns -l openchoreo.dev/project=doclet

# 5. Check pods in data plane
kubectl get pods -n dp-default-doclet-development-4cc7110c

# 6. Check pod events and logs
kubectl describe pod <name> -n <dp-namespace>
kubectl logs <name> -n <dp-namespace>
```

### Flux Notifications

Flux is configured to fire alerts on sync failures. Check:

```bash
kubectl get alerts -n flux-system
kubectl logs -n flux-system deploy/notification-controller --tail=50
```

### Force Clean Rebuild

If a component's build artifacts are stale or broken:

```bash
# 1. Delete the old WorkflowRun
kubectl delete workflowrun <name> -n default

# 2. Delete the corresponding release from gitops repo
cd /tmp/openchoreo-gitops
rm namespaces/default/projects/doclet/components/<name>/releases/<release>.yaml
git add -A && git commit -m "Remove stale release" && git push origin main

# 3. Create a new WorkflowRun
kubectl apply -f <new-workflowrun>.yaml
```

---

## 11. Cluster-Specific Reference

| Setting | Value |
|---------|-------|
| **Domain** | `amernas.work` |
| **Talos Node** | `192.168.0.100` (interface: `enp7s0`) |
| **K8s API** | `https://192.168.0.100:6443` |
| **Kubeconfig** | `pulumi/talos-cluster-baremetal/outputs/kubeconfig` |
| **Shared Gateway** | `gateway-shared` in `openchoreo-gateway` (IP: `192.168.0.14`, ports 80/443) |
| **Keepalived VIP** | `192.168.0.53` (DNS failover between K8s and TrueNAS) |
| **TrueNAS** | `192.168.0.129` (interface: `eno1`) |
| **In-Cluster Registry** | `registry.openchoreo-workflow-plane.svc.cluster.local:10082` |
| **External Registry** | `192.168.0.100:30082` (NodePort) |
| **GitOps Repo** | `https://github.com/yehia2amer/openchoreo-gitops` |
| **Source Repo (demo)** | `https://github.com/openchoreo/sample-workloads` |
| **Flux GitRepository** | `sample-gitops` in `flux-system` |
| **GatewayClass** | `kgateway` |
| **StorageClass** | `longhorn` |
| **Pulumi Stack** | `talos-baremetal` (passphrase: `openchoreo-talos-baremetal`) |

### Useful Aliases

```bash
export KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig

# Force Flux sync
alias flux-sync='kubectl annotate gitrepository sample-gitops -n flux-system "reconcile.fluxcd.io/requestedAt=$(date +%s)" --overwrite'

# Watch all OpenChoreo resources
alias oc-status='kubectl get components,workloads,componentreleases,releasebindings,renderedreleases -n default'

# Watch data plane pods
alias oc-pods='kubectl get pods -A -l openchoreo.dev/project'
```

### Deployed Projects (Current State)

| Project | Components | Dev | Staging | Prod |
|---------|-----------|-----|---------|------|
| `doclet` | collab-svc, document-svc, frontend, nats, postgres | All 5 deployed | nats, postgres | (none) |
| `arr-stack` | sonarr, deep-agent (broken - no workload) | sonarr only | (none) | (none) |
| `dfg` | (empty) | (none) | (none) | (none) |

---

## Appendix A: CRD Quick Reference

All CRDs use `apiVersion: openchoreo.dev/v1alpha1`.

### Project

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Project
metadata:
  name: <project-name>            # Required
  namespace: default              # Required
  annotations:
    openchoreo.dev/display-name: "Human Name"
    openchoreo.dev/description: "Description"
spec:
  deploymentPipelineRef:
    name: standard                # Required — ref to DeploymentPipeline
```

### Component

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: <component-name>          # Required
  namespace: default              # Required
spec:
  owner:
    projectName: <project>        # Required
  componentType:
    name: deployment/<type>       # Required — service, web-application, database, message-broker, usecase
    kind: ComponentType           # Optional, default: ComponentType
  autoBuild: false                # Optional — triggers build on git push
  autoDeploy: false               # Optional — auto-creates ReleaseBinding on release creation
  parameters: {}                  # Optional — ComponentType-specific params (replicas, port, etc.)
  traits: []                      # Optional — list of attached traits
  workflow:                       # Optional — required for CI/CD
    name: <workflow-name>         # Required if workflow present
    kind: Workflow                # Optional, default: ClusterWorkflow
    parameters: {}                # Workflow-specific params
```

### Workload

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Workload
metadata:
  name: <workload-name>           # Required
  namespace: default              # Required
spec:
  owner:
    projectName: <project>        # Required
    componentName: <component>    # Required
  container:
    image: <image:tag>            # Required
    command: []                   # Optional
    args: []                      # Optional
    env:                          # Optional
      - key: <KEY>
        value: <value>            # or valueFrom.secretKeyRef
    files: []                     # Optional — mounted config files
  endpoints:                      # Optional (map of name -> endpoint)
    <endpoint-name>:
      type: HTTP                  # HTTP, gRPC, GraphQL, Websocket, TCP, UDP
      port: 8080                  # 1-65535
      visibility: [external]      # project (implicit), namespace, internal, external
  dependencies:                   # Optional
    endpoints:
      - component: <dep-component>
        name: <endpoint-name>
        visibility: project       # project or namespace
        envBindings:
          address: <ENV_VAR_NAME>
```

### ComponentRelease (Immutable)

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: ComponentRelease
metadata:
  name: <component>-<hash-or-date>  # Required, immutable
  namespace: default
spec:
  owner:
    projectName: <project>
    componentName: <component>
  componentType: { ... }          # Snapshot of ComponentType spec
  componentProfile: { ... }       # Snapshot of Component parameters + traits
  workload: { ... }               # Snapshot of Workload container + endpoints + deps
```

Generated by `occ componentrelease generate` or the CI pipeline. Never edit after creation.

### ReleaseBinding

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: ReleaseBinding
metadata:
  name: <component>-<environment>  # Required
  namespace: default
spec:
  owner:
    projectName: <project>        # Required
    componentName: <component>    # Required
  environment: <env-name>         # Required — development, staging, production
  releaseName: <release-name>     # Required — points to ComponentRelease
  componentTypeEnvironmentConfigs: {}  # Optional — override replicas, resources
  traitEnvironmentConfigs: {}          # Optional — override trait params per env
  workloadOverrides:                   # Optional — override env vars, files
    container:
      env:
        - key: <KEY>
          value: <value>
```

---

## Appendix B: Available Workflows

### docker-gitops-release

Build from Dockerfile, push to in-cluster registry, generate GitOps release.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `repository.url` | Yes | - | Git repo URL |
| `repository.revision.branch` | No | `main` | Branch to build from |
| `repository.revision.commit` | No | `""` | Specific commit (empty = HEAD) |
| `repository.appPath` | No | `/` | Path to app within repo |
| `repository.secretRef` | No | `""` | SecretReference name for private repos |
| `docker.context` | No | `.` | Docker build context |
| `docker.filePath` | No | `./Dockerfile` | Path to Dockerfile |
| `workloadDescriptorPath` | No | `workload.yaml` | Path to workload descriptor in source |
| `componentName` | Yes | - | Component name |
| `projectName` | Yes | - | Project name |

### react-gitops-release

Build React app (with Node.js), push to registry, generate GitOps release.

Same parameters as `docker-gitops-release` plus:

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `nodeVersion` | No | `20` | Node.js version (16, 18, 20, 22) |

### google-cloud-buildpacks-gitops-release

Build with Google Cloud Buildpacks, push to registry, generate GitOps release.

Same `repository` parameters. Uses buildpacks instead of Dockerfile — no `docker` parameters needed.

### bulk-gitops-release

Promote releases across environments. Used for bulk promotion, not individual builds.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `targetEnv` | Yes | - | Target environment name |
| `usePipeline` | Yes | - | DeploymentPipeline name |
| `project` | No | `""` | Specific project (empty = all) |

---

## Appendix C: k3d vs Talos Divergences

| Area | k3d (Default Dev) | Talos Baremetal | Fix Applied |
|------|-------------------|-----------------|-------------|
| **PodSecurity** | Not enforced | Default `baseline` (rejects privileged) | Pre-create `workflows-default` ns with `pod-security.kubernetes.io/enforce: privileged` |
| **Registry DNS** | `registry.kube-system.svc.cluster.local:5000` (HTTP) | Exposed via NodePort (`192.168.0.100:30082`) + internal DNS | CoreDNS rewrite + registry trust |
| **Registry protocol** | HTTP only | HTTPS via Gateway (self-signed CA) | CA cert propagated to build pods |
| **StorageClass** | `local-path` (auto) | `longhorn` (must configure) | Pulumi creates StorageClass |
| **Postgres PGDATA** | Works with default | `PGDATA` must differ from volume mount point | Set `PGDATA=/var/lib/postgresql/data/pgdata` |
| **Gateway API** | Generic implementation | kgateway (Cilium-based) | Cilium GatewayClass in Pulumi |
| **DNS resolution** | Docker DNS | AdGuard Home + keepalived VIP (192.168.0.53) | Split-horizon DNS with failover |
| **TLS certificates** | Self-signed (local) | Cloudflare Origin + Let's Encrypt staging | cert-manager with ClusterIssuers |
