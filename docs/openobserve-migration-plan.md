# OpenSearch → OpenObserve Migration Plan

**Date**: 2026-04-05  
**Cluster**: Talos Baremetal (single-node, `192.168.0.100:6443`)  
**Namespace**: `openchoreo-observability-plane`

---

## Current State

| Component | Role | Resources | Storage |
|-----------|------|-----------|---------|
| `opensearch-master-0` | Logs + Traces backend | 1 CPU req, 100Mi mem req | 8Gi PVC |
| `opensearch-setup-logs` | Index/pipeline init (completed Job) | — | — |
| `opensearch-setup-tracing` | Index/pipeline init (completed Job) | — | — |
| `observer` | API server (Backstage → OpenSearch) | 100m/200m CPU, 128Mi/200Mi mem | — |
| Fluent Bit (DaemonSet) | Log shipper → OpenSearch | Part of observability-plane chart | — |
| OTel Collector | Trace shipper → OpenSearch | Part of observability-plane chart | — |

**Observer currently connects directly to OpenSearch** via:
- `OPENSEARCH_ADDRESS=https://opensearch:9200`
- `OPENSEARCH_USERNAME` / `OPENSEARCH_PASSWORD` from `observer-secret`

**Observer adapter system** exists but is disabled:
- `LOGS_ADAPTER_ENABLED=false` (URL: `http://logs-adapter:9098`)
- `TRACING_ADAPTER_ENABLED=false` (URL: `http://tracing-adapter:9100`)

---

## Target State

| Component | Role | Chart |
|-----------|------|-------|
| **OpenObserve** (standalone) | Unified logs + traces backend | `openobserve-standalone` (bundled in both modules) |
| **Fluent Bit** (new config) | Log shipper → OpenObserve | Bundled in `observability-logs-openobserve` |
| **OTel Collector** (new config) | Trace shipper → OpenObserve | Bundled in `observability-tracing-openobserve` |
| **logs-adapter** | Translates Observer queries → OpenObserve API | `observability-logs-openobserve` adapter |
| **tracing-adapter** | Translates Observer queries → OpenObserve API | `observability-tracing-openobserve` adapter |
| **Observer** | API server with adapters enabled | Same chart, new Helm values |

**Key insight**: Observer doesn't query OpenObserve directly. Instead, the adapter services translate Observer's query protocol into OpenObserve's API. Observer just needs `logsAdapter.enabled=true` and `tracingAdapter.enabled=true`.

---

## Migration Strategy: Parallel Deploy, Then Switch

```
Phase 1: Deploy OpenObserve + Adapters (OpenSearch stays running)
Phase 2: Enable Observer adapters (switch reads to OpenObserve)
Phase 3: Validate everything works via Backstage UI
Phase 4: Remove OpenSearch (cleanup)
```

### Why parallel?
- Single-node cluster — we can't afford downtime
- Both modules install their own OpenObserve standalone, but we use ONE shared instance
- The logging module installs first (includes OpenObserve standalone)
- The tracing module reuses the same OpenObserve by disabling its bundled standalone

---

## Phase 1: Deploy OpenObserve + Modules

### Step 1.1: Store OpenObserve credentials in OpenBao

```bash
kubectl exec -it -n openbao openbao-0 -- \
    bao kv put secret/openobserve-admin-credentials \
    ZO_ROOT_USER_EMAIL='admin@openchoreo.local' \
    ZO_ROOT_USER_PASSWORD='<generate-secure-password>'
```

### Step 1.2: Create ExternalSecret for OpenObserve credentials

```yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: openobserve-admin-credentials
  namespace: openchoreo-observability-plane
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: default
  target:
    name: openobserve-admin-credentials
  data:
    - secretKey: ZO_ROOT_USER_EMAIL
      remoteRef:
        key: openobserve-admin-credentials
        property: ZO_ROOT_USER_EMAIL
    - secretKey: ZO_ROOT_USER_PASSWORD
      remoteRef:
        key: openobserve-admin-credentials
        property: ZO_ROOT_USER_PASSWORD
```

### Step 1.3: Install Logging Module (includes OpenObserve standalone)

