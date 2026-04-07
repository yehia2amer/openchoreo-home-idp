# FluxCD-Managed Resource Inventory

> **Date:** 2026-04-07 · **Cluster:** talos-baremetal
> **GitOps Repo:** https://github.com/yehia2amer/openchoreo-gitops (branch: `main`)

## How FluxCD is Deployed

FluxCD is deployed **entirely via Pulumi** (`components/flux_gitops.py`):

1. Pulumi applies `flux-install.yaml` (8,612 lines) — installs all FluxCD controllers and CRDs
2. Pulumi creates a `GitRepository` source pointing to the gitops repo
3. Pulumi creates 5 `Kustomization` resources that reconcile paths from the gitops repo
4. Pulumi creates a Telegram notification provider and alert

**Key insight:** FluxCD itself is a Pulumi-managed resource, but the *resources FluxCD deploys* are gitops-managed (not in Pulumi state).

## FluxCD Controllers (flux-system namespace)

| Controller | Status |
|------------|--------|
| `helm-controller` | 1/1 Running |
| `image-automation-controller` | 1/1 Running |
| `image-reflector-controller` | 1/1 Running |
| `kustomize-controller` | 1/1 Running |
| `notification-controller` | 1/1 Running |
| `source-controller` | 1/1 Running |

## Source

| Kind | Name | URL | Branch | Status |
|------|------|-----|--------|--------|
| `GitRepository` | `sample-gitops` | `https://github.com/yehia2amer/openchoreo-gitops` | `main` | ✅ Stored artifact (`main@sha1:cd6d5dd6`) |

**No HelmRepositories** are defined — all Helm charts consumed by FluxCD HelmReleases use inline `spec.chart.spec.sourceRef` pointing to OCI/HTTP repos, not FluxCD HelmRepository objects.

## Kustomizations

| Name | Path (in gitops repo) | Depends On | Status |
|------|----------------------|------------|--------|
| `oc-namespaces` | `clusters/talos-baremetal/namespaces/` | — | ✅ Applied |
| `oc-platform-shared` | `clusters/talos-baremetal/platform-shared/` | `oc-namespaces` | ✅ Applied |
| `oc-infrastructure` | `clusters/talos-baremetal/infrastructure/` | `oc-platform-shared` | ✅ Applied |
| `oc-platform` | `clusters/talos-baremetal/platform/` | `oc-infrastructure` | ✅ Applied |
| `oc-demo-projects` | `clusters/talos-baremetal/demo-projects/` | `oc-platform` | ✅ Applied |

All kustomizations reconciled to `main@sha1:cd6d5dd6daf9449947cdd440233d6bb0f4e4c547`.

## Notifications

| Kind | Name | Details |
|------|------|---------|
| `Provider` | `telegram` | Telegram bot for Flux alerts |
| `Alert` | `flux-alerts` | Sends alerts on FluxCD events |

## Resources Created by FluxCD (via gitops repo)

### Namespaces (from oc-namespaces)

| Namespace | Purpose |
|-----------|---------|
| `backstage-fork` | Backstage fork deployment |
| `external-dns` | ExternalDNS instances |
| `openchoreo-gateway` | Shared gateway for all services |
| `keepalived` | VRRP-based IP failover + AdGuard DNS |

### HelmReleases (from oc-infrastructure)

| Name | Namespace | Chart | Status |
|------|-----------|-------|--------|
| `external-dns-cloudflare` | `external-dns` | `external-dns@1.20.0` | ✅ Ready (UpgradeSucceeded) |
| `external-dns-adguard-k8s` | `external-dns` | external-dns (AdGuard provider) | ❌ Stalled (RetriesExceeded — failed to install) |
| `external-dns-adguard-truenas` | `external-dns` | external-dns (AdGuard provider) | ❌ Stalled (RetriesExceeded — failed to install) |

### Gateway API Resources (from oc-platform-shared / oc-platform)

**Gateway:**

| Name | Namespace | GatewayClass | Address | Status |
|------|-----------|-------------|---------|--------|
| `gateway-shared` | `openchoreo-gateway` | `kgateway` | `192.168.0.10` | ✅ Programmed |

**HTTPRoutes (from oc-platform — openchoreo-gateway namespace):**

