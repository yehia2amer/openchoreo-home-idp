# ADR-007: GCP Observability — Cloud-Native Smart-Split Strategy

**Status**: Accepted  
**Date**: 2026-04-16  
**Deciders**: Yehia Amer  
**Context**: GCP platform epic requires an observability stack that satisfies both GCP-native cost/ops efficiency and Backstage Observer UI compatibility

---

## Context

The GCP platform deployment needs observability (metrics, logs, traces) that works with the existing OpenChoreo Backstage Observer UI. GKE clusters already include Cloud Logging and Cloud Monitoring at the cluster level, and GCP Managed Prometheus is available as a zero-ops metrics backend. However, the Backstage Observer plugin only supports three adapter types: OpenObserve, OpenSearch, and Prometheus. No GCP-native adapters exist.

### The Problem

| Symptom | Impact |
|---------|--------|
| Backstage Observer has no GCP Cloud Trace or Cloud Logging adapter | Sending all telemetry to GCP-native services breaks the Backstage UI |
| Self-hosted Prometheus on GCP duplicates what GKE already provides for free | Unnecessary operational overhead and cost |
| A single OTel Collector destination forces a choice between GCP-native and Backstage-compatible | Either the UI breaks or GCP-native services go unused |
| Odigos supports multiple Destination CRs per signal type | Fan-out to multiple backends is possible without a custom collector |

### Constraints

- **No new Observer adapter implementations** — the upstream OpenChoreo Backstage plugin is not modified
- **No modifications to upstream OpenChoreo Helm charts** — all changes are additive, in the gitops layer
- **No changes to the baremetal observability stack** — `observability-self-hosted` component remains untouched
- **No self-hosted Prometheus on GCP** — GKE Managed Prometheus replaces it
- **No custom OTel Collector** — Odigos-managed collectors only; no hand-rolled DaemonSets or Deployments
- **ADR-006 Kustomize Components** is the proven branching mechanism for platform-specific resource sets

---

## Decision

**Use a "smart-split" strategy: route metrics to GCP Managed Prometheus (Prometheus-compatible, Observer adapter works unchanged), and dual-ship logs and traces to both GCP Cloud Trace and a lightweight OpenObserve instance (for Backstage UI compatibility). Odigos provides universal auto-instrumentation with multiple Destination CRs for fan-out.**

### Architecture

```
GKE Cluster
├── GCP Managed Prometheus (metrics)
│   └── Prometheus-compatible scrape endpoint
│       └── Observer Prometheus adapter → Backstage UI (unchanged)
│
├── Odigos (auto-instrumentation layer)
│   ├── Destination CR: googlecloud → Cloud Trace (logs + traces)
│   └── Destination CR: otlp → OpenObserve (logs + traces)
│       └── Observer OpenObserve adapter → Backstage UI
│
└── OpenObserve (lightweight, in-cluster)
    └── HTTPRoute → Backstage Observer UI
```

### Smart-Split Rationale

| Signal | Backend | Why |
|--------|---------|-----|
| Metrics | GCP Managed Prometheus | GKE native, zero-ops, Prometheus-compatible scrape endpoint; existing Observer Prometheus adapter works without modification |
| Logs + Traces | Cloud Trace (via Odigos `googlecloud` Destination) | GCP-native retention, alerting, and cost efficiency |
| Logs + Traces | OpenObserve (via Odigos `otlp` Destination) | Backstage Observer UI requires an OpenObserve or Prometheus adapter; no GCP-native adapter exists |

Odigos supports multiple Destination CRs targeting the same signal type. The two Destination CRs (`googlecloud` and `otlp`) are additive — Odigos fans out to both without any custom collector configuration.

### Components Built

All observability resources live in a single Kustomize Component following ADR-006:

```
infrastructure/components/observability-cloud/   (kind: Component)
├── kustomization.yaml
├── openobserve-helmrepository.yaml
├── openobserve-helmrelease.yaml          # Lightweight; fluent-bit disabled
├── openobserve-externalsecret.yaml       # Admin credentials from GCP Secret Manager
├── observer-oauth-externalsecret.yaml    # Observer OAuth credentials
├── openobserve-httproute.yaml            # Backstage UI access
├── odigos-namespace.yaml
├── odigos-helmrepository.yaml
├── odigos-helmrelease.yaml
├── odigos-action.yaml                    # OpenChoreo label extraction
├── odigos-destination-googlecloud.yaml   # Cloud Trace destination
└── odigos-destination-otlp.yaml          # OpenObserve destination
```

The component is activated in the GCP platform overlay only:

```yaml
# infrastructure/platforms/gcp/03-platform/kustomization.yaml
components:
  - ../../../components/observability-cloud   # GCP only; baremetal uses observability-self-hosted
```

### Pulumi Prerequisites

Pulumi handles the genuinely imperative parts (per ADR-001 boundary rules):

