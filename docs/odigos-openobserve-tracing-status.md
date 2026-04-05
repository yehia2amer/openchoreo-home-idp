# Odigos + OpenObserve Tracing: Current Status & Next Steps

**Date**: 2026-04-05
**Author**: Agent session notes

---

## 1. What We're Trying to Achieve

End-to-end distributed tracing visible in Backstage UI:
- **Odigos** auto-instruments workloads in `dp-*` namespaces (language-agnostic, zero-config)
- Traces flow: App → Odiglet → Odigos Gateway → OTel Collector → **OpenObserve**
- **Observer** (Backstage backend) queries traces via **tracing-adapter** → OpenObserve
- User sees traces in Backstage → Logs/Traces/Incidents tabs

---

## 2. What Works ✅

| Component | Status |
|-----------|--------|
| **Odigos installed** (v1.23.0) | Running in `odigos-system` with privileged PSA labels |
| **Language detection** | Go (document-svc, collab-svc, nats), Python (trace-test-app), nginx (frontend), postgres |
| **Python auto-instrumentation** | Odigos injects OTel SDK via env vars + init container. Confirmed working. |
| **Go eBPF instrumentation** | Partially works — `document-svc` produced 43 real trace spans. `collab-svc` failed (stripped binary, no DWARF). |
| **Odigos Destination** | `openobserve-via-collector` CR sends to `opentelemetry-collector.openchoreo-observability-plane:4317` |
| **OpenObserve traces stream** | Exists with 43 spans (from first batch before K8sAttributesResolver was added) |
| **Observer + tracing-adapter** | Running, but queries fail with schema mismatch |
| **K8sAttributesResolver action** | Created and reconciled — adds `openchoreo.dev/*` pod labels to trace spans on the odiglet node collector |

## 3. The Problem ❌

### 3a. Tracing-adapter schema mismatch (original issue)

The **tracing-adapter-openobserve** queries OpenObserve for field `service_openchoreo_dev_namespace` but traces only contain `service_k8s_namespace_name`. This is because Odigos adds standard k8s resource attributes, not OpenChoreo-specific ones.

**Error from tracing-adapter logs:**
```
Search field not found: Schema error: No field named service_openchoreo_dev_namespace.
Valid fields are: default._timestamp, default.end_time, default.operation_name, 
default.reference_parent_span_id, default.span_id, default.span_kind, default.start_time, default.trace_id.
```

### 3b. New traces stopped arriving after K8sAttributesResolver was added

After creating the `K8sAttributesResolver` action (to extract `openchoreo.dev/*` pod labels):
- Odigos autoscaler reconciled the action and created a `k8sattributes/odigos-k8sattributes` processor
- The processor was added to the **odiglet node collector** (`odigos-data-collection` ConfigMap) traces pipeline
- Both the odiglet data-collection container and odigos-gateway were automatically restarted by Odigos
- **After this point, zero new traces arrived in OpenObserve** despite:
  - The trace-test-app being healthy and serving HTTP 200s
  - The OTLP endpoint being reachable from the app pod
  - No errors in odiglet or gateway logs
  - Gateway receiving 0 spans (confirmed via Prometheus metrics)

The 43 traces from the initial batch (before the action was added) remain in OpenObserve.

---

## 4. What We Tried

### Fix attempt 1: K8sAttributesResolver action
```yaml
apiVersion: actions.odigos.io/v1alpha1
kind: K8sAttributesResolver
metadata:
  name: openchoreo-labels
  namespace: odigos-system
spec:
  actionName: "Extract OpenChoreo pod labels"
  signals: [TRACES]
  labelsAttributes:
    - labelKey: "openchoreo.dev/namespace"
      attributeKey: "openchoreo.dev/namespace"
      from: pod
    - labelKey: "openchoreo.dev/project"
      attributeKey: "openchoreo.dev/project"
      from: pod
    # ... plus component, environment, UIDs
```

**Result**: The action was accepted and reconciled. The odiglet `odigos-data-collection` ConfigMap now includes:
```yaml
k8sattributes/odigos-k8sattributes:
  auth_type: serviceAccount
  extract:
    labels:
      - from: pod
        key: openchoreo.dev/namespace
        tag_name: openchoreo.dev/namespace
      # ... all 7 labels
  filter:
    node_from_env_var: NODE_NAME
  passthrough: false
  pod_association:
    # (uses default - likely client IP)
```

The processor is in the traces pipeline:
```yaml
traces:
  exporters: [loadbalancing/traces]
  processors: [batch, memory_limiter, resource/node-name, resourcedetection, k8sattributes/odigos-k8sattributes, odigostrafficmetrics]
  receivers: [otlp/in, odigosebpf]
```

**But after this change, NO new traces flow through the pipeline.**

