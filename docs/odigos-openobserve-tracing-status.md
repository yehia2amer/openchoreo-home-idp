# Odigos + OpenObserve Tracing: Diagnosis, Resolution & Pulumi Codification

**Date**: 2026-04-05
**Status**: ✅ RESOLVED — Traces visible in Backstage UI

---

## 1. Goal

End-to-end distributed tracing visible in Backstage UI:
- **Odigos** auto-instruments workloads in `dp-*` namespaces (language-agnostic, zero-config)
- Traces flow: App → Odiglet → Odigos Gateway → OTel Collector → **OpenObserve**
- **Observer** (Backstage backend) queries traces via **tracing-adapter** → OpenObserve
- User sees traces in Backstage → Logs/Traces/Incidents tabs

---

## 2. The Problem

### 2a. Tracing-adapter schema mismatch

The **tracing-adapter-openobserve** queries OpenObserve for field `service_openchoreo_dev_namespace` but traces only contained `service_k8s_namespace_name`. This is because Odigos adds standard k8s resource attributes (like `k8s.namespace.name`), not OpenChoreo-specific ones (like `openchoreo.dev/namespace`).

**Error from tracing-adapter logs:**
```
Search field not found: Schema error: No field named service_openchoreo_dev_namespace.
Valid fields are: default._timestamp, default.end_time, default.operation_name, ...
```

The tracing-adapter needs OpenChoreo labels (`openchoreo.dev/namespace`, `openchoreo.dev/project`, `openchoreo.dev/environment`, `openchoreo.dev/component`) as resource attributes on trace spans. These labels exist on the pods but were not being extracted into OTel resource attributes.

### 2b. Apparent "traces stopped" after adding K8sAttributesResolver

After creating the K8sAttributesResolver action to extract OpenChoreo pod labels, it appeared that traces stopped flowing entirely. Investigation revealed this was a **misdiagnosis** — see Section 4.

---

## 3. Root Cause Analysis

### Why traces appeared to stop (red herring)

The original test app (`trace-test-app`) used Python's **stdlib `http.server.BaseHTTPRequestHandler`**. This module has **NO OpenTelemetry auto-instrumentation library**. OTel Python only auto-instruments frameworks like Flask, Django, FastAPI, requests, urllib3, etc.

The 43 traces that existed before were from:
- `document-svc` (35 spans — Go eBPF)
- `trace-test-app` (6 spans — from earlier session with different app version)
- `collab-svc` (2 spans — Go eBPF)

After the K8sAttributesResolver was added, the odiglet restarted. We were sending traffic to the stdlib test app expecting new Python spans, but **none were generated** because stdlib `http.server` isn't instrumented.

### Proof the pipeline was never broken

A manual trace sent via `curl -X POST /v1/traces` to the odiglet went through the entire pipeline successfully:
- odiglet received it (1 span in receiver metrics)
- loadbalancing exporter sent it to gateway (1 span)
- Arrived in OpenObserve as `manual-test` service

The k8sattributes processor was working correctly all along.

### Real fix: Use an instrumented framework

Replacing the test app with **Flask** immediately produced traces:
- Flask requests → auto-instrumented by `opentelemetry-instrumentation-flask`
- `requests` library calls → auto-instrumented by `opentelemetry-instrumentation-requests` and `opentelemetry-instrumentation-urllib3`
- Rich span metadata including HTTP method, URL, status code, exceptions

---

## 4. What We Did (Chronological)

### Step 1: Created Odigos K8sAttributes Action (ad-hoc kubectl)
Applied a `K8sAttributesResolver` CR to extract OpenChoreo pod labels into trace resource attributes:

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
    - labelKey: "openchoreo.dev/environment"
      attributeKey: "openchoreo.dev/environment"
      from: pod
    - labelKey: "openchoreo.dev/component"
      attributeKey: "openchoreo.dev/component"
      from: pod
    - labelKey: "openchoreo.dev/component-uid"
      attributeKey: "openchoreo.dev/component-uid"
      from: pod
    - labelKey: "openchoreo.dev/environment-uid"
      attributeKey: "openchoreo.dev/environment-uid"
      from: pod
    - labelKey: "openchoreo.dev/project-uid"
      attributeKey: "openchoreo.dev/project-uid"
      from: pod
