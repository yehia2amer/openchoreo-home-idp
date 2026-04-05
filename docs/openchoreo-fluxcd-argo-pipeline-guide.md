# OpenChoreo FluxCD + Argo Build Pipeline — Architecture & Operations Guide

**Date**: 2026-04-05
**Cluster**: Talos Baremetal (`192.168.0.100:6443`)
**Platform**: OpenChoreo + FluxCD + Argo Workflows
**Pulumi Stack**: `talos-baremetal`

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [The Full Pipeline: From Git Push to Running Pod](#2-the-full-pipeline)
3. [Pulumi Deployment Steps (0–9)](#3-pulumi-deployment-steps)
4. [WorkflowRun Lifecycle](#4-workflowrun-lifecycle)
5. [k3d vs Talos Divergences](#5-k3d-vs-talos-divergences)
6. [Known Issues & Fixes Applied](#6-known-issues--fixes-applied)
7. [Troubleshooting Guide](#7-troubleshooting-guide)
8. [Making Everything Work Out-of-the-Box](#8-making-everything-work-out-of-the-box)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Developer Workflow                        │
│                                                                  │
│  Source Repo                    GitOps Repo                      │
│  (sample-workloads)            (openchoreo-gitops)               │
│       │                              ▲                           │
│       │ clone                        │ push PR / merge           │
│       ▼                              │                           │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              Argo Workflows (Workflow Plane)          │       │
│  │                                                       │       │
│  │  WorkflowRun  ──►  8-step pipeline:                  │       │
│  │    1. clone-source                                    │       │
│  │    2. resolve-refs                                    │       │
│  │    3. build-push (Podman/buildah → registry)          │       │
│  │    4. clone-gitops-repo                               │       │
│  │    5. generate-gitops-resources (occ CLI)             │       │
│  │    6. commit-changes                                  │       │
│  │    7. push-to-remote                                  │       │
│  │    8. create-pull-request (GitHub API)                │       │
│  └──────────────────────────────────────────────────────┘       │
│       │                              │                           │
│       │ image                        │ PR merged                 │
│       ▼                              ▼                           │
│  ┌──────────┐              ┌──────────────────┐                 │
│  │ Registry │              │    Flux CD        │                 │
│  │ (in-clus)│              │  (flux-system)    │                 │
│  └──────────┘              │                   │                 │
│                            │  GitRepository    │                 │
│                            │    └─► Kustomizations:             │
│                            │      oc-namespaces                  │
│                            │        └─► oc-platform-shared       │
│                            │          └─► oc-platform            │
│                            │            └─► oc-demo-projects     │
│                            └──────────────────┘                 │
│                                     │                            │
│                                     │ sync                       │
│                                     ▼                            │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              OpenChoreo Control Plane                  │       │
│  │                                                       │       │
│  │  Component ──► ComponentRelease ──► ReleaseBinding    │       │
│  │                                         │             │       │
│  │  Workload + ComponentType               │             │       │
│  │    └─► runtime config + env injection   │             │       │
│  └─────────────────────────────────────────┼─────────────┘       │
│                                            │ reconcile           │
│                                            ▼                     │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              Data Plane (namespace per env)           │       │
│  │                                                       │       │
│  │  dp-default-doclet-development-*                      │       │
│  │    ├─ nats (StatefulSet)                              │       │
│  │    ├─ postgres (StatefulSet)                          │       │
│  │    ├─ document-svc (Deployment)                       │       │
│  │    ├─ collab-svc (Deployment)                         │       │
│  │    └─ frontend (Deployment)                           │       │
│  └──────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### Key Resource Relationships

```
Project
  └─ Component (references source repo)
       └─ Workload (defines container spec via ComponentType)
       └─ ComponentRelease (built image tag, generated by occ CLI)
            └─ ReleaseBinding (binds release to environment)
                 └─ Resolves endpoint dependencies → injects env vars
                      └─ Creates Deployment/StatefulSet in data plane
```

---

## 2. The Full Pipeline

### Step-by-Step: Source Code → Running Pod

| # | What | Where | Automated? |
|---|------|-------|-----------|
| 1 | Developer pushes code | Source repo (sample-workloads) | Manual |
| 2 | WorkflowRun CR created | `default` namespace | Manual or `DemoAppBootstrap` |
| 3 | Argo picks up WorkflowRun | `workflows-default` namespace | Automatic |
| 4 | Source cloned, image built with Podman | Workflow pod | Automatic |
| 5 | Image pushed to in-cluster registry | `192.168.0.100:30082` | Automatic |
| 6 | `occ` generates ComponentRelease + ReleaseBinding | Filesystem in pod | Automatic |
| 7 | Changes committed, pushed, PR created | GitOps repo on GitHub | Automatic |
| 8 | PR merged | GitHub | Manual or `DemoAppBootstrap` |
| 9 | Flux detects new commit, syncs | `flux-system` namespace | Automatic (1m interval) |
| 10 | OpenChoreo reconciles ReleaseBinding | Control plane | Automatic |
| 11 | Deployment created with env vars injected | Data plane namespace | Automatic |

### Critical Dependency: Endpoint Resolution

The frontend component depends on `document-svc` and `collab-svc` endpoints. These are defined as `connections` in the Workload spec. The control plane resolves these connections into environment variables (`DOC_SERVICE_URL`, `COLLAB_SERVICE_URL`) **only when** the dependency components have a `ComponentRelease` and `ReleaseBinding` that are Ready.

**If dependencies aren't deployed first, the frontend gets `env: []` and crashes.**

---

## 3. Pulumi Deployment Steps

```
Step 0:  Cilium CNI
Step 1:  Prerequisites
           ├─ cert-manager
           ├─ external-secrets
           ├─ Control Plane namespace
           ├─ Data Plane namespace
           ├─ OpenBao (secrets engine)
           ├─ ClusterSecretStore
           ├─ workflows-default namespace    ← NEW: PodSecurity labels
           └─ CoreDNS rewrite (if needed)
Step 2:  TLS Setup (self-signed CA → cluster certs)
Step 3:  Control Plane (Helm chart: API, Thunder, Backstage)
Step 4:  Data Plane (register with control plane)
Step 5:  Workflow Plane (Argo Workflows + docker-gitops-release Workflow)
Step 6:  Observability Plane (OpenSearch + Observer)
Step 7:  FluxCD + GitOps
           ├─ Install Flux controllers
           ├─ GitRepository (sample-gitops)
           ├─ Kustomizations chain (namespaces → platform → projects)
           ├─ Notification Provider + Alert    ← NEW
           └─ ReleaseBinding healthChecks      ← NEW
Step 7.5: CoreDNS LAN DNS + Gateway IP pinning (baremetal only)
Step 8:  Integration Tests
Step 9:  DemoAppBootstrap (optional)           ← NEW
           ├─ Build document-svc + collab-svc (parallel)
           ├─ Build frontend (after backends)
           ├─ Merge 3 PRs via GitHub API
           ├─ Force Flux reconciliation
           └─ Wait for all ReleaseBindings Ready
```

---

## 4. WorkflowRun Lifecycle

### Creating a WorkflowRun

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: WorkflowRun
metadata:
  name: document-svc-bootstrap
  namespace: default
spec:
  workflow:
    kind: Workflow
    name: docker-gitops-release
    parameters:
      componentName: document-svc
      projectName: doclet
      docker:
        context: /project-doclet-app/service-go-document
        filePath: /project-doclet-app/service-go-document/Dockerfile
      repository:
        appPath: /project-doclet-app/service-go-document
        revision:
          branch: main
          commit: ""
        url: https://github.com/openchoreo/sample-workloads.git
      workloadDescriptorPath: workload.yaml
```

### The 8-Step Pipeline

| Step | Name | What It Does | Duration |
|------|------|-------------|----------|
| 1 | `clone-source` | Clones source repo at specified branch/commit | ~10s |
| 2 | `resolve-refs` | Resolves component references | ~5s |
| 3 | `build-push` | Builds container image with Podman, pushes to registry | 3-8 min |
| 4 | `clone-gitops-repo` | Clones the gitops repo with GitHub PAT | ~10s |
| 5 | `generate-gitops-resources` | Runs `occ componentrelease generate` in filesystem mode | ~5s |
| 6 | `commit-changes` | Git commit of generated manifests | ~5s |
| 7 | `push-to-remote` | Git push to a `release/<component>-<hash>` branch | ~10s |
| 8 | `create-pull-request` | Creates a PR on GitHub via API | ~5s |

### Important Caveats

- **`occ componentrelease generate` is NOT idempotent**: If a ComponentRelease with the same name already exists in the gitops repo, it fails hard. Must delete existing or use a different commit SHA.
- **Parallel builds are slower**: On a single-node cluster, running 2+ builds simultaneously causes ~1.5x slowdown due to CPU contention.
- **Build pods need privileged access**: Podman/buildah requires `pod-security.kubernetes.io/enforce: privileged` on the `workflows-default` namespace.

---

## 5. k3d vs Talos Divergences

| Area | k3d (Default Dev) | Talos Baremetal | Fix Applied |
|------|-------------------|-----------------|-------------|
| **PodSecurity** | Not enforced | Default `baseline` (rejects privileged) | Pre-create `workflows-default` ns with `privileged` labels |
| **Registry DNS** | `registry.kube-system.svc.cluster.local:5000` (HTTP) | Exposed via NodePort (`192.168.0.100:30082`) + HTTPRoute | CoreDNS rewrite + Gateway HTTPRoute + TLS trust |
| **Registry protocol** | HTTP only | HTTPS via Gateway (self-signed CA) | Copy CA cert into build pods, configure Podman trust |
| **StorageClass** | `local-path` (auto-provisioned) | Must configure explicitly | Pulumi creates StorageClass |
| **Postgres PGDATA** | Works with default | `PGDATA` must differ from mount point | Fixed in workload descriptor |
| **Gateway API** | Generic implementation | Cilium GatewayClass | Cilium-specific config in Pulumi |
| **DNS resolution** | Docker DNS | CoreDNS with custom LAN entries | `coredns_lan.py` component |

---

## 6. Known Issues & Fixes Applied

### 6.1 Frontend CrashLoopBackOff (Missing Env Vars)

**Root cause**: `document-svc` and `collab-svc` had no ComponentRelease or ReleaseBinding because tutorial Steps 6.1/6.2 were never executed. The frontend's endpoint dependencies couldn't resolve → `env: []`.

**Fix**: Triggered WorkflowRuns for all 3 backend components, merged resulting PRs. Now automated by `DemoAppBootstrap`.

See: `docs/openchoreo-frontend-crashloop-diagnosis-and-fix.md`

### 6.2 PodSecurity Blocks Podman Builds

**Root cause**: Talos enforces `baseline` PodSecurity by default. `workflows-default` namespace (created dynamically by OpenChoreo) didn't have `privileged` labels.

**Fix**: Pre-create `workflows-default` in `prerequisites.py` with privileged labels.

### 6.3 Registry HTTPS on Talos

**Root cause**: k3d uses HTTP for registry, Talos needs HTTPS via Gateway with self-signed CA.

**Fix**: CoreDNS rewrite rules + Gateway HTTPRoute + CA cert propagation handled in Pulumi.

### 6.4 ComponentRelease Name Collision

**Root cause**: Running `occ componentrelease generate` when a release with the same name already exists in the gitops repo.

**Workaround**: Use a different commit SHA or delete the existing release first. The `DemoAppBootstrap` uses unique run names (`*-bootstrap`) to avoid collision on first run.

---

## 7. Troubleshooting Guide

### Check Flux Sync Status

```bash
export KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig
kubectl get kustomizations -n flux-system
kubectl get gitrepositories -n flux-system
```

All should show `Ready=True`. If not:

```bash
# Get detailed error
kubectl describe kustomization <name> -n flux-system

# Force reconciliation
kubectl annotate gitrepository sample-gitops \
  -n flux-system \
  reconcile.fluxcd.io/requestedAt="$(date +%s)" \
  --overwrite
```

### Check WorkflowRun Status

```bash
kubectl get workflowruns -n default
kubectl describe workflowrun <name> -n default

# Check individual task logs
kubectl get pods -n workflows-default
kubectl logs <pod-name> -n workflows-default -c main
```

### Check ReleaseBinding Status

```bash
kubectl get releasebindings -n default
kubectl describe releasebinding <name> -n default
```

Look for conditions:
- `Ready=True` — deployment is up
- `Deployed=True` — resources created in data plane
- `Synced=True` — in sync with component definition

### Check Data Plane Pods

```bash
# Find the namespace
kubectl get ns | grep dp-default

# Check pods
kubectl get pods -n dp-default-doclet-development-<hash>

# Check env vars on a deployment
kubectl get deployment <name> -n dp-default-doclet-development-<hash> -o jsonpath='{.spec.template.spec.containers[0].env}' | jq
```

### Check Flux Notifications

```bash
# Check alert firing
kubectl get alerts -n flux-system
kubectl describe alert openchoreo-sync-alerts -n flux-system

# Check notification controller logs
kubectl logs -n flux-system deploy/notification-controller --tail=50
```

### Common Failure Patterns

| Symptom | Cause | Fix |
|---------|-------|-----|
| Pod `CrashLoopBackOff` with "missing DOC_SERVICE_URL" | Dependency components have no ReleaseBinding | Build & deploy dependencies first |
| WorkflowRun stuck at `build-push` | PodSecurity blocking privileged containers | Check `workflows-default` ns labels |
| `generate-gitops-resources` fails with "already exists" | ComponentRelease name collision | Delete existing or use different commit |
| Flux shows `ReconciliationFailed` | Bad YAML in gitops repo or merge conflict | Check gitops repo, fix manifests |
| WorkflowRun `clone-gitops-repo` fails | GitHub PAT expired or missing | Check OpenBao `secret/gitops-token` |
| Pods stuck in `ImagePullBackOff` | Registry unreachable or image not built | Check registry NodePort, image tag |

---

## 8. Making Everything Work Out-of-the-Box

### Clean Environment Deployment

With the `DemoAppBootstrap` component enabled (`enable_demo_app_bootstrap: true`), a `pulumi up` on a fresh cluster will:

1. Deploy all infrastructure (Steps 0–8)
2. Automatically trigger builds for all 3 demo app components
3. Merge the resulting PRs on GitHub
4. Force Flux to sync the new manifests
5. Verify all ReleaseBindings are Ready

**Total time**: ~25-35 minutes (infrastructure: ~15 min, builds: ~10-15 min, sync: ~2-3 min)

### Prerequisites for Clean Deployment

1. **GitHub PAT** must be configured in Pulumi config (encrypted)
2. **GitOps repo** must exist with initial structure (from tutorial Step 4)
3. **Source repo** (`sample-workloads`) must be accessible
4. **Network**: Node must reach GitHub API and `ghcr.io` for container images

### Config Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `enable_flux` | `false` | Install Flux CD and sync gitops repo |
| `enable_demo_app_bootstrap` | `false` | Automate build + deploy of demo app |
| `enable_observability` | `false` | Deploy OpenSearch + Observer stack |

### Flux Notification Configuration

The default setup uses a generic webhook provider that logs to the notification-controller stdout.

#### Telegram Setup

To send alerts to Telegram:

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather) and get the bot token
2. Get your chat/group/channel ID (use [@userinfobot](https://t.me/userinfobot) or the API)
3. Add the bot to your chat/group
4. Configure in `Pulumi.talos-baremetal.yaml`:
   ```yaml
   openchoreo:flux_telegram_bot_token:
     secure: <encrypted-token>   # use `pulumi config set --secret`
   openchoreo:flux_telegram_chat_id: "-1001234567890"
   ```
   Or via CLI:
   ```bash
   cd pulumi
   pulumi config set --secret flux_telegram_bot_token "123456:ABC-DEF..."
   pulumi config set flux_telegram_chat_id "-1001234567890"
   ```
5. Run `pulumi up` — the Provider will be created with `type: telegram`

You'll receive Telegram messages for any Kustomization or GitRepository sync errors.

#### Slack / Discord / Teams

To use other providers, update the Provider in `flux_gitops.py`:
```python
spec={
    "type": "slack",  # or "discord", "msteams"
    "address": "https://hooks.slack.com/services/...",
    "secretRef": {"name": "slack-webhook-url"},
}
```
Create the corresponding Secret in `flux-system` namespace.

### Monitoring ReleaseBinding Health

Flux's `healthChecks` on the `oc-demo-projects` Kustomization will cause the Kustomization to report `Ready=False` if any ReleaseBinding in the `default` namespace is unhealthy. This surfaces dependency resolution failures in `kubectl get kustomizations -n flux-system` output.
