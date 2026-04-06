# OpenChoreo Project Onboarding Guide (GitOps-Only, No UI)

This guide walks through deploying a new project with multiple applications and databases on OpenChoreo using only FluxCD and the GitOps repo. No UI involved.

We use a concrete example throughout: a project called **"taskboard"** with:

- `api-server` — Go REST API (needs CI/CD build)
- `web-app` — React frontend (needs CI/CD build)
- `postgres` — PostgreSQL database (pre-built image)
- `redis` — Redis cache (pre-built image)

---

## Table of Contents

1. [How the Deployment Lifecycle Works](#how-the-deployment-lifecycle-works)
2. [GitOps Repo Structure](#gitops-repo-structure)
3. [Option A: Pre-Built Docker Images (No CI)](#option-a-pre-built-docker-images-no-ci)
4. [Option B: Source Code with CI/CD Pipeline](#option-b-source-code-with-cicd-pipeline)
5. [Verifying Deployment](#verifying-deployment)
6. [Promoting to Staging/Production](#promoting-to-stagingproduction)
7. [Troubleshooting](#troubleshooting)
8. [Reference: OpenChoreo Resource Hierarchy](#reference-openchoreo-resource-hierarchy)

---

## How the Deployment Lifecycle Works

OpenChoreo uses a layered abstraction model. Understanding the chain is critical:

```
Project
  └── Component (what to deploy — metadata + build config)
        └── Workload (how to run it — image, env vars, ports, dependencies)
              └── ComponentRelease (immutable snapshot of Component + Workload + ComponentType)
                    └── ReleaseBinding (binds a release to an Environment)
                          └── RenderedRelease (controller materializes actual K8s resources)
                                └── Deployment + Service + HTTPRoute + PVC + ...
```

**Key rules:**

- **Component** = declaration of intent ("I have a Go API called api-server")
- **Workload** = runtime specification ("use this image, expose port 8080, connect to postgres")
- **ComponentRelease** = immutable snapshot. Once created, never modified. New builds create new releases.
- **ReleaseBinding** = "deploy release X to environment Y". Change the `releaseName` to roll forward/back.
- **ComponentType** = platform-level template that defines what K8s resources get created (Deployment, Service, HTTPRoute, etc.). You don't write these — they already exist in your platform config.

**What Flux does:** Flux watches the gitops repo. When you commit a new ComponentRelease + ReleaseBinding, Flux syncs them to the cluster. The OpenChoreo controller sees the new ReleaseBinding, renders the actual K8s resources (Deployment, Service, etc.), and deploys them.

**Two paths to get a ComponentRelease:**

| Path | When to Use | How It Works |
|------|-------------|-------------|
| **Manual** (Option A) | Pre-built images (databases, caches, infra) | You write the ComponentRelease YAML by hand using `occ` CLI or copy from an existing one |
| **CI Pipeline** (Option B) | App code that needs building | A WorkflowRun triggers Argo Workflows, which builds the image, runs `occ` CLI to generate the ComponentRelease, commits to a branch, and opens a PR |

---

## GitOps Repo Structure

Every project follows this directory layout inside the gitops repo:

```
namespaces/
  default/                              # Kubernetes namespace
    projects/
      taskboard/                        # Your project
        project.yaml                    # Project definition
        components/
          api-server/
            component.yaml              # Component definition
            workload.yaml               # Workload specification
            releases/
              api-server-<hash>.yaml    # ComponentRelease (immutable)
            release-bindings/
              api-server-development.yaml   # Binds release → environment
          web-app/
            component.yaml
            workload.yaml
            releases/
              web-app-<hash>.yaml
            release-bindings/
              web-app-development.yaml
          postgres/
            component.yaml
            workload.yaml
            releases/
              postgres-20260406-1.yaml
            release-bindings/
              postgres-development.yaml
          redis/
            component.yaml
            workload.yaml
            releases/
              redis-20260406-1.yaml
            release-bindings/
              redis-development.yaml
```

Flux Kustomizations already watch `namespaces/` recursively — you just add files and commit.

---

## Option A: Pre-Built Docker Images (No CI)

Use this for databases, caches, message brokers, and any component where you already have a container image (e.g., `postgres:16-alpine`, `redis:7-alpine`, or your own registry image).

### Step 1: Create the Project

```yaml
# namespaces/default/projects/taskboard/project.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Project
metadata:
  annotations:
    openchoreo.dev/description: Task Board — collaborative task management
    openchoreo.dev/display-name: Task Board
  labels:
    openchoreo.dev/name: taskboard
  name: taskboard
  namespace: default
spec:
  deploymentPipelineRef:
    name: standard
```

`deploymentPipelineRef: standard` gives you the `development → staging → production` promotion path that's already defined in your platform config.

### Step 2: Create Components (Metadata)

Components declare WHAT you're deploying and its type. The `componentType` determines what K8s resources get created.

**Available component types** (defined in `platform/component-types/`):

| ComponentType Name | Use For | Creates |
|--------------------|---------|---------|
| `deployment/service` | Backend APIs, microservices | Deployment + Service + HTTPRoute |
| `deployment/web-application` | Frontends, web UIs | Deployment + Service + HTTPRoute |
| `deployment/database` | PostgreSQL, MySQL, etc. | Deployment + Service + PVC (with trait) |
| `deployment/message-broker` | NATS, RabbitMQ, Kafka | Deployment + Service |

**Postgres component:**

```yaml
# namespaces/default/projects/taskboard/components/postgres/component.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: postgres
  namespace: default
spec:
  owner:
    projectName: taskboard
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

The `persistent-volume` trait automatically creates a PVC and mounts it into the container. The `storageClass` defaults to `longhorn` and `size` defaults to `1Gi` (configurable per-environment).

**Redis component:**

```yaml
# namespaces/default/projects/taskboard/components/redis/component.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: redis
  namespace: default
spec:
  owner:
    projectName: taskboard
  componentType:
    name: deployment/message-broker
    kind: ComponentType
  parameters:
    replicas: 1
    port: 6379
```

No `workflow` section — these components don't need CI/CD.

### Step 3: Create Workloads (Runtime Spec)

Workloads define HOW the container runs: image, env vars, ports, and inter-component dependencies.

**Postgres workload:**

```yaml
# namespaces/default/projects/taskboard/components/postgres/workload.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Workload
metadata:
  name: postgres
  namespace: default
spec:
  owner:
    componentName: postgres
    projectName: taskboard
  container:
    image: postgres:16-alpine
    env:
      - key: POSTGRES_USER
        value: "taskboard"
      - key: POSTGRES_PASSWORD
        value: "taskboard"
      - key: POSTGRES_DB
        value: "taskboard"
      - key: PGDATA
        value: "/var/lib/postgresql/data/pgdata"
  endpoints:
    tcp:
      type: TCP
      port: 5432
```

**Redis workload:**

```yaml
# namespaces/default/projects/taskboard/components/redis/workload.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Workload
metadata:
  name: redis
  namespace: default
spec:
  owner:
    componentName: redis
    projectName: taskboard
  container:
    image: redis:7-alpine
    args:
      - "--appendonly"
      - "yes"
  endpoints:
    tcp:
      type: TCP
      port: 6379
```

### Step 4: Generate ComponentReleases

ComponentReleases are immutable snapshots. For pre-built images, you generate them using the `occ` CLI:

```bash
# Clone the gitops repo locally
git clone https://github.com/<your-org>/openchoreo-gitops.git
cd openchoreo-gitops

# Generate ComponentRelease for postgres
occ componentrelease generate \
  --mode file-system \
  --namespace default \
  --project taskboard \
  --component postgres \
  --name postgres-20260406-1

# Generate ComponentRelease for redis
occ componentrelease generate \
  --mode file-system \
  --namespace default \
  --project taskboard \
  --component redis \
  --name redis-20260406-1
```

This reads the Component + Workload + ComponentType YAMLs and produces an immutable snapshot at:
- `namespaces/default/projects/taskboard/components/postgres/releases/postgres-20260406-1.yaml`
- `namespaces/default/projects/taskboard/components/redis/releases/redis-20260406-1.yaml`

**If you don't have `occ` CLI installed**, you can copy and adapt an existing release file. The key fields are the `spec.componentProfile`, `spec.componentType`, and `spec.workload` sections — they're snapshots of the Component, ComponentType, and Workload at release time.

### Step 5: Create ReleaseBindings

ReleaseBindings connect a specific release to an environment:

```yaml
# namespaces/default/projects/taskboard/components/postgres/release-bindings/postgres-development.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: ReleaseBinding
metadata:
  name: postgres-development
  namespace: default
spec:
  environment: development
  owner:
    componentName: postgres
    projectName: taskboard
  releaseName: postgres-20260406-1
```

```yaml
# namespaces/default/projects/taskboard/components/redis/release-bindings/redis-development.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: ReleaseBinding
metadata:
  name: redis-development
  namespace: default
spec:
  environment: development
  owner:
    componentName: redis
    projectName: taskboard
  releaseName: redis-20260406-1
```

### Step 6: Commit and Push

```bash
git add namespaces/default/projects/taskboard/
git commit -m "Add taskboard project with postgres and redis"
git push origin main
```

Flux detects the change within its reconciliation interval (default: 5 minutes). Force immediate sync:

```bash
kubectl annotate gitrepository sample-gitops -n flux-system \
  "reconcile.fluxcd.io/requestedAt=$(date +%s)" --overwrite
```

### Step 7: Watch It Deploy

```bash
# Watch Flux pick up the changes
kubectl get kustomization -n flux-system -w

# Watch the OpenChoreo controller create resources
kubectl get componentreleases.openchoreo.dev -n default
kubectl get releasebindings.openchoreo.dev -n default
kubectl get renderedrelease -n default

# Watch the actual pods come up (namespace is auto-generated)
kubectl get pods -A -l openchoreo.dev/project=taskboard
```

The data plane namespace follows the pattern: `dp-<namespace>-<project>-<environment>-<hash>`

---

## Option B: Source Code with CI/CD Pipeline

Use this when you have source code that needs to be built into a Docker image. The CI/CD pipeline handles: clone → build → push → generate ComponentRelease → commit → open PR.

### Step 1: Create Project (same as Option A)

Same `project.yaml` as above.

### Step 2: Create Components WITH Workflow Config

The key difference: components that need CI/CD include a `workflow` section and `autoBuild: true`.

**API Server component:**

```yaml
# namespaces/default/projects/taskboard/components/api-server/component.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: api-server
  namespace: default
spec:
  owner:
    projectName: taskboard
  componentType:
    name: deployment/service
    kind: ComponentType
  autoBuild: true
  workflow:
    name: docker-gitops-release
    kind: Workflow
    parameters:
      componentName: "api-server"
      projectName: "taskboard"
      repository:
        url: "https://github.com/<your-org>/taskboard.git"
        revision:
          branch: "main"
        appPath: "/services/api-server"
      docker:
        context: "/services/api-server"
        filePath: "/services/api-server/Dockerfile"
      workloadDescriptorPath: "workload.yaml"
  parameters:
    exposed: true
    replicas: 1
    port: 8080
```

**Web App component:**

```yaml
# namespaces/default/projects/taskboard/components/web-app/component.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: web-app
  namespace: default
spec:
  owner:
    projectName: taskboard
  componentType:
    name: deployment/web-application
    kind: ComponentType
  autoBuild: true
  workflow:
    name: docker-gitops-release
    kind: Workflow
    parameters:
      componentName: "web-app"
      projectName: "taskboard"
      repository:
        url: "https://github.com/<your-org>/taskboard.git"
        revision:
          branch: "main"
        appPath: "/frontend"
      docker:
        context: "/frontend"
        filePath: "/frontend/Dockerfile"
      workloadDescriptorPath: "workload.yaml"
  parameters:
    replicas: 1
    port: 80
```

### Step 3: Create Workloads with Dependencies

Workloads reference other components via the `dependencies` section. OpenChoreo resolves these at deploy time and injects the connection URLs as environment variables.

**API Server workload** (depends on postgres and redis):

```yaml
# namespaces/default/projects/taskboard/components/api-server/workload.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Workload
metadata:
  name: api-server-workload
  namespace: default
spec:
  owner:
    componentName: api-server
    projectName: taskboard
  container:
    image: PLACEHOLDER
    env:
      - key: APP_PORT
        value: "8080"
  dependencies:
    endpoints:
      - component: postgres
        name: tcp
        visibility: project
        envBindings:
          address: DATABASE_URL
      - component: redis
        name: tcp
        visibility: project
        envBindings:
          address: REDIS_URL
  endpoints:
    http:
      port: 8080
      type: HTTP
```

The `image: PLACEHOLDER` will be overwritten by the CI pipeline with the actual built image tag. The `dependencies.endpoints` section tells OpenChoreo to inject `DATABASE_URL` and `REDIS_URL` env vars pointing to the postgres and redis services within the same project/environment.

**Web App workload** (depends on api-server):

```yaml
# namespaces/default/projects/taskboard/components/web-app/workload.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Workload
metadata:
  name: web-app-workload
  namespace: default
spec:
  owner:
    componentName: web-app
    projectName: taskboard
  container:
    image: PLACEHOLDER
    env:
      - key: REACT_APP_API_URL
        value: "/api-server-http"
  endpoints:
    http:
      port: 80
      type: HTTP
      visibility:
        - external
```

### Step 4: Commit the Component + Workload Files

```bash
git add namespaces/default/projects/taskboard/
git commit -m "Add taskboard project components and workloads"
git push origin main
```

At this point Flux syncs and the OpenChoreo controller sees the Components and Workloads, but nothing deploys yet — there are no ComponentReleases or ReleaseBindings.

### Step 5: Ensure Secrets Are in OpenBao

The CI pipeline needs GitHub tokens to clone source repos and push to the gitops repo. These are stored in OpenBao:

```bash
# Verify the secrets exist
kubectl exec -n openchoreo-control-plane openbao-0 -- \
  vault kv get -mount=secret git-token
kubectl exec -n openchoreo-control-plane openbao-0 -- \
  vault kv get -mount=secret gitops-token

# If missing, create them:
kubectl exec -n openchoreo-control-plane openbao-0 -- \
  vault kv put -mount=secret git-token git-token="ghp_YOUR_TOKEN"
kubectl exec -n openchoreo-control-plane openbao-0 -- \
  vault kv put -mount=secret gitops-token git-token="ghp_YOUR_TOKEN"
```

### Step 6: Trigger the Build Pipeline

Create a WorkflowRun for each component that needs building:

```yaml
# Apply this to the cluster (not the gitops repo)
apiVersion: openchoreo.dev/v1alpha1
kind: WorkflowRun
metadata:
  name: api-server-build-001
  namespace: default
  labels:
    openchoreo.dev/project: taskboard
    openchoreo.dev/component: api-server
spec:
  workflow:
    kind: Workflow
    name: docker-gitops-release
    parameters:
      componentName: api-server
      projectName: taskboard
      docker:
        context: /services/api-server
        filePath: /services/api-server/Dockerfile
      repository:
        appPath: /services/api-server
        revision:
          branch: main
          commit: ""
        url: https://github.com/<your-org>/taskboard.git
      workloadDescriptorPath: workload.yaml
```

```bash
kubectl apply -f api-server-workflowrun.yaml
kubectl apply -f web-app-workflowrun.yaml
```

### What Happens Next (Automatically)

The pipeline executes these steps in an Argo Workflow:

```
1. clone-source         — Clones your source repo
2. build-image          — Builds Docker image using Kaniko
3. push-image           — Pushes to the in-cluster registry
4. extract-descriptor   — Reads workload.yaml from source
5. clone-gitops         — Clones the gitops repo
6. create-feature-branch — Creates release/<component>-<timestamp>
7. generate-gitops-resources — Runs 3 occ CLI commands:
     occ workload create          — Updates workload.yaml with real image tag
     occ componentrelease generate — Creates immutable ComponentRelease
     occ releasebinding generate  — Creates/updates ReleaseBinding
8. git-commit-push-pr   — Commits changes, pushes branch, opens PR
```

### Step 7: Merge the PRs

After the pipeline completes, you'll find open PRs in the gitops repo:

```bash
gh pr list --repo <your-org>/openchoreo-gitops
```

Merge them:

```bash
gh pr merge <PR_NUMBER> --repo <your-org>/openchoreo-gitops --merge
```

### Step 8: Force Flux Reconciliation

```bash
kubectl annotate gitrepository sample-gitops -n flux-system \
  "reconcile.fluxcd.io/requestedAt=$(date +%s)" --overwrite
```

### Step 9: Wait for Deployment

```bash
# Watch ReleaseBindings reach Ready
kubectl get releasebindings.openchoreo.dev -n default -w

# Watch pods come up
kubectl get pods -A -l openchoreo.dev/project=taskboard -w
```

---

## Verifying Deployment

### Check the Full Chain

```bash
# 1. Components registered
kubectl get components.openchoreo.dev -n default -l openchoreo.dev/project=taskboard

# 2. Releases created
kubectl get componentreleases.openchoreo.dev -n default -l openchoreo.dev/project=taskboard

# 3. Release bindings ready
kubectl get releasebindings.openchoreo.dev -n default \
  -o jsonpath='{range .items[?(@.spec.owner.projectName=="taskboard")]}{.metadata.name}: {range .status.conditions[?(@.type=="Ready")]}{.status}{end}{"\n"}{end}'

# 4. Rendered releases applied
kubectl get renderedrelease -n default

# 5. Actual workloads running
kubectl get deployments -A -l openchoreo.dev/project=taskboard
kubectl get pods -A -l openchoreo.dev/project=taskboard
kubectl get svc -A -l openchoreo.dev/project=taskboard
```

### Check Dependency Resolution

For components with dependencies, verify the ReleaseBinding resolved connections:

```bash
kubectl get releasebinding api-server-development -n default \
  -o jsonpath='{.status.resolvedConnections}' | python3 -m json.tool
```

This shows the actual URLs injected into the container for `DATABASE_URL`, `REDIS_URL`, etc.

---

## Promoting to Staging/Production

The `standard` deployment pipeline defines: `development → staging → production`.

To promote a release to staging:

```yaml
# namespaces/default/projects/taskboard/components/api-server/release-bindings/api-server-staging.yaml
apiVersion: openchoreo.dev/v1alpha1
kind: ReleaseBinding
metadata:
  name: api-server-staging
  namespace: default
spec:
  environment: staging
  owner:
    componentName: api-server
    projectName: taskboard
  releaseName: api-server-f3a5cd49
```

Commit, push, and Flux deploys it to the staging environment (separate data plane namespace, potentially separate data plane cluster).

To roll back: change the `releaseName` to a previous release and commit.

---

## Troubleshooting

### ComponentRelease Name Collision (Exit Code 1 at generate-gitops-resources)

If `occ componentrelease generate` fails, it's usually because a release with the same name already exists in the gitops repo. This happens when:
- You re-run a pipeline for the same source code at the same commit
- The image digest hasn't changed, so the hash suffix is identical

**Fix:** Delete the existing release file from the gitops repo, delete the WorkflowRun, and re-trigger.

### Flux Kustomization Not Ready

```bash
kubectl get kustomization -n flux-system
```

If `oc-demo-projects` shows `HealthCheckFailed`, check which resources failed:

```bash
kubectl get kustomization oc-demo-projects -n flux-system \
  -o jsonpath='{.status.conditions[?(@.type=="Healthy")].message}'
```

Common cause: ReleaseBindings in the gitops repo but no corresponding ComponentRelease (Flux creates the binding, controller can't find the release).

### WorkflowRun Stuck or Failed

```bash
# Check WorkflowRun status
kubectl get workflowrun <name> -n default -o jsonpath='{.status.tasks}' | python3 -m json.tool

# Check Argo Workflow pods
kubectl get pods -n workflows-default -l workflows.argoproj.io/workflow=<name>

# Get logs from a specific step
kubectl logs -n workflows-default <pod-name> -c main
```

### Pods Not Starting

```bash
# Find the data plane namespace
kubectl get ns -l openchoreo.dev/project=taskboard

# Check pod events
kubectl describe pod -n <dp-namespace> <pod-name>
```

Common issues:
- Image pull errors → Check registry URL and image tag in the Workload
- PVC pending → Check storageClass exists (`longhorn` must be installed)
- CrashLoopBackOff → Check container logs and env var resolution

---

## Reference: OpenChoreo Resource Hierarchy

```
Platform Level (shared across all projects):
├── ComponentType          — Templates for K8s resource generation
│   ├── deployment/service
│   ├── deployment/web-application
│   ├── deployment/database
│   └── deployment/message-broker
├── Trait                  — Composable capabilities (persistent-volume, api-management)
├── Environment            — development, staging, production
├── DeploymentPipeline     — Promotion path (dev → staging → prod)
└── Workflow               — CI/CD pipeline definition (docker-gitops-release)

Project Level:
├── Project                — Logical grouping of components
│   └── Components
│       ├── Component      — WHAT to deploy + build config
│       ├── Workload       — HOW to run (image, env, ports, deps)
│       ├── ComponentRelease — Immutable snapshot (Component + Workload + Type)
│       └── ReleaseBinding — Binds release → environment

Cluster Level (auto-managed by controller):
├── RenderedRelease        — Materialized K8s resources from a binding
├── Deployment             — Actual pod spec
├── Service                — ClusterIP service
├── HTTPRoute              — Gateway API routing
├── PersistentVolumeClaim  — Storage (from persistent-volume trait)
├── NetworkPolicy          — Auto-generated per-component
└── ConfigMap              — Environment config injection
```

### Component Naming Convention

| Resource | Name Pattern |
|----------|-------------|
| ComponentRelease | `<component>-<hash>` (CI) or `<component>-<date>-<seq>` (manual) |
| ReleaseBinding | `<component>-<environment>` |
| RenderedRelease | `<component>-<environment>` |
| Deployment | `<component>-<environment>-<hash>` |
| Service | `<component>` (within data plane namespace) |
| Data Plane Namespace | `dp-<namespace>-<project>-<environment>-<hash>` |

### Minimum Viable Deployment (Pre-Built Image)

To deploy a single component with a pre-built image, you need exactly 5 files:

```
project.yaml           → Project definition
component.yaml         → Component metadata
workload.yaml          → Container spec
releases/<name>.yaml   → ComponentRelease snapshot
release-bindings/<name>.yaml → Environment binding
```

### Minimum Viable Deployment (With CI/CD)

To deploy a component from source, you need 3 files committed + 1 WorkflowRun applied:

```
project.yaml           → Project definition
component.yaml         → Component metadata (with workflow section)
workload.yaml          → Container spec (image will be overwritten by CI)
+ kubectl apply WorkflowRun CR → Triggers the pipeline
```

The pipeline automatically generates the ComponentRelease, ReleaseBinding, and opens a PR.
