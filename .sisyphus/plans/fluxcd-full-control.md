# FluxCD Full Control: Eliminate Pulumi Middle Step

## TL;DR

> **Quick Summary**: Migrate all Kubernetes resource management from Pulumi to FluxCD, so after Talos cluster creation the pipeline is: Pulumi (Talos+Cilium+Longhorn+FluxBootstrap+OpenBao+Thunder) → FluxCD (everything else). Creates a numbered infrastructure layer system in the existing openchoreo-gitops repo with Kustomize overlays for all 4 platforms.
> 
> **Deliverables**:
> - FluxCD HelmReleases for: cert-manager, ESO, kgateway, kubernetes-replicator, Docker Registry, CP, DP, WP, OP, Odigos, observability stack
> - FluxCD Kustomizations with `dependsOn` chains for infrastructure ordering
> - K8s Jobs for: plane registration, plane linking
> - Flux `postBuild` variable substitution for workflow templates
> - Kustomize overlays per platform (k3d, rancher-desktop, talos-vm, talos-baremetal)
> - Pulumi stripped down to: Talos + Cilium + GW API CRDs + Longhorn + flux bootstrap + OpenBao + Thunder + PushSecrets + ClusterSecretStore
> - Standalone pytest E2E test suite (extracted from Pulumi integration tests)
> - Rollback artifacts per wave (git tags + Pulumi state backups)
> 
> **Estimated Effort**: XL (4 migration waves + foundation + final verification)
> **Parallel Execution**: YES — 5 waves, 5-8 tasks per wave
> **Critical Path**: Wave 0 (foundation) → Wave 1 (prerequisites) → Wave 2 (TLS+secrets) → Wave 3 (planes) → Wave 4 (linking+observability+cleanup)

---

## Context

### Original Request
Eliminate the Pulumi middle step between Talos cluster creation and FluxCD-managed applications. Currently the pipeline is 3 phases (Talos → Pulumi OpenChoreo install → FluxCD apps). Target: 2 phases (Pulumi minimal → FluxCD everything).

### Interview Summary
**Key Discussions**:
- Pulumi scope: Talos + Cilium + GW API CRDs + Longhorn + flux bootstrap + OpenBao + Thunder + PushSecrets + ClusterSecretStore + seed secrets
- Link Planes: K8s Job managed by FluxCD
- GitOps structure: Hybrid — numbered infra layers (00-04) + OpenChoreo app layers (platform-shared/namespaces/projects)
- Migration: Incremental in 4 waves with rollback per wave
- CA sync: kubernetes-replicator (replaces CopyCA dynamic provider)
- OpenBao + Thunder: Keep in Pulumi (imperative seeding, OIDC bootstrap)
- Tests: Extract to standalone pytest E2E suite
- GitOps repo: Extend existing openchoreo-gitops
- Workflow templates: Flux `postBuild` variable substitution
- Multi-platform: All 4 platforms via Kustomize overlays
- Rollback: Git tag + Pulumi state backup per wave