### Fix attempt 2: Full restart of odiglet + gateway + trace-test pod
- Deleted odiglet pod (new one created by DaemonSet)
- Rolled out restart of odigos-gateway
- Killed and recreated trace-test-app pod
- Generated 10+ HTTP requests
- Waited 60-90 seconds for batch flush
- **Still 0 new traces in OpenObserve**

### Fix attempt 3: Verified connectivity
- `odigos-data-collection-local-traffic.odigos-system:4318` reachable from dp namespace (HTTP 200 to OTLP endpoint)
- `odigos-gateway` headless service has endpoints
- No errors in any component logs
- kgateway not blocking (no "not responding" warnings)

---

## 5. Root Cause Hypotheses

### Hypothesis A: k8sattributes pod_association issue
The `k8sattributes` processor on the odiglet uses `passthrough: false` which means it tries to correlate spans to pods using the **client IP**. For spans received via the `otlp/in` receiver (from Python apps sending over HTTP), the client IP is the **app pod IP** — this should work since the processor filters by node (`spec.nodeName=talos-c43-5pl`).

But if the pod_association can't match the pod (e.g., the pod just started and isn't in the k8s API cache yet), the processor might **drop the span** or **block the pipeline**.

**Test**: Remove the K8sAttributesResolver action and see if traces flow again.

### Hypothesis B: k8sattributes RBAC issue
The odiglet ServiceAccount might not have permissions to list/watch pods with the new label extraction config. The processor silently fails.

**Test**: Check ClusterRole/ClusterRoleBinding for odiglet.

### Hypothesis C: Loadbalancing exporter stale after config reload
The `loadbalancing/traces` exporter resolves `odigos-gateway.odigos-system` via k8s DNS. After the gateway pods were replaced (rollout restart), the loadbalancer might have cached stale endpoints.

**Test**: Check if odiglet data-collection has any loadbalancing-related error logs.

### Hypothesis D: Pipeline config error
The addition of the `k8sattributes/odigos-k8sattributes` processor might have introduced a config error that causes the OTel collector in the odiglet to silently fail processing spans (no error logs, just drops them).

**Test**: Enable debug logging on odiglet data-collection container.

---

## 6. Recommended Next Steps (Priority Order)

### Step 1: Verify if removing the action fixes trace flow
```bash
kubectl delete k8sattributesresolver openchoreo-labels -n odigos-system
kubectl delete action migrated-legacy-openchoreo-labels -n odigos-system
# Wait for odiglet data-collection to restart
# Generate traffic and check OpenObserve for new traces
```
If traces flow again → the k8sattributes processor is the culprit.

### Step 2: Alternative approach — use Odigos RenameAttribute action
Instead of k8sattributes (which adds a heavy processor), use a lightweight `RenameAttribute` action to copy existing attributes:
- The odiglet already has `k8s.namespace.name` → can we derive `openchoreo.dev/namespace` from it?
- No, because `k8s.namespace.name` = `dp-default-doclet-development-50ce4d9b` while `openchoreo.dev/namespace` = `default`

### Step 3: Alternative approach — add labels via OTel Collector (bypass Odigos processor)
Configure the **existing OpenChoreo OTel Collector** (`opentelemetry-collector` in `openchoreo-observability-plane`) to extract pod labels. It already has a `k8sattributes` processor with `key_regex: (.*)`. The issue is that traces from Odigos gateway arrive with the gateway's pod IP, not the app pod IP.

Fix: Add `pod_association` based on resource attributes:
```yaml
k8sattributes:
  pod_association:
    - sources:
      - from: resource_attribute
        name: k8s.pod.name
    - sources:
      - from: resource_attribute
        name: k8s.namespace.name
```

### Step 4: Alternative approach — send Odigos traces directly to OpenObserve
Skip our OTel Collector entirely. Change the Odigos Destination to send directly to OpenObserve's OTLP endpoint:
```
OTLP_GRPC_ENDPOINT: openobserve:5080
```
This removes one hop but loses the k8sattributes enrichment from our collector.

### Step 5: Debug with verbose logging
If the above doesn't clarify:
```bash
# Enable debug logging on odiglet data-collection
kubectl edit cm odigos-data-collection -n odigos-system
# Change telemetry.logs.level from "info" to "debug"
# Then restart odiglet
```

### Step 6: Fix kgateway restart race condition
**Important operational fix**: After any service changes (new Helm releases, new services), restart kgateway:
```bash
kubectl rollout restart deployment/kgateway -n openchoreo-control-plane
kubectl rollout restart deployment/gateway-default -n openchoreo-control-plane
kubectl rollout restart deployment/gateway-default -n openchoreo-data-plane
kubectl rollout restart deployment/gateway-default -n openchoreo-observability-plane
```

---

## 7. Current Cluster State

