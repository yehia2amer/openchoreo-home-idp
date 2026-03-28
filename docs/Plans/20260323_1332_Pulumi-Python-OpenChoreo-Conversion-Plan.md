# Pulumi + Python — OpenChoreo v1.0 Conversion Plan

**Date:** 2026-03-23 13:32  
**Scope:** Convert the existing Terraform/OpenTofu pipeline (50 resources, 6 modules) to Pulumi with Python  
**Constraints:** Strict Python, multiplatform scripts using UV script syntax (PEP 723), proper provider selection

---

## 1. Provider Mapping (Terraform → Pulumi)

| Terraform Provider        | Pulumi Package             | Purpose                                                        |
|---------------------------|----------------------------|----------------------------------------------------------------|
| `hashicorp/helm ~> 2.17`  | `pulumi-kubernetes` (helm) | Helm releases (OCI & HTTP repos)                               |
| `hashicorp/kubernetes`    | `pulumi-kubernetes`        | Namespaces, ServiceAccounts, ConfigMaps, CustomResources       |
| `hashicorp/null`          | `pulumi-command`           | Local-exec kubectl/helm commands                               |
| `hashicorp/time`          | Built-in `time.sleep()`    | Wait delays between resources (Python native or Command sleep) |
| *(none — manual kubectl)* | `pulumi-vault`             | OpenBao secrets, auth, policies (proper provider instead of CLI exec) |

### Key Provider Decisions

1. **OpenBao → `pulumi-vault`**: Instead of shelling out to `bao kv put` / `bao write` via postStart hooks, use the Vault provider pointed at OpenBao's API (`http://localhost:8200` via port-forward or `openbao.openbao.svc:8200`). This replaces inline shell scripts with proper secret management resources.

2. **CRD Instances → `pulumi_kubernetes.apiextensions.CustomResource`**: ExternalSecrets, ClusterSecretStore, ClusterDataPlane, ClusterWorkflowPlane, ClusterObservabilityPlane, GitRepository, Kustomizations — all created natively instead of kubectl heredocs.

3. **Helm Charts → `pulumi_kubernetes.helm.v4.Chart`**: Supports both OCI registries (`oci://ghcr.io/...`) and HTTP repositories (`https://twuni.github.io/...`). Values passed as Python dicts (rendered from YAML templates via Jinja2 or plain Python dicts).

4. **Shell Commands → `pulumi_command.local.Command`**: For operations that have no native provider (Gateway API CRD install from URL, CoreDNS ConfigMap apply from remote YAML, Thunder install with upstream values URL).

---

## 2. Folder Structure

```
pulumi/
├── Pulumi.yaml                    # Project definition
├── Pulumi.dev.yaml                # Stack config (dev/k3d)
├── __main__.py                    # Entry point — orchestrates all components
├── config.py                      # Load Pulumi config into typed dataclass
├── requirements.txt               # Python dependencies
├── components/
│   ├── __init__.py
│   ├── prerequisites.py           # Gateway API, cert-manager, ESO, kgateway, OpenBao
│   ├── openbao_config.py          # Vault provider: secrets, auth, policies (replaces postStart)
│   ├── control_plane.py           # Thunder, ExternalSecret, CP Helm chart
│   ├── data_plane.py              # Namespace, copy CA, DP Helm chart, register ClusterDataPlane
│   ├── workflow_plane.py          # Registry, copy CA, WP Helm chart, workflow templates, register
│   ├── observability_plane.py     # Namespace, CA, ExternalSecrets, Obs Helm charts, register
│   ├── flux_gitops.py             # Flux install, GitRepository, Kustomizations
│   └── link_planes.py             # Patch DP/WP with observability ref
├── values/
│   ├── openbao.py                 # Returns dict for OpenBao Helm values
│   ├── control_plane.py           # Returns dict for CP Helm values
│   ├── data_plane.py              # Returns dict for DP Helm values
│   ├── workflow_plane.py          # Returns dict for WP Helm values
│   ├── registry.py                # Returns dict for docker-registry values
│   └── observability_plane.py     # Returns dict for Obs Plane Helm values
├── scripts/
│   └── bootstrap_k3d.py           # UV script: create k3d cluster + run pulumi up
└── helpers/
    ├── __init__.py
    ├── copy_ca.py                 # Reusable: copy cluster-gateway-ca ConfigMap
    ├── register_plane.py          # Reusable: wait for TLS secret, build plane CRD
    └── wait.py                    # Reusable: sleep/wait helpers
```

