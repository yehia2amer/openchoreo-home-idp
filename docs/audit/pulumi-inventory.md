# Pulumi-Managed Resource Inventory

> **Stack:** `talos-baremetal` · **Resources:** 269 · **Date:** 2026-04-07
> **Cluster:** Talos Linux bare-metal, single-node K8s v1.33.0

## Feature Flags (talos-baremetal)

| Flag | Value |
|------|-------|
| `enable_flux` | `true` |
| `enable_observability` | `true` |
| `enable_openobserve` | `true` |
| `enable_rca` | `true` |
| `enable_demo_app_bootstrap` | `true` |
| `tls_enabled` | `true` |
| `cilium_pre_installed` | `true` (platform default) |
| `cilium_l2_announcements_enabled` | `true` (platform default) |
| `gateway_mode` | `cilium` (platform default) |
| `domain_base` | `amernas.work` |
| `gateway_pin_ip` | `192.168.0.14` |

## Deployment Sequence

From `__main__.py`, the deployment runs in this order:

| Step | Component | Condition | File |
|------|-----------|-----------|------|
| 0 | Cilium CNI + Gateway API | `cilium_pre_installed=false` | `cilium.py` |
| 0.5 | **Cilium L2 (standalone)** | `cilium_pre_installed=true` ← **active** | `cilium_l2.py` |
| 1 | Prerequisites | Always | `prerequisites.py` |
| 1.5 | TLS Setup | `tls_enabled=true` ← **active** | `tls_setup.py` |
| 2 | Control Plane | Always | `control_plane.py` |
| 3 | Data Plane | Always | `data_plane.py` |
| 4 | Workflow Plane | Always | `workflow_plane.py` |
| 5 | Observability Plane | `enable_observability=true` ← **active** | `observability_plane.py` |
| 6 | Link Planes | Observability enabled | `link_planes.py` |
| 6.5 | Odigos | `enable_openobserve=true` AND `enable_observability=true` ← **active** | `odigos.py` |
| 7 | Flux CD & GitOps | `enable_flux=true` ← **active** | `flux_gitops.py` |
| 8 | Integration Tests | Always | `integration_tests.py` |
| 9 | Demo App Bootstrap | `enable_demo_app_bootstrap=true` AND `enable_flux=true` AND `github_pat` set ← **active** | `demo_app_bootstrap.py` |

**Note:** On `talos-baremetal`, Cilium is pre-installed by the nested `talos-cluster-baremetal` Pulumi project. Step 0 is skipped; Step 0.5 applies L2 announcement policies only.

## Namespaces Created by Pulumi

| Namespace | Created By | Component |
|-----------|-----------|-----------|
| `cert-manager` | `prerequisites.py` | cert-manager Helm chart |
| `external-secrets` | `prerequisites.py` | external-secrets Helm chart |
| `openchoreo-control-plane` | `prerequisites.py` | Control Plane |
| `openchoreo-data-plane` | `prerequisites.py` | Data Plane |
| `openbao` | `prerequisites.py` | OpenBao Helm chart |
| `workflows-default` | `prerequisites.py` | Workflow execution namespace |
| `thunder` | `prerequisites.py` | Thunder IdP |
| `openchoreo-workflow-plane` | `prerequisites.py` | Workflow Plane |
| `openchoreo-observability-plane` | `prerequisites.py` | Observability Plane |
| `odigos-system` | `odigos.py` | Odigos auto-instrumentation |
| `flux-system` | `flux_gitops.py` | FluxCD controllers |

**Total: 11 namespaces** created directly by Pulumi.

## Helm Charts Deployed by Pulumi

