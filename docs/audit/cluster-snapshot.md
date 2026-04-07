# Kubernetes Cluster State Snapshot

> **Date:** 2026-04-07 · **Cluster:** talos-baremetal (single-node Talos Linux)
> **K8s Version:** v1.33.0 · **CNI:** Cilium · **Storage:** Longhorn

## Namespaces (25 total)

### System Namespaces (4)

| Namespace | Age | Owner |
|-----------|-----|-------|
| `default` | 7d7h | Kubernetes |
| `kube-node-lease` | 7d7h | Kubernetes |
| `kube-public` | 7d7h | Kubernetes |
| `kube-system` | 7d7h | Kubernetes (+ Cilium, CoreDNS, snapshot-controller) |

### Cluster Bootstrap — Nested Pulumi (2)

| Namespace | Age | Owner |
|-----------|-----|-------|
| `cilium-secrets` | 7d6h | talos-cluster-baremetal Pulumi project |
| `longhorn-system` | 6d21h | talos-cluster-baremetal Pulumi project |

### Pulumi-Created (11)

| Namespace | Age | Owner |
|-----------|-----|-------|
| `cert-manager` | 6d20h | Pulumi (prerequisites.py) |
| `external-secrets` | 6d20h | Pulumi (prerequisites.py) |
| `openbao` | 6d20h | Pulumi (prerequisites.py) |
| `openchoreo-control-plane` | 6d20h | Pulumi (prerequisites.py) |
| `openchoreo-data-plane` | 6d20h | Pulumi (prerequisites.py) |
| `openchoreo-workflow-plane` | 6d18h | Pulumi (prerequisites.py) |
| `openchoreo-observability-plane` | 6d7h | Pulumi (observability_plane.py) |
| `thunder` | 6d19h | Pulumi (prerequisites.py) |
| `odigos-system` | 2d6h | Pulumi (odigos.py) |
| `flux-system` | 5d23h | Pulumi (flux_gitops.py) |
| `workflows-default` | 2d20h | Pulumi (prerequisites.py) |

### FluxCD-Created (4)

| Namespace | Age | Owner |
|-----------|-----|-------|
| `backstage-fork` | 23h | FluxCD (oc-namespaces) |
| `external-dns` | 23h | FluxCD (oc-namespaces) |
| `openchoreo-gateway` | 23h | FluxCD (oc-namespaces) |
| `keepalived` | 19h | FluxCD (oc-namespaces) |

### Operator-Created (4)

| Namespace | Age | Owner |
|-----------|-----|-------|
| `arr-stack` | 2d1h | OpenChoreo operator (project namespace) |
| `dp-default-arr-stack-development-8dda33b1` | 2d1h | OpenChoreo operator (data plane namespace) |
| `dp-default-doclet-development-50ce4d9b` | 2d23h | OpenChoreo operator (data plane namespace) |
| `dp-default-doclet-staging-cba15825` | 2d23h | OpenChoreo operator (data plane namespace) |

## Workloads

### Deployments (65 total)