**Research Findings**:
- Legacy `talos-fluxcd` project proves numbered layer pattern with `dependsOn` chains
- Cilium CNI install MUST stay outside FluxCD (chicken-and-egg)
- `cilium-gateway` acts as universal "cluster ready" gate
- core/configs split pattern enables complex dependency chains
- OpenChoreo docs recommend 3-layer Kustomization: platform-shared → platform → projects
- FluxCD HelmRelease does server-side apply (handles CRD ordering better than Pulumi's v4.Chart)

### Metis Review
**Identified Gaps** (addressed):
- Multi-platform support: covered via Kustomize overlays per platform
- Helm release name conflicts: plan requires exact release name matching
- Pulumi state hygiene: `pulumi state delete` before FluxCD adoption (no `pulumi up` removal)
- PushSecret source secrets: seed secrets stay in Pulumi
- FluxCD health checks for Job completion: verified — Flux supports Job health checks via `healthChecks`
- CopyCA does Secret→ConfigMap transform: kubernetes-replicator with Secret type replication + cert-manager trust-manager as fallback
- Dynamic Helm values: enumerated per component, converted to static YAML or Flux `valuesFrom` ConfigMaps
- Partial wave failure rollback: git tag + Pulumi state backup per wave

---

## Work Objectives

### Core Objective
Migrate all Kubernetes resource management (Helm charts, manifests, CRDs, Jobs) from Pulumi to FluxCD GitOps, keeping only the minimal imperative bootstrap (Talos, Cilium, OpenBao, Thunder) in Pulumi.

### Concrete Deliverables
- `openchoreo-gitops` repo: new `clusters/`, `infrastructure/` directories with FluxCD manifests
- `pulumi/`: stripped-down codebase with only Phase 1 components
- `tests/e2e/`: standalone pytest E2E suite
- Per-wave rollback artifacts (git tags, Pulumi state exports)

### Definition of Done
- [ ] `flux get kustomizations -A` — all Kustomizations Ready
- [ ] `flux get helmreleases -A` — all HelmReleases reconciled
- [ ] `kubectl get pods -A` — all platform pods Running
- [ ] `pytest tests/e2e/ -v` — all E2E tests pass
- [ ] `pulumi stack export` — no URNs for migrated components
- [ ] Delete a FluxCD-managed resource → auto-heals within 5m

### Must Have
- All Helm charts currently in Pulumi managed as FluxCD HelmReleases
- Proper `dependsOn` chains matching current Pulumi dependency order
- kubernetes-replicator for CA secret cross-namespace sync
- K8s Jobs for plane registration + linking with proper RBAC
- Flux `postBuild` variable substitution for workflow templates
- Kustomize overlays for k3d, rancher-desktop, talos-vm, talos-baremetal
- Rollback capability per wave (git tag + state backup)
- Standalone E2E test suite
- Exact Helm release name preservation (no rename conflicts)

### Must NOT Have (Guardrails)
- DO NOT have any resource managed by BOTH Pulumi and FluxCD simultaneously
- DO NOT use `pulumi up` to remove migrated resources (use `pulumi state delete` first)
- DO NOT change Helm release names during migration
- DO NOT include OpenBao or Thunder in FluxCD (stays in Pulumi)
- DO NOT migrate more than one "layer" per wave without testing
- DO NOT hardcode platform-specific values in base manifests (use overlays)
- DO NOT commit plaintext secrets to the gitops repo
- DO NOT break existing openchoreo-gitops app-layer structure
- DO NOT include multi-cluster support
- DO NOT clean up dead code (separate issue)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES — `pulumi/tests/` has ~150 pytest tests
- **Automated tests**: Tests-after (E2E suite runs after each wave)
- **Framework**: pytest with kubectl/flux CLI assertions
- **Per-wave gate**: `pytest tests/e2e/ -m <wave_marker> -v` must pass before next wave

### QA Policy
Every task includes agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **FluxCD manifests**: `flux reconcile kustomization <name>` + `flux get kustomizations`
- **HelmReleases**: `flux get helmreleases -A` + `kubectl get pods -n <namespace>`
- **State handoff**: `pulumi stack export | jq '.deployment.resources[].urn'` — verify absence
- **Drift healing**: `kubectl delete <resource>` → wait → verify recreation

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 0 (Foundation — bootstrap + repo structure):
├── Task 1: Create gitops repo infrastructure layer directories [quick]
├── Task 2: Create Kustomize base + overlay structure per platform [quick]
├── Task 3: Create cluster entry points (clusters/<platform>/kustomization.yaml) [quick]
├── Task 4: Move flux bootstrap to Pulumi Phase 1 (before OpenChoreo) [deep]
├── Task 5: Consolidate Pulumi Phase 1 (Talos+Cilium+OpenBao+Thunder+secrets) [deep]
└── Task 6: Extract integration tests to standalone pytest E2E suite [unspecified-high]

Wave 1 (Prerequisites — easy Helm charts):
├── Task 7: cert-manager FluxCD HelmRelease + state handoff [unspecified-high]
├── Task 8: ESO FluxCD HelmRelease + state handoff [unspecified-high]
├── Task 9: kgateway CRDs + controller FluxCD HelmReleases + state handoff [unspecified-high]
├── Task 10: kubernetes-replicator FluxCD HelmRelease (NEW) [quick]
├── Task 11: Cilium L2 configs as FluxCD Kustomization [quick]
└── Task 12: Wave 1 rollback artifact + E2E gate [quick]

Wave 2 (TLS + Platform Helm charts):
├── Task 13: TLS CA chain as FluxCD manifests (ClusterIssuer, Certificates) [unspecified-high]
├── Task 14: Docker Registry FluxCD HelmRelease [quick]
├── Task 15: Control Plane FluxCD HelmRelease + values ConfigMap [deep]
├── Task 16: Data Plane FluxCD HelmRelease + CA replication annotations [deep]
├── Task 17: Workflow Plane FluxCD HelmRelease + postBuild variables [deep]
└── Task 18: Wave 2 rollback artifact + E2E gate [quick]

Wave 3 (Registration + Observability + Linking):
├── Task 19: Plane registration K8s Jobs (DP, WP, OP) + RBAC [deep]
├── Task 20: Observability Plane FluxCD HelmReleases (OpenObserve/Prometheus/Observer) [unspecified-high]
├── Task 21: Odigos FluxCD HelmRelease [quick]
├── Task 22: Link Planes K8s Job + RBAC [deep]
├── Task 23: Workflow templates with Flux postBuild substitution [deep]
└── Task 24: Wave 3 rollback artifact + E2E gate [quick]

Wave 4 (Cleanup + Final):
├── Task 25: Strip Pulumi: remove all migrated components from code [deep]
├── Task 26: Update Pulumi __main__.py to Phase 1 only flow [deep]
├── Task 27: Full E2E test suite run + drift healing test [unspecified-high]
└── Task 28: Documentation update (README, deployment guide) [writing]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1-3 | None | 4, 7-11 | 0 |
| 4 | 1-3 | 5, 7 | 0 |
| 5 | 4 | 7-11 | 0 |
| 6 | None | 12, 18, 24, 27 | 0 |
| 7-9 | 5 | 13-17 | 1 |
| 10-11 | 5 | 16 | 1 |
| 12 | 7-11 | 13 | 1 |
| 13 | 12 | 15-17 | 2 |
| 14 | 12 | 17 | 2 |
| 15 | 13 | 19 | 2 |
| 16 | 10, 13 | 19 | 2 |
| 17 | 13, 14 | 23 | 2 |
| 18 | 13-17 | 19 | 2 |
| 19 | 15-17 | 22 | 3 |
| 20 | 13 | 22 | 3 |
| 21 | 12 | 25 | 3 |
| 22 | 19, 20 | 25 | 3 |
| 23 | 17 | 25 | 3 |
| 24 | 19-23 | 25 | 3 |
| 25-26 | 24 | 27 | 4 |
| 27 | 25-26 | 28 | 4 |
| 28 | 27 | FINAL | 4 |
| F1-F4 | 28 | Done | FINAL |

### Agent Dispatch Summary

- **Wave 0**: 6 tasks — T1-T3 → `quick`, T4-T5 → `deep`, T6 → `unspecified-high`
- **Wave 1**: 6 tasks — T7-T9 → `unspecified-high`, T10-T12 → `quick`
- **Wave 2**: 6 tasks — T13 → `unspecified-high`, T14 → `quick`, T15-T17 → `deep`, T18 → `quick`
- **Wave 3**: 6 tasks — T19,T22,T23 → `deep`, T20 → `unspecified-high`, T21,T24 → `quick`
- **Wave 4**: 4 tasks — T25-T26 → `deep`, T27 → `unspecified-high`, T28 → `writing`
- **FINAL**: 4 tasks — F1 → `oracle`, F2-F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

### Wave 0: Foundation

- [x] 1. Create gitops repo infrastructure layer directories

  **What to do**:
  - In the `openchoreo-gitops` repo, create the numbered infrastructure layer directory structure:
    ```
    infrastructure/
    ├── base/
    │   ├── 00-crds/                    # Gateway API CRDs (managed by FluxCD for upgrades)
    │   ├── 01-prerequisites/
    │   │   ├── cert-manager/
    │   │   │   ├── core/               # HelmRelease + HelmRepository
    │   │   │   └── configs/            # ClusterIssuers (depends on cert-manager running)
    │   │   ├── external-secrets/
    │   │   │   ├── core/
    │   │   │   └── configs/            # ClusterSecretStore (stays Pulumi, but ESO operator here)
    │   │   ├── kgateway/
    │   │   │   ├── crds/
    │   │   │   └── controller/
    │   │   └── kubernetes-replicator/
    │   │       └── core/
    │   ├── 02-tls/
    │   │   ├── ca-chain/               # ClusterIssuer, CA Certificate
    │   │   └── wildcard-certs/         # Per-plane wildcard Certificates
    │   ├── 03-platform/
    │   │   ├── control-plane/          # CP HelmRelease + values ConfigMap
    │   │   ├── data-plane/             # DP HelmRelease + CA replication annotations
    │   │   ├── workflow-plane/         # WP HelmRelease + Docker Registry
    │   │   ├── observability-plane/    # OP HelmReleases (OpenObserve, Prometheus, Observer)
    │   │   └── odigos/                 # Odigos HelmRelease
    │   ├── 04-registration/
    │   │   ├── register-planes/        # K8s Jobs + RBAC for plane CRD registration
    │   │   └── link-planes/            # K8s Job + RBAC for plane linking
    │   └── 05-network/
    │       └── cilium-configs/         # L2 announcement policy, LoadBalancerIPPool
    clusters/
    ├── talos-baremetal/
    │   ├── kustomization.yaml          # Master entry: includes numbered layer Kustomizations
    │   ├── 00-crds.yaml
    │   ├── 01-prerequisites.yaml
    │   ├── 02-tls.yaml
    │   ├── 03-platform.yaml
    │   ├── 04-registration.yaml
    │   └── 05-network.yaml
    ├── k3d/
    ├── talos-vm/
    └── rancher-desktop/
    ```
  - Create placeholder `kustomization.yaml` in each base directory
  - Each cluster directory references the base with Kustomize overlays

  **Must NOT do**:
  - DO NOT modify existing `namespaces/`, `platform-shared/`, `projects/` directories
  - DO NOT add any actual HelmRelease manifests yet (that's later tasks)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 2, 3, 6)
  - **Parallel Group**: Wave 0
  - **Blocks**: Tasks 4, 7-11
  - **Blocked By**: None

  **References**:
  - `talos-fluxcd/clusters/lab-amer-talos/` — Legacy cluster entry point with numbered files
  - `talos-fluxcd/infrastructure/base/` — Legacy base directory with core/configs split
  - `openchoreo-gitops` repo current structure — existing namespaces/platform-shared/projects dirs

  **Acceptance Criteria**:
  ```
  Scenario: Directory structure created correctly
    Tool: Bash
    Steps:
      1. ls -R infrastructure/base/ in openchoreo-gitops repo
      2. Assert: directories 00-crds through 05-network exist
      3. Assert: each has kustomization.yaml
      4. ls clusters/ — Assert: talos-baremetal, k3d, talos-vm, rancher-desktop dirs exist
    Expected Result: Full directory tree with placeholder kustomization.yaml files
    Evidence: .sisyphus/evidence/task-1-directory-structure.txt
  ```

  **Commit**: YES — `feat(gitops): add FluxCD infrastructure layer directory structure`

- [x] 2. Create Kustomize base + overlay structure per platform

  **What to do**:
  - Create platform-specific overlay directories under `clusters/<platform>/overlays/`
  - Each overlay contains patches for platform-specific values:
    - `talos-baremetal`: domain=amernas.work, TLS enabled, L2 announcements for enp7s0
    - `k3d`: domain=openchoreo.localhost, no TLS, no L2
    - `talos-vm`: domain=openchoreo.localhost, no TLS, L2 for dev
    - `rancher-desktop`: domain=openchoreo.localhost, no TLS, no L2
  - Create a `clusters/<platform>/vars/` ConfigMap for Flux `postBuild` variable substitution:
    ```yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: cluster-vars
      namespace: flux-system
    data:
      DOMAIN_BASE: "amernas.work"        # or "openchoreo.localhost"
      REGISTRY_ENDPOINT: "registry.openchoreo-workflow-plane.svc.cluster.local:5000"
      GATEWAY_ENDPOINT: "openchoreo-api.amernas.work"
      TLS_ENABLED: "true"
      PLATFORM: "talos-baremetal"
    ```
  - Map every dynamic value from `pulumi/config.py` and `pulumi/values/*.py` to ConfigMap entries

  **Must NOT do**:
  - DO NOT hardcode platform-specific values in `infrastructure/base/`

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 1, 3, 6)
  - **Parallel Group**: Wave 0
  - **Blocks**: Tasks 7-11 (overlays needed before HelmReleases)
  - **Blocked By**: None

  **References**:
  - `pulumi/config.py` — All config constants and OpenChoreoConfig dataclass
  - `pulumi/platforms/talos_baremetal.py` — Baremetal platform profile (domain, CNI, gateway, L2 settings)
  - `pulumi/platforms/k3d.py` — k3d platform profile
  - `pulumi/Pulumi.talos-baremetal.yaml` — Stack config with actual values for baremetal
  - `pulumi/Pulumi.dev.yaml` — Stack config for k3d

  **Acceptance Criteria**:
  ```
  Scenario: Platform ConfigMaps have correct values
    Tool: Bash
    Steps:
      1. Read clusters/talos-baremetal/vars/cluster-vars.yaml
      2. Assert: DOMAIN_BASE=amernas.work, TLS_ENABLED=true
      3. Read clusters/k3d/vars/cluster-vars.yaml
      4. Assert: DOMAIN_BASE=openchoreo.localhost, TLS_ENABLED=false
    Expected Result: Each platform has correct variable values
    Evidence: .sisyphus/evidence/task-2-platform-vars.txt
  ```

  **Commit**: YES (groups with Task 1)

- [x] 3. Create cluster entry points (master kustomization.yaml per platform)

  **What to do**:
  - Create `clusters/<platform>/kustomization.yaml` — the master entry point FluxCD reads
  - Each references numbered Kustomization files (00-crds.yaml through 05-network.yaml)
  - Create the numbered FluxCD Kustomization resource files with `dependsOn` chains:
    ```yaml
    # clusters/talos-baremetal/01-prerequisites.yaml
    apiVersion: kustomize.toolkit.fluxcd.io/v1
    kind: Kustomization
    metadata:
      name: prerequisites
      namespace: flux-system
    spec:
      interval: 5m
      path: ./infrastructure/base/01-prerequisites
      prune: true
      sourceRef:
        kind: GitRepository
        name: openchoreo-gitops
      dependsOn:
        - name: crds
      postBuild:
        substituteFrom:
          - kind: ConfigMap
            name: cluster-vars
    ```
  - Define the full `dependsOn` chain: 00-crds → 01-prerequisites → 02-tls → 03-platform → 04-registration → 05-network
  - Include the existing OpenChoreo app-layer Kustomizations (oc-namespaces, oc-platform-shared, oc-platform, oc-demo-projects) with `dependsOn: [registration]`

  **Must NOT do**:
  - DO NOT break the existing app-layer Kustomization chain

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 1, 2, 6)
  - **Parallel Group**: Wave 0
  - **Blocks**: Tasks 4, 7-11
  - **Blocked By**: None

  **References**:
  - `talos-fluxcd/clusters/lab-amer-talos/kustomization.yaml` — Legacy master entry point
  - `talos-fluxcd/clusters/lab-amer-talos/01-infrastructure-network.yaml` — Legacy numbered Kustomization with `dependsOn`
  - `pulumi/components/flux_gitops.py:94-174` — Current Kustomization definitions with dependency chain

  **Acceptance Criteria**:
  ```
  Scenario: dependsOn chain is complete and correct
    Tool: Bash
    Steps:
      1. For each numbered yaml in clusters/talos-baremetal/, parse dependsOn
      2. Assert: 01 depends on 00, 02 depends on 01, 03 depends on 02, 04 depends on 03
      3. Assert: oc-platform depends on [04-registration, oc-namespaces, oc-platform-shared]
    Expected Result: Complete dependency chain with no circular deps
    Evidence: .sisyphus/evidence/task-3-dependency-chain.txt
  ```

  **Commit**: YES (groups with Task 1)