| Name | Hostnames | Backend Namespace |
|------|-----------|-------------------|
| `alertmanager` | `alertmanager.amernas.work` | `openchoreo-observability-plane` |
| `api` | `api.amernas.work` | `openchoreo-control-plane` |
| `argo-server` | `argo.amernas.work` | `openchoreo-workflow-plane` |
| `backstage` | `backstage.amernas.work` | `openchoreo-control-plane` |
| `hubble-ui` | `hubble.amernas.work` | `kube-system` |
| `longhorn-ui` | `longhorn.amernas.work` | `longhorn-system` |
| `observer` | `observer.amernas.work` | `openchoreo-observability-plane` |
| `openbao-ui` | `openbao.amernas.work` | `openbao` |
| `openobserve-ui` | `openobserve.amernas.work` | `openchoreo-observability-plane` |
| `opensearch` | `opensearch.amernas.work` | `openchoreo-observability-plane` |
| `prometheus` | `prometheus.amernas.work` | `openchoreo-observability-plane` |
| `rca-agent` | `rca-agent.amernas.work` | `openchoreo-observability-plane` |
| `registry` | `registry.amernas.work` | `openchoreo-workflow-plane` |
| `thunder` | `thunder.amernas.work` | `thunder` |
| `wildcard-data-plane` | `*.amernas.work` | `openchoreo-data-plane` |

**HTTPRoute (from oc-platform — backstage-fork namespace):**

| Name | Hostnames | Backend |
|------|-----------|---------|
| `backstage-fork` | `portal.amernas.work` | `backstage-fork` service |

### ReferenceGrants (from oc-platform-shared)

Allow `gateway-shared` in `openchoreo-gateway` to route to backends in other namespaces:

| Namespace | Name |
|-----------|------|
| `backstage-fork` | `allow-gateway-routing` |
| `kube-system` | `allow-gateway-routing` |
| `longhorn-system` | `allow-gateway-routing` |
| `openbao` | `allow-gateway-routing` |
| `openchoreo-control-plane` | `allow-gateway-routing` |
| `openchoreo-data-plane` | `allow-gateway-routing` |
| `openchoreo-observability-plane` | `allow-gateway-routing` |
| `openchoreo-workflow-plane` | `allow-gateway-routing` |
| `thunder` | `allow-gateway-routes` |

### Deployments (from oc-platform)

| Name | Namespace | Details |
|------|-----------|---------|
| `backstage-fork` | `backstage-fork` | Fork of Backstage portal |
| `adguard-home-k8s` | `keepalived` | AdGuard Home DNS server |

### DaemonSets (from oc-infrastructure)

| Name | Namespace | Details |
|------|-----------|---------|
| `keepalived` | `keepalived` | VRRP-based virtual IP management |

### Certificates (from oc-infrastructure)

| Name | Namespace | Issuer | Secret |
|------|-----------|--------|--------|
| `wildcard-amernas-work` | `openchoreo-gateway` | `letsencrypt-dns01` | `wildcard-amernas-work-tls` |

### ClusterIssuers (from oc-infrastructure)

| Name | Type | Status |
|------|------|--------|
| `letsencrypt-dns01` | ACME (DNS-01 via Cloudflare) | ✅ Ready |

### ExternalSecrets (from oc-platform-shared / oc-infrastructure)

| Name | Namespace | Source |
|------|-----------|--------|
| `cloudflare-dns-api-token` | `cert-manager` | ClusterSecretStore `default` |
| `adguard-k8s-credentials` | `external-dns` | ClusterSecretStore `default` |
| `adguard-truenas-credentials` | `external-dns` | ClusterSecretStore `default` |
| `cloudflare-externaldns-token` | `external-dns` | ClusterSecretStore `default` |
| `keepalived-vrrp-auth` | `keepalived` | ClusterSecretStore `default` |
| `backstage-fork-secrets` | `backstage-fork` | ClusterSecretStore `default` |

### OpenChoreo Demo Projects (from oc-demo-projects)

The `oc-demo-projects` kustomization deploys OpenChoreo Project/Component/Environment CRs for the `doclet` demo application (and possibly `arr-stack`).

## Ownership Boundary: Pulumi vs FluxCD

Per `docs/adr/001-pulumi-fluxcd-boundary.md`:

| Layer | Owner | Examples |
|-------|-------|---------|
| **Infrastructure** | Pulumi | Namespaces (core 11), CRDs, Helm charts (16), TLS CA chain, OpenBao, ESO |
| **Platform extensions** | FluxCD | Shared gateway, HTTPRoutes, ExternalDNS, keepalived, backstage-fork |
| **Application workloads** | FluxCD / OpenChoreo operators | Demo projects, dp-default-* namespaces, workflow builds |
| **Cluster bootstrap** | Nested Pulumi | Cilium, Longhorn, Gateway API CRDs, Talos config |