| Namespace | Deployment | Replicas | Owner |
|-----------|-----------|----------|-------|
| **backstage-fork** | `backstage-fork` | 1/1 | FluxCD |
| **cert-manager** | `cert-manager-helm-9ee3a4b1` | 1/1 | Pulumi |
| **cert-manager** | `cert-manager-helm-9ee3a4b1-cainjector` | 1/1 | Pulumi |
| **cert-manager** | `cert-manager-helm-9ee3a4b1-webhook` | 1/1 | Pulumi |
| **dp-default-arr-stack-*…** | `sonarr-development-*` | 1/1 | OpenChoreo operator |
| **dp-default-doclet-dev…** | `collab-svc-development-*` | 1/1 | OpenChoreo operator |
| **dp-default-doclet-dev…** | `document-svc-development-*` | 1/1 | OpenChoreo operator |
| **dp-default-doclet-dev…** | `frontend-development-*` | 1/1 | OpenChoreo operator |
| **dp-default-doclet-dev…** | `nats-development-*` | 1/1 | OpenChoreo operator |
| **dp-default-doclet-dev…** | `postgres-development-*` | 1/1 | OpenChoreo operator |
| **dp-default-doclet-stag…** | `nats-staging-*` | 1/1 | OpenChoreo operator |
| **dp-default-doclet-stag…** | `postgres-staging-*` | 1/1 | OpenChoreo operator |
| **external-dns** | `external-dns-adguard-k8s` | 1/1 | FluxCD HelmRelease |
| **external-dns** | `external-dns-adguard-truenas` | 1/1 | FluxCD HelmRelease |
| **external-dns** | `external-dns-cloudflare` | 1/1 | FluxCD HelmRelease |
| **external-secrets** | `external-secrets` | 1/1 | Pulumi |
| **external-secrets** | `external-secrets-cert-controller` | 1/1 | Pulumi |
| **external-secrets** | `external-secrets-webhook` | 1/1 | Pulumi |
| **flux-system** | `helm-controller` | 1/1 | Pulumi |
| **flux-system** | `image-automation-controller` | 1/1 | Pulumi |
| **flux-system** | `image-reflector-controller` | 1/1 | Pulumi |
| **flux-system** | `kustomize-controller` | 1/1 | Pulumi |
| **flux-system** | `notification-controller` | 1/1 | Pulumi |
| **flux-system** | `source-controller` | 1/1 | Pulumi |
| **keepalived** | `adguard-home-k8s` | 1/1 | FluxCD |
| **kube-system** | `cilium-operator` | 1/1 | Nested Pulumi |
| **kube-system** | `coredns` | 2/2 | Kubernetes/Talos |
| **kube-system** | `hubble-relay` | 1/1 | Nested Pulumi (Cilium) |
| **kube-system** | `hubble-ui` | 1/1 | Nested Pulumi (Cilium) |
| **kube-system** | `snapshot-controller` | 2/2 | Nested Pulumi |
| **longhorn-system** | `csi-attacher` | 3/3 | Nested Pulumi (Longhorn) |
| **longhorn-system** | `csi-provisioner` | 3/3 | Nested Pulumi (Longhorn) |
| **longhorn-system** | `csi-resizer` | 3/3 | Nested Pulumi (Longhorn) |
| **longhorn-system** | `csi-snapshotter` | 3/3 | Nested Pulumi (Longhorn) |
| **longhorn-system** | `longhorn-driver-deployer` | 1/1 | Nested Pulumi (Longhorn) |
| **longhorn-system** | `longhorn-ui` | 2/2 | Nested Pulumi (Longhorn) |
| **odigos-system** | `odigos-autoscaler` | 1/1 | Pulumi |
| **odigos-system** | `odigos-gateway` | 2/2 | Pulumi |
| **odigos-system** | `odigos-instrumentor` | 2/2 | Pulumi |
| **odigos-system** | `odigos-scheduler` | 1/1 | Pulumi |
| **odigos-system** | `odigos-ui` | 1/1 | Pulumi |
| **openchoreo-control-plane** | `backstage` | 1/1 | Pulumi (CP Helm) |
| **openchoreo-control-plane** | `cluster-gateway` | 1/1 | Pulumi (CP Helm) |
| **openchoreo-control-plane** | `controller-manager` | 1/1 | Pulumi (CP Helm) |
| **openchoreo-control-plane** | `gateway-default` | 1/1 | Pulumi (CP Helm) |
| **openchoreo-control-plane** | `kgateway` | 1/1 | Pulumi (kgateway-crds Helm) |
| **openchoreo-control-plane** | `openchoreo-api` | 1/1 | Pulumi (CP Helm) |
| **openchoreo-data-plane** | `cluster-agent-dataplane` | 1/1 | Pulumi (DP Helm) |
| **openchoreo-data-plane** | `gateway-default` | 1/1 | Pulumi (DP Helm) |
| **openchoreo-gateway** | `gateway-shared` | 1/1 | FluxCD (Gateway resource) |
| **openchoreo-observability-plane** | `ai-rca-agent` | 0/0 | Pulumi (OP Helm) |
| **openchoreo-observability-plane** | `cluster-agent-observabilityplane` | 1/1 | Pulumi (OP Helm) |
| **openchoreo-observability-plane** | `controller-manager` | 1/1 | Pulumi (OP Helm) |
| **openchoreo-observability-plane** | `gateway-default` | 1/1 | Pulumi (OP Helm) |
| **openchoreo-observability-plane** | `kube-state-metrics` | 1/1 | Pulumi (metrics-prometheus) |
| **openchoreo-observability-plane** | `logs-adapter-openobserve` | 1/1 | Pulumi (logs-openobserve) |
| **openchoreo-observability-plane** | `metrics-adapter-prometheus` | 1/1 | Pulumi (metrics-prometheus) |
| **openchoreo-observability-plane** | `observer` | 1/1 | Pulumi (OP Helm) |
| **openchoreo-observability-plane** | `opentelemetry-collector` | 1/1 | Pulumi (OP Helm) |
| **openchoreo-observability-plane** | `prometheus-operator` | 1/1 | Pulumi (metrics-prometheus) |
| **openchoreo-observability-plane** | `tracing-adapter-openobserve` | 1/1 | Pulumi (tracing-openobserve) |
| **openchoreo-workflow-plane** | `argo-server` | 1/1 | Pulumi (WP Helm) |
| **openchoreo-workflow-plane** | `argo-workflow-controller` | 1/1 | Pulumi (WP Helm) |
| **openchoreo-workflow-plane** | `cluster-agent-workflowplane` | 1/1 | Pulumi (WP Helm) |
| **openchoreo-workflow-plane** | `registry` | 1/1 | Pulumi (docker-registry) |
| **thunder** | `thunder-deployment` | 1/1 | Pulumi (Thunder Helm) |