---

## 3. Module-by-Module Conversion Strategy

### 3.1 Prerequisites (13 TF resources → ~10 Pulumi resources)

| Terraform Resource                    | Pulumi Equivalent                                                       | Notes                                        |
|---------------------------------------|-------------------------------------------------------------------------|----------------------------------------------|
| `null_resource.gateway_api_crds`      | `Command("gateway-api-crds", create="kubectl apply --server-side ...")` | Remote URL manifest — keep as Command        |
| `time_sleep.after_gateway_api`        | `Command("wait-gw", create="sleep 5")`                                 | Or Python time.sleep in ResourceOptions      |
| `helm_release.cert_manager`           | `k8s.helm.v4.Chart("cert-manager", ...)`                               | OCI: `oci://quay.io/jetstack/charts`         |
| `helm_release.external_secrets`       | `k8s.helm.v4.Chart("external-secrets", ...)`                           | OCI: `oci://ghcr.io/external-secrets/charts` |
| `kubernetes_namespace.control_plane`  | `k8s.core.v1.Namespace("control-plane", ...)`                          | Native resource                              |
| `helm_release.kgateway_crds`         | `k8s.helm.v4.Chart("kgateway-crds", ...)`                              | OCI: `oci://cr.kgateway.dev/...`             |
| `helm_release.kgateway`              | `k8s.helm.v4.Chart("kgateway", ...)`                                   | OCI: `oci://cr.kgateway.dev/...`             |
| `helm_release.openbao`               | `k8s.helm.v4.Chart("openbao", ...)`                                    | OCI: `oci://ghcr.io/openbao/charts`          |
| `null_resource.openbao_ready`        | `Command("openbao-ready", create="kubectl wait ...")`                   | Wait for pod Ready                           |
| `null_resource.store_github_pat`     | `vault.kv.SecretV2` (×2)                                               | **Vault provider** for git-token, gitops-token|
| `kubernetes_service_account.eso_openbao` | `k8s.core.v1.ServiceAccount(...)`                                   | Native resource                              |
| `null_resource.cluster_secret_store` | `k8s.apiextensions.CustomResource("cluster-secret-store", ...)`         | Native CRD instance                          |
| `null_resource.coredns_rewrite`      | `Command("coredns-rewrite", create="kubectl apply -f ...")`            | Remote URL — keep as Command                 |

**OpenBao Config (replaces postStart hook):**  
Instead of the shell script in `values-openbao.yaml.tpl` postStart, use `pulumi-vault`:
- `vault.AuthBackend("k8s-auth", type="kubernetes")` — enable K8s auth
- `vault.kubernetes.AuthBackendConfig(...)` — configure K8s auth
- `vault.Policy(...)` × 2 — reader + writer policies
- `vault.kubernetes.AuthBackendRole(...)` × 2 — reader + writer roles
- `vault.kv.SecretV2(...)` × 14 — all seed secrets

> **Decision point**: The OpenBao Helm chart in dev mode auto-initializes. The postStart hook seeds secrets/auth. With `pulumi-vault`, we install OpenBao with a **minimal** postStart (or none) and use the Vault provider to configure everything after the pod is ready. This is cleaner and fully declarative.
>
> **Implementation**: OpenBao Helm values will have `injector.enabled: false`, `server.dev.enabled: true`, `server.dev.devRootToken: <token>` — no postStart. A separate `openbao_config.py` component uses `pulumi-vault` with `address="http://localhost:8200"` (via kubectl port-forward started as a Command) or by using the in-cluster address after a port-forward shim.
>
> **Practical approach**: Since Pulumi runs locally (not in-cluster), the Vault provider needs reachable access. Use a `Command` to set up a kubectl port-forward to openbao-0:8200, then the Vault provider connects to `http://localhost:8200`. The port-forward is ephemeral and only needed during `pulumi up`.