```

**Result**: Odigos auto-migrated this to the newer `Action` CRD (`odigos.io/v1alpha1/Action`) with `k8sAttributes` spec. The autoscaler reconciled it into a `k8sattributes/odigos-k8sattributes` processor on the odiglet's data-collection pipeline.

> **Note**: Per Odigos docs, the correct CRD going forward is `odigos.io/v1alpha1 Action` with `spec.k8sAttributes`, not the deprecated `actions.odigos.io/v1alpha1 K8sAttributesResolver`.

### Step 2: Investigation of "stopped traces"
- Verified RBAC: odiglet ServiceAccount has full pod list/watch across all namespaces ✅
- Verified pipeline config: k8sattributes processor correctly configured with `passthrough: false`, `pod_association` by resource_attribute (`k8s.pod.name` + `k8s.namespace.name`) ✅
- Verified connectivity: OTLP endpoint reachable from dp namespace ✅
- Verified odiglet metrics: **zero received spans** — the receiver was healthy but nothing was sending
- Sent manual trace via curl: **went through end-to-end** — proved pipeline was NOT broken
- Discovered root cause: stdlib `http.server` has no OTel instrumentation

### Step 3: Replaced test app with Flask
Created a Flask-based trace-test-app that uses auto-instrumentable frameworks:
- Flask for HTTP server (auto-instrumented)
- `requests` library for downstream calls (auto-instrumented)

### Step 4: Verified OpenChoreo labels in OpenObserve
After generating traffic through the Flask app and the Go `document-svc`:

```
✅ service_openchoreo_dev_component: document-svc
✅ service_openchoreo_dev_environment: development
✅ service_openchoreo_dev_namespace: default
✅ service_openchoreo_dev_project: doclet
```

Both Python (Flask via SDK) and Go (eBPF) traces now carry the OpenChoreo labels.

### Step 5: Restarted tracing-adapter
The adapter was caching the schema error. After restart, it successfully connected and queried traces using the `service_openchoreo_dev_namespace` field.

### Step 6: Confirmed in Backstage UI
User confirmed traces are now visible in the Backstage UI.

---

## 5. Final Trace Counts in OpenObserve

| Service | Spans | Source |
|---------|-------|--------|
| document-svc-development-a2c28cff | 40 | Go eBPF |
| trace-test-app | 17 | Python Flask (SDK via Odigos loader) |
| collab-svc-development-aa9896d4 | 2 | Go eBPF |
| manual-test | 1 | Manual curl probe |
| **Total** | **60** | |

---

## 6. What Needs Pulumi Codification

### 6a. ✅ Already in Pulumi
- Odigos namespace + Helm release + Destination CR (`pulumi/components/odigos.py`)
- OpenObserve ExternalSecret + logging/tracing adapters (`pulumi/components/observability_plane.py`)
- OpenBao seeding for openobserve credentials (`pulumi/components/prerequisites.py`)

### 6b. 🔴 Ad-hoc — MUST be codified in Pulumi

| Item | What was done ad-hoc | Pulumi action needed |
|------|---------------------|---------------------|
| **Odigos K8sAttributes Action** | `kubectl apply` of K8sAttributesResolver CR | Add `Action` CR to `pulumi/components/odigos.py` — use the `odigos.io/v1alpha1 Action` kind (not the deprecated `K8sAttributesResolver`) |
| **Odigos Source (namespace-level)** | Created via Odigos auto-detection / CLI | Add `Source` CR to `pulumi/components/odigos.py` targeting `dp-*` namespaces (or make it dynamic via DemoAppBootstrap) |

### 6c. 🟡 Test-only — can be cleaned up

| Item | Notes |
|------|-------|
| **trace-test-app Deployment + Service** | Flask test app in `dp-default-doclet-development-50ce4d9b`. Used for validation. Can be deleted once we confirm real app traces work. |

### 6d. 🟢 One-time ops — no Pulumi needed

| Item | Notes |
|------|-------|
| **tracing-adapter restart** | One-time fix. The adapter only errored because the schema fields didn't exist yet. On a clean deploy, the Action CR will be in place before the adapter starts querying, so the fields will exist from the first trace. |

---

## 7. Correct Odigos Action CRD (for Pulumi)

Per the [Odigos K8sAttributes docs](https://docs.odigos.io/oss/pipeline/actions/attributes/k8sattributes), the canonical format is:

```yaml
apiVersion: odigos.io/v1alpha1
kind: Action
metadata:
  name: openchoreo-labels
  namespace: odigos-system
spec:
  actionName: "Extract OpenChoreo pod labels"
  signals:
    - TRACES
  k8sAttributes:
    labelsAttributes:
      - labelKey: "openchoreo.dev/namespace"
        attributeKey: "openchoreo.dev/namespace"
        from: pod
      - labelKey: "openchoreo.dev/project"
        attributeKey: "openchoreo.dev/project"
        from: pod
      - labelKey: "openchoreo.dev/environment"
        attributeKey: "openchoreo.dev/environment"
        from: pod
      - labelKey: "openchoreo.dev/component"
        attributeKey: "openchoreo.dev/component"
        from: pod
      - labelKey: "openchoreo.dev/component-uid"
        attributeKey: "openchoreo.dev/component-uid"
        from: pod
      - labelKey: "openchoreo.dev/environment-uid"
        attributeKey: "openchoreo.dev/environment-uid"
        from: pod
      - labelKey: "openchoreo.dev/project-uid"
        attributeKey: "openchoreo.dev/project-uid"
        from: pod