### StatefulSets (5)

| Namespace | StatefulSet | Replicas | Owner |
|-----------|-----------|----------|-------|
| `openbao` | `openbao` | 1/1 | Pulumi |
| `openchoreo-observability-plane` | `alertmanager-openchoreo-observability` | 1/1 | Pulumi (metrics-prometheus) |
| `openchoreo-observability-plane` | `openobserve` | 1/1 | Pulumi (logs-openobserve) |
| `openchoreo-observability-plane` | `opensearch-master` | 1/1 | Pulumi (logs-opensearch) |
| `openchoreo-observability-plane` | `prometheus-openchoreo-observability` | 1/1 | Pulumi (metrics-prometheus) |

### DaemonSets (7)

| Namespace | DaemonSet | Ready | Owner |
|-----------|----------|-------|-------|
| `keepalived` | `keepalived` | 1 | FluxCD |
| `kube-system` | `cilium` | 1 | Nested Pulumi |
| `kube-system` | `cilium-envoy` | 1 | Nested Pulumi (Cilium) |
| `longhorn-system` | `engine-image-ei-b4bcf0a5` | 1 | Nested Pulumi (Longhorn) |
| `longhorn-system` | `longhorn-csi-plugin` | 1 | Nested Pulumi (Longhorn) |
| `longhorn-system` | `longhorn-manager` | 1 | Nested Pulumi (Longhorn) |
| `odigos-system` | `odiglet` | 1 | Pulumi |
| `openchoreo-observability-plane` | `fluent-bit` | 1 | Pulumi (OP Helm) |

## Gateway API

### Gateways (4)

| Name | Namespace | GatewayClass | External IP | Status | Owner |
|------|-----------|-------------|-------------|--------|-------|
| `gateway-default` | `openchoreo-control-plane` | `kgateway` | `192.168.0.14` | ✅ Programmed | Pulumi |
| `gateway-default` | `openchoreo-data-plane` | `kgateway` | *(pending)* | ✅ Programmed | Pulumi |
| `gateway-shared` | `openchoreo-gateway` | `kgateway` | `192.168.0.10` | ✅ Programmed | FluxCD |
| `gateway-default` | `openchoreo-observability-plane` | `kgateway` | *(pending)* | ✅ Programmed | Pulumi |

**Note:** DP and OP `gateway-default` services show ClusterIP only — no external IP assigned via CiliumLoadBalancerIPPool. Only CP gateway and the shared gateway have external IPs.

### HTTPRoutes (25)

