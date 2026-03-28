# Plan: Native Pulumi Providers, Cilium, Rich Outputs & Python Libraries

**Date:** 2026-07-02  
**Scope:** Four interrelated improvements to the Pulumi OpenChoreo codebase  
**Status:** PENDING APPROVAL

---

## Table of Contents

1. [Summary of Changes](#1-summary-of-changes)
2. [Task A — Pulumi Native Registry Packages](#2-task-a--pulumi-native-registry-packages)
3. [Task B — Cilium CNI Integration](#3-task-b--cilium-cni-integration)
4. [Task C — Rich Terraform-Style Outputs](#4-task-c--rich-terraform-style-outputs)
5. [Task D — Replace Shell Commands with Python Libraries](#5-task-d--replace-shell-commands-with-python-libraries)
6. [Dependency Changes (pyproject.toml)](#6-dependency-changes-pyprojecttoml)
7. [Migration Strategy & Risk Assessment](#7-migration-strategy--risk-assessment)
8. [Execution Order](#8-execution-order)

---

## 1. Summary of Changes

| Task | Description | Files Changed | New Dependencies |
|------|-------------|---------------|------------------|
| A | Replace eligible Helm charts / commands with Pulumi native providers | 4 files modified, 0 new | `pulumi-kubernetes-cert-manager`, `pulumi-cilium` |
| B | Add optional Cilium CNI installation (Cilium Edition) | 3 files modified, 2 new | `pulumi-cilium` (shared with A) |
| C | Add comprehensive outputs (URLs, usernames, passwords, pod status) | 2 files modified | — |
| D | Replace shell commands with `kubernetes` Python client and `hvac` | 6 files modified, 1 new helper | `kubernetes`, `hvac` |

---

## 2. Task A — Pulumi Native Registry Packages

### Research Results

| Pulumi Package | Version | Could Replace | Verdict | Reason |
|----------------|---------|---------------|---------|--------|
| `pulumi-kubernetes-cert-manager` | v0.2.0 | cert-manager Helm chart in `prerequisites.py` | **YES — adopt** | Strongly-typed `CertManager` resource. Replaces Helm chart with native resource that manages CRDs automatically. |
| `pulumi-cilium` | v0.2.1 | (new — no current equivalent) | **YES — adopt** | `cilium.Install` resource. Needed for Task B (Cilium Edition). |
| `pulumi-vault` | v7.7.0 | `kubectl exec openbao-0 -- bao kv put` in `prerequisites.py` | **NO — use `hvac` instead** | Pulumi Vault provider needs a reachable Vault API URL from the Pulumi host. OpenBao runs inside k3d — requires port-forward or NodePort. The `hvac` Python library (Task D) achieves the same via `kubectl port-forward` in a cleaner way. |
| `pulumi-flux` | v1.0.1 | Flux install + GitRepository / Kustomizations in `flux_gitops.py` | **NO — keep current approach** | `FluxBootstrapGit` creates commits in the Git repo (writes a `flux-system/` directory). Our current approach only installs Flux manifests and creates GitRepository/Kustomization CRs, which is lighter and doesn't require Git write access. |
| `pulumi-opensearch` | v2.3.1 | OpenSearch sub-charts in `observability_plane.py` | **NO — not applicable** | This provider *manages* OpenSearch resources (index templates, roles, etc.) — it doesn't *install* OpenSearch. We install OpenSearch via the observability Helm sub-charts. No OpenSearch configuration to manage post-install. |
| `pulumi-kubernetes-coredns` | v0.1.0 | CoreDNS ConfigMap rewrite in `prerequisites.py` | **NO — overkill** | We apply a single ConfigMap from a remote URL. The CoreDNS Pulumi component deploys an entire CoreDNS chart. Our current `ConfigGroup` is more appropriate. |

### Adopted Changes

#### A1. Replace cert-manager Helm chart with `pulumi-kubernetes-cert-manager`

**File:** `components/prerequisites.py`

**Before (current):**
```python
cert_manager = k8s.helm.v4.Chart(
    "cert-manager",
    chart=CERT_MANAGER_CHART_REPO + "/cert-manager",
    version=cfg.cert_manager_version,
    namespace="cert-manager",
    values={"crds": {"enabled": True}},
    opts=pulumi.ResourceOptions(depends_on=[cert_manager_ns]),
)
```

**After (proposed):**
```python
from pulumi_kubernetes_cert_manager import CertManager

cert_manager = CertManager(
    "cert-manager",
    install_crds=True,
    helm_options=CertManagerHelmOptionsArgs(
        namespace="cert-manager",
        version=cfg.cert_manager_version,
    ),
    opts=pulumi.ResourceOptions(depends_on=[cert_manager_ns]),
)
```

**Benefits:**
- Strongly-typed Python class with IDE autocompletion for all cert-manager options
- CRD lifecycle managed natively (no `values={"crds": {"enabled": True}}` workaround)
- Upgrade path: cert-manager-specific config changes surfaced as type errors at dev time

---

## 3. Task B — Cilium CNI Integration

### Background

The official OpenChoreo k3d config (`config.yaml`) uses the default k3s CNI (Flannel) and does **not** install Cilium. OpenChoreo supports two editions:

- **Cilium Edition:** Full Zero Trust security with eBPF-based network policies, traffic encryption, mTLS. Supports ALL add-on modules including governance.
- **Generic CNI Edition:** Basic Kubernetes networking (Flannel, Calico, etc.). Limited observability, no governance support.

Currently we deploy the **Generic CNI Edition**. This task adds **optional** Cilium support, gated by a config flag.

### k3d Requirements for Cilium

To use Cilium on k3d, the cluster must be created with Flannel disabled:

```yaml
# k3d config.yaml additions
options:
  k3s:
    extraArgs:
      - arg: "--flannel-backend=none"
        nodeFilters: [server:*]
      - arg: "--disable-network-policy"
        nodeFilters: [server:*]
```

> **IMPORTANT:** This means existing clusters using Flannel cannot switch to Cilium without recreation. The bootstrap script must be updated to conditionally add these flags.

### Implementation Plan

#### B1. New config flag: `enable_cilium`

**File:** `config.py`

Add:
```python
# In OpenChoreoConfig dataclass
enable_cilium: bool

# In load_config()
enable_cilium = cfg.get_bool("enable_cilium") or False
```

#### B2. New component: `components/cilium.py`

```python
"""Cilium CNI — optional, installed before all other components."""
import pulumi
import pulumi_cilium as cilium

def deploy(cfg, k8s_provider):
    provider = cilium.Provider("cilium-provider", kubernetes=cilium.ProviderKubernetesArgs(
        config_path=cfg.kubeconfig_path,
        config_context=cfg.kubeconfig_context,
    ))
    
    install = cilium.Install("cilium", values={
        "hubble": {
            "relay": {"enabled": True},
            "ui": {"enabled": True},
        },
        "operator": {"replicas": 1},  # k3d: single node
    }, opts=pulumi.ResourceOptions(provider=provider))
    
    return install
```

#### B3. Orchestration update

**File:** `__main__.py`

```python
# Before prerequisites
cilium_install = None
if cfg.enable_cilium:
    from components import cilium
    cilium_install = cilium.deploy(cfg, k8s_provider)

# Prerequisites now depend on Cilium (if enabled)
prereq_depends = [cilium_install] if cilium_install else []
prereqs = prerequisites.deploy(cfg, k8s_provider, extra_depends=prereq_depends)
```

#### B4. Bootstrap script update

**File:** `scripts/bootstrap_k3d.py`

When `enable_cilium` is set, the downloaded k3d config will be patched to add `--flannel-backend=none` and `--disable-network-policy` to the k3s extraArgs before cluster creation.

> **NOTE:** Cilium adds ~200 MB of images and takes ~60-90s extra to initialize. Timeout constants should account for this.

---

## 4. Task C — Rich Terraform-Style Outputs

### Current Outputs (7)

```python
pulumi.export("backstage_url", ...)
pulumi.export("api_url", ...)
pulumi.export("thunder_url", ...)
pulumi.export("argo_workflows_url", ...)
pulumi.export("observer_url", ...)
pulumi.export("opensearch_dashboards_url", ...)
pulumi.export("data_plane_gateway", ...)
```

### Proposed Outputs (~20)

**File:** `__main__.py`

```python
# ─── URLs ───
pulumi.export("backstage_url", cfg.backstage_url)
pulumi.export("api_url", cfg.api_url)
pulumi.export("thunder_url", cfg.thunder_url)
pulumi.export("argo_workflows_url", f"http://localhost:{cfg.wp_argo_port}")
pulumi.export("observer_url", cfg.observer_url)
pulumi.export("opensearch_dashboards_url", f"http://localhost:{cfg.opensearch_dashboards_port}")
pulumi.export("data_plane_gateway_http", cfg.dp_http_url)
pulumi.export("data_plane_gateway_https", cfg.dp_https_url)

# ─── Credentials ───
pulumi.export("opensearch_username", cfg.opensearch_username)
pulumi.export("opensearch_password", pulumi.Output.secret(cfg.opensearch_password))
pulumi.export("openbao_root_token", pulumi.Output.secret(cfg.openbao_root_token))

# ─── Cluster Info ───
pulumi.export("kubeconfig_context", cfg.kubeconfig_context)
pulumi.export("domain_base", cfg.domain_base)
pulumi.export("openchoreo_version", cfg.openchoreo_version)
pulumi.export("edition", "cilium" if cfg.enable_cilium else "generic-cni")

# ─── Feature Flags ───
pulumi.export("cilium_enabled", cfg.enable_cilium)
pulumi.export("flux_enabled", cfg.enable_flux)
pulumi.export("observability_enabled", cfg.enable_observability)

# ─── Namespaces ───
pulumi.export("namespaces", {
    "control_plane": NS_CONTROL_PLANE,
    "data_plane": NS_DATA_PLANE,
    "workflow_plane": NS_WORKFLOW_PLANE,
    "observability_plane": NS_OBSERVABILITY_PLANE,
})
```

Sensitive values (passwords, tokens) will be wrapped in `pulumi.Output.secret()` so they're masked in `pulumi stack output` by default but accessible with `--show-secrets`.

### Bootstrap Script Output Update

**File:** `scripts/bootstrap_k3d.py`

After `pulumi up`, display a summary table:

```
╔══════════════════════════════════════════════════════════════╗
║                 OpenChoreo v1.0.0 — Deployed                ║
╠══════════════════════════════════════════════════════════════╣
║ Backstage UI     │ http://openchoreo.localhost:8080          ║
║ API              │ http://api.openchoreo.localhost:8080      ║
║ Thunder (IdP)    │ http://thunder.openchoreo.localhost:8080  ║
║ Argo Workflows   │ http://localhost:10081                    ║
║ Observer API     │ http://observer.openchoreo.localhost:11080║
║ OpenSearch       │ http://localhost:11081                    ║
║ Data Plane GW    │ http://openchoreo.localhost:19080         ║
╠══════════════════════════════════════════════════════════════╣
║ OpenSearch User  │ admin                                     ║
║ OpenSearch Pass  │ ******* (pulumi stack output --show-se..) ║
║ OpenBao Token    │ ******* (pulumi stack output --show-se..) ║
║ Edition          │ generic-cni                               ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 5. Task D — Replace Shell Commands with Python Libraries

### Priority Ranking

| Priority | Shell Command | Current Location | Replacement | New Library |
|----------|--------------|------------------|-------------|-------------|
| **P0** | `kubectl exec openbao-0 -- bao kv put` | `prerequisites.py` | `hvac` Python library (Vault/OpenBao client) | `hvac` |
| **P1** | `kubectl get secret ... \| base64 -d && kubectl create configmap` | `helpers/copy_ca.py` (called 3×) | `kubernetes` Python client: `read_namespaced_secret()` + `create/patch_namespaced_config_map()` | `kubernetes` |
| **P2** | `kubectl get secret ... \| base64 -d` + heredoc YAML + `kubectl apply -f -` | `helpers/register_plane.py` (called 3×) | `kubernetes` client: `read_namespaced_secret()` + `create_cluster_custom_object()` | `kubernetes` |
| **P3** | `kubectl patch clusterdataplane ... && kubectl patch clusterworkflowplane ...` | `components/link_planes.py` | `kubernetes` client: `patch_cluster_custom_object()` × 2 | `kubernetes` |
| **P4** | `kubectl label namespace ...` | `components/control_plane.py` | `kubernetes` client: `patch_namespace()` | `kubernetes` |
| **P5** | `kubectl wait pod/openbao-0`, `kubectl wait secret/...`, `kubectl wait deployment/...` | `prerequisites.py`, `register_plane.py`, `flux_gitops.py` | `kubernetes` client with watch/poll loop | `kubernetes` |
| skip | `sleep N` | `helpers/wait.py` | Keep as-is — harmless and portable | — |
| skip | `docker exec` (machine-id) | `observability_plane.py` | Keep as-is — k3d-only edge case, one-shot | — |
| skip | All `subprocess.run` in bootstrap | `scripts/bootstrap_k3d.py` | Keep as-is — k3d/pulumi CLIs have no Python SDK | — |

### Implementation Details

#### D-P0: OpenBao secrets via `hvac` (security improvement)

**Current (insecure):** Root token appears in `pulumi_command.local.Command` shell string — visible in Pulumi state and process lists.

**File:** `components/prerequisites.py` → new helper `helpers/openbao_secrets.py`

```python
"""Store secrets in OpenBao using the hvac Python library."""
import hvac

def store_secrets(openbao_addr: str, root_token: str, github_pat: str) -> None:
    client = hvac.Client(url=openbao_addr, token=root_token)
    client.secrets.kv.v2.create_or_update_secret(
        path="git-token",
        secret={"token": github_pat},
        mount_point="secret",
    )
    client.secrets.kv.v2.create_or_update_secret(
        path="gitops-token",
        secret={"token": github_pat},
        mount_point="secret",
    )
```

**Challenge:** OpenBao runs inside k3d (no host-accessible endpoint by default). Two options:
1. **Option A (recommended):** Use `kubectl port-forward` via `subprocess` in a context manager, then call `hvac` against `localhost:8200`. This is still cleaner than `kubectl exec` because the token isn't passed as a shell argument.
2. **Option B:** Create a NodePort Service for OpenBao in the Pulumi stack. Adds a resource but makes OpenBao accessible from the host.

**Recommendation:** Option A — port-forward wrapper.

#### D-P1: `copy_ca` → Kubernetes Python client

**File:** `helpers/copy_ca.py` (complete rewrite)

**Before (shell):** `kubectl get secret ... | base64 -d && kubectl create configmap ...`

**After (Python):**
```python
"""Copy cluster-gateway-ca certificate to a target namespace."""
from kubernetes import client as k8s_client, config as k8s_config

def copy_ca(kubeconfig_path: str, kubeconfig_context: str,
            source_ns: str, target_ns: str, secret_name: str, configmap_name: str) -> None:
    k8s_config.load_kube_config(config_file=kubeconfig_path, context=kubeconfig_context)
    v1 = k8s_client.CoreV1Api()

    # Read source secret
    secret = v1.read_namespaced_secret(secret_name, source_ns)
    ca_crt = base64.b64decode(secret.data["ca.crt"]).decode()

    # Create or update configmap in target namespace
    cm = k8s_client.V1ConfigMap(
        metadata=k8s_client.V1ObjectMeta(name=configmap_name, namespace=target_ns),
        data={"ca.crt": ca_crt},
    )
    try:
        v1.create_namespaced_config_map(target_ns, cm)
    except k8s_client.ApiException as e:
        if e.status == 409:
            v1.patch_namespaced_config_map(configmap_name, target_ns, cm)
        else:
            raise
```

This will be wrapped in a Pulumi dynamic provider to integrate with the resource graph.

#### D-P2: `register_plane` → Kubernetes Python client

**File:** `helpers/register_plane.py` (complete rewrite)

**Before (shell):** Complex heredoc + awk + `kubectl apply -f -` (the BSD sed workaround)

**After (Python):**
```python
"""Register a plane (Data/Workflow/Observability) as a cluster custom resource."""
from kubernetes import client as k8s_client

def register_plane(kubeconfig_path, kubeconfig_context,
                   plane_ns, kind, name, spec_body) -> None:
    k8s_config.load_kube_config(...)
    custom = k8s_client.CustomObjectsApi()
    v1 = k8s_client.CoreV1Api()

    # Read agent TLS CA
    secret = v1.read_namespaced_secret("cluster-agent-tls", plane_ns)
    ca_crt = base64.b64decode(secret.data["ca.crt"]).decode()

    # Build custom resource body (pure Python dict — no sed/awk/heredoc)
    body = {
        "apiVersion": "openchoreo.dev/v1alpha1",
        "kind": kind,
        "metadata": {"name": name},
        "spec": {**spec_body, "clusterAgent": {"clientCA": {"value": ca_crt}}},
    }
    
    # Apply (create or patch)
    try:
        custom.create_cluster_custom_object("openchoreo.dev", "v1alpha1", plural, body)
    except k8s_client.ApiException as e:
        if e.status == 409:
            custom.patch_cluster_custom_object("openchoreo.dev", "v1alpha1", plural, name, body)
        else:
            raise
```

**Benefits:** Eliminates the fragile heredoc+awk approach, cross-platform by default, no BSD vs GNU tool differences.

#### D-P3: `link_planes` → Kubernetes Python client

**File:** `components/link_planes.py` (rewrite)

Replace `kubectl patch` commands with two `patch_cluster_custom_object()` calls.

#### D-P4: Namespace labeling → Kubernetes Python client

**File:** `components/control_plane.py`

Replace `kubectl label namespace` command with `patch_namespace()`.

#### D-P5: `kubectl wait` commands → Kubernetes watch/poll

**Files:** `prerequisites.py`, `register_plane.py`, `flux_gitops.py`

Replace `kubectl wait` with polling loops using the `kubernetes` Python client's watch API. All wrapped in a reusable helper:

```python
def wait_for_condition(api_func, name, namespace, condition, timeout):
    """Poll a Kubernetes resource until a condition is met."""
    ...
```

### Pulumi Dynamic Providers

The Python library calls (P0–P5) run **imperative** code but need to participate in Pulumi's **declarative** resource graph. We'll create **Pulumi dynamic providers** for:

1. `CopyCAProvider` — wraps `copy_ca()` as a Pulumi resource with proper create/delete/diff
2. `RegisterPlaneProvider` — wraps `register_plane()` 
3. `OpenBaoSecretsProvider` — wraps `store_secrets()`
4. `LinkPlanesProvider` — wraps the two patch calls
5. `WaitProvider` — wraps `wait_for_condition()`

Dynamic providers give us:
- Proper dependency tracking (other resources can `depends_on` them)
- Idempotent create/update/delete lifecycle
- State tracking in Pulumi state file
- No `pulumi_command` dependency for these operations

---

## 6. Dependency Changes (pyproject.toml)

### New Dependencies

```toml
dependencies = [
    "pulumi>=3.0.0,<4.0.0",
    "pulumi-kubernetes>=4.0.0,<5.0.0",
    "pulumi-command>=1.0.0,<2.0.0",       # still needed for: sleep, docker exec
    "pulumi-kubernetes-cert-manager>=0.2.0",  # NEW — Task A
    "pulumi-cilium>=0.2.0",                   # NEW — Task B
    "pyyaml>=6.0",
    "kubernetes>=31.0.0",                     # NEW — Task D (k8s Python client)
    "hvac>=2.3.0",                            # NEW — Task D-P0 (OpenBao/Vault client)
]
```

### Removed Dependencies (eventually)

Once all P0–P5 replacements are done, `pulumi-command` usage drops from 13 invocations to 2 (sleep + docker exec). It cannot be fully removed yet.

---

## 7. Migration Strategy & Risk Assessment

### Strategy: Incremental In-Place Replacement

Each task can be merged independently. Recommended order minimizes risk:

1. **Task C (Outputs)** — Pure additive, zero risk. No existing behavior changes.
2. **Task A (cert-manager native)** — Single chart replacement. Easy rollback (revert to Helm chart).
3. **Task D (Python libraries)** — Replace shell commands one at a time. Each replacement is independently testable.
4. **Task B (Cilium)** — New optional feature behind `enable_cilium` flag. Requires cluster recreation for existing setups.

### Risk Matrix

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Cilium + k3d incompatibility | High | Low | Cilium on k3d is well-documented. Test with `cilium status` and `cilium connectivity test`. |
| `hvac` library can't reach OpenBao | Medium | Medium | Use port-forward wrapper. Fallback: keep `kubectl exec` command. |
| Dynamic providers add complexity | Medium | Low | Each provider is small (<50 lines). Well-tested pattern in Pulumi Python. |
| `pulumi-kubernetes-cert-manager` version lag | Low | Low | Falls back to underlying Helm chart. Can pin version. |
| Existing Pulumi state drift on upgrade | Medium | Medium | Run `pulumi preview` before `pulumi up`. The state migration from Helm chart → native resource will show as delete+create for cert-manager. |

### State Migration Note

Replacing the cert-manager Helm chart with the native `CertManager` resource will cause Pulumi to:
1. **Delete** the old `k8s.helm.v4.Chart("cert-manager")` resource
2. **Create** the new `CertManager("cert-manager")` resource

This means cert-manager will be briefly uninstalled and reinstalled. Since cert-manager CRDs and certs persist (CRDs are not deleted on Helm uninstall by default), this should be safe. However, for existing clusters, it's recommended to run this during a maintenance window.

---

## 8. Execution Order

```
Phase 1 — Zero Risk (additive only)
  ├── Task C: Add rich outputs to __main__.py
  └── Task C: Update bootstrap_k3d.py summary table

Phase 2 — Low Risk (single chart swap)
  ├── Task A1: Add pulumi-kubernetes-cert-manager to pyproject.toml
  └── Task A1: Replace cert-manager Helm chart in prerequisites.py

Phase 3 — Medium Risk (shell → Python, one at a time)
  ├── Task D-P0: OpenBao secrets via hvac (helpers/openbao_secrets.py)
  ├── Task D-P1: copy_ca rewrite (helpers/copy_ca.py)
  ├── Task D-P2: register_plane rewrite (helpers/register_plane.py)
  ├── Task D-P3: link_planes rewrite (components/link_planes.py)
  ├── Task D-P4: namespace label → patch_namespace (components/control_plane.py)
  └── Task D-P5: kubectl wait → k8s watch/poll (shared helper)

Phase 4 — New Feature (optional, behind flag)
  ├── Task B1: Add enable_cilium config flag
  ├── Task B2: Create components/cilium.py
  ├── Task B3: Update __main__.py orchestration
  └── Task B4: Update bootstrap_k3d.py for Cilium k3d config
```

### Full Test

After all phases:
1. Delete k3d cluster: `k3d cluster delete openchoreo`
2. Re-run bootstrap: `uv run scripts/bootstrap_k3d.py`
3. Verify: all 42+ pods Running, all URLs responding, `pulumi stack output` shows all outputs
4. Optionally: recreate with `enable_cilium=true` and verify Cilium pods + `cilium status`

---

**AWAITING APPROVAL — no code changes will be made until this plan is approved.**