### Odigos Resources
```
Namespace: odigos-system
Pods: odiglet (DaemonSet), odigos-gateway (2 replicas), odigos-autoscaler, odigos-instrumentor (2), odigos-scheduler, odigos-ui
CRs: 
  - Destination: openobserve-via-collector (OTLP gRPC to our OTel Collector:4317)
  - Source: doclet-development (namespace-level, dp-default-doclet-development-50ce4d9b)
  - K8sAttributesResolver: openchoreo-labels (extracts 7 openchoreo.dev/* pod labels)
  - Action: migrated-legacy-openchoreo-labels (auto-created from above)
```

### Trace Pipeline Path
```
Python app (OTLP HTTP) ──→ odiglet:4318 (otlp/in receiver)
Go app (eBPF) ──→ odiglet (odigosebpf receiver)
    │
    ▼
odiglet data-collection pipeline:
  receivers: [otlp/in, odigosebpf]
  processors: [batch, memory_limiter, resource/node-name, resourcedetection, 
               k8sattributes/odigos-k8sattributes, odigostrafficmetrics]
  exporters: [loadbalancing/traces]
    │
    ▼
odigos-gateway (loadbalancing via headless service)
  traces/in → traces/default → traces/generic-openobserve-via-collector
  exporter: otlp/generic-openobserve-via-collector
    │
    ▼
OTel Collector (openchoreo-observability-plane:4317)
  processors: [k8sattributes, tail_sampling]
  exporters: [opensearch, otlphttp/openobserve]
    │
    ▼
OpenObserve (openobserve:5080) → traces stream "default"
    │
    ▼
tracing-adapter-openobserve (port 9100) ──→ Observer (port 8080) ──→ Backstage UI
```

### Test App
```
Name: trace-test-app
Namespace: dp-default-doclet-development-50ce4d9b
Language: Python 3.12 (detected by Odigos)
Labels: openchoreo.dev/namespace=default, openchoreo.dev/project=doclet, 
        openchoreo.dev/environment=development, openchoreo.dev/component=trace-test
Purpose: Generates HTTP trace spans for testing the pipeline
Status: Running, serving HTTP 200, Odigos instrumented (OTEL_* env vars injected)
Note: NOT an OpenChoreo managed component — won't appear in Backstage catalog
```

### OpenObserve Traces
```
Stream: default (type: traces)
Records: 43 (all from initial batch before K8sAttributesResolver)
Fields include: trace_id, span_id, operation_name, service_name, 
  service_k8s_namespace_name, service_k8s_deployment_name, etc.
Missing: openchoreo_dev_namespace, openchoreo_dev_project (the fields tracing-adapter needs)
```

---

## 8. Key Learnings

1. **Odigos K8sAttributesResolver is deprecated** — auto-migrated to `odigosv1.Action` format
2. **Odigos Python auto-instrumentation works** — injects via env vars, no init container needed for simple apps
3. **Go eBPF needs DWARF symbols** — stripped binaries fail with "decoding dwarf section info at offset 0x0: too short"
4. **`python3 -c` short-lived commands crash OTel exporter** — `RuntimeError: cannot schedule new futures after interpreter shutdown`
5. **kgateway xDS blocks all endpoints if ANY service is unresolvable** — restart kgateway after adding new services
6. **The odigos-data-collection ConfigMap is auto-managed** — Odigos autoscaler reconciles it when Actions/Processors change
7. **Odigos uses a 3-hop trace pipeline**: odiglet (node) → gateway (cluster) → destination — not a direct export
8. **OpenObserve flattens resource attributes** with `service_` prefix: `k8s.namespace.name` → `service_k8s_namespace_name`

---

## 9. Files Modified This Session (Odigos-related)

| File | Change |
|------|--------|
| `pulumi/components/odigos.py` | **NEW** — Odigos Helm + Destination CR + namespace with privileged PSA |
| `pulumi/config.py` | Added `odigos_version` config |
| `pulumi/__main__.py` | Replaced OTel Operator step 6.5 with Odigos |
| `pulumi/Pulumi.talos-baremetal.yaml` | Added `odigos_version: "1.23.0"` |

Commits: `fad17f9` (pushed to main)

---

## 10. Open Beads

| ID | Title | Priority |
|----|-------|----------|
| `fdy` | Pulumi: Fluent Bit dual-ship config (OpenSearch + OpenObserve outputs) | P2 |
| `hq6` | Pulumi: OTel Collector dual-export config (OpenSearch + OpenObserve) | P2 |
| `je5` | Phase 4: Remove OpenSearch + cleanup | P2 |
| (new needed) | Fix trace pipeline: K8sAttributesResolver blocking spans | P1 |
| (new needed) | Tracing-adapter schema mismatch: needs openchoreo.dev/* fields | P1 |