```bash
helm upgrade --install observability-logs-openobserve \
  oci://ghcr.io/openchoreo/helm-charts/observability-logs-openobserve \
  --namespace openchoreo-observability-plane \
  --version 0.4.2 \
  --set openobserve-standalone.persistence.size=10Gi \
  --set openobserve-standalone.resources.requests.memory=500Mi \
  --set openobserve-standalone.resources.limits.memory=1000Mi \
  --set openobserve-standalone.resources.limits.cpu=500m
```

This deploys:
- **OpenObserve standalone** (`openobserve` pod, port 5080)
- **Fluent Bit** DaemonSet (ships logs to OpenObserve)
- **logs-adapter** (translates Observer queries → OpenObserve, port 9098)
- **openObserveSetup** Job (creates indexes/streams)

### Step 1.4: Install Tracing Module (reuses existing OpenObserve)

```bash
helm upgrade --install observability-tracing-openobserve \
  oci://ghcr.io/openchoreo/helm-charts/observability-tracing-openobserve \
  --namespace openchoreo-observability-plane \
  --version 0.2.1 \
  --set openobserve-standalone.enabled=false
```

**Critical**: `openobserve-standalone.enabled=false` avoids a second OpenObserve instance conflicting with the one from the logging module.

This deploys:
- **OTel Collector** (ships traces to OpenObserve, port 4317/4318)
- **tracing-adapter** (translates Observer queries → OpenObserve, port 9100)

### Step 1.5: Validate OpenObserve is receiving data

```bash
# Check OpenObserve pod is running
kubectl get pods -n openchoreo-observability-plane -l app.kubernetes.io/name=openobserve

# Check logs-adapter is running
kubectl get pods -n openchoreo-observability-plane | grep logs-adapter

# Check tracing-adapter is running
kubectl get pods -n openchoreo-observability-plane | grep tracing-adapter

# Check Fluent Bit is running
kubectl get pods -n openchoreo-observability-plane | grep fluent-bit

# Check OTel Collector is running
kubectl get pods -n openchoreo-observability-plane | grep opentelemetry

# Port-forward OpenObserve UI to verify data ingestion
kubectl port-forward svc/openobserve -n openchoreo-observability-plane 5080:5080
# Visit http://localhost:5080 and log in
```

---

## Phase 2: Switch Observer to Use Adapters

### Step 2.1: Update Observer Helm values

```bash
helm upgrade openchoreo-observability-plane-9d9acc01 \
  -n openchoreo-observability-plane \
  --reuse-values \
  --set observer.logsAdapter.enabled=true \
  --set observer.logsAdapter.url=http://logs-adapter:9098 \
  --set observer.tracingAdapter.enabled=true \
  --set observer.tracingAdapter.url=http://tracing-adapter:9100 \
  oci://ghcr.io/openchoreo/helm-charts/openchoreo-observability-plane \
  --version 1.0.0
```

### Step 2.2: Verify Observer logs show adapter usage

```bash
kubectl logs -n openchoreo-observability-plane deploy/observer --tail=20
# Should show:
# "Using logs adapter" instead of "Using OpenSearch for component logs"
# "Using tracing adapter" instead of "Using OpenSearch for traces"
```

---

## Phase 3: Validate via Backstage UI

1. Open Backstage → navigate to a component
2. Check **Logs** tab → should show logs from OpenObserve via adapter
3. Check **Traces** tab → should show traces from OpenObserve via adapter
4. Check **Incidents** tab → should still work (uses Prometheus, not affected)
5. Run the same curl test that previously failed:
   ```bash
   curl -k 'https://observer.openchoreo.local:11085/api/v1/logs/query?...'
   ```

---

## Phase 4: Remove OpenSearch (after validation)

### Step 4.1: Remove OpenSearch from Helm values

Update Pulumi to disable OpenSearch in the observability plane chart:
```python
# In pulumi/values/observability_plane.py
"opensearch": {"enabled": False}
```

### Step 4.2: Clean up OpenSearch resources

