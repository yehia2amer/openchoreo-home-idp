# OpenChoreo v1.0.0 on K3d — Complete Installation & Operations Guide

> **Date:** March 23, 2026  
> **OpenChoreo Version:** 1.0.0 (GA)  
> **Branch:** `release-v1.0`  
> **Cluster Runtime:** k3d with k3s v1.32.9  
> **GitOps:** FluxCD syncing from `yehia2amer/openchoreo-home-idp`

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Step 1: Create the K3d Cluster](#3-step-1-create-the-k3d-cluster)
4. [Step 2: Install Platform Prerequisites](#4-step-2-install-platform-prerequisites)
5. [Step 3: Install Control Plane](#5-step-3-install-control-plane)
6. [Step 4: Install Data Plane](#6-step-4-install-data-plane)
7. [Step 5: Install Workflow Plane](#7-step-5-install-workflow-plane)
8. [Step 6: Install Observability Plane](#8-step-6-install-observability-plane)
9. [Step 7: Install Flux CD & GitOps](#9-step-7-install-flux-cd--gitops)
10. [Service Access Reference](#10-service-access-reference)
11. [Credentials & Secrets Management](#11-credentials--secrets-management)
12. [Troubleshooting](#12-troubleshooting)
13. [Cleanup](#13-cleanup)

---

## 1. Architecture Overview

OpenChoreo has four planes, each in its own namespace:

| Plane | Namespace | Purpose |
|-------|-----------|---------|
| **Control Plane** | `openchoreo-control-plane` | API server, Backstage UI, controllers, Thunder identity provider |
| **Data Plane** | `openchoreo-data-plane` | Runs workloads, routes traffic via Gateway |
| **Workflow Plane** | `openchoreo-workflow-plane` | Argo Workflows for builds, container registry |
| **Observability Plane** | `openchoreo-observability-plane` | Logs (OpenSearch + Fluent Bit), Metrics (Prometheus), Traces (OpenSearch) |

Supporting infrastructure:
- **cert-manager** — TLS certificate management
- **External Secrets Operator** — Syncs secrets from OpenBao
- **kgateway** — Gateway API implementation
- **OpenBao** — Secret vault (HashiCorp Vault fork)
- **Thunder** — OAuth2/OIDC identity provider
- **Flux CD** — GitOps controller syncing resources from Git

---

## 2. Prerequisites

### Required Tools

| Tool | Minimum Version | Install |
|------|----------------|---------|
| Docker | v26+ (8 GB RAM, 4 CPU) | `brew install --cask docker` |
| k3d | v5.8+ | `brew install k3d` |
| kubectl | v1.32+ | `brew install kubectl` |
| Helm | v3.12+ | `brew install helm` |

### Verify

```bash
docker version --format '{{.Server.Version}}'
k3d version
kubectl version --client -o yaml | grep gitVersion
helm version --short
```

---

## 3. Step 1: Create the K3d Cluster

### Download the cluster configuration:

```bash
curl -fsSL -o /tmp/k3d-openchoreo-config.yaml \
  https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/install/k3d/single-cluster/config.yaml
```

### Configuration details

The config creates a single-server cluster named `openchoreo` with these port mappings:

| Port | Maps To | Purpose |
|------|---------|---------|
| 6550 | kube API | Kubernetes API server |
| 8080 | 8080 | Control Plane HTTP (UI, API) |
| 8443 | 8443 | Control Plane HTTPS |
| 19080 | 19080 | Data Plane HTTP (workloads) |
| 19443 | 19443 | Data Plane HTTPS |
| 10081 | 10081 | Argo Workflows UI |
| 10082 | 10082 | Container Registry |
| 11080 | 11080 | Observability Plane HTTP |
| 11085 | 11085 | Observability Plane HTTPS |
| 11081 | 5601 | OpenSearch Dashboards |
| 11082 | 9200 | OpenSearch API |

Key k3s options:
- Traefik disabled (kgateway used instead)
- `host.k3d.internal` added to API server TLS SANs
- Insecure registry configured at `host.k3d.internal:10082`
- Kubelet eviction thresholds relaxed for local dev

### Create the cluster:

```bash
k3d cluster create --config /tmp/k3d-openchoreo-config.yaml
```

### Verify:

```bash
kubectl cluster-info
kubectl get nodes
```

---

## 4. Step 2: Install Platform Prerequisites

### Quick install (recommended):

```bash
curl -fsSL https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/install/k3d/k3d-prerequisites.sh | bash
```

This script installs all of the following in order.

### Manual install (if you prefer step-by-step):

#### 4.1 Gateway API CRDs

```bash
kubectl apply --server-side \
  -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.1/experimental-install.yaml
```

#### 4.2 cert-manager v1.19.4

```bash
helm upgrade --install cert-manager oci://quay.io/jetstack/charts/cert-manager \
  --namespace cert-manager --create-namespace \
  --version v1.19.4 \
  --set crds.enabled=true \
  --wait --timeout 180s
```

#### 4.3 External Secrets Operator v2.0.1

```bash
helm upgrade --install external-secrets oci://ghcr.io/external-secrets/charts/external-secrets \
  --namespace external-secrets --create-namespace \
  --version 2.0.1 \
  --set installCRDs=true \
  --wait --timeout 180s
```

#### 4.4 kgateway v2.2.1

```bash
# CRDs first
helm upgrade --install kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds \
  --namespace openchoreo-control-plane --create-namespace \
  --version v2.2.1

# Controller
helm upgrade --install kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
  --namespace openchoreo-control-plane --create-namespace \
  --version v2.2.1 \
  --set controller.extraEnv.KGW_ENABLE_GATEWAY_API_EXPERIMENTAL_FEATURES=true
```

#### 4.5 OpenBao v0.25.6

```bash
helm upgrade --install openbao oci://ghcr.io/openbao/charts/openbao \
  --namespace openbao --create-namespace \
  --version 0.25.6 \
  --values https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/install/k3d/common/values-openbao.yaml \
  --wait --timeout 300s
```

OpenBao is installed in **dev mode** with root token `root`. Its `postStart` script automatically:
- Enables Kubernetes auth
- Creates reader/writer policies
- Seeds sample secrets (Backstage, OpenSearch, Observer, etc.)

#### 4.6 ClusterSecretStore

```bash
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: ServiceAccount
metadata:
  name: external-secrets-openbao
  namespace: openbao
---
apiVersion: external-secrets.io/v1
kind: ClusterSecretStore
metadata:
  name: default
spec:
  provider:
    vault:
      server: "http://openbao.openbao.svc:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "openchoreo-secret-writer-role"
          serviceAccountRef:
            name: "external-secrets-openbao"
            namespace: "openbao"
EOF
```

#### 4.7 CoreDNS Rewrite

Rewrites `*.openchoreo.localhost` to `host.k3d.internal` inside the cluster so pods can reach services via the k3d load balancer:

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/install/k3d/common/coredns-custom.yaml
```

### Verify prerequisites:

```bash
kubectl get pods -n cert-manager
kubectl get pods -n external-secrets
kubectl get pods -n openbao
kubectl get pods -n openchoreo-control-plane -l app.kubernetes.io/name=kgateway
kubectl get clustersecretstore default
```

---

## 5. Step 3: Install Control Plane

### 5.1 Install Thunder (Identity Provider) v0.28.0

```bash
helm upgrade --install thunder oci://ghcr.io/openchoreo/helm-charts/thunder \
  --namespace thunder --create-namespace \
  --version 0.28.0 \
  --values https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/install/k3d/common/values-thunder.yaml \
  --wait --timeout 300s
```

Thunder provides OAuth2/OIDC with a pre-configured admin user.

### 5.2 Create Backstage Secrets

Backstage (the web console) needs secrets from OpenBao. Create External Secrets:

```bash
kubectl apply -f - <<'EOF'
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: backstage-secrets
  namespace: openchoreo-control-plane
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: default
  target:
    name: backstage-secrets
  data:
  - secretKey: BACKEND_SECRET
    remoteRef:
      key: backstage-backend-secret
      property: value
  - secretKey: CLIENT_SECRET
    remoteRef:
      key: backstage-client-secret
      property: value
  - secretKey: JENKINS_API_KEY
    remoteRef:
      key: backstage-jenkins-api-key
      property: value
EOF
```

### 5.3 Install the Control Plane v1.0.0

```bash
helm upgrade --install openchoreo-control-plane oci://ghcr.io/openchoreo/helm-charts/openchoreo-control-plane \
  --version 1.0.0 \
  --namespace openchoreo-control-plane \
  --values https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/install/k3d/single-cluster/values-cp.yaml \
  --timeout 10m
```

### 5.4 Label the namespace

```bash
kubectl label namespace openchoreo-control-plane openchoreo.dev/control-plane=true
```

### Verify:

```bash
kubectl get deployments -n openchoreo-control-plane
# Expected: 6 deployments, all AVAILABLE
# - backstage, cluster-gateway, kgateway, kgateway-crds, openchoreo-api, openchoreo-controller-manager
```

---

## 6. Step 4: Install Data Plane

### 6.1 Install the Data Plane v1.0.0

```bash
helm upgrade --install openchoreo-data-plane oci://ghcr.io/openchoreo/helm-charts/openchoreo-data-plane \
  --version 1.0.0 \
  --namespace openchoreo-data-plane --create-namespace \
  --values https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/install/k3d/single-cluster/values-dp.yaml \
  --timeout 10m
```

### 6.2 Register ClusterDataPlane

Wait for the agent TLS secret, then register:

```bash
kubectl wait secret/cluster-agent-tls -n openchoreo-data-plane --for=jsonpath='{.type}'=kubernetes.io/tls --timeout=120s

AGENT_CA=$(kubectl get secret cluster-agent-tls -n openchoreo-data-plane -o jsonpath='{.data.ca\.crt}' | base64 -d)

kubectl apply -f - <<EOF
apiVersion: openchoreo.dev/v1alpha1
kind: ClusterDataPlane
metadata:
  name: default
spec:
  planeID: default
  clusterAgent:
    clientCA:
      value: |
$(echo "$AGENT_CA" | sed 's/^/        /')
  gateway:
    httpURL: http://openchoreo.localhost:19080
    httpsURL: https://openchoreo.localhost:19443
EOF
```

### Verify:

```bash
kubectl get clusterdataplane default
kubectl get pods -n openchoreo-data-plane
```

---

## 7. Step 5: Install Workflow Plane

### 7.1 Install the container registry

```bash
helm upgrade --install registry oci://ghcr.io/openchoreo/helm-charts/docker-registry \
  --namespace openchoreo-workflow-plane --create-namespace \
  --version 3.0.0 \
  --values https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/install/k3d/single-cluster/values-registry.yaml
```

### 7.2 Install the Workflow Plane v1.0.0

```bash
helm upgrade --install openchoreo-workflow-plane oci://ghcr.io/openchoreo/helm-charts/openchoreo-workflow-plane \
  --version 1.0.0 \
  --namespace openchoreo-workflow-plane \
  --values https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/install/k3d/single-cluster/values-wp.yaml \
  --timeout 10m
```

### 7.3 Apply base workflow templates (k3d-specific)

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/samples/getting-started/workflow-templates/checkout-source.yaml
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/samples/getting-started/workflow-templates.yaml
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/samples/getting-started/workflow-templates/publish-image-k3d.yaml
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/samples/getting-started/workflow-templates/generate-workload-k3d.yaml
```

These create 7 `ClusterWorkflowTemplates`:
- `checkout-source`
- `paketo-buildpacks-build`, `gcp-buildpacks-build`, `ballerina-buildpack-build`
- `containerfile-build`
- `publish-image`
- `generate-workload`

### 7.4 Register ClusterWorkflowPlane

```bash
kubectl wait secret/cluster-agent-tls -n openchoreo-workflow-plane --for=jsonpath='{.type}'=kubernetes.io/tls --timeout=120s

AGENT_CA=$(kubectl get secret cluster-agent-tls -n openchoreo-workflow-plane -o jsonpath='{.data.ca\.crt}' | base64 -d)

kubectl apply -f - <<EOF
apiVersion: openchoreo.dev/v1alpha1
kind: ClusterWorkflowPlane
metadata:
  name: default
spec:
  planeID: default
  clusterAgent:
    clientCA:
      value: |
$(echo "$AGENT_CA" | sed 's/^/        /')
EOF
```

### Verify:

```bash
kubectl get clusterworkflowplane default
kubectl get clusterworkflowtemplates.argoproj.io
kubectl get pods -n openchoreo-workflow-plane
```

---

## 8. Step 6: Install Observability Plane

### 8.1 Namespace and CA

```bash
kubectl create namespace openchoreo-observability-plane --dry-run=client -o yaml | kubectl apply -f -

CA_CRT=$(kubectl get secret cluster-gateway-ca -n openchoreo-control-plane -o jsonpath='{.data.ca\.crt}' | base64 -d)
kubectl create configmap cluster-gateway-ca \
  --from-literal=ca.crt="$CA_CRT" \
  -n openchoreo-observability-plane --dry-run=client -o yaml | kubectl apply -f -
```

### 8.2 OpenSearch credentials ExternalSecrets

```bash
kubectl apply -f - <<'EOF'
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: observer-opensearch-credentials
  namespace: openchoreo-observability-plane
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: default
  target:
    name: observer-opensearch-credentials
  data:
  - secretKey: username
    remoteRef:
      key: opensearch-username
      property: value
  - secretKey: password
    remoteRef:
      key: opensearch-password
      property: value
---
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: opensearch-admin-credentials
  namespace: openchoreo-observability-plane
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: default
  target:
    name: opensearch-admin-credentials
  data:
  - secretKey: username
    remoteRef:
      key: opensearch-username
      property: value
  - secretKey: password
    remoteRef:
      key: opensearch-password
      property: value
---
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: observer-secret
  namespace: openchoreo-observability-plane
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: default
  target:
    name: observer-secret
  data:
  - secretKey: OBSERVER_OAUTH_CLIENT_SECRET
    remoteRef:
      key: observer-oauth-client-secret
      property: value
EOF
```

### 8.3 Generate machine-id (for Fluent Bit)

```bash
docker exec k3d-openchoreo-server-0 sh -c \
  "cat /proc/sys/kernel/random/uuid | tr -d '-' > /etc/machine-id"
```

### 8.4 Install system services + modules (quick install)

```bash
curl -fsSL https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/install/k3d/k3d-observability-plane.sh | bash
```

This installs:
- `openchoreo-observability-plane` v1.0.0 (core services: observer, cluster-agent, cluster-gateway)
- `observability-logs-opensearch` v0.3.11 (OpenSearch + Fluent Bit for logs)
- `observability-tracing-opensearch` v0.3.10 (OpenSearch for traces)
- `observability-metrics-prometheus` v0.2.5 (Prometheus for metrics)

### 8.5 Register ClusterObservabilityPlane

```bash
AGENT_CA=$(kubectl get secret cluster-agent-tls -n openchoreo-observability-plane -o jsonpath='{.data.ca\.crt}' | base64 -d)

kubectl apply -f - <<EOF
apiVersion: openchoreo.dev/v1alpha1
kind: ClusterObservabilityPlane
metadata:
  name: default
spec:
  planeID: default
  clusterAgent:
    clientCA:
      value: |
$(echo "$AGENT_CA" | sed 's/^/        /')
  observerURL: http://observer.openchoreo.localhost:11080
EOF
```

### 8.6 Link planes to observability

```bash
kubectl patch clusterdataplane default --type merge \
  -p '{"spec":{"observabilityPlaneRef":{"kind":"ClusterObservabilityPlane","name":"default"}}}'

kubectl patch clusterworkflowplane default --type merge \
  -p '{"spec":{"observabilityPlaneRef":{"kind":"ClusterObservabilityPlane","name":"default"}}}'
```

### Verify:

```bash
kubectl get clusterobservabilityplane default
kubectl get pods -n openchoreo-observability-plane
# All pods should be Running (observer, cluster-agent, cluster-gateway, opensearch, fluent-bit, prometheus, etc.)
```

---

## 9. Step 7: Install Flux CD & GitOps

### 9.1 Install Flux CD

```bash
kubectl apply -f https://github.com/fluxcd/flux2/releases/latest/download/install.yaml

kubectl wait -n flux-system --for=condition=available --timeout=120s \
  deployment/source-controller \
  deployment/kustomize-controller \
  deployment/helm-controller
```

### 9.2 Store GitHub PAT in OpenBao

The PAT needs `repo` scope for private repos and PR creation:

```bash
GITHUB_PAT="<your-github-personal-access-token>"

kubectl exec -n openbao openbao-0 -- sh -c "
  export BAO_ADDR=http://127.0.0.1:8200 BAO_TOKEN=root
  bao kv put secret/git-token git-token='${GITHUB_PAT}'
  bao kv put secret/gitops-token git-token='${GITHUB_PAT}'
"
```

### 9.3 Apply Flux resources

Your GitOps repo (fork of `openchoreo/sample-gitops`) should contain:
- `flux/gitrepository.yaml` — points to your repo
- `flux/namespaces-kustomization.yaml` — syncs namespace definitions
- `flux/platform-shared-kustomization.yaml` — syncs Argo ClusterWorkflowTemplates
- `flux/oc-demo-platform-kustomization.yaml` — syncs ComponentTypes, Workflows, Traits, Environments, DeploymentPipelines
- `flux/oc-demo-projects-kustomization.yaml` — syncs Projects and Components

```bash
kubectl apply -f flux/gitrepository.yaml
kubectl apply -f flux/namespaces-kustomization.yaml
kubectl apply -f flux/platform-shared-kustomization.yaml
kubectl apply -f flux/oc-demo-platform-kustomization.yaml
kubectl apply -f flux/oc-demo-projects-kustomization.yaml
```

### Verify:

```bash
kubectl get gitrepository -n flux-system
kubectl get kustomization -n flux-system
# All should show READY=True

# Verify synced resources
kubectl get componenttypes.openchoreo.dev -n default
kubectl get workflows.openchoreo.dev -n default
kubectl get projects.openchoreo.dev -n default
kubectl get components.openchoreo.dev -n default
```

---

## 10. Service Access Reference

### URLs (accessible from your host machine)

| Service | URL | Purpose |
|---------|-----|---------|
| **Backstage (Web Console)** | http://openchoreo.localhost:8080 | Main UI for managing projects, components, environments |
| **OpenChoreo API** | http://api.openchoreo.localhost:8080 | REST API for programmatic access |
| **Thunder (Identity Provider)** | http://thunder.openchoreo.localhost:8080 | OAuth2/OIDC login, token endpoints |
| **Data Plane Gateway** | http://openchoreo.localhost:19080 | Traffic routing to deployed workloads |
| **Argo Workflows UI** | http://localhost:10081 | Build pipeline monitoring |
| **Container Registry** | http://localhost:10082 | Docker registry for built images |
| **Observer API** | http://observer.openchoreo.localhost:11080 | Logs/metrics query API |
| **OpenSearch Dashboards** | http://localhost:11081 | Log exploration and visualization |
| **OpenSearch API** | https://localhost:11082 | Direct OpenSearch access |
| **RCA Agent** | http://rca-agent.openchoreo.localhost:11080 | Root cause analysis |

### OAuth2 Endpoints (Thunder)

| Endpoint | URL |
|----------|-----|
| Authorization | http://thunder.openchoreo.localhost:8080/oauth2/authorize |
| Token | http://thunder.openchoreo.localhost:8080/oauth2/token |
| JWKS | http://thunder.openchoreo.localhost:8080/oauth2/jwks |
| Userinfo | http://thunder.openchoreo.localhost:8080/oauth2/userinfo |

### Kubernetes API

```bash
kubectl config use-context k3d-openchoreo
# or
export KUBECONFIG=$(k3d kubeconfig write openchoreo)
```

---

## 11. Credentials & Secrets Management

### OpenBao (Secret Vault)

OpenBao runs in **dev mode** with root token `root`. All secrets are stored at `secret/data/<key>`.

**Access OpenBao CLI:**
```bash
kubectl exec -n openbao openbao-0 -- sh -c \
  "export BAO_ADDR=http://127.0.0.1:8200 BAO_TOKEN=root; bao kv list secret/"
```

### Secret Reference Table

| Secret Key | Value | Used By |
|------------|-------|---------|
| `backstage-backend-secret` | `local-dev-backend-secret` | Backstage backend encryption |
| `backstage-client-secret` | `backstage-portal-secret` | Backstage OIDC client |
| `backstage-jenkins-api-key` | `placeholder-not-in-use` | Unused placeholder |
| `observer-oauth-client-secret` | `openchoreo-observer-resource-reader-client-secret` | Observer API OAuth |
| `rca-oauth-client-secret` | `openchoreo-rca-agent-secret` | RCA Agent OAuth |
| `opensearch-username` | `admin` | OpenSearch admin user |
| `opensearch-password` | `ThisIsTheOpenSearchPassword1` | OpenSearch admin password |
| `git-token` | `<your-github-pat>` | Source repo access in workflows |
| `gitops-token` | `<your-github-pat>` | GitOps repo access (PR creation) |
| `github-pat` | `fake-github-token-for-development` | Sample apps placeholder |
| `npm-token` | `fake-npm-token-for-development` | Sample apps placeholder |
| `docker-username` | `dev-user` | Sample apps placeholder |
| `docker-password` | `dev-password` | Sample apps placeholder |
| `username` | `dev-user` | Generic sample credential |
| `password` | `dev-password` | Generic sample credential |

### Thunder (Identity Provider) Users

Thunder is pre-configured with an admin user. Default credentials:

| Field | Value |
|-------|-------|
| Username | `admin@openchoreo.dev` |
| Password | `admin` |

### OpenSearch Dashboards

| Field | Value |
|-------|-------|
| URL | http://localhost:11081 |
| Username | `admin` |
| Password | `ThisIsTheOpenSearchPassword1` |

### How ExternalSecrets Work

```
OpenBao (Vault) ──> ClusterSecretStore ──> ExternalSecret ──> Kubernetes Secret
```

1. **OpenBao** stores key-value pairs at `secret/data/<name>`
2. **ClusterSecretStore** `default` connects External Secrets Operator to OpenBao via Kubernetes auth
3. **ExternalSecret** CRs in each namespace define which OpenBao keys to sync into Kubernetes Secrets
4. **ESO** polls every `refreshInterval` and creates/updates the target Secret

### Adding a new secret:

```bash
# 1. Store in OpenBao
kubectl exec -n openbao openbao-0 -- sh -c \
  "export BAO_ADDR=http://127.0.0.1:8200 BAO_TOKEN=root; bao kv put secret/my-key value='my-value'"

# 2. Create ExternalSecret
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: my-secret
  namespace: <target-namespace>
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: default
  target:
    name: my-secret
  data:
  - secretKey: MY_KEY
    remoteRef:
      key: my-key
      property: value
EOF
```

---

## 12. Troubleshooting

### External Secrets timeout during helm install

ESO chart may time out on first run due to image pull. Solution:
```bash
kubectl wait -n external-secrets --for=condition=available --timeout=300s deployment --all
helm upgrade --install external-secrets oci://ghcr.io/external-secrets/charts/external-secrets \
  --namespace external-secrets --version 2.0.1 --set installCRDs=true --wait --timeout 180s
```

### Thunder deployment not visible after first install

Thunder's setup Job runs as a pre-install hook. Run `helm upgrade` to trigger the main deployment:
```bash
helm upgrade thunder oci://ghcr.io/openchoreo/helm-charts/thunder \
  --namespace thunder --version 0.28.0 \
  --values https://raw.githubusercontent.com/openchoreo/openchoreo/release-v1.0/install/k3d/common/values-thunder.yaml \
  --wait --timeout 300s
```

### Observer pod in CreateContainerConfigError

The observer needs `observer-secret`. Create it:
```bash
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: observer-secret
  namespace: openchoreo-observability-plane
spec:
  refreshInterval: 1h
  secretStoreRef: { kind: ClusterSecretStore, name: default }
  target: { name: observer-secret }
  data:
  - secretKey: OBSERVER_OAUTH_CLIENT_SECRET
    remoteRef: { key: observer-oauth-client-secret, property: value }
EOF
```

### DNS resolution issues inside the cluster

Verify CoreDNS rewrite is active:
```bash
kubectl get configmap coredns-custom -n kube-system -o yaml
kubectl run dns-test --rm -i --restart=Never --image=busybox:1.36 -- nslookup api.openchoreo.localhost
```

### Check all pods status

```bash
kubectl get pods -A --no-headers | grep -v "Running\|Completed"
```

---

## 13. Cleanup

### Delete the cluster entirely

```bash
k3d cluster delete openchoreo
```

### Reset and recreate

```bash
k3d cluster delete openchoreo
k3d cluster create --config /tmp/k3d-openchoreo-config.yaml
# Then re-run all installation steps
```