| Namespace | Name | Hostnames | Owner |
|-----------|------|-----------|-------|
| `backstage-fork` | `backstage-fork` | `portal.amernas.work` | FluxCD |
| `dp-default-arr-stack-*…` | `sonarr-endpoint-*` | `endpoint-1-sonarr-development-*.amernas.work` | OpenChoreo |
| `dp-default-doclet-dev…` | `document-svc-http-*` | `development-default.amernas.work` | OpenChoreo |
| `dp-default-doclet-dev…` | `frontend-http-*` | `http-frontend-development-*.amernas.work` | OpenChoreo |
| `openchoreo-control-plane` | `backstage` | `backstage.amernas.work` | Pulumi (CP Helm) |
| `openchoreo-control-plane` | `openchoreo-api` | `api.amernas.work` | Pulumi (CP Helm) |
| `openchoreo-gateway` | `alertmanager` | `alertmanager.amernas.work` | FluxCD |
| `openchoreo-gateway` | `api` | `api.amernas.work` | FluxCD |
| `openchoreo-gateway` | `argo-server` | `argo.amernas.work` | FluxCD |
| `openchoreo-gateway` | `backstage` | `backstage.amernas.work` | FluxCD |
| `openchoreo-gateway` | `hubble-ui` | `hubble.amernas.work` | FluxCD |
| `openchoreo-gateway` | `longhorn-ui` | `longhorn.amernas.work` | FluxCD |
| `openchoreo-gateway` | `observer` | `observer.amernas.work` | FluxCD |
| `openchoreo-gateway` | `openbao-ui` | `openbao.amernas.work` | FluxCD |
| `openchoreo-gateway` | `openobserve-ui` | `openobserve.amernas.work` | FluxCD |
| `openchoreo-gateway` | `opensearch` | `opensearch.amernas.work` | FluxCD |
| `openchoreo-gateway` | `prometheus` | `prometheus.amernas.work` | FluxCD |
| `openchoreo-gateway` | `rca-agent` | `rca-agent.amernas.work` | FluxCD |
| `openchoreo-gateway` | `registry` | `registry.amernas.work` | FluxCD |
| `openchoreo-gateway` | `thunder` | `thunder.amernas.work` | FluxCD |
| `openchoreo-gateway` | `wildcard-data-plane` | `*.amernas.work` | FluxCD |
| `openchoreo-observability-plane` | `ai-rca-agent` | `rca-agent.amernas.work` | Pulumi (OP Helm) |
| `openchoreo-observability-plane` | `observer` | `observer.amernas.work` | Pulumi (OP Helm) |
| `openchoreo-observability-plane` | `openobserve` / `openobserve-ui` | `openobserve.amernas.work` | Pulumi |
| `thunder` | `thunder-httproute` | `thunder.amernas.work` | Pulumi (Thunder Helm) |

## Certificates & TLS

### Certificates (12)

| Name | Namespace | Issuer | Secret | Owner |
|------|-----------|--------|--------|-------|
| `openchoreo-ca` | `cert-manager` | `selfsigned-bootstrap` | `openchoreo-ca-secret` | Pulumi |
| `cluster-gateway-ca` | `openchoreo-control-plane` | `openchoreo-ca` | `cluster-gateway-ca` | Pulumi (CP Helm) |
| `cluster-gateway-tls` | `openchoreo-control-plane` | `openchoreo-ca` | `cluster-gateway-tls` | Pulumi (CP Helm) |
| `controller-manager-webhook-server-cert` | `openchoreo-control-plane` | `openchoreo-ca` | `controller-manager-webhook-server-cert` | Pulumi (CP Helm) |
| `cp-gateway-tls` | `openchoreo-control-plane` | `openchoreo-ca` | `cp-gateway-tls` | Pulumi |
| `cluster-agent-dataplane-tls` | `openchoreo-data-plane` | `openchoreo-ca` | `cluster-agent-tls` | Pulumi (DP Helm) |
| `dp-gateway-tls` | `openchoreo-data-plane` | `openchoreo-ca` | `dp-gateway-tls` | Pulumi |
| `openchoreo-data-plane-*-serving-cert` | `openchoreo-data-plane` | `openchoreo-ca` | `webhook-server-cert` | Pulumi (DP Helm) |
| `wildcard-amernas-work` | `openchoreo-gateway` | `letsencrypt-dns01` | `wildcard-amernas-work-tls` | FluxCD |
| `cluster-agent-observabilityplane-tls` | `openchoreo-observability-plane` | `openchoreo-ca` | `cluster-agent-tls` | Pulumi (OP Helm) |
| `op-gateway-tls` | `openchoreo-observability-plane` | `openchoreo-ca` | `op-gateway-tls` | Pulumi |
| `cluster-agent-workflowplane-tls` | `openchoreo-workflow-plane` | `openchoreo-ca` | `cluster-agent-tls` | Pulumi (WP Helm) |