```bash
# Delete completed setup jobs
kubectl delete job opensearch-setup-logs opensearch-setup-tracing -n openchoreo-observability-plane

# OpenSearch StatefulSet will be removed by Helm
# PVC will be retained (manual cleanup):
kubectl delete pvc opensearch-master-opensearch-master-0 -n openchoreo-observability-plane
```

### Step 4.3: Remove OpenSearch credentials

```bash
# Remove from OpenBao
kubectl exec -it -n openbao openbao-0 -- bao kv delete secret/opensearch-username
kubectl exec -it -n openbao openbao-0 -- bao kv delete secret/opensearch-password

# Remove ExternalSecrets
kubectl delete externalsecret opensearch-admin-credentials observer-opensearch-credentials \
  -n openchoreo-observability-plane
```

### Step 4.4: Clean up Observer env vars

Remove `OPENSEARCH_ADDRESS`, `OPENSEARCH_USERNAME`, `OPENSEARCH_PASSWORD` from extraEnvs and observer-secret (no longer needed when adapters are the data source).

---

## Pulumi Implementation Plan

All of the above will be codified in Pulumi:

| File | Changes |
|------|---------|
| `pulumi/config.py` | Add `enable_openobserve: bool`, `openobserve_admin_email: str`, `openobserve_admin_password: str` (encrypted) |
| `pulumi/components/observability_plane.py` | Add OpenObserve credential ExternalSecret, install logging + tracing modules as Helm releases |
| `pulumi/values/observability_plane.py` | Add `logsAdapter.enabled`, `tracingAdapter.enabled`, `logsAdapter.url`, `tracingAdapter.url` when OpenObserve is enabled |
| `pulumi/values/openobserve_logging.py` (new) | Values for `observability-logs-openobserve` chart |
| `pulumi/values/openobserve_tracing.py` (new) | Values for `observability-tracing-openobserve` chart |
| `pulumi/Pulumi.talos-baremetal.yaml` | Set `enable_openobserve: true`, encrypted credentials |

### Dependency chain:
```
OpenBao secrets → ExternalSecret → openobserve-admin-credentials Secret
  → Logging module Helm release (installs OpenObserve + Fluent Bit + logs-adapter)
    → Tracing module Helm release (installs OTel Collector + tracing-adapter, no OpenObserve)
      → Observer Helm upgrade (enable adapters)
```

---

## Resource Impact (Single-Node Baremetal)

| Component | CPU req | Memory req | Storage |
|-----------|---------|------------|---------|
| OpenObserve standalone | 20m | 500Mi | 10Gi PVC |
| Fluent Bit (DaemonSet) | 25m | 125Mi | hostPath |
| OTel Collector | 50m | 100Mi | — |
| logs-adapter | 50m | 128Mi | — |
| tracing-adapter | 50m | 128Mi | — |
| **Total new** | **195m** | **981Mi** | **10Gi** |
| **OpenSearch removed** | **-1000m** | **-100Mi** | **-8Gi** |
| **Net change** | **-805m CPU** | **+881Mi mem** | **+2Gi** |

> **Note**: OpenSearch requested 1 full CPU but only 100Mi memory (likely underprovisioned). OpenObserve uses more memory but far less CPU. Net effect is positive for a CPU-constrained single node.

---

## Rollback Plan

If OpenObserve doesn't work:
1. Disable adapters: `observer.logsAdapter.enabled=false`, `observer.tracingAdapter.enabled=false`
2. Observer falls back to direct OpenSearch (still running in parallel)
3. Uninstall module charts:
   ```bash
   helm uninstall observability-tracing-openobserve -n openchoreo-observability-plane
   helm uninstall observability-logs-openobserve -n openchoreo-observability-plane
   ```

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Two Fluent Bit DaemonSets (old from obs-plane + new from logging module) | Check if obs-plane chart has a `fluent-bit.enabled` toggle; disable the old one |
| Two OTel Collectors competing | Same — check if obs-plane chart bundles one we need to disable |
| OpenObserve + OpenSearch both using disk on single node | Temporary during parallel phase; clean up in Phase 4 |
| Adapter services not matching Observer's query format | Adapters are built by OpenChoreo team specifically for this; should work |
| Memory pressure on single node | Monitor with `kubectl top nodes` after deployment |