- [x] 4. Move FluxCD bootstrap to Pulumi Phase 1

  **What to do**:
  - Currently Flux is installed in Step 7 (after all planes). Move it to run IMMEDIATELY after Cilium+Longhorn in Phase 1
  - In `pulumi/talos-cluster-baremetal/__main__.py`, add flux bootstrap:
    1. After Cilium and Longhorn are installed, install Flux CD controllers using the local `flux-install.yaml`
    2. Create the GitRepository pointing to `openchoreo-gitops`
    3. Create the root Kustomization pointing to `clusters/<platform>/`
  - Alternatively, use `flux bootstrap github` via subprocess command
  - The FluxCD Kustomizations will start reconciling but will wait on `dependsOn` until infrastructure layers are populated
  - Ensure OpenBao/Thunder (also Phase 1) run BEFORE Flux starts reconciling infra layers (OpenBao/Thunder create the secrets that ESO/PushSecrets need)
  - Update `pulumi/__main__.py` to SKIP Step 7 (flux_gitops) since it moves to Phase 1

  **Must NOT do**:
  - DO NOT delete the existing `flux_gitops.py` yet (Wave 4 cleanup)
  - DO NOT change the gitops repo URL or branch

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`pulumi-remediation-loop`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential after Tasks 1-3
  - **Blocks**: Task 5
  - **Blocked By**: Tasks 1-3

  **References**:
  - `pulumi/talos-cluster-baremetal/__main__.py` — Phase 1 entry point
  - `pulumi/components/flux_gitops.py:38-52` — Current Flux install + wait logic
  - `pulumi/flux-install.yaml` — Local Flux install manifest (8612 lines)
  - `pulumi/__main__.py:120-140` — Step 7 Flux deployment condition
  - `talos-fluxcd/terraform/Other/talos-cilium/talos.tf` — Legacy: Terraform bootstrap sequence

  **Acceptance Criteria**:
  ```
  Scenario: Flux controllers running after Phase 1
    Tool: Bash (kubectl)
    Steps:
      1. After pulumi up on talos-cluster-baremetal, run: kubectl get pods -n flux-system
      2. Assert: source-controller, kustomize-controller, helm-controller Running
      3. Run: kubectl get gitrepositories -n flux-system
      4. Assert: openchoreo-gitops GitRepository exists and Ready
    Expected Result: FluxCD running and connected to gitops repo
    Evidence: .sisyphus/evidence/task-4-flux-bootstrap.txt

  Scenario: Flux Kustomizations in pending state (waiting for content)
    Tool: Bash (kubectl)
    Steps:
      1. kubectl get kustomizations -n flux-system
      2. Assert: infrastructure Kustomizations exist but may show "path not found" (content not yet in repo)
    Expected Result: Kustomizations created, waiting for gitops repo content
    Evidence: .sisyphus/evidence/task-4-kustomizations-pending.txt
  ```

  **Commit**: YES — `refactor(pulumi): move FluxCD bootstrap to Phase 1 (before OpenChoreo planes)`