All certificates show **Ready=True**.

### ClusterIssuers (3)

| Name | Type | Owner |
|------|------|-------|
| `selfsigned-bootstrap` | SelfSigned | Pulumi |
| `openchoreo-ca` | CA (from openchoreo-ca-secret) | Pulumi |
| `letsencrypt-dns01` | ACME (DNS-01 via Cloudflare) | FluxCD |

## External Secrets Operator

### ExternalSecrets (18)

| Namespace | Name | Store | Owner |
|-----------|------|-------|-------|
| `backstage-fork` | `backstage-fork-secrets` | `default` | FluxCD |
| `cert-manager` | `cloudflare-dns-api-token` | `default` | FluxCD |
| `external-dns` | `adguard-k8s-credentials` | `default` | FluxCD |
| `external-dns` | `adguard-truenas-credentials` | `default` | FluxCD |
| `external-dns` | `cloudflare-externaldns-token` | `default` | FluxCD |
| `keepalived` | `keepalived-vrrp-auth` | `default` | FluxCD |
| `openchoreo-control-plane` | `backstage-secrets` | `default` | Pulumi |
| `openchoreo-observability-plane` | `observer-opensearch-credentials` | `default` | Pulumi |
| `openchoreo-observability-plane` | `observer-secret` | `default` | Pulumi |
| `openchoreo-observability-plane` | `openobserve-admin-credentials` | `default` | Pulumi |
| `openchoreo-observability-plane` | `opensearch-admin-credentials` | `default` | Pulumi |
| `openchoreo-observability-plane` | `rca-agent-secret` | `default` | Pulumi |
| `workflows-default` | `collab-svc-bootstrap-gitops-git-secret` | `default` | OpenChoreo operator |
| `workflows-default` | `collab-svc-bootstrap-source-git-secret` | `default` | OpenChoreo operator |
| `workflows-default` | `document-svc-bootstrap-gitops-git-secret` | `default` | OpenChoreo operator |
| `workflows-default` | `document-svc-bootstrap-source-git-secret` | `default` | OpenChoreo operator |
| `workflows-default` | `frontend-bootstrap-gitops-git-secret` | `default` | OpenChoreo operator |
| `workflows-default` | `frontend-bootstrap-source-git-secret` | `default` | OpenChoreo operator |

All ExternalSecrets show **SecretSynced=True**.

### PushSecrets (4)

| Namespace | Name | Status | Owner |
|-----------|------|--------|-------|
| `openbao` | `backstage-fork-secrets` | Synced | Pulumi |
| `openbao` | `dev-secrets` | Synced | Pulumi |
| `openbao` | `git-secrets` | Synced | Pulumi |
| `openbao` | `openobserve-creds` | Synced | Pulumi |

## CRDs (161 total)

Top API groups by CRD count:

| API Group | CRDs |
|-----------|------|
| `longhorn.io` | ~12 |
| `openchoreo.dev` | ~16 |
| `monitoring.coreos.com` | ~8 |
| `cilium.io` | ~6 |
| `gateway.networking.k8s.io` | ~4 |
| `odigos.io` / `actions.odigos.io` | ~4 |
| `notification.toolkit.fluxcd.io` | ~2 |
| `generators.external-secrets.io` | ~2 |
| cert-manager, external-secrets, flux, kgateway | Various |

## Cilium Networking

| Resource | Name | Details |
|----------|------|---------|
| `CiliumL2AnnouncementPolicy` | `homelab-l2-policy` | L2 announcements for LoadBalancer services |
| DaemonSet | `cilium` | 1 node — CNI agent |
| DaemonSet | `cilium-envoy` | 1 node — L7 proxy for Gateway API |
| Deployment | `cilium-operator` | 1/1 — manages CiliumEndpoints, policies |
| Deployment | `hubble-relay` | 1/1 — observability relay |
| Deployment | `hubble-ui` | 1/1 — observability dashboard |