### 3.2 Control Plane (6 TF resources → 5 Pulumi resources)

| Terraform Resource                        | Pulumi Equivalent                                                   |
|-------------------------------------------|---------------------------------------------------------------------|
| `null_resource.thunder_install`           | `Command("thunder", create="helm upgrade --install ...")`          |
| `time_sleep.after_thunder`                | `Command("wait-thunder", create="sleep 10")`                       |
| `null_resource.backstage_secrets`         | `k8s.apiextensions.CustomResource("backstage-secrets", ...)`       |
| `time_sleep.after_backstage_secret`       | `Command("wait-eso-sync", create="sleep 10")`                     |
| `helm_release.control_plane`              | `k8s.helm.v4.Chart("control-plane", ...)`                          |
| `null_resource.label_namespace`           | `Command("label-ns", create="kubectl label ns ...")`              |

**Thunder**: Must remain as a Command because it needs `--values <remote-URL>` from the upstream repo. Pulumi Helm Chart doesn't support fetching remote values files.

**Values**: `values-cp.yaml.tpl` → Python dict in `values/control_plane.py` returning the same structure.

### 3.3 Data Plane (5 TF resources → 5 Pulumi resources)

| Terraform Resource                         | Pulumi Equivalent                                                    |
|--------------------------------------------|----------------------------------------------------------------------|
| `kubernetes_namespace.data_plane`          | `k8s.core.v1.Namespace("data-plane", ...)`                          |
| `null_resource.copy_ca`                    | `helpers.copy_ca("data-plane", "openchoreo-data-plane")`             |
| `helm_release.data_plane`                  | `k8s.helm.v4.Chart("data-plane", ...)`                               |
| `time_sleep.wait_for_tls`                  | `Command("wait-dp-tls", create="kubectl wait secret/...")`          |
| `null_resource.register_data_plane`        | `helpers.register_plane("data-plane", "ClusterDataPlane", ...)`      |

**Reusable helpers**: The CA copy and plane registration patterns repeat across data/workflow/observability planes → extract into helper functions.

### 3.4 Workflow Plane (6 TF resources → 6 Pulumi resources)

| Terraform Resource                            | Pulumi Equivalent                                                    |
|-----------------------------------------------|----------------------------------------------------------------------|
| `helm_release.registry`                       | `k8s.helm.v4.Chart("registry", ...)`                                 |
| `null_resource.copy_ca`                       | `helpers.copy_ca("workflow-plane", "openchoreo-workflow-plane")`      |
| `helm_release.workflow_plane`                 | `k8s.helm.v4.Chart("workflow-plane", ...)`                            |
| `null_resource.workflow_templates`            | `Command("workflow-templates", create="kubectl apply -f ...")`       |
| `time_sleep.wait_for_tls`                     | `Command("wait-wp-tls", create="kubectl wait secret/...")`          |
| `null_resource.register_workflow_plane`       | `helpers.register_plane("workflow-plane", "ClusterWorkflowPlane")`   |

**docker-registry**: HTTP repo `https://twuni.github.io/docker-registry.helm` — NOT OCI.

### 3.5 Observability Plane (12 TF resources → 12 Pulumi resources)

| Terraform Resource                              | Pulumi Equivalent                                                       |
|-------------------------------------------------|-------------------------------------------------------------------------|
| `kubernetes_namespace.obs`                      | `k8s.core.v1.Namespace("obs-plane", ...)`                               |
| `null_resource.copy_ca`                         | `helpers.copy_ca("obs-plane", "openchoreo-observability-plane")`         |
| `null_resource.opensearch_admin_creds`          | `k8s.apiextensions.CustomResource("opensearch-admin-creds", ...)`        |
| `null_resource.observer_opensearch_creds`       | `k8s.apiextensions.CustomResource("observer-opensearch-creds", ...)`     |
| `null_resource.observer_secret`                 | `k8s.apiextensions.CustomResource("observer-secret", ...)`               |
| `null_resource.machine_id`                      | `Command("machine-id", create="docker exec ...")`                       |
| `helm_release.obs_plane`                        | `k8s.helm.v4.Chart("obs-plane", ...)`                                    |
| `helm_release.logs_opensearch`                  | `k8s.helm.v4.Chart("logs-opensearch", ...)`                              |
| `helm_release.traces_opensearch`                | `k8s.helm.v4.Chart("traces-opensearch", ...)`                            |
| `helm_release.metrics_prometheus`               | `k8s.helm.v4.Chart("metrics-prometheus", ...)`                           |
| `time_sleep.wait_for_obs_tls`                   | `Command("wait-obs-tls", create="kubectl wait secret/...")`             |
| `null_resource.register_obs_plane`              | `helpers.register_plane("obs-plane", "ClusterObservabilityPlane", ...)` |