| Chart | Namespace | Source | Version | Component |
|-------|-----------|--------|---------|-----------|
| `cert-manager` | `cert-manager` | `oci://quay.io/jetstack/charts` | v1.19.4 | Prerequisites |
| `external-secrets` | `external-secrets` | `oci://ghcr.io/external-secrets/charts` | 2.0.1 | Prerequisites |
| `kgateway-crds` | (cluster-wide) | `oci://cr.kgateway.dev/kgateway-dev/charts` | v2.2.1 | Prerequisites |
| `openbao` | `openbao` | `oci://ghcr.io/openbao/charts` | 0.25.6 | Prerequisites |
| `thunder` | `thunder` | `oci://ghcr.io/asgardeo/helm-charts` | 0.28.0 | Prerequisites |
| `openchoreo-control-plane` | `openchoreo-control-plane` | `oci://ghcr.io/openchoreo/helm-charts` | 1.0.0 | Control Plane |
| `openchoreo-data-plane` | `openchoreo-data-plane` | `oci://ghcr.io/openchoreo/helm-charts` | 1.0.0 | Data Plane |
| `docker-registry` | `openchoreo-workflow-plane` | `https://twuni.github.io/docker-registry.helm` | 3.0.0 | Workflow Plane |
| `openchoreo-workflow-plane` | `openchoreo-workflow-plane` | `oci://ghcr.io/openchoreo/helm-charts` | 1.0.0 | Workflow Plane |
| `openchoreo-observability-plane` | `openchoreo-observability-plane` | `oci://ghcr.io/openchoreo/helm-charts` | 1.0.0 | Observability Plane |
| `observability-logs-opensearch` | `openchoreo-observability-plane` | `oci://ghcr.io/openchoreo/helm-charts` | 0.3.11 | Observability Plane |
| `observability-tracing-opensearch` | `openchoreo-observability-plane` | `oci://ghcr.io/openchoreo/helm-charts` | 0.3.10 | Observability Plane |
| `observability-metrics-prometheus` | `openchoreo-observability-plane` | `oci://ghcr.io/openchoreo/helm-charts` | 0.2.5 | Observability Plane |
| `observability-logs-openobserve` | `openchoreo-observability-plane` | `oci://ghcr.io/openchoreo/helm-charts` | 0.4.2 | Observability Plane |
| `observability-tracing-openobserve` | `openchoreo-observability-plane` | `oci://ghcr.io/openchoreo/helm-charts` | 0.2.1 | Observability Plane |
| `odigos` | `odigos-system` | Helm chart (version 1.23.0) | 1.23.0 | Odigos |

**Total: 16 Helm charts** deployed by Pulumi.

## CRDs Installed by Pulumi

Pulumi installs ~45 CRDs across these groups:

- **cert-manager.io** — Certificate, Issuer, ClusterIssuer, etc.
- **external-secrets.io** — ExternalSecret, ClusterSecretStore, PushSecret, etc.
- **gateway.networking.k8s.io** — Gateway, GatewayClass, HTTPRoute, ReferenceGrant (experimental install)
- **kgateway.dev** — GatewayParameters
- **openchoreo.dev** — Project, Component, Environment, Workflow, Workload, etc.
- **monitoring.coreos.com** — ServiceMonitor, PodMonitor, Prometheus, Alertmanager, PrometheusRule, etc.
- **odigos.io / actions.odigos.io** — InstrumentedApplication, InstrumentationConfig, CollectorGateway, OdigosConfiguration, etc.

## Non-Helm Resources Created by Pulumi

### Step 0.5: Cilium L2 (cilium_l2.py)

- `CiliumL2AnnouncementPolicy` — `homelab-l2-policy` (L2 load-balancer announcements)
- `CiliumLoadBalancerIPPool` — IP pool for bare-metal LB services

### Step 1: Prerequisites (prerequisites.py)