- [x] 5. Consolidate Pulumi Phase 1 (Talos+Cilium+OpenBao+Thunder+secrets)

  **What to do**:
  - Restructure `pulumi/__main__.py` to clearly separate Phase 1 (Pulumi-managed) from Phase 2 (FluxCD-managed)
  - Phase 1 order:
    1. Step 0: Cilium CNI (existing)
    2. Step 0.5: Cilium L2 (keep temporarily — moves to FluxCD in Wave 1)
    3. Step 1-partial: OpenBao install + seeding (from prerequisites.py)
    4. Step 1-partial: Thunder install + bootstrap (from control_plane.py Thunder section)
    5. Step 1-partial: PushSecrets + ClusterSecretStore (from prerequisites.py)
    6. Step 1-partial: Seed K8s Secrets (GitHub PAT, bootstrap configs)
    7. NEW: FluxCD bootstrap (from Task 4)
  - Add feature flag `cfg.fluxcd_manages_infra` (default False) to gate the Phase 2 skip
  - When `fluxcd_manages_infra=True`, Pulumi skips Steps 1-9 except the Phase 1 items above
  - This allows incremental migration: flag starts False (current behavior), flips True when FluxCD is ready

  **Must NOT do**:
  - DO NOT delete any existing component files yet
  - DO NOT break the current `pulumi up` flow (feature flag gates the change)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`pulumi-remediation-loop`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential after Task 4
  - **Blocks**: Tasks 7-11
  - **Blocked By**: Task 4

  **References**:
  - `pulumi/__main__.py` — Full orchestrator with Steps 0-9
  - `pulumi/components/prerequisites.py` — OpenBao, ESO, cert-manager, kgateway, PushSecrets
  - `pulumi/components/control_plane.py:55-140` — Thunder bootstrap section
  - `pulumi/config.py` — OpenChoreoConfig dataclass (add `fluxcd_manages_infra` field)

  **Acceptance Criteria**:
  ```
  Scenario: Feature flag False — current behavior preserved
    Tool: Bash
    Steps:
      1. Set fluxcd_manages_infra=false in Pulumi config
      2. Run pulumi preview
      3. Assert: all existing resources still managed (no diff)
    Expected Result: Backward compatible — no behavior change when flag is off
    Evidence: .sisyphus/evidence/task-5-backward-compat.txt

  Scenario: Feature flag True — only Phase 1 resources
    Tool: Bash
    Steps:
      1. Set fluxcd_manages_infra=true in Pulumi config
      2. Run pulumi preview
      3. Assert: only Cilium, OpenBao, Thunder, PushSecrets, ClusterSecretStore, FluxCD resources in preview
      4. Assert: cert-manager, ESO, kgateway, CP, DP, WP, OP NOT in preview
    Expected Result: Pulumi manages only Phase 1 when flag is on
    Evidence: .sisyphus/evidence/task-5-phase1-only.txt
  ```

  **Commit**: YES — `refactor(pulumi): add fluxcd_manages_infra feature flag for incremental migration`

- [x] 6. Extract integration tests to standalone pytest E2E suite

  **What to do**:
  - Create `tests/e2e/` directory with pytest infrastructure
  - Extract the 43 integration test checks from `pulumi/components/integration_tests.py` into pytest functions
  - Categories with pytest markers: `@pytest.mark.flux`, `@pytest.mark.prerequisites`, `@pytest.mark.control_plane`, `@pytest.mark.data_plane`, `@pytest.mark.workflow_plane`, `@pytest.mark.observability`
  - Each test uses kubectl/kubernetes-client to check resource state (no Pulumi dependency)
  - Add new FluxCD-specific tests: `test_helmreleases_reconciled`, `test_kustomizations_ready`, `test_drift_healing`
  - Create `conftest.py` with kubeconfig fixture
  - Create `pytest.ini` with marker registration

  **Must NOT do**:
  - DO NOT delete the original integration_tests.py yet (Wave 4)
  - DO NOT require Pulumi to be installed to run tests

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`tdd-guide`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 1-3)
  - **Parallel Group**: Wave 0
  - **Blocks**: Tasks 12, 18, 24, 27
  - **Blocked By**: None

  **References**:
  - `pulumi/components/integration_tests.py` — Current 43 integration test definitions
  - `pulumi/tests/conftest.py` — Existing pytest fixtures (kubeconfig, kube_context)
  - `pulumi/tests/` — Existing ~150 pytest tests to not conflict with

  **Acceptance Criteria**:
  ```
  Scenario: E2E tests run independently of Pulumi
    Tool: Bash
    Steps:
      1. cd tests/e2e && pytest --collect-only
      2. Assert: 43+ test functions collected
      3. Assert: markers include flux, prerequisites, control_plane, etc.
      4. pytest -m prerequisites -v (against running cluster)
      5. Assert: all prerequisites tests pass
    Expected Result: Standalone E2E suite with pytest markers
    Evidence: .sisyphus/evidence/task-6-e2e-tests.txt
  ```

  **Commit**: YES — `test: extract integration tests to standalone pytest E2E suite`

---

### Wave 1: Prerequisites (Easy Helm Charts)

- [x] 7. cert-manager FluxCD HelmRelease + state handoff

  **What to do**:
  - Create `infrastructure/base/01-prerequisites/cert-manager/core/helmrelease.yaml`:
    - HelmRepository pointing to `https://charts.jetstack.io`
    - HelmRelease for cert-manager with values matching `pulumi/components/prerequisites.py` cert-manager section
    - `spec.releaseName: cert-manager` (MUST match existing Pulumi release name)
    - `installCRDs: true`
  - Create platform overlays for cert-manager (baremetal needs gateway API integration)
  - **State handoff protocol**:
    1. Create git tag: `git tag pre-wave1-certmanager`
    2. Export Pulumi state: `pulumi stack export > .sisyphus/backups/pre-wave1-certmanager.json`
    3. Push FluxCD manifest to gitops repo
    4. Wait for FluxCD to reconcile cert-manager HelmRelease
    5. Verify: `flux get helmreleases cert-manager -n cert-manager`
    6. Delete from Pulumi state: `pulumi state delete <cert-manager-urn>` (NOT `pulumi up`)
    7. Run E2E tests: `pytest tests/e2e/ -m prerequisites -v`

  **Must NOT do**:
  - DO NOT use `pulumi up` to remove cert-manager (it will DELETE the resource)
  - DO NOT change the Helm release name from what Pulumi used

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`senior-devops`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 8, 9 — after state handoff order: 7→8→9)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 13 (TLS needs cert-manager)
  - **Blocked By**: Task 5

  **References**:
  - `pulumi/components/prerequisites.py` — cert-manager Helm release definition, values, version
  - `talos-fluxcd/infrastructure/base/cert-manager/core/cert-manager-helmrelease.yaml` — Legacy HelmRelease example
  - `pulumi/config.py` — CERT_MANAGER_VERSION, chart repo URL

  **Acceptance Criteria**:
  ```
  Scenario: cert-manager reconciled by FluxCD
    Tool: Bash
    Steps:
      1. flux get helmreleases -n cert-manager
      2. Assert: cert-manager shows "Release reconciliation succeeded"
      3. kubectl get pods -n cert-manager
      4. Assert: cert-manager, cert-manager-webhook, cert-manager-cainjector Running
    Expected Result: cert-manager healthy under FluxCD management
    Evidence: .sisyphus/evidence/task-7-certmanager-flux.txt

  Scenario: Pulumi state no longer contains cert-manager
    Tool: Bash
    Steps:
      1. pulumi stack export -s talos-baremetal | jq '.deployment.resources[].urn' | grep cert-manager
      2. Assert: empty output (no cert-manager URNs)
    Expected Result: Clean state separation
    Evidence: .sisyphus/evidence/task-7-pulumi-state-clean.txt
  ```

  **Commit**: YES — `feat(gitops): add cert-manager FluxCD HelmRelease`