### 3.6 Flux GitOps (7 TF resources → 7 Pulumi resources)

| Terraform Resource                           | Pulumi Equivalent                                                      |
|----------------------------------------------|------------------------------------------------------------------------|
| `null_resource.install_flux`                 | `Command("install-flux", create="kubectl apply -f ...")`               |
| `null_resource.wait_flux`                    | `Command("wait-flux", create="kubectl wait ...")`                      |
| `null_resource.git_repository`               | `k8s.apiextensions.CustomResource("git-repository", ...)`              |
| `null_resource.kustomization_namespaces`     | `k8s.apiextensions.CustomResource("kust-namespaces", ...)`             |
| `null_resource.kustomization_platform_shared`| `k8s.apiextensions.CustomResource("kust-platform-shared", ...)`        |
| `null_resource.kustomization_platform`       | `k8s.apiextensions.CustomResource("kust-platform", ...)`               |
| `null_resource.kustomization_projects`       | `k8s.apiextensions.CustomResource("kust-projects", ...)`               |

### 3.7 Link Planes (1 TF resource → 1 Pulumi resource)

| Terraform Resource              | Pulumi Equivalent                                                  |
|---------------------------------|--------------------------------------------------------------------|
| `null_resource.link_planes`     | `Command("link-planes", create="kubectl patch ...")`               |

---

## 4. OpenBao Configuration via Vault Provider

Instead of the monolithic postStart shell script in `values-openbao.yaml.tpl`, use `pulumi-vault` for declarative management:

### 4.1 Vault Provider Configuration

```python
import pulumi_vault as vault

vault_provider = vault.Provider("openbao",
    address="http://127.0.0.1:8200",
    token=config.openbao_root_token,
    skip_child_token=True,
)
```

**Access strategy**: After OpenBao is deployed and ready, start a background `kubectl port-forward` to make it reachable locally, then use the Vault provider.

### 4.2 Resources to Create

| Resource Type                       | Count | Details                                                     |
|-------------------------------------|-------|-------------------------------------------------------------|
| `vault.AuthBackend`                 | 1     | `kubernetes` auth method                                    |
| `vault.kubernetes.AuthBackendConfig`| 1     | K8s host, CA cert                                           |
| `vault.Policy`                      | 2     | `openchoreo-secret-reader-policy`, `openchoreo-secret-writer-policy` |
| `vault.kubernetes.AuthBackendRole`  | 2     | Reader role (dp*), Writer role (openbao, workflow-plane)    |
| `vault.kv.SecretV2`                 | 14    | All seed secrets (npm-token, docker-*, backstage-*, etc.)   |

### 4.3 Seed Secrets List

```
secret/npm-token              → value: "fake-npm-token-for-development"
secret/docker-username        → value: "dev-user"
secret/docker-password        → value: "dev-password"
secret/github-pat             → value: "fake-github-token-for-development"
secret/username               → value: "dev-user"
secret/password               → value: "dev-password"
secret/backstage-backend-secret → value: "local-dev-backend-secret"
secret/backstage-client-secret  → value: "backstage-portal-secret"
secret/backstage-jenkins-api-key → value: "placeholder-not-in-use"
secret/observer-oauth-client-secret → value: "openchoreo-observer-resource-reader-client-secret"
secret/rca-oauth-client-secret → value: "openchoreo-rca-agent-secret"
secret/opensearch-username    → value: <from config>
secret/opensearch-password    → value: <from config>
secret/git-token              → value: <github_pat from config> (conditional)
secret/gitops-token           → value: <github_pat from config> (conditional)
```