## Persistent Volumes (32 total)

### Bound PVs (12)

| PV | Size | Claim Namespace | Claim | Purpose |
|----|------|----------------|-------|---------|
| `pvc-05657224…` | 128Mi | `openchoreo-observability-plane` | `ai-rca-agent-data` | RCA agent data |
| `pvc-43708d83…` | 128Mi | `openchoreo-observability-plane` | `observer-alerts-data` | Observer alerts |
| `pvc-477b674e…` | 1Gi | `dp-default-doclet-dev…` | `postgres-development-*-data-storage` | Postgres dev |
| `pvc-697617a3…` | 1Gi | `dp-default-doclet-stag…` | `postgres-staging-*-data-storage` | Postgres staging |
| `pvc-744c095c…` | 8Gi | `openchoreo-observability-plane` | `opensearch-master-*-0` | OpenSearch data |
| `pvc-8aba54b6…` | 10Gi | `openchoreo-observability-plane` | `data-openobserve-0` | OpenObserve data |
| `pvc-87a1e764…` | 5Gi | `workflows-default` | `backstage-fork-build-*-workspace` | Active build |
| `pvc-e65f639f…` | 5Gi | `workflows-default` | `backstage-fork-build-*-workspace` | Active build |
| `pvc-e8c5c748…` | 10Gi | `openchoreo-workflow-plane` | `registry` | Docker registry |
| `pvc-f188a06b…` | 5Gi | `workflows-default` | `backstage-fork-build-*-workspace` | Active build |
| `pvc-f2f97cd4…` | 1Gi | `thunder` | `thunder-database-pvc` | Thunder DB |
| `pvc-fb837a69…` | 5Gi | `workflows-default` | `backstage-fork-build-*-workspace` | Active build |

### Released (Orphaned) PVs (20)

All `Released` PVs are from completed workflow builds in `workflows-default` or old database PVCs. These PVs retain data but are not bound to any active claim.

| Pattern | Count | Sizes |
|---------|-------|-------|
| `*-bootstrap-workspace` | 6 | 2Gi each |
| `*-build-*-workspace` | 4 | 5Gi each |
| `*-manual-01-workspace` | 2 | 2Gi each |
| `*-build-00*-workspace` | 2 | 2Gi each |
| `postgres-*-data-storage` (old) | 4 | 1Gi each |
| `backstage-fork-rebrand-*` | 2 | 5Gi each |

**Total orphaned storage: ~58Gi** that could be reclaimed.

## OpenChoreo Custom Resources (default namespace)

### Projects (3)

| Name | Age |
|------|-----|
| `arr-stack` | 2d1h |
| `dfg` | 4h24m |
| `doclet` | 2d23h |

### Components (7)

| Name | Project | Type |
|------|---------|------|
| `collab-svc` | doclet | deployment/service |
| `deep-agent` | arr-stack | deployment/usecase |
| `document-svc` | doclet | deployment/service |
| `frontend` | doclet | deployment/web-application |
| `nats` | doclet | deployment/message-broker |
| `postgres` | doclet | deployment/database |
| `sonarr` | arr-stack | deployment/web-application |

### Environments (3)

`development`, `staging`, `production`

### Deployment Pipelines (1)

`standard`

### Component Types (5)

`database`, `message-broker`, `service`, `usecase`, `web-application`

### Workflows (4)

`bulk-gitops-release`, `docker-gitops-release`, `google-cloud-buildpacks-gitops-release`, `react-gitops-release`

### Workloads (6)

| Name | Project | Component |
|------|---------|-----------|
| `collab-svc-workload` | doclet | collab-svc |
| `document-svc-workload` | doclet | document-svc |
| `frontend-workload` | doclet | frontend |
| `nats` | doclet | nats |
| `postgres` | doclet | postgres |
| `sonarr-workload` | arr-stack | sonarr |

### Release Bindings (8)