- [x] 8. ESO FluxCD HelmRelease + state handoff

  **What to do**:
  - Create `infrastructure/base/01-prerequisites/external-secrets/core/helmrelease.yaml`
  - HelmRepository + HelmRelease for external-secrets-operator
  - `spec.releaseName` must match Pulumi's release name
  - ClusterSecretStore configs remain in Pulumi (depends on OpenBao)
  - Same state handoff protocol as Task 7

  **Must NOT do**:
  - DO NOT move ClusterSecretStore to FluxCD (it references OpenBao which is Pulumi-managed)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`senior-devops`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (after Task 7 state handoff)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 13
  - **Blocked By**: Task 5

  **References**:
  - `pulumi/components/prerequisites.py` — ESO Helm release definition
  - `talos-fluxcd/infrastructure/base/external-secrets/core/external-secrets-helmrelease.yaml` — Legacy example

  **Acceptance Criteria**:
  ```
  Scenario: ESO reconciled by FluxCD
    Tool: Bash
    Steps:
      1. flux get helmreleases -n external-secrets
      2. Assert: external-secrets shows "Release reconciliation succeeded"
      3. kubectl get pods -n external-secrets
      4. Assert: external-secrets pods Running
    Expected Result: ESO healthy under FluxCD management
    Evidence: .sisyphus/evidence/task-8-eso-flux.txt
  ```

  **Commit**: YES — `feat(gitops): add ESO FluxCD HelmRelease`

- [x] 9. kgateway CRDs + controller FluxCD HelmReleases + state handoff

  **What to do**:
  - Create `infrastructure/base/01-prerequisites/kgateway/crds/helmrelease.yaml` — kgateway-crds chart
  - Create `infrastructure/base/01-prerequisites/kgateway/controller/helmrelease.yaml` — kgateway controller
  - CRDs HelmRelease must reconcile BEFORE controller (use `dependsOn`)
  - Same state handoff protocol

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`senior-devops`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 7, 8)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 15 (CP needs kgateway)
  - **Blocked By**: Task 5

  **References**:
  - `pulumi/components/prerequisites.py` — kgateway Helm releases (crds + controller)

  **Acceptance Criteria**:
  ```
  Scenario: kgateway reconciled by FluxCD
    Tool: Bash
    Steps:
      1. flux get helmreleases -A | grep kgateway
      2. Assert: both kgateway-crds and kgateway show reconciled
    Expected Result: kgateway healthy under FluxCD
    Evidence: .sisyphus/evidence/task-9-kgateway-flux.txt
  ```

  **Commit**: YES (groups with Task 7)

- [x] 10. kubernetes-replicator FluxCD HelmRelease (NEW component)

  **What to do**:
  - Create `infrastructure/base/01-prerequisites/kubernetes-replicator/core/helmrelease.yaml`
  - HelmRepository: `https://helm.mittwald.de`
  - This is a NEW component replacing the CopyCA dynamic provider
  - Configure to watch annotations for secret replication
  - Later tasks (DP, WP, OP) will annotate the CA secret for cross-namespace replication

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 7-9)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 16 (DP needs replicator for CA sync)
  - **Blocked By**: Task 5

  **References**:
  - `talos-fluxcd/infrastructure/base/kubernetes-replicator/` — Legacy HelmRelease example
  - `pulumi/helpers/copy_ca.py` — Current CopyCA logic being replaced

  **Acceptance Criteria**:
  ```
  Scenario: kubernetes-replicator running
    Tool: Bash
    Steps:
      1. kubectl get pods -n kubernetes-replicator
      2. Assert: replicator pod Running
    Expected Result: Replicator ready to sync annotated secrets
    Evidence: .sisyphus/evidence/task-10-replicator.txt
  ```

  **Commit**: YES (groups with Task 7)

- [x] 11. Cilium L2 configs as FluxCD Kustomization

  **What to do**:
  - Create `infrastructure/base/05-network/cilium-configs/` with:
    - `cilium-l2-announcement-policy.yaml` (from `pulumi/components/cilium_l2.py`)
    - `cilium-loadbalancer-ip-pool.yaml` (from `pulumi/components/cilium_l2.py`)
  - Platform overlays: baremetal has specific interfaces (enp7s0) and IP ranges (192.168.0.x)
  - k3d/rancher-desktop may not need L2 configs at all (conditional include)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 7-10)
  - **Parallel Group**: Wave 1
  - **Blocks**: None directly
  - **Blocked By**: Task 5

  **References**:
  - `pulumi/components/cilium_l2.py` — Current L2 config manifests
  - `talos-fluxcd/infrastructure/base/cilium/configs/` — Legacy L2 configs

  **Acceptance Criteria**:
  ```
  Scenario: Cilium L2 policies applied
    Tool: Bash (kubectl)
    Steps:
      1. kubectl get ciliuml2announcementpolicies
      2. Assert: policy exists
      3. kubectl get ciliumloadbalancerippools
      4. Assert: pool exists with correct CIDR
    Expected Result: L2 networking configured via FluxCD
    Evidence: .sisyphus/evidence/task-11-cilium-l2.txt
  ```

  **Commit**: YES (groups with Task 7)

- [x] 12. Wave 1 rollback artifact + E2E gate

  **What to do**:
  - Create git tag: `post-wave1`
  - Export Pulumi state: `pulumi stack export > .sisyphus/backups/post-wave1.json`
  - Run full E2E suite: `pytest tests/e2e/ -v`
  - Verify no dual ownership (Pulumi + FluxCD on same resource)
  - Document wave 1 results

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (gate for Wave 2)
  - **Blocks**: Task 13
  - **Blocked By**: Tasks 7-11

  **Acceptance Criteria**:
  ```
  Scenario: Wave 1 gate passes
    Tool: Bash
    Steps:
      1. pytest tests/e2e/ -m prerequisites -v
      2. Assert: all pass
      3. flux get helmreleases -A
      4. Assert: cert-manager, ESO, kgateway, kubernetes-replicator all reconciled
    Expected Result: Wave 1 complete, safe to proceed
    Evidence: .sisyphus/evidence/task-12-wave1-gate.txt
  ```

  **Commit**: NO (verification only)

---

### Wave 2: TLS + Platform Helm Charts

- [x] 13. TLS CA chain as FluxCD manifests

  **What to do**:
  - Create `infrastructure/base/02-tls/ca-chain/` with:
    - `bootstrap-issuer.yaml` — self-signed ClusterIssuer
    - `ca-certificate.yaml` — CA Certificate from bootstrap issuer
    - `ca-issuer.yaml` — ClusterIssuer using the CA
  - Create `infrastructure/base/02-tls/wildcard-certs/` with per-plane wildcards
  - Platform overlay: baremetal uses `*.amernas.work`, others use `*.openchoreo.localhost`
  - Add replication annotations to the CA secret so kubernetes-replicator syncs it to plane namespaces
  - State handoff for TLS resources from Pulumi

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`senior-devops`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (must complete before Tasks 15-17)
  - **Parallel Group**: Wave 2 lead
  - **Blocks**: Tasks 15-17
  - **Blocked By**: Task 12

  **References**:
  - `pulumi/components/tls_setup.py` — Current TLS CA chain definition
  - `talos-fluxcd/infrastructure/base/cert-manager/configs/` — Legacy cert-manager configs/issuers

  **Acceptance Criteria**:
  ```
  Scenario: CA chain established and replicated
    Tool: Bash (kubectl)
    Steps:
      1. kubectl get clusterissuers
      2. Assert: openchoreo-bootstrap-issuer and openchoreo-ca exist, Ready=True
      3. kubectl get secrets cluster-gateway-ca -n openchoreo-control-plane
      4. Assert: TLS secret exists with ca.crt
      5. kubectl get secrets cluster-gateway-ca -n openchoreo-data-plane
      6. Assert: replicated by kubernetes-replicator
    Expected Result: CA chain working, secrets replicated across namespaces
    Evidence: .sisyphus/evidence/task-13-tls-chain.txt
  ```

  **Commit**: YES — `feat(gitops): add TLS CA chain as FluxCD manifests`