---

## 5. Configuration Management

### Pulumi.yaml (Project)

```yaml
name: openchoreo-k3d
runtime:
  name: python
  options:
    virtualenv: venv
description: OpenChoreo v1.0 on k3d — Pulumi Python
```

### Pulumi.dev.yaml (Stack Config)

```yaml
config:
  openchoreo-k3d:kubeconfig_context: k3d-openchoreo
  openchoreo-k3d:domain_base: openchoreo.localhost
  openchoreo-k3d:tls_enabled: false
  openchoreo-k3d:is_k3d: true
  openchoreo-k3d:k3d_cluster_name: openchoreo
  openchoreo-k3d:enable_flux: true
  openchoreo-k3d:enable_observability: true
  openchoreo-k3d:gitops_repo_url: https://github.com/yehia2amer/openchoreo-home-idp
  openchoreo-k3d:gitops_repo_branch: main
  # Sensitive values via `pulumi config set --secret`
  openchoreo-k3d:openbao_root_token:
    secure: ...
  openchoreo-k3d:github_pat:
    secure: ...
```

### requirements.txt

```
pulumi>=3.0.0,<4.0.0
pulumi-kubernetes>=4.0.0,<5.0.0
pulumi-command>=1.0.0,<2.0.0
pulumi-vault>=6.0.0,<7.0.0
pyyaml>=6.0
```

---

## 6. Python Bootstrap Script (UV Syntax)

**File**: `scripts/bootstrap_k3d.py`

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "httpx>=0.25.0",
#   "pyyaml>=6.0",
# ]
# requires-python = ">=3.9"
# ///
```

### Responsibilities

1. Download k3d config YAML from upstream (httpx)
2. Patch cluster name in YAML (pyyaml)
3. Create/verify k3d cluster (subprocess — k3d CLI)
4. Verify cluster health (subprocess — kubectl)
5. Run `pulumi up --yes` in the pulumi/ directory

### Multiplatform Notes

- Use `pathlib.Path` for all file paths
- Use `subprocess.run()` with `shell=False` for portability
- Use `shutil.which()` to detect CLI tools (k3d, kubectl, pulumi)
- Use `tempfile` for temp config files
- No bash-isms, no `/bin/bash` interpreter

---

## 7. Dependency Flow (Execution Order)

```
Gateway API CRDs
  └─ cert-manager
       └─ External Secrets Operator
            ├─ kgateway CRDs → kgateway
            └─ OpenBao (Helm)
                 └─ OpenBao Ready (wait)
                      ├─ OpenBao Config (vault provider: auth, policies, roles, secrets)
                      │    └─ ClusterSecretStore (CustomResource)
                      │         └─ Control Plane
                      │              ├─ Thunder (Command)
                      │              │    └─ Backstage ExternalSecret (CustomResource)
                      │              │         └─ CP Helm Chart
                      │              │              └─ Label Namespace
                      │              │
                      │              ├─ Data Plane
                      │              │    └─ Namespace → Copy CA → DP Helm Chart → Wait TLS → Register ClusterDataPlane
                      │              │
                      │              ├─ Workflow Plane
                      │              │    └─ Registry Helm → Copy CA → WP Helm Chart → Templates → Wait TLS → Register ClusterWorkflowPlane
                      │              │
                      │              └─ Observability Plane (optional)
                      │                   └─ Namespace → CA + ExternalSecrets → machine-id
                      │                        └─ Obs Helm → Logs/Traces/Metrics Helm
                      │                             └─ Wait TLS → Register ClusterObservabilityPlane
                      │
                      └─ GitHub PAT secrets (conditional, vault provider)
                      