```

Key differences from our ad-hoc version:
- Uses `apiVersion: odigos.io/v1alpha1` + `kind: Action` (not deprecated `actions.odigos.io/v1alpha1/K8sAttributesResolver`)
- Spec uses `k8sAttributes.labelsAttributes` (nested under `k8sAttributes`)
- The deprecated `K8sAttributesResolver` is auto-migrated by Odigos but should not be used for new deployments

---

## 8. Full Trace Pipeline (Verified Working)

```
App pods (dp-* namespaces)
  │
  ├─ Python/Node.js/Java/etc (SDK via Odigos loader + LD_PRELOAD)
  │   → OTLP HTTP → odigos-data-collection-local-traffic:4318
  │
  ├─ Go (eBPF probes via odiglet)
  │   → odigosebpf receiver (shared memory FD)
  │
  ▼
odiglet data-collection (node-level collector, DaemonSet)
  processors: [batch, memory_limiter, resource/node-name, resourcedetection,
               k8sattributes/odigos-k8sattributes, odigostrafficmetrics]
  ├─ k8sattributes extracts openchoreo.dev/* pod labels → resource attributes
  exporters: [loadbalancing/traces → odigos-gateway headless]
  │
  ▼
odigos-gateway (cluster-level collector, 2 replicas)
  pipelines: traces/in → traces/default → traces/generic-openobserve-via-collector
  exporter: otlp → opentelemetry-collector.openchoreo-observability-plane:4317
  │
  ▼
OTel Collector (OpenChoreo observability plane)
  processors: [k8sattributes, tail_sampling]
  exporters: [opensearch, otlphttp/openobserve]
  │
  ▼
OpenObserve (openobserve:5080) → traces stream "default"
  ├─ Flattens resource attributes with service_ prefix
  │   e.g., openchoreo.dev/namespace → service_openchoreo_dev_namespace
  │
  ▼
tracing-adapter-openobserve (port 9100)
  ├─ Queries: WHERE service_openchoreo_dev_namespace = 'default'
  │
  ▼
Observer API (port 8080) → Backstage UI
```

---

## 9. Key Learnings

1. **Odigos K8sAttributesResolver is deprecated** — auto-migrated to `odigos.io/v1alpha1 Action` format. Use `Action` kind in Pulumi.
2. **Python stdlib `http.server` is NOT auto-instrumented** — only frameworks (Flask, Django, FastAPI, etc.) have OTel instrumentation. Use Flask for test apps.
3. **Odigos Python instrumentation uses LD_PRELOAD loader** — the `/var/odigos/` directory is mounted via the Odigos device plugin (`instrumentation.odigos.io/generic`). PYTHONPATH is set to include auto-instrumentation sitecustomize.
4. **Go eBPF needs DWARF symbols** — stripped binaries fail with "decoding dwarf section info at offset 0x0: too short".
5. **OpenObserve flattens resource attributes** with `service_` prefix: `openchoreo.dev/namespace` → `service_openchoreo_dev_namespace`.
6. **OpenObserve schema is dynamic** — fields don't exist until the first document containing them is ingested. The tracing-adapter will error until traces with the required fields arrive.
7. **Odigos uses a 3-hop trace pipeline**: odiglet (node) → gateway (cluster) → destination.
8. **The odigos-data-collection ConfigMap is auto-managed** — Odigos autoscaler reconciles it when Actions change.
9. **Manual span probes are invaluable** for debugging — `curl -X POST /v1/traces` with a hand-crafted OTLP JSON payload proves the pipeline works independently of app instrumentation.
10. **kgateway xDS blocks all endpoints if ANY service is unresolvable** — restart kgateway after adding new services.

---

## 10. Files Modified

| File | Change | Status |
|------|--------|--------|
| `pulumi/components/odigos.py` | Odigos Helm + Destination CR + namespace | ✅ In Pulumi |
| `pulumi/config.py` | `odigos_version` config | ✅ In Pulumi |
| `pulumi/__main__.py` | Step 6.5: Odigos | ✅ In Pulumi |
| `pulumi/Pulumi.talos-baremetal.yaml` | `odigos_version: "1.23.0"` | ✅ In Pulumi |
| **K8sAttributes Action CR** | Extracts openchoreo.dev/* pod labels | 🔴 Ad-hoc, needs Pulumi |
| **trace-test-app** | Flask test app in dp namespace | 🟡 Test-only, clean up |

---

## 11. Open Items

| Priority | Item |
|----------|------|
| **P1** | Codify Odigos K8sAttributes Action in `pulumi/components/odigos.py` |
| **P2** | Codify Fluent Bit dual-ship config (bead `fdy`) |
| **P2** | Codify OTel Collector dual-export config (bead `hq6`) |
| **P2** | Phase 4: Remove OpenSearch + cleanup (bead `je5`) |
| **P3** | Clean up trace-test-app from dp namespace |
| **P3** | Rebuild Go demo app without strip flags for full eBPF tracing |