- [x] 14. Docker Registry FluxCD HelmRelease

  **What to do**:
  - Create `infrastructure/base/03-platform/workflow-plane/registry-helmrelease.yaml`
  - Simple Helm chart, values from `pulumi/values/registry.py`
  - State handoff from Pulumi

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 13)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 17
  - **Blocked By**: Task 12

  **References**:
  - `pulumi/values/registry.py` — Docker registry Helm values

  **Acceptance Criteria**:
  ```
  Scenario: Docker registry running via FluxCD
    Tool: Bash
    Steps:
      1. flux get helmreleases -n openchoreo-workflow-plane | grep registry
      2. Assert: reconciled
    Expected Result: Registry running under FluxCD
    Evidence: .sisyphus/evidence/task-14-registry.txt
  ```

  **Commit**: YES (groups with Task 13)

- [x] 15. Control Plane FluxCD HelmRelease + values ConfigMap

  **What to do**:
  - Create `infrastructure/base/03-platform/control-plane/helmrelease.yaml`
  - Convert dynamic values from `pulumi/values/control_plane.py` to static YAML ConfigMap
  - Use Flux `valuesFrom` to reference the ConfigMap for platform-specific values
  - `spec.releaseName` must match Pulumi's existing release name
  - CP depends on: cert-manager (TLS), ESO (ExternalSecrets), kgateway (Gateway API), Thunder (IdP — Pulumi-managed)
  - Backstage ExternalSecret manifest included (references OpenBao via ClusterSecretStore)
  - State handoff from Pulumi

  **Must NOT do**:
  - DO NOT move Thunder install/bootstrap (stays in Pulumi)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`senior-devops`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 13 TLS)
  - **Parallel Group**: Wave 2 (after TLS)
  - **Blocks**: Task 19 (plane registration)
  - **Blocked By**: Task 13

  **References**:
  - `pulumi/values/control_plane.py` — Dynamic Helm values (ALL must be converted to static)
  - `pulumi/components/control_plane.py` — CP deployment logic, Thunder dependency
  - `pulumi/config.py` — All dynamic config values used by CP

  **Acceptance Criteria**:
  ```
  Scenario: Control Plane reconciled by FluxCD
    Tool: Bash
    Steps:
      1. flux get helmreleases -n openchoreo-control-plane
      2. Assert: openchoreo-control-plane reconciled
      3. kubectl get pods -n openchoreo-control-plane
      4. Assert: all CP pods Running
    Expected Result: CP healthy under FluxCD
    Evidence: .sisyphus/evidence/task-15-cp-flux.txt
  ```

  **Commit**: YES — `feat(gitops): add CP/DP/WP FluxCD HelmReleases`

- [x] 16. Data Plane FluxCD HelmRelease + CA replication annotations

  **What to do**:
  - Create `infrastructure/base/03-platform/data-plane/helmrelease.yaml`
  - Convert values from `pulumi/values/data_plane.py` to static YAML
  - Add kubernetes-replicator annotation to CA secret for DP namespace replication
  - Include CiliumClusterwideNetworkPolicy (from `data_plane.py`)
  - State handoff from Pulumi

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`senior-devops`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 15, 17 after TLS)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 19
  - **Blocked By**: Tasks 10, 13

  **References**:
  - `pulumi/values/data_plane.py` — Dynamic Helm values
  - `pulumi/components/data_plane.py` — DP deployment + CiliumClusterwideNetworkPolicy + CA copy

  **Acceptance Criteria**:
  ```
  Scenario: Data Plane reconciled with replicated CA
    Tool: Bash
    Steps:
      1. flux get helmreleases -n openchoreo-data-plane
      2. Assert: reconciled
      3. kubectl get secrets cluster-gateway-ca -n openchoreo-data-plane
      4. Assert: CA secret exists (replicated)
    Expected Result: DP healthy with CA secret synced
    Evidence: .sisyphus/evidence/task-16-dp-flux.txt
  ```

  **Commit**: YES (groups with Task 15)

- [x] 17. Workflow Plane FluxCD HelmRelease + postBuild variables

  **What to do**:
  - Create `infrastructure/base/03-platform/workflow-plane/helmrelease.yaml`
  - Convert values from `pulumi/values/workflow_plane.py` to static YAML
  - Workflow templates: use Flux `postBuild.substitute` for `${REGISTRY_ENDPOINT}` and `${GATEWAY_ENDPOINT}`
  - Include workflow template manifests in gitops repo (downloaded from OpenChoreo release, with placeholder variables)
  - State handoff from Pulumi

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`senior-devops`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 15, 16 after TLS)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 23 (workflow template details)
  - **Blocked By**: Tasks 13, 14

  **References**:
  - `pulumi/values/workflow_plane.py` — Dynamic Helm values
  - `pulumi/components/workflow_plane.py:75-105` — sed-based workflow template patching logic

  **Acceptance Criteria**:
  ```
  Scenario: Workflow Plane reconciled with templates
    Tool: Bash
    Steps:
      1. flux get helmreleases -n openchoreo-workflow-plane
      2. Assert: reconciled
      3. kubectl get clusterworkflowtemplates
      4. Assert: workflow templates exist with correct endpoints (not placeholder vars)
    Expected Result: WP healthy with substituted template values
    Evidence: .sisyphus/evidence/task-17-wp-flux.txt
  ```

  **Commit**: YES (groups with Task 15)

- [x] 18. Wave 2 rollback artifact + E2E gate

  **What to do**:
  - Same as Task 12 but for Wave 2
  - Run: `pytest tests/e2e/ -v` (full suite including control_plane, data_plane, workflow_plane markers)
  - Verify all HelmReleases reconciled
  - Create git tag `post-wave2` + state backup

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (gate)
  - **Blocks**: Task 19
  - **Blocked By**: Tasks 13-17

  **Acceptance Criteria**:
  ```
  Scenario: Wave 2 gate passes
    Tool: Bash
    Steps:
      1. pytest tests/e2e/ -v
      2. Assert: all pass including plane-specific tests
    Expected Result: Wave 2 complete, safe to proceed
    Evidence: .sisyphus/evidence/task-18-wave2-gate.txt
  ```

  **Commit**: NO

---

### Wave 3: Registration + Observability + Linking

- [x] 19. Plane registration K8s Jobs (DP, WP, OP) + RBAC

  **What to do**:
  - Create `infrastructure/base/04-registration/register-planes/`:
    - `rbac.yaml` — ServiceAccount, ClusterRole, ClusterRoleBinding for Job to read secrets + create CRDs
    - `register-data-plane-job.yaml` — Job that: waits for `cluster-agent-tls` secret, reads `ca.crt`, creates ClusterDataPlane CRD
    - `register-workflow-plane-job.yaml` — Same pattern for ClusterWorkflowPlane
    - `register-observability-plane-job.yaml` — Same for ClusterObservabilityPlane
  - Each Job uses `kubectl` container image (bitnami/kubectl or similar)
  - FluxCD Kustomization for 04-registration has `dependsOn: [platform]` and `healthChecks` on Job completion
  - Jobs are idempotent (check if CRD exists before creating)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`senior-devops`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 20, 21)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 22 (linking needs registered planes)
  - **Blocked By**: Tasks 15-17

  **References**:
  - `pulumi/helpers/register_plane.py` — Current RegisterPlane logic
  - `pulumi/helpers/dynamic_providers.py` — RegisterPlane dynamic provider
  - `talos-fluxcd/infrastructure/base/` — Legacy patterns for K8s Jobs

  **Acceptance Criteria**:
  ```
  Scenario: All 3 plane registration Jobs completed
    Tool: Bash (kubectl)
    Steps:
      1. kubectl get jobs -n openchoreo-system | grep register
      2. Assert: register-data-plane, register-workflow-plane, register-observability-plane show 1/1 Completions
      3. kubectl get clusterdataplanes
      4. Assert: ClusterDataPlane exists
      5. kubectl get clusterworkflowplanes
      6. Assert: ClusterWorkflowPlane exists
    Expected Result: All planes registered via K8s Jobs
    Evidence: .sisyphus/evidence/task-19-register-planes.txt
  ```

  **Commit**: YES — `feat(gitops): add plane registration K8s Jobs with RBAC`

