# ADR-006: Kustomize Components for Platform Feature Flags — Multi-Platform Infrastructure Toggles

**Status**: Accepted  
**Date**: 2026-04-10  
**Deciders**: Yehia Amer  
**Context**: Multi-platform support (baremetal, k3d, GCP, AWS, Azure) requires toggling platform-specific infrastructure without Helm conditionals or repo duplication

---

## Context

OpenChoreo targets multiple deployment platforms — baremetal (Talos), k3d (local dev), and planned cloud targets (GCP, AWS, Azure). Each platform requires a different combination of infrastructure features:

### The Problem

| Symptom | Impact |
|---------|--------|
| Baremetal needs Cilium L2 announcements; k3d uses Docker networking | Can't use a single set of manifests for all platforms |
| Baremetal/k3d use self-signed TLS; cloud platforms need managed CAs | TLS issuer must be swappable per platform |
| Self-hosted registry vs. cloud-managed registry per platform | Registry configuration varies structurally, not just by value |
| Observability stack differs (self-hosted OpenObserve vs. cloud-managed) | Entire resource sets must toggle on/off, not just field values |
| Flux `postBuild` variable substitution can change values but cannot add or remove whole resources | Structural toggles need a different mechanism |

### Constraints

- **Flux `.spec.components` is broken** — fluxcd/kustomize-controller#1506 prevents using Flux's native component support
- **Helm conditionals** would require wrapping all infrastructure in a single mega-chart with `values.yaml` flags
- **Separate repos per platform** would create N copies of shared manifests with inevitable drift

---

## Decision

**Use Kustomize Components (`kind: Component`) for structural resource toggling; platform overlays compose base + components per wave.**

### Architecture

```
infrastructure/
├── base/                        # Shared manifests (all platforms)
│   ├── 00-crds/
│   ├── 01-prerequisites/
│   ├── 02-tls/
│   ├── 03-platform/
│   ├── 04-registration/
│   └── 05-network/
│
├── components/                  # Kustomize Components (kind: Component)
│   ├── cilium-l2/               # L2 announcement policies
│   ├── issuer-selfsigned/       # Self-signed CA issuer
│   ├── registry-self-hosted/    # In-cluster Docker registry
│   ├── observability-self-hosted/
│   ├── network-cilium-policy/
│   ├── kubernetes-replicator/
│   ├── issuer-gcp-cas/          # (stub) GCP CA Service
│   ├── registry-cloud/          # (stub) Cloud registry
│   ├── observability-cloud/     # (stub) Cloud observability
│   ├── secrets-gcp-sm/          # (stub) GCP Secret Manager
│   ├── secrets-openbao/         # (stub) OpenBao backend
│   └── issuer-letsencrypt/      # (stub) Let's Encrypt
│
└── platforms/                   # Per-platform wave overlays
    ├── baremetal/
    │   ├── 00-crds/kustomization.yaml
    │   ├── 01-prerequisites/kustomization.yaml
    │   ├── 02-tls/kustomization.yaml
    │   ├── 03-platform/kustomization.yaml
    │   ├── 04-registration/kustomization.yaml
    │   └── 05-network/kustomization.yaml
    ├── k3d/                     # Same structure, different components
    ├── gcp/                     # (stub)
    ├── aws/                     # (stub)
    └── azure/                   # (stub)
```

### How It Works

Each FluxCD wave Kustomization's `path:` points to a platform overlay directory. The overlay's `kustomization.yaml` composes shared base resources with platform-specific components:

```yaml
# infrastructure/platforms/baremetal/05-network/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../../base/05-network/cilium-configs
components:
  - ../../../components/cilium-l2          # baremetal needs L2 announcements
```

```yaml
# infrastructure/platforms/k3d/05-network/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../../base/05-network/cilium-configs
                                            # no cilium-l2 — k3d uses Docker networking
```

Components are referenced in the **filesystem `kustomization.yaml`** using the `components:` field — NOT via Flux's `.spec.components` (broken per fluxcd/kustomize-controller#1506).

### Component ↔ Platform Mapping

The mapping between Pulumi `PlatformProfile` boolean fields and Kustomize Components is documented in [Component-Platform Mapping](../component-platform-mapping.md). This ensures that Pulumi bootstrap decisions (Phase 1) align with FluxCD component composition (Phase 2).

---

## Consequences

### Positive

- **No repo duplication** — All platforms share `infrastructure/base/`; only the component selection varies
- **Declarative composition** — Adding a feature to a platform is a one-line `components:` entry in the overlay
- **Independent toggles** — Components are orthogonal; adding `registry-cloud` doesn't affect `issuer-selfsigned`
- **Standard Kustomize** — `kind: Component` is a native Kustomize feature (alpha since v4.1); no custom tooling
- **Wave-aligned** — Components slot into the existing 6-wave dependency chain without new FluxCD Kustomization resources

### Negative

- **`kind: Component` is alpha** — The Kustomize API is `kustomize.config.k8s.io/v1alpha1`; potential breaking changes
- **No runtime validation** — A platform overlay that omits a required component produces a broken deployment at reconciliation time, not at build time
- **Filesystem-only composition** — Component selection is expressed in YAML files on disk, not in a central config; requires reading multiple `kustomization.yaml` files to understand a platform's full feature set

### Risks

- **Flux bug #1506 persists** — If Flux never fixes `.spec.components`, the filesystem-level workaround becomes permanent
- **Component count growth** — As more platforms and features are added, the combinatorial explosion of components × waves could make overlays hard to audit
- **`$patch: delete` fragility** — Resource removal via strategic merge patch depends on exact resource names; refactoring base resource names can silently break component patches

---

## Alternatives Considered

### 1. Helm Conditionals (Single Mega-Chart)

Wrap all infrastructure in a Helm chart with `values.yaml` flags like `ciliumL2.enabled: true`.

**Rejected because**:
- Couples all infrastructure into one release; a cert-manager bug blocks the entire platform
- Helm template logic (`{{- if .Values.x }}`) is harder to review than declarative Kustomize composition
- Existing infrastructure is already structured as independent HelmReleases per component
- Version pinning per sub-component becomes difficult

### 2. Flux `postBuild` Variable Substitution

Use `${ENABLE_CILIUM_L2}` variables and conditional logic to toggle resources.

**Rejected because**:
- Flux `postBuild.substitute` replaces string values — it cannot add or remove entire resources
- Would require wrapping every optional resource in a Helm chart with conditional templates (collapses back to Alternative 1)
- No way to conditionally include a Kustomize resource reference via variable substitution

### 3. Separate Repositories Per Platform

Fork `openchoreo-gitops` into `openchoreo-gitops-baremetal`, `openchoreo-gitops-k3d`, etc.

**Rejected because**:
- Shared manifests (`infrastructure/base/`) would drift between repos
- Bug fixes require cherry-picking across N repos
- Exponential maintenance burden as platforms grow

---

## Future Work

- **Promote `gcp`, `aws`, `azure` platform overlays** from stubs to active once cloud-specific components are implemented
- **Add a CI validation step** that runs `kustomize build` on every platform overlay to catch missing components before merge
- **Consider a platform manifest file** (e.g., `platforms/baremetal/profile.yaml`) that declares the component set centrally, reducing the need to inspect each wave's `kustomization.yaml`