| Name | Project | Component | Environment |
|------|---------|-----------|-------------|
| `collab-svc-development` | doclet | collab-svc | development |
| `document-svc-development` | doclet | document-svc | development |
| `frontend-development` | doclet | frontend | development |
| `nats-development` | doclet | nats | development |
| `nats-staging` | doclet | nats | staging |
| `postgres-development` | doclet | postgres | development |
| `postgres-staging` | doclet | postgres | staging |
| `sonarr-development` | arr-stack | sonarr | development |

## LoadBalancer Services

| Namespace | Service | Cluster IP | External IP |
|-----------|---------|-----------|-------------|
| `openchoreo-control-plane` | `gateway-default` | 10.103.133.185 | 192.168.0.14 (via Cilium L2) |
| `openchoreo-data-plane` | `gateway-default` | 10.104.74.83 | *(none)* |
| `openchoreo-gateway` | `gateway-shared` | 10.109.202.177 | 192.168.0.10 (via Cilium L2) |
| `openchoreo-observability-plane` | `gateway-default` | 10.108.59.140 | *(none)* |
| `openchoreo-observability-plane` | `openchoreo-observability-prometheus` | 10.109.62.140 | *(none)* |

## FluxCD Resources

| Kind | Namespace | Name | Status |
|------|-----------|------|--------|
| `GitRepository` | `flux-system` | `sample-gitops` | ✅ Stored artifact |
| `Kustomization` | `flux-system` | `oc-namespaces` | ✅ Applied |
| `Kustomization` | `flux-system` | `oc-platform-shared` | ✅ Applied |
| `Kustomization` | `flux-system` | `oc-infrastructure` | ✅ Applied |
| `Kustomization` | `flux-system` | `oc-platform` | ✅ Applied |
| `Kustomization` | `flux-system` | `oc-demo-projects` | ✅ Applied |
| `HelmRelease` | `external-dns` | `external-dns-cloudflare` | ✅ Ready |
| `HelmRelease` | `external-dns` | `external-dns-adguard-k8s` | ❌ Stalled (RetriesExceeded) |
| `HelmRelease` | `external-dns` | `external-dns-adguard-truenas` | ❌ Stalled (RetriesExceeded) |
| `Provider` | `flux-system` | `telegram` | Active |
| `Alert` | `flux-system` | `flux-alerts` | Active |

## ReferenceGrants (9)

| Namespace | Name | Purpose |
|-----------|------|---------|
| `backstage-fork` | `allow-gateway-routing` | Routes from gateway-shared |
| `kube-system` | `allow-gateway-routing` | Routes from gateway-shared |
| `longhorn-system` | `allow-gateway-routing` | Routes from gateway-shared |
| `openbao` | `allow-gateway-routing` | Routes from gateway-shared |
| `openchoreo-control-plane` | `allow-gateway-routing` | Routes from gateway-shared |
| `openchoreo-data-plane` | `allow-gateway-routing` | Routes from gateway-shared |
| `openchoreo-observability-plane` | `allow-gateway-routing` | Routes from gateway-shared |
| `openchoreo-workflow-plane` | `allow-gateway-routing` | Routes from gateway-shared |
| `thunder` | `allow-gateway-routes` | Routes from gateway-shared |

## Health Issues

| Issue | Details | Severity |
|-------|---------|----------|
| 2 failed HelmReleases | `external-dns-adguard-k8s`, `external-dns-adguard-truenas` — RetriesExceeded | ⚠️ Warning |
| DP gateway no external IP | `openchoreo-data-plane/gateway-default` — no Cilium LB IP assigned | ⚠️ Warning |
| OP gateway no external IP | `openchoreo-observability-plane/gateway-default` — no Cilium LB IP assigned | ⚠️ Warning |
| 20 orphaned PVs | ~58Gi of Released PVs from completed workflow builds | ℹ️ Info |
| `ai-rca-agent` scaled to 0 | 0/0 replicas — likely intentional (disabled or pending config) | ℹ️ Info |
| `dfg` project — origin unknown | Created 4h ago, not in gitops kustomization paths | ❓ Unknown |
| `deep-agent` component — origin unknown | Component in `arr-stack` project, type `usecase`, created 6h ago | ❓ Unknown |