- [x] 20. Observability Plane FluxCD HelmReleases

  **What to do**:
  - Create `infrastructure/base/03-platform/observability-plane/`:
    - `openobserve-helmrelease.yaml` (or `opensearch-helmrelease.yaml` depending on config)
    - `prometheus-helmrelease.yaml`
    - `observer-helmrelease.yaml`
    - ExternalSecret manifests for observability secrets
  - Convert values from `pulumi/values/observability_plane.py` to static YAML
  - Platform overlays: baremetal uses OpenObserve, k3d may use OpenSearch
  - State handoff from Pulumi

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`senior-devops`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 19, 21)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 22 (linking includes OP)
  - **Blocked By**: Task 13 (TLS for observability)

  **References**:
  - `pulumi/values/observability_plane.py` — Dynamic Helm values for all observability components
  - `pulumi/components/observability_plane.py` — Full observability deployment logic

  **Acceptance Criteria**:
  ```
  Scenario: Observability stack reconciled
    Tool: Bash
    Steps:
      1. flux get helmreleases -n openchoreo-observability-plane
      2. Assert: all observability HelmReleases reconciled
      3. kubectl get pods -n openchoreo-observability-plane
      4. Assert: all pods Running
    Expected Result: Full observability stack under FluxCD
    Evidence: .sisyphus/evidence/task-20-observability.txt
  ```

  **Commit**: YES — `feat(gitops): add observability plane FluxCD HelmReleases`

- [x] 21. Odigos FluxCD HelmRelease

  **What to do**:
  - Create `infrastructure/base/03-platform/odigos/helmrelease.yaml`
  - Simple HelmRelease, conditional on platform (optional component)
  - State handoff from Pulumi

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 19, 20)
  - **Parallel Group**: Wave 3
  - **Blocks**: None
  - **Blocked By**: Task 12

  **References**:
  - `pulumi/components/odigos.py` — Current Odigos deployment

  **Acceptance Criteria**:
  ```
  Scenario: Odigos reconciled (if enabled)
    Tool: Bash
    Steps:
      1. flux get helmreleases -A | grep odigos
      2. Assert: reconciled (or not present if platform doesn't enable it)
    Expected Result: Odigos managed by FluxCD
    Evidence: .sisyphus/evidence/task-21-odigos.txt
  ```

  **Commit**: YES (groups with Task 20)

- [x] 22. Link Planes K8s Job + RBAC

  **What to do**:
  - Create `infrastructure/base/04-registration/link-planes/`:
    - `rbac.yaml` — ServiceAccount, Role for patching plane CRDs
    - `link-planes-job.yaml` — Job that patches ClusterDataPlane and ClusterWorkflowPlane with `observabilityPlaneRef`
  - Job uses kubectl to JSON-patch the plane CRDs
  - Depends on all 3 plane registration Jobs completing
  - Idempotent (checks if already linked)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`senior-devops`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (after Tasks 19, 20)
  - **Blocks**: Task 25
  - **Blocked By**: Tasks 19, 20

  **References**:
  - `pulumi/components/link_planes.py` — Current link planes logic
  - `pulumi/helpers/register_plane.py` — Plane CRD structure

  **Acceptance Criteria**:
  ```
  Scenario: Planes linked successfully
    Tool: Bash (kubectl)
    Steps:
      1. kubectl get jobs -n openchoreo-system | grep link-planes
      2. Assert: 1/1 Completions
      3. kubectl get clusterdataplanes -o jsonpath='{.items[0].spec.observabilityPlaneRef}'
      4. Assert: observabilityPlaneRef is set
    Expected Result: All planes linked
    Evidence: .sisyphus/evidence/task-22-link-planes.txt
  ```

  **Commit**: YES (groups with Task 19)

- [x] 23. Workflow templates with Flux postBuild substitution

  **What to do**:
  - Download OpenChoreo workflow templates from release
  - Replace hardcoded endpoints with Flux variables: `${REGISTRY_ENDPOINT}`, `${GATEWAY_ENDPOINT}`
  - Commit templates to gitops repo under `infrastructure/base/03-platform/workflow-plane/templates/`
  - FluxCD Kustomization for workflow-plane uses `postBuild.substituteFrom` ConfigMap
  - Document: when upgrading OpenChoreo, templates must be re-downloaded and variable-patched

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`senior-devops`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 19-22)
  - **Parallel Group**: Wave 3
  - **Blocks**: None
  - **Blocked By**: Task 17

  **References**:
  - `pulumi/components/workflow_plane.py:75-105` — Current sed-based template patching

  **Acceptance Criteria**:
  ```
  Scenario: Workflow templates have correct substituted values
    Tool: Bash (kubectl)
    Steps:
      1. kubectl get clusterworkflowtemplates -o yaml | grep -c '${' 
      2. Assert: 0 (no unsubstituted variables)
      3. kubectl get clusterworkflowtemplates -o yaml | grep REGISTRY_ENDPOINT
      4. Assert: 0 (variable was substituted with actual value)
    Expected Result: Templates deployed with actual endpoint values
    Evidence: .sisyphus/evidence/task-23-workflow-templates.txt
  ```

  **Commit**: YES — `feat(gitops): add workflow templates with Flux variable substitution`

- [x] 24. Wave 3 rollback artifact + E2E gate

  **What to do**: Same as Task 12/18 but for Wave 3. Full E2E suite. Git tag `post-wave3` + state backup.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (gate)
  - **Blocks**: Task 25
  - **Blocked By**: Tasks 19-23

  **Acceptance Criteria**:
  ```
  Scenario: Wave 3 gate passes
    Tool: Bash
    Steps:
      1. pytest tests/e2e/ -v
      2. Assert: all pass
      3. flux get kustomizations -A && flux get helmreleases -A
      4. Assert: everything reconciled
    Expected Result: Wave 3 complete
    Evidence: .sisyphus/evidence/task-24-wave3-gate.txt
  ```

  **Commit**: NO

---

### Wave 4: Cleanup + Final

- [x] 25. Strip Pulumi: remove all migrated components from code

  **What to do**:
  - With `fluxcd_manages_infra=True` confirmed working, remove dead code:
    - Delete: `components/prerequisites.py` (cert-manager, ESO, kgateway sections — keep OpenBao, Thunder, PushSecrets)
    - Delete: `components/tls_setup.py` (moved to FluxCD)
    - Delete: `components/control_plane.py` (CP section — keep Thunder section)
    - Delete: `components/data_plane.py` (moved to FluxCD)
    - Delete: `components/workflow_plane.py` (moved to FluxCD)
    - Delete: `components/observability_plane.py` (moved to FluxCD)
    - Delete: `components/cilium_l2.py` (moved to FluxCD)
    - Delete: `components/link_planes.py` (moved to FluxCD)
    - Delete: `components/odigos.py` (moved to FluxCD)
    - Delete: `components/flux_gitops.py` (bootstrap moved to Phase 1)
    - Delete: `helpers/copy_ca.py` (replaced by kubernetes-replicator)
    - Delete: `helpers/register_plane.py` (replaced by K8s Jobs)
    - Delete: `values/control_plane.py`, `values/data_plane.py`, `values/workflow_plane.py`, `values/observability_plane.py`, `values/registry.py`
  - Clean corresponding Pulumi state entries
  - Keep: `components/cilium.py`, `values/openbao.py`, Thunder-related code, PushSecret code

  **Must NOT do**:
  - DO NOT delete until ALL waves pass E2E
  - DO NOT delete OpenBao or Thunder related code

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 26)
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 27
  - **Blocked By**: Task 24

  **References**:
  - `pulumi/__main__.py` — Full orchestrator
  - All `pulumi/components/*.py` files
  - All `pulumi/values/*.py` files

  **Acceptance Criteria**:
  ```
  Scenario: Pulumi codebase is Phase 1 only
    Tool: Bash
    Steps:
      1. ls pulumi/components/
      2. Assert: only cilium.py, integration_tests.py (temporary), and OpenBao/Thunder-related files remain
      3. pulumi preview -s talos-baremetal
      4. Assert: only Phase 1 resources in preview (Cilium, OpenBao, Thunder, FluxCD bootstrap)
    Expected Result: Lean Pulumi with only imperative bootstrap
    Evidence: .sisyphus/evidence/task-25-pulumi-stripped.txt
  ```

  **Commit**: YES — `refactor(pulumi): remove all FluxCD-migrated components`