- 11 Namespaces (listed above)
- `ServiceAccount` — `external-secrets-openbao` (ESO → OpenBao auth)
- `ClusterSecretStore` — `default` (OpenBao backend)
- `ExternalSecret` — `backstage-secrets` (openchoreo-control-plane)
- `ExternalSecret` — `opensearch-admin-credentials` (openchoreo-observability-plane)
- `ExternalSecret` — `observer-opensearch-credentials` (openchoreo-observability-plane)
- `ExternalSecret` — `observer-secret` (openchoreo-observability-plane)
- `ExternalSecret` — `openobserve-admin-credentials` (openchoreo-observability-plane)
- `ExternalSecret` — `rca-agent-secret` (openchoreo-observability-plane)
- `PushSecret` — `backstage-fork-secrets` (openbao → backstage-fork)
- `PushSecret` — `dev-secrets` (openbao → dev secrets)
- `PushSecret` — `git-secrets` (openbao → git secrets)
- `PushSecret` — `openobserve-creds` (openbao → openobserve credentials)
- OpenBao configuration via dynamic providers (vault mounts, policies, secrets)
- WorkflowTemplates applied from remote YAML files

### Step 1.5: TLS Setup (tls_setup.py)

- `ClusterIssuer` — `selfsigned-bootstrap` (self-signed issuer)
- `Certificate` — `openchoreo-ca` in `cert-manager` (CA certificate)
- `ClusterIssuer` — `openchoreo-ca` (CA issuer)
- `Certificate` — `cp-gateway-tls` in `openchoreo-control-plane`
- `Certificate` — `dp-gateway-tls` in `openchoreo-data-plane`
- `Certificate` — `op-gateway-tls` in `openchoreo-observability-plane`
- CA Secret copy operations (copies CA to multiple namespaces)

### Step 6.5: Odigos (odigos.py)

- Odigos Helm chart (creates controllers, DaemonSet `odiglet`, CRDs)

### Step 7: FluxCD (flux_gitops.py)

- FluxCD install manifest (8,612 lines — controllers, CRDs, RBAC)
- `GitRepository` — `sample-gitops` (source: `https://github.com/yehia2amer/openchoreo-gitops`)
- 5 `Kustomization` resources: `oc-namespaces`, `oc-platform-shared`, `oc-infrastructure`, `oc-platform`, `oc-demo-projects`
- Flux notification: `Provider/telegram`, `Alert/flux-alerts`

### Step 9: Demo App Bootstrap (demo_app_bootstrap.py)

- Triggers WorkflowRuns for demo apps
- Merges PRs via GitHub API
- Verifies deployment success

## Pulumi State Summary (269 resources)

| Resource Type | Count |
|---------------|-------|
| Dynamic providers (pulumi:providers:pulumi-python) | 71 |
| CRDs (kubernetes:apiextensions) | 45 |
| Helm releases (kubernetes:helm.sh/v3:Release) | 12 |
| ServiceAccounts | 12 |
| Namespaces | 11 |
| Deployments | 11 |
| ConfigMaps | 9 |
| ClusterRoles / ClusterRoleBindings | ~8 |
| Secrets | ~7 |
| Services | ~7 |
| Other (Certificates, Issuers, ExternalSecrets, etc.) | ~76 |

## Nested Project: talos-cluster-baremetal

The `talos-cluster-baremetal/` directory is a separate Pulumi project that bootstraps the bare-metal cluster. It manages:

| Resource | Details |
|----------|---------|
| Talos machine config | Single-node Talos Linux bootstrap |
| **Cilium CNI** | Pre-installed in `kube-system` (why Step 0 is skipped) |
| **Longhorn** | Distributed storage in `longhorn-system` |
| **Gateway API CRDs** | Experimental install |
| **snapshot-controller** | Volume snapshot support |

## Dead Code

- `components/otel_operator.py` — Never imported from `__main__.py`. The OpenTelemetry Operator approach was superseded by **Odigos** (auto-instrumentation). This file can be safely removed.

## Outputs Exported

```
backstage_url, api_url, thunder_url, argo_workflows_url, observer_url,
opensearch_dashboards_url, data_plane_gateway_http, data_plane_gateway_https,
opensearch_username, opensearch_password (secret), openbao_root_token (secret),
kubeconfig_context, domain_base, openchoreo_version, platform, edition,
cilium_enabled, flux_enabled, observability_enabled, demo_app_bootstrap_enabled,
namespaces (map)
```