1. **GKE cluster**: `monitoring_config.managed_prometheus.enabled = True` — enables GCP Managed Prometheus at cluster creation time
2. **GCP Secret Manager**: secret created for OpenObserve admin credentials (imperative API call; ExternalSecrets CRs are declarative and live in the component)
3. **Stack output**: `observability_mode` exported as a stack output and environment variable for downstream reference
4. **Pulumi config**: `enable_observability: "true"` set in `Pulumi.gcp.yaml`

Everything else (HelmReleases, ExternalSecrets, HTTPRoutes, Odigos Destinations) is declarative and lives in the Kustomize component, reconciled by FluxCD.

### Component vs. Platform Mapping

| Component | baremetal | k3d | GCP |
|-----------|-----------|-----|-----|
| `observability-self-hosted` | yes | yes | no |
| `observability-cloud` | no | no | yes |

The two components are mutually exclusive by convention. A platform overlay includes exactly one.

---

## Consequences

### Positive

- **No Observer adapter changes** — GCP Managed Prometheus exposes a Prometheus-compatible endpoint; the existing Observer Prometheus adapter works without modification
- **GCP-native retention and alerting** — Cloud Trace receives all traces and logs; GCP alerting policies and dashboards work as expected
- **Backstage UI compatibility** — OpenObserve receives the same traces and logs via Odigos fan-out; the Observer OpenObserve adapter works unchanged
- **Zero-ops metrics** — GCP Managed Prometheus eliminates the need to run, scale, or back up a self-hosted Prometheus instance
- **ADR-006 compliance** — The entire stack is a single Kustomize Component; activating GCP observability is a one-line `components:` entry in the platform overlay
- **ADR-001 compliance** — Pulumi handles only the imperative parts (cluster config, secret creation); all K8s resources are FluxCD-managed

### Negative

- **Dual-ship cost** — Logs and traces are sent to both Cloud Trace and OpenObserve; storage costs are roughly doubled for those signals
- **OpenObserve operational overhead** — A lightweight OpenObserve instance runs in-cluster solely for Backstage UI compatibility; it adds a HelmRelease to manage
- **Odigos dependency** — The fan-out strategy depends on Odigos supporting multiple Destination CRs per signal type; a regression in Odigos would break one of the two destinations

### Risks

- **OpenObserve resource usage** — Even with fluent-bit disabled, OpenObserve consumes cluster resources. If GCP node costs are a concern, the OpenObserve HelmRelease values should be tuned for minimal footprint.
- **Odigos version compatibility** — Odigos `googlecloud` and `otlp` Destination CR schemas may change between versions; the HelmRelease version pin in the component must be updated deliberately.
- **GCP Managed Prometheus scrape gaps** — If a workload does not expose a `/metrics` endpoint, it will not appear in the Observer Prometheus view. Odigos covers traces and logs for those workloads, but metrics coverage depends on instrumentation.

---

## Alternatives Considered

### 1. Send Everything to GCP-Native Services Only

Route all metrics, logs, and traces to Cloud Monitoring, Cloud Logging, and Cloud Trace. Skip OpenObserve entirely.

**Rejected because**: Backstage Observer has no GCP-native adapters. The UI would show no data. Implementing a new Observer adapter is out of scope and would require modifying upstream OpenChoreo.

### 2. Self-Hosted Prometheus on GCP

Deploy a Prometheus HelmRelease on GCP, mirroring the baremetal stack exactly.

**Rejected because**: GKE already provides GCP Managed Prometheus at no additional operational cost. Running a self-hosted Prometheus duplicates infrastructure, adds operational burden (storage, scaling, backup), and ignores a free GCP-native capability.

### 3. Custom OTel Collector with Multiple Exporters

Deploy a hand-rolled OpenTelemetry Collector DaemonSet configured with both a `googlecloud` exporter and an `otlp` exporter.

**Rejected because**: Odigos already manages OTel Collectors and supports multiple Destination CRs natively. A custom collector would duplicate Odigos's job, require manual DaemonSet management, and violate the constraint against custom OTel Collectors.

### 4. Single Destination — OpenObserve Only (Skip Cloud Trace)

Send all telemetry only to OpenObserve; skip GCP Cloud Trace entirely.

**Rejected because**: GCP-native observability (alerting, dashboards, log-based metrics) would be unavailable. The value of running on GCP includes its managed observability services; ignoring them wastes the platform's capabilities.

---

## Future Work

- **Tune OpenObserve resource requests/limits** in the component HelmRelease values once GCP node sizing is finalized
- **Evaluate Cloud Monitoring dashboards** as a complement to Backstage Observer for ops-facing views
- **Consider removing OpenObserve** if the upstream OpenChoreo Observer plugin gains a GCP-native adapter
- **Add `kustomize build` CI validation** for the `observability-cloud` component (per ADR-006 Future Work)