- [x] 26. Update Pulumi __main__.py to Phase 1 only flow

  **What to do**:
  - Rewrite `__main__.py` to reflect the new Phase 1 only flow:
    1. Step 0: Cilium CNI
    2. Step 1: OpenBao + seeding
    3. Step 2: Thunder + bootstrap
    4. Step 3: PushSecrets + ClusterSecretStore + seed secrets
    5. Step 4: FluxCD bootstrap (install controllers + GitRepository + root Kustomization)
  - Remove the `fluxcd_manages_infra` feature flag (it's now the only mode)
  - Remove Steps 2-9 from the old flow
  - Update docstrings and comments

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 25)
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 27
  - **Blocked By**: Task 24

  **References**:
  - `pulumi/__main__.py` — Current full orchestrator
  - `pulumi/talos-cluster-baremetal/__main__.py` — Phase 0 (Talos) reference

  **Acceptance Criteria**:
  ```
  Scenario: Clean Phase 1 pulumi up
    Tool: Bash
    Steps:
      1. pulumi up -s talos-baremetal --yes
      2. Assert: 0 errors
      3. Assert: only Phase 1 resources created/updated
    Expected Result: Clean Phase 1 deployment
    Evidence: .sisyphus/evidence/task-26-phase1-pulumi.txt
  ```

  **Commit**: YES (groups with Task 25)

- [x] 27. Full E2E test suite run + drift healing test

  **What to do**:
  - Run complete E2E suite: `pytest tests/e2e/ -v`
  - Run drift healing test: delete cert-manager deployment, wait 2min, verify recreated
  - Verify all FluxCD resources: `flux get all -A`
  - Verify Pulumi state: only Phase 1 URNs
  - Verify no dual ownership

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (after Tasks 25-26)
  - **Blocks**: Task 28
  - **Blocked By**: Tasks 25-26

  **Acceptance Criteria**:
  ```
  Scenario: Complete system verification
    Tool: Bash
    Steps:
      1. pytest tests/e2e/ -v — Assert: all pass
      2. flux get all -A — Assert: all Ready/Reconciled
      3. kubectl delete deployment cert-manager -n cert-manager
      4. sleep 120
      5. kubectl get deployment cert-manager -n cert-manager — Assert: recreated
      6. pulumi stack export | jq URNs — Assert: only Phase 1
    Expected Result: Full system healthy, drift healing working
    Evidence: .sisyphus/evidence/task-27-full-verification.txt
  ```

  **Commit**: NO (verification only)

- [x] 28. Documentation update (README, deployment guide)

  **What to do**:
  - Update project README with new 2-phase architecture
  - Document the new deployment flow: Phase 1 (Pulumi) → Phase 2 (FluxCD)
  - Document gitops repo structure
  - Document rollback procedures
  - Document how to add new platform overlays
  - Document workflow template upgrade process

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (after Task 27)
  - **Blocks**: FINAL
  - **Blocked By**: Task 27

  **Acceptance Criteria**:
  ```
  Scenario: Documentation is complete
    Tool: Bash
    Steps:
      1. Verify README.md has updated architecture section
      2. Verify deployment guide covers both phases
    Expected Result: Complete documentation
    Evidence: .sisyphus/evidence/task-28-docs.txt
  ```

  **Commit**: YES — `docs: update README and deployment guide for FluxCD-first architecture`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns. Check evidence files. Compare deliverables against plan. Verify no resource has dual Pulumi+FluxCD ownership.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Validate all FluxCD manifests: `flux validate --path infrastructure/`. Run `pulumi preview` on stripped Pulumi. Lint all YAML. Check for hardcoded secrets, platform-specific values in base manifests, missing `dependsOn` chains.
  Output: `Flux Validate [PASS/FAIL] | Pulumi Preview [PASS/FAIL] | YAML Lint [PASS/FAIL] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Execute full E2E: `pytest tests/e2e/ -v`. Verify every FluxCD HelmRelease is reconciled. Test drift healing (delete cert-manager deployment → verify recreation). Verify plane registration Jobs completed. Verify Link Planes Job completed. Save all output to `.sisyphus/evidence/final-qa/`.
  Output: `E2E Tests [N/N pass] | HelmReleases [N/N reconciled] | Drift Heal [PASS/FAIL] | Jobs [N/N completed] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  For each wave: verify git tag exists, Pulumi state backup exists. Verify no Pulumi URNs remain for migrated components. Verify no FluxCD-managed resource has Pulumi annotations. Verify all 4 platform overlays exist and are syntactically valid. Flag unaccounted changes.
  Output: `Waves [N/N clean] | State [CLEAN/N orphans] | Overlays [4/4 valid] | VERDICT`

---

## Commit Strategy

- **Wave 0**: `feat(gitops): add FluxCD infrastructure layer structure to openchoreo-gitops`
- **Wave 0**: `refactor(pulumi): consolidate Phase 1 (Talos+Cilium+OpenBao+Thunder+secrets)`
- **Wave 0**: `test: extract integration tests to standalone pytest E2E suite`
- **Wave 1**: `feat(gitops): add cert-manager + ESO + kgateway FluxCD HelmReleases`
- **Wave 1**: `feat(gitops): add kubernetes-replicator + Cilium L2 configs`
- **Wave 2**: `feat(gitops): add TLS CA chain + platform plane HelmReleases (CP/DP/WP)`
- **Wave 3**: `feat(gitops): add plane registration/linking Jobs + observability + workflow templates`
- **Wave 4**: `refactor(pulumi): remove all migrated components, Phase 1 only`
- **Wave 4**: `docs: update README and deployment guide for FluxCD-first architecture`

---

## Success Criteria

### Verification Commands
```bash
# FluxCD Kustomizations all Ready
flux get kustomizations -A  # Expected: all Ready=True

# FluxCD HelmReleases all reconciled
flux get helmreleases -A  # Expected: all Release reconciliation succeeded

# All platform pods running
kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded  # Expected: empty

# E2E tests pass
pytest tests/e2e/ -v  # Expected: all pass

# Pulumi state clean
pulumi stack export -s talos-baremetal | jq '.deployment.resources[].urn' | grep -v "talos\|cilium\|openbao\|thunder\|flux-bootstrap\|pushsecret\|clustersecretstore"  # Expected: empty

# Drift healing works
kubectl delete deployment cert-manager -n cert-manager && sleep 120 && kubectl get deployment cert-manager -n cert-manager  # Expected: recreated
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All FluxCD Kustomizations Ready
- [ ] All FluxCD HelmReleases reconciled
- [ ] All E2E tests pass
- [ ] Pulumi state contains only Phase 1 resources
- [ ] Drift healing verified
- [ ] All 4 platform overlays working