Link Planes (patch DP/WP with obs ref) ← depends on all planes
Flux GitOps (optional) ← depends on CP + DP + WP
```

---

## 8. Helm Chart Registry Reference

| Chart                              | Registry Type | Repository URL                                         |
|------------------------------------|---------------|--------------------------------------------------------|
| cert-manager                       | OCI           | `oci://quay.io/jetstack/charts`                        |
| external-secrets                   | OCI           | `oci://ghcr.io/external-secrets/charts`                |
| kgateway-crds                      | OCI           | `oci://cr.kgateway.dev/kgateway-dev/charts`            |
| kgateway                           | OCI           | `oci://cr.kgateway.dev/kgateway-dev/charts`            |
| openbao                            | OCI           | `oci://ghcr.io/openbao/charts`                         |
| thunder                            | OCI           | `oci://ghcr.io/asgardeo/helm-charts`                   |
| docker-registry                    | HTTP          | `https://twuni.github.io/docker-registry.helm`         |
| openchoreo-control-plane           | OCI           | `oci://ghcr.io/openchoreo/helm-charts`                 |
| openchoreo-data-plane              | OCI           | `oci://ghcr.io/openchoreo/helm-charts`                 |
| openchoreo-workflow-plane          | OCI           | `oci://ghcr.io/openchoreo/helm-charts`                 |
| openchoreo-observability-plane     | OCI           | `oci://ghcr.io/openchoreo/helm-charts`                 |
| observability-logs-opensearch      | OCI           | `oci://ghcr.io/openchoreo/helm-charts`                 |
| observability-tracing-opensearch   | OCI           | `oci://ghcr.io/openchoreo/helm-charts`                 |
| observability-metrics-prometheus   | OCI           | `oci://ghcr.io/openchoreo/helm-charts`                 |

---

## 9. Known Gotchas (from Terraform Experience)

These lessons MUST be carried into the Pulumi implementation:

1. **Thunder chart is under `asgardeo`** registry, NOT `openchoreo`
2. **docker-registry uses HTTP repo** (`https://twuni.github.io/docker-registry.helm`), NOT OCI
3. **ClusterDataPlane CRD** uses nested `spec.gateway.ingress.external.{http,https}.{host,port}` structure
4. **Backstage expects lowercase-hyphenated** secret keys (`backend-secret`, not `backendSecret`)
5. **OpenBao dev mode** needs `sleep` after pod Ready for postStart to complete
6. **cluster-gateway-ca**: Must copy from control-plane namespace to data/workflow/observability namespaces
7. **Observability logs/traces**: OpenSearch initialization is slow — need 900s+ timeout
8. **Flux install**: Use latest release YAML from GitHub, wait for 3 deployments before creating resources
9. **Gateway API CRDs**: Must use `--server-side` flag for apply
10. **Thunder needs upstream values**: Must pass `--values <remote-URL>` — can't inline all values

---

## 10. Implementation Order

| Phase | Task                                                | Est. Resources |
|-------|-----------------------------------------------------|----------------|
| 1     | Create `pulumi/` folder with project config         | 3 files        |
| 2     | Implement `config.py` (typed config loader)         | 1 file         |
| 3     | Implement `helpers/` (copy_ca, register_plane, wait)| 4 files        |
| 4     | Implement `values/` (all 6 value builders)          | 6 files        |
| 5     | Implement `components/prerequisites.py`             | 1 file         |
| 6     | Implement `components/openbao_config.py`            | 1 file         |
| 7     | Implement `components/control_plane.py`             | 1 file         |
| 8     | Implement `components/data_plane.py`                | 1 file         |
| 9     | Implement `components/workflow_plane.py`             | 1 file         |
| 10    | Implement `components/observability_plane.py`        | 1 file         |
| 11    | Implement `components/flux_gitops.py`                | 1 file         |
| 12    | Implement `components/link_planes.py`                | 1 file         |
| 13    | Implement `__main__.py` (orchestrator)               | 1 file         |
| 14    | Implement `scripts/bootstrap_k3d.py` (UV script)    | 1 file         |
| 15    | Test: `pulumi preview` then `pulumi up`              | —              |

**Total**: ~25 files, ~50 Pulumi resources

---

## 11. Outputs (Same as Terraform)

```python
pulumi.export("backstage_url", backstage_url)
pulumi.export("api_url", api_url)
pulumi.export("thunder_url", thunder_url)
pulumi.export("argo_workflows_url", f"http://localhost:{config.wp_argo_port}")
pulumi.export("observer_url", observer_url)
pulumi.export("opensearch_dashboards_url", f"http://localhost:{config.opensearch_dashboards_port}")
pulumi.export("data_plane_gateway", dp_http_url)
```
