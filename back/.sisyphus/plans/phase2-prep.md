# Phase 2 Preparation — Longhorn Storage + Cilium Skip Flag

## TL;DR

> **Quick Summary**: Add Longhorn storage to Phase 1 (talos-cluster-baremetal) and a `cilium_pre_installed` flag to Phase 2 (OpenChoreo installer) so that Phase 2 can deploy without Cilium conflicts and with a working default StorageClass for PVCs.
> 
> **Deliverables**:
> - Longhorn v1.9.1 Helm release in `pulumi/talos-cluster-baremetal/__main__.py` (namespace, CRDs, Helm release, VolumeSnapshotClass)
> - `cilium_pre_installed` field on `PlatformProfile` (types.py) set to `True` for talos-baremetal
> - Step 0 guard in `pulumi/__main__.py` that skips Cilium+Gateway CRDs when pre-installed
> 
> **Estimated Effort**: Medium (7 tasks, ~2 hours implementation)
> **Parallel Execution**: YES - 2 waves + final verification
> **Critical Path**: Task 1 → Task 2 → Task 3 → Task 5 → Task 6 → Task 7 → F1-F4

---

## Context

### Original Request
User wants to prepare for OpenChoreo Phase 2 by resolving two blockers:
1. No StorageClass exists — Phase 2 PVCs (Thunder, Docker Registry) need one
2. Phase 1 already installs Cilium v1.17.6, but Phase 2 tries to install Cilium v1.19.2 — conflict

### Interview Summary
**Key Discussions**:
- Longhorn goes in Phase 1 (`talos-cluster-baremetal/__main__.py`) after Cilium, using the same `k8s.helm.v3.Release` pattern
- 1:1 mapping from FluxCD reference configs at `/Users/yamer003/Desktop/personal-projects/talos-fluxcd/infrastructure/base/longhorn`
- Namespace created explicitly with pod-security `privileged` labels (user chose this over Helm auto-create)
- VolumeSnapshotClass + external-snapshotter included (user chose to include)
- CiliumLoadBalancerIPPool + L2AnnouncementPolicy deferred — handle later if needed
- Skip flag: `cilium_pre_installed: bool = False` on PlatformProfile (not raw config flag) — matches codebase design philosophy

**Research Findings**:
- Phase 1 Cilium uses `k8s.helm.v3.Release` (server-side Helm) — Longhorn must use same pattern
- Phase 1 insertion point: after `cilium_secrets_ns_labels` (line 448), before Exports (line 450)
- Phase 2 Step 0 condition: `if cfg.platform.cni_mode == "cilium" or cfg.platform.gateway_mode == "cilium"` — hardcoded, no skip
- `prerequisites.py` already handles `gateway_mode=="cilium"` correctly (skips CRD install at line 71)
- Longhorn disk mount already prepared at OS level by `render_storage_patch()` in `patches.py`
- Longhorn reference config: chart v1.9.1, 1 replica, ext4, Retain, no overlays

### Metis Review
**Identified Gaps** (addressed):
- HTTPRoute doesn't belong in Phase 1 (no Gateway object) → **Deferred** — no HTTPRoute in this plan
- `csi.*.revisionHistoryLimit` not a valid Longhorn Helm value → **Dropped** from values
- `volumeBindingMode` not a Helm value → **Dropped** — accept `Immediate` default (fine for single-node)
- Snapshot-controller deployment needed, not just CRDs → **Included** in plan
- `defaultSettings.defaultDataPath` should be set to `/var/lib/longhorn` → **Added** to values
- Pulumi state risk: flag on existing stack could trigger delete → **Documented** as new-deployment-only flag
- FluxCD configs exist in separate repo (Metis looked in wrong repo) → **Confirmed** present at external path

---

## Work Objectives

### Core Objective
Enable Phase 2 (OpenChoreo) installation by providing a default StorageClass (Longhorn) and preventing Cilium reinstallation conflict on talos-baremetal.

### Concrete Deliverables
- `pulumi/talos-cluster-baremetal/__main__.py`: Longhorn namespace, external-snapshotter (CRDs + controller), Longhorn Helm release, VolumeSnapshotClass
- `pulumi/talos-cluster-baremetal/Pulumi.dev.yaml`: `longhorn_version: "1.9.1"` config key
- `pulumi/platforms/types.py`: `cilium_pre_installed: bool = False` field
- `pulumi/platforms/talos_baremetal.py`: `cilium_pre_installed=True`
- `pulumi/__main__.py`: Step 0 guard with `and not cfg.platform.cilium_pre_installed`

### Definition of Done
- [ ] `pulumi preview --stack dev` in `talos-cluster-baremetal/` shows new Longhorn resources, zero changes to existing
- [ ] `pytest tests/` in `talos-cluster-baremetal/` — all 16 existing tests pass
- [ ] `ruff check .` + `ruff format --check .` — zero violations in both projects
- [ ] `pulumi preview --stack talos-baremetal` in `pulumi/` shows Step 0 resources absent
- [ ] Python assertions confirm `cilium_pre_installed` defaults to `False` and is `True` for talos-baremetal

### Must Have
- Longhorn Helm release v1.9.1 with `defaultReplicaCount: 1`, `defaultClassReplicaCount: 1`, `defaultDataPath: /var/lib/longhorn`
- `longhorn-system` namespace with `pod-security.kubernetes.io/*: privileged` labels
- VolumeSnapshotClass `longhorn-snapshot-class` with Retain policy
- External-snapshotter CRDs + snapshot-controller deployment
- `cilium_pre_installed` field on PlatformProfile, `True` for talos-baremetal only
- Step 0 in Phase 2 skipped when `cilium_pre_installed=True`

### Must NOT Have (Guardrails)
- **No HTTPRoute** in Phase 1 — no parent Gateway exists; defer to Phase 2 or later
- **No CiliumLoadBalancerIPPool or L2AnnouncementPolicy** — explicitly deferred
- **No custom StorageClass** — accept Longhorn's default SC (it's the only SC, so it's default)
- **No `volumeBindingMode` in Helm values** — not a valid Helm value; `Immediate` is fine for single-node
- **No `csi.*.revisionHistoryLimit` in Helm values** — not a valid Longhorn Helm value
- **No `create_namespace=True` on Helm release** — namespace created explicitly for labels
- **No modifications to `patches.py`** — disk mount already correct and tested
- **No modifications to existing Phase 1 resources** (CRDs, Cilium, namespace labels)
- **No changes to `k3d.py`, `rancher_desktop.py`, `talos.py`, `resolver.py`** — inherit default `False`
- **No changes to `prerequisites.py`** — `gateway_mode=="cilium"` branch already correct
- **No changes to `components/cilium.py`** — guard is in `__main__.py`, not the component
- **No new dependencies in `pyproject.toml`** — `pulumi-kubernetes >=4,<5` covers everything
- **No `k8s.helm.v4.Chart`** — Phase 1 uses `k8s.helm.v3.Release` exclusively
- **No excessive comments or over-abstraction** — follow existing code style exactly

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES — `pytest tests/` in talos-cluster-baremetal (16 tests)
- **Automated tests**: Tests-after (regression check — existing tests must pass)
- **Framework**: pytest (already configured)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Infrastructure/Pulumi**: Use Bash — `pulumi preview`, `pytest`, `ruff`, Python assertions
- **Config verification**: Use Bash — Python one-liners to import and assert field values

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — Phase 2 skip flag, all independent):
├── Task 1: Add cilium_pre_installed field to PlatformProfile [quick]
├── Task 2: Set cilium_pre_installed=True for talos-baremetal [quick] (depends: Task 1)
├── Task 3: Guard Step 0 with cilium_pre_installed check [quick] (depends: Task 1)

Wave 2 (After Wave 1 — Phase 1 Longhorn stack, sequential within):
├── Task 4: Add longhorn_version config + longhorn-system namespace [quick]
├── Task 5: Add external-snapshotter CRDs + snapshot-controller [unspecified-high] (depends: Task 4)
├── Task 6: Add Longhorn Helm release [unspecified-high] (depends: Task 5)
├── Task 7: Add VolumeSnapshotClass [quick] (depends: Task 6)

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay

Critical Path: Task 1 → Task 2/3 → Task 4 → Task 5 → Task 6 → Task 7 → F1-F4 → user okay
Parallel Speedup: ~40% faster than sequential (Wave 1 tasks 2+3 in parallel)
Max Concurrent: 3 (Wave 1)
```

### Dependency Matrix

| Task | Blocked By | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 2, 3 | 1 |
| 2 | 1 | F1-F4 | 1 |
| 3 | 1 | F1-F4 | 1 |
| 4 | — | 5 | 2 |
| 5 | 4 | 6 | 2 |
| 6 | 5 | 7 | 2 |
| 7 | 6 | F1-F4 | 2 |

### Agent Dispatch Summary

- **Wave 1**: **3** — T1 → `quick`, T2 → `quick`, T3 → `quick`
- **Wave 2**: **4** — T4 → `quick`, T5 → `unspecified-high`, T6 → `unspecified-high`, T7 → `quick`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Add `cilium_pre_installed` field to PlatformProfile

  **What to do**:
  - Open `pulumi/platforms/types.py`
  - Add `cilium_pre_installed: bool = False` field to the `PlatformProfile` dataclass
  - Place it in the Networking/CNI section (after `cilium_l2_interfaces` field, around line 75)
  - Add a comment: `# Whether Cilium was pre-installed by Phase 1 (e.g. talos-cluster-baremetal)`
  - Run `ruff check pulumi/platforms/types.py` and `ruff format --check pulumi/platforms/types.py`

  **Must NOT do**:
  - Do NOT add this field to any platform factory files — only to the dataclass definition
  - Do NOT change the `frozen=True` decorator or any existing fields
  - Do NOT add type imports — `bool` is a builtin

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single-file, single-line addition to an existing dataclass
  - **Skills**: []
    - No domain-specific skills needed for a simple field addition

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (starts immediately)
  - **Blocks**: Tasks 2, 3
  - **Blocked By**: None

  **References**:

  **Pattern References** (existing code to follow):
  - `pulumi/platforms/types.py:71-75` — The "Bare-metal Cilium L2" section shows the exact pattern: field with `bool` type and default value, preceded by a comment. Add the new field immediately after `cilium_l2_interfaces: list[str] = field(default_factory=list)` (line 75)

  **API/Type References**:
  - `pulumi/platforms/types.py:11-75` — The full `PlatformProfile` dataclass definition. The class uses `@dataclass(frozen=True)` so all fields are read-only after construction.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Field exists and defaults to False
    Tool: Bash
    Preconditions: Working directory is pulumi/
    Steps:
      1. Run: python -c "from platforms.types import PlatformProfile; import inspect; sig = inspect.signature(PlatformProfile); assert 'cilium_pre_installed' in sig.parameters; assert sig.parameters['cilium_pre_installed'].default is False; print('PASS: field exists with default False')"
      2. Assert exit code 0 and output contains "PASS"
    Expected Result: Field exists on PlatformProfile with default value False
    Failure Indicators: ImportError, AttributeError, or AssertionError
    Evidence: .sisyphus/evidence/task-1-field-exists.txt

  Scenario: Ruff passes with no violations
    Tool: Bash
    Preconditions: ruff installed
    Steps:
      1. Run: ruff check pulumi/platforms/types.py
      2. Run: ruff format --check pulumi/platforms/types.py
      3. Assert both exit code 0
    Expected Result: Zero lint/format violations
    Failure Indicators: Non-zero exit code, violation output
    Evidence: .sisyphus/evidence/task-1-ruff.txt
  ```

  **Commit**: YES (commit 1)
  - Message: `feat(platform): add cilium_pre_installed field to PlatformProfile`
  - Files: `pulumi/platforms/types.py`
  - Pre-commit: `ruff check pulumi/platforms/types.py`

- [x] 2. Set `cilium_pre_installed=True` for talos-baremetal platform

  **What to do**:
  - Open `pulumi/platforms/talos_baremetal.py`
  - Add `cilium_pre_installed=True` to the `PlatformProfile(...)` constructor call
  - Place it logically near other Cilium-related fields (after `cilium_l2_interfaces` or similar)
  - Run `ruff check pulumi/platforms/talos_baremetal.py`

  **Must NOT do**:
  - Do NOT modify any other platform factory files (`k3d.py`, `rancher_desktop.py`, `talos.py`)
  - Do NOT change any existing field values in the talos-baremetal profile
  - Do NOT add comments beyond what's necessary for the constructor argument

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single-file, single-line addition to a constructor call
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 3, after Task 1)
  - **Parallel Group**: Wave 1 (after Task 1)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `pulumi/platforms/talos_baremetal.py:14-44` — The `talos_baremetal()` function constructs a `PlatformProfile(...)` with all fields. Add `cilium_pre_installed=True` near the other Cilium fields (`cni_mode="cilium"` at line 18, `cilium_auto_mount_bpf=False` at line 27, etc.)

  **API/Type References**:
  - `pulumi/platforms/types.py` — The PlatformProfile dataclass (modified by Task 1) defines the field

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: talos-baremetal profile has cilium_pre_installed=True
    Tool: Bash
    Preconditions: Task 1 completed, working directory is pulumi/
    Steps:
      1. Run: python -c "from platforms.talos_baremetal import talos_baremetal; p = talos_baremetal(); assert p.cilium_pre_installed is True; print('PASS: talos-baremetal has cilium_pre_installed=True')"
      2. Assert exit code 0 and output contains "PASS"
    Expected Result: talos-baremetal profile returns True for cilium_pre_installed
    Failure Indicators: ImportError, AssertionError, or TypeError
    Evidence: .sisyphus/evidence/task-2-talos-baremetal.txt

  Scenario: Other platforms still default to False
    Tool: Bash
    Preconditions: Task 1 completed, working directory is pulumi/
    Steps:
      1. Run: python -c "from platforms.k3d import k3d; p = k3d(); assert p.cilium_pre_installed is False; print('PASS: k3d defaults to False')"
      2. Run: python -c "from platforms.talos import talos; p = talos(); assert p.cilium_pre_installed is False; print('PASS: talos defaults to False')"
      3. Assert both exit code 0
    Expected Result: Non-baremetal platforms inherit False default
    Failure Indicators: AssertionError
    Evidence: .sisyphus/evidence/task-2-other-platforms.txt
  ```

  **Commit**: YES (commit 2)
  - Message: `feat(platform): set cilium_pre_installed=True for talos-baremetal`
  - Files: `pulumi/platforms/talos_baremetal.py`
  - Pre-commit: `ruff check pulumi/platforms/talos_baremetal.py`

- [x] 3. Guard Step 0 with `cilium_pre_installed` check (Phase 2)

  **What to do**:
  - Open `pulumi/__main__.py`
  - Find the Step 0 guard at line 41: `if cfg.platform.cni_mode == "cilium" or cfg.platform.gateway_mode == "cilium":`
  - Change it to: `if (cfg.platform.cni_mode == "cilium" or cfg.platform.gateway_mode == "cilium") and not cfg.platform.cilium_pre_installed:`
  - This skips the entire Step 0 block (Gateway API CRDs + Cilium Helm install) when the platform declares Cilium pre-installed
  - Run `ruff check pulumi/__main__.py` and `ruff format --check pulumi/__main__.py`

  **Must NOT do**:
  - Do NOT modify any other Step (1-8) in `__main__.py`
  - Do NOT modify `components/cilium.py` — the guard is here in `__main__.py`
  - Do NOT modify `components/prerequisites.py` — the `gateway_mode=="cilium"` branch at line 71 already correctly handles CRD skip
  - Do NOT change the indented block inside the if statement — only the condition on line 41
  - Do NOT add logging, print statements, or comments about the skip

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single-line condition change in an existing if statement
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 2, after Task 1)
  - **Parallel Group**: Wave 1 (after Task 1)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `pulumi/__main__.py:39-56` — Step 0 block. Line 41 is the condition. Lines 42-56 are the body (Gateway API CRDs + Cilium install). The entire body is skipped by the guard.

  **API/Type References**:
  - `pulumi/platforms/types.py` — `PlatformProfile.cilium_pre_installed` field (added by Task 1)
  - `pulumi/config.py:241` — `cfg.platform` is the resolved PlatformProfile

  **WHY Each Reference Matters**:
  - `__main__.py:39-56` — This is THE exact code being modified. The executor needs to see the full Step 0 block to understand what's being guarded.
  - `types.py` — Confirms the field name and type to use in the condition
  - `config.py:241` — Shows how `cfg.platform` is populated (via `resolve_platform`)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Step 0 condition includes cilium_pre_installed guard
    Tool: Bash
    Preconditions: Task 1 completed
    Steps:
      1. Run: grep -n "cilium_pre_installed" pulumi/__main__.py
      2. Assert output shows the guard on the Step 0 condition line
      3. Run: grep -c "and not cfg.platform.cilium_pre_installed" pulumi/__main__.py
      4. Assert count is exactly 1
    Expected Result: Guard appears exactly once on the Step 0 condition
    Failure Indicators: Count is 0 (not added) or >1 (duplicated)
    Evidence: .sisyphus/evidence/task-3-guard-check.txt

  Scenario: Ruff passes with no violations
    Tool: Bash
    Preconditions: File modified
    Steps:
      1. Run: ruff check pulumi/__main__.py
      2. Run: ruff format --check pulumi/__main__.py
      3. Assert both exit code 0
    Expected Result: Zero lint/format violations
    Failure Indicators: Non-zero exit code
    Evidence: .sisyphus/evidence/task-3-ruff.txt
  ```

  **Commit**: YES (commit 3)
  - Message: `feat(openchoreo): skip Cilium install when pre-installed by Phase 1`
  - Files: `pulumi/__main__.py`
  - Pre-commit: `ruff check pulumi/__main__.py`

- [x] 4. Add `longhorn_version` config + `longhorn-system` namespace (Phase 1)

  **What to do**:
  - Open `pulumi/talos-cluster-baremetal/__main__.py`
  - Add config variable around line 54 (after `cilium_version`): `longhorn_version = cfg.get("longhorn_version") or "1.9.1"`
  - After the `cilium_secrets_ns_labels` block (after line 448), add the `longhorn-system` namespace resource:
    ```python
    longhorn_ns = k8s.core.v1.Namespace(
        "longhorn-system",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name="longhorn-system",
            labels={
                "pod-security.kubernetes.io/enforce": "privileged",
                "pod-security.kubernetes.io/audit": "privileged",
                "pod-security.kubernetes.io/warn": "privileged",
            },
        ),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[cilium],
        ),
    )
    ```
  - Open `pulumi/talos-cluster-baremetal/Pulumi.dev.yaml`
  - Add: `openchoreo-talos-cluster-baremetal:longhorn_version: "1.9.1"`
  - Run `ruff check pulumi/talos-cluster-baremetal/__main__.py`

  **Must NOT do**:
  - Do NOT use `create_namespace=True` on the Helm release later — this namespace is created explicitly for labels
  - Do NOT modify `patches.py` — the disk mount is already configured
  - Do NOT modify any existing resources or their dependency chains
  - Do NOT add the namespace to the Exports section yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Config variable + single resource addition, straightforward
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (sequential within Wave 2)
  - **Parallel Group**: Wave 2 (first task)
  - **Blocks**: Task 5
  - **Blocked By**: None (can start immediately, parallel with Wave 1)

  **References**:

  **Pattern References**:
  - `pulumi/talos-cluster-baremetal/__main__.py:48` — `cilium_version = cfg.get("cilium_version") or "1.17.6"` — Exact pattern for config variable
  - `pulumi/talos-cluster-baremetal/__main__.py:436-448` — `cilium_secrets_ns_labels` NamespacePatch — Shows namespace resource pattern with labels and provider. Note: that one is a NamespacePatch (patching existing), ours is a `Namespace` (creating new)
  - `pulumi/talos-cluster-baremetal/Pulumi.dev.yaml:5` — `openchoreo-talos-cluster-baremetal:cilium_version: "1.17.6"` — Exact pattern for config key in stack YAML

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Config variable exists and reads version
    Tool: Bash
    Preconditions: File modified
    Steps:
      1. Run: grep -n "longhorn_version" pulumi/talos-cluster-baremetal/__main__.py
      2. Assert output shows the config read line
      3. Run: grep "longhorn_version" pulumi/talos-cluster-baremetal/Pulumi.dev.yaml
      4. Assert output shows "1.9.1"
    Expected Result: Config variable defined in both files
    Failure Indicators: grep returns empty
    Evidence: .sisyphus/evidence/task-4-config.txt

  Scenario: Namespace resource has correct labels
    Tool: Bash
    Preconditions: File modified
    Steps:
      1. Run: grep -A 10 '"longhorn-system"' pulumi/talos-cluster-baremetal/__main__.py | grep "pod-security"
      2. Assert output contains all three pod-security labels (enforce, audit, warn)
    Expected Result: All three pod-security.kubernetes.io labels present with "privileged" value
    Failure Indicators: Missing labels
    Evidence: .sisyphus/evidence/task-4-namespace.txt

  Scenario: Ruff passes
    Tool: Bash
    Steps:
      1. Run: ruff check pulumi/talos-cluster-baremetal/__main__.py
      2. Assert exit code 0
    Expected Result: Zero violations
    Evidence: .sisyphus/evidence/task-4-ruff.txt
  ```

  **Commit**: YES (commit 4)
  - Message: `feat(talos-baremetal): add longhorn-system namespace and config`
  - Files: `pulumi/talos-cluster-baremetal/__main__.py`, `pulumi/talos-cluster-baremetal/Pulumi.dev.yaml`
  - Pre-commit: `ruff check pulumi/talos-cluster-baremetal/__main__.py`

- [x] 5. Add external-snapshotter CRDs + snapshot-controller (Phase 1)

  **What to do**:
  - After the `longhorn_ns` resource in `pulumi/talos-cluster-baremetal/__main__.py`, add:
  - **Step A**: Install external-snapshotter CRDs via `k8s.yaml.v2.ConfigGroup` pointing to the GitHub release YAML:
    ```python
    SNAPSHOT_CRD_VERSION = "v8.3.0"
    snapshot_crds = k8s.yaml.v2.ConfigGroup(
        "external-snapshotter-crds",
        yaml=[
            f"https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/{SNAPSHOT_CRD_VERSION}/client/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml",
            f"https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/{SNAPSHOT_CRD_VERSION}/client/config/crd/snapshot.storage.k8s.io_volumesnapshotcontents.yaml",
            f"https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/{SNAPSHOT_CRD_VERSION}/client/config/crd/snapshot.storage.k8s.io_volumesnapshots.yaml",
        ],
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[longhorn_ns],
        ),
    )
    ```
  - **Step B**: Install snapshot-controller via `k8s.yaml.v2.ConfigGroup` (or individual resources):
    ```python
    snapshot_controller = k8s.yaml.v2.ConfigGroup(
        "snapshot-controller",
        yaml=[
            f"https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/{SNAPSHOT_CRD_VERSION}/deploy/kubernetes/snapshot-controller/rbac-snapshot-controller.yaml",
            f"https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/{SNAPSHOT_CRD_VERSION}/deploy/kubernetes/snapshot-controller/setup-snapshot-controller.yaml",
        ],
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[snapshot_crds],
        ),
    )
    ```
  - Run `ruff check pulumi/talos-cluster-baremetal/__main__.py`

  **Must NOT do**:
  - Do NOT use a Helm chart for external-snapshotter — the reference config uses raw CRD YAMLs, and the upstream project provides them as raw manifests
  - Do NOT install these into `longhorn-system` namespace — the controller goes to `kube-system` (default in the upstream manifest)
  - Do NOT pin to a different version than what's compatible with Longhorn v1.9.1 (v8.3.0 is compatible)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Needs to handle remote YAML URLs, verify compatibility, and manage the CRD + controller deployment correctly
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (second task, sequential)
  - **Blocks**: Task 6
  - **Blocked By**: Task 4

  **References**:

  **Pattern References**:
  - `pulumi/talos-cluster-baremetal/__main__.py:354-370` — Gateway API CRDs installed via `k8s.yaml.ConfigFile` (6 individual files). This is the pattern for installing remote CRD YAMLs. Note: Phase 1 uses `k8s.yaml.ConfigFile` (singular), but `k8s.yaml.v2.ConfigGroup` accepts a list and is cleaner for multiple files.

  **External References**:
  - GitHub: `https://github.com/kubernetes-csi/external-snapshotter/tree/v8.3.0/client/config/crd` — CRD definitions
  - GitHub: `https://github.com/kubernetes-csi/external-snapshotter/tree/v8.3.0/deploy/kubernetes/snapshot-controller` — Controller deployment manifests

  **WHY Each Reference Matters**:
  - `__main__.py:354-370` — Shows the existing pattern for applying remote CRD YAMLs with the k8s_provider. Use the same provider threading and depends_on pattern.
  - GitHub external-snapshotter — These are the actual upstream manifests. v8.3.0 is the latest compatible version with CSI snapshotter protocol used by Longhorn v1.9.1.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: External-snapshotter CRDs resource defined
    Tool: Bash
    Preconditions: Task 4 completed
    Steps:
      1. Run: grep -n "external-snapshotter-crds" pulumi/talos-cluster-baremetal/__main__.py
      2. Assert output shows ConfigGroup resource
      3. Run: grep "v8.3.0" pulumi/talos-cluster-baremetal/__main__.py
      4. Assert version reference exists
    Expected Result: ConfigGroup with 3 CRD URLs at v8.3.0
    Failure Indicators: Missing resource or wrong version
    Evidence: .sisyphus/evidence/task-5-crds.txt

  Scenario: Snapshot-controller resource defined
    Tool: Bash
    Preconditions: CRDs defined
    Steps:
      1. Run: grep -n "snapshot-controller" pulumi/talos-cluster-baremetal/__main__.py
      2. Assert output shows controller ConfigGroup
      3. Run: grep -A 3 "snapshot-controller" pulumi/talos-cluster-baremetal/__main__.py | grep "depends_on"
      4. Assert depends_on includes snapshot_crds
    Expected Result: Controller depends on CRDs
    Failure Indicators: Missing dependency chain
    Evidence: .sisyphus/evidence/task-5-controller.txt

  Scenario: Ruff passes
    Tool: Bash
    Steps:
      1. Run: ruff check pulumi/talos-cluster-baremetal/__main__.py
      2. Assert exit code 0
    Expected Result: Zero violations
    Evidence: .sisyphus/evidence/task-5-ruff.txt
  ```

  **Commit**: YES (commit 5)
  - Message: `feat(talos-baremetal): add external-snapshotter CRDs and controller`
  - Files: `pulumi/talos-cluster-baremetal/__main__.py`
  - Pre-commit: `ruff check pulumi/talos-cluster-baremetal/__main__.py`

- [x] 6. Add Longhorn v1.9.1 Helm release (Phase 1)

  **What to do**:
  - After the `snapshot_controller` resource in `pulumi/talos-cluster-baremetal/__main__.py`, add a `LONGHORN_VALUES` dict constant and the Helm release:
    ```python
    LONGHORN_VALUES = {
        "preUpgradeChecker": {
            "jobEnabled": False,
        },
        "defaultSettings": {
            "defaultReplicaCount": 1,
            "defaultDataPath": "/var/lib/longhorn",
        },
        "persistence": {
            "defaultFsType": "ext4",
            "reclaimPolicy": "Retain",
            "defaultClassReplicaCount": 1,
        },
    }

    longhorn = k8s.helm.v3.Release(
        "longhorn",
        name="longhorn",
        chart="longhorn",
        version=longhorn_version,
        namespace="longhorn-system",
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://charts.longhorn.io",
        ),
        values=LONGHORN_VALUES,
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[longhorn_ns, snapshot_controller],
        ),
    )
    ```
  - Key points:
    - Uses `k8s.helm.v3.Release` (NOT v4.Chart) — matching existing Cilium pattern
    - `namespace="longhorn-system"` — the namespace already exists from Task 4
    - NO `create_namespace=True` — namespace created explicitly in Task 4
    - `depends_on=[longhorn_ns, snapshot_controller]` — waits for namespace + snapshot CRDs/controller
    - `defaultDataPath: "/var/lib/longhorn"` — matches the Talos disk mount from `render_storage_patch()`
    - `defaultReplicaCount: 1` AND `defaultClassReplicaCount: 1` — both needed (they control different things: internal replica count vs StorageClass annotation)
  - Run `ruff check` and `pytest tests/`

  **Must NOT do**:
  - Do NOT use `k8s.helm.v4.Chart` — Phase 1 uses v3.Release exclusively
  - Do NOT add `create_namespace=True` — namespace created in Task 4 with pod-security labels
  - Do NOT add `volumeBindingMode` to values — not a valid Helm value
  - Do NOT add `csi.*.revisionHistoryLimit` to values — not a valid Helm value
  - Do NOT add more Helm values than specified — keep it minimal, matching the validated reference
  - Do NOT place `LONGHORN_VALUES` inside the Helm release call — define it as a top-level constant (matching `CILIUM_VALUES` pattern at line 375)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Helm release configuration requires careful value mapping and dependency threading
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (third task, sequential)
  - **Blocks**: Task 7
  - **Blocked By**: Task 5

  **References**:

  **Pattern References**:
  - `pulumi/talos-cluster-baremetal/__main__.py:375-414` — `CILIUM_VALUES` dict. This is the exact pattern for defining Helm values as a top-level constant. The Longhorn values dict should follow the same style.
  - `pulumi/talos-cluster-baremetal/__main__.py:417-431` — Cilium `k8s.helm.v3.Release`. This is the exact pattern for the Helm release resource including `repository_opts`, `values`, and `opts` with `provider` and `depends_on`.
  - `pulumi/talos-cluster-baremetal/patches.py:79-106` — `render_storage_patch()` mounts the Longhorn disk at `/var/lib/longhorn`. The `defaultDataPath` value MUST match this path.

  **External References**:
  - Longhorn Helm chart values: `https://github.com/longhorn/charts/blob/longhorn-1.9.1/charts/longhorn/values.yaml` — Full default values reference. Only override what's in our LONGHORN_VALUES dict.

  **WHY Each Reference Matters**:
  - `CILIUM_VALUES` pattern — Shows code style for value dicts (Python dicts, not YAML)
  - Cilium Helm release — Shows the exact Pulumi resource constructor pattern to replicate
  - `render_storage_patch()` — Confirms `/var/lib/longhorn` is the correct data path
  - Upstream values.yaml — Validates that our overrides are valid keys

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: LONGHORN_VALUES dict has correct structure
    Tool: Bash
    Preconditions: File modified
    Steps:
      1. Run: python3 -c "
    import ast, sys
    with open('pulumi/talos-cluster-baremetal/__main__.py') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'LONGHORN_VALUES':
                    print('PASS: LONGHORN_VALUES found')
                    sys.exit(0)
    print('FAIL: LONGHORN_VALUES not found')
    sys.exit(1)
    "
      2. Assert exit code 0
    Expected Result: LONGHORN_VALUES is a top-level constant assignment
    Failure Indicators: Not found or defined inline
    Evidence: .sisyphus/evidence/task-6-values.txt

  Scenario: Helm release uses v3.Release (not v4.Chart)
    Tool: Bash
    Preconditions: File modified
    Steps:
      1. Run: grep -n "helm.v3.Release" pulumi/talos-cluster-baremetal/__main__.py | grep -i longhorn
      2. Assert output shows longhorn Helm release using v3
      3. Run: grep -c "helm.v4.Chart" pulumi/talos-cluster-baremetal/__main__.py
      4. Assert count is 0
    Expected Result: Longhorn uses v3.Release, no v4.Chart anywhere in file
    Failure Indicators: v4.Chart found, or longhorn not using v3.Release
    Evidence: .sisyphus/evidence/task-6-helm-version.txt

  Scenario: Forbidden values NOT present
    Tool: Bash
    Preconditions: File modified
    Steps:
      1. Run: grep -c "revisionHistoryLimit" pulumi/talos-cluster-baremetal/__main__.py
      2. Assert count is 0
      3. Run: grep -c "volumeBindingMode" pulumi/talos-cluster-baremetal/__main__.py
      4. Assert count is 0
    Expected Result: Invalid Helm values not present
    Failure Indicators: Non-zero count for forbidden values
    Evidence: .sisyphus/evidence/task-6-forbidden-values.txt

  Scenario: All 16 existing tests still pass
    Tool: Bash
    Preconditions: File modified
    Steps:
      1. Run: cd pulumi/talos-cluster-baremetal && pytest tests/
      2. Assert "16 passed" in output and exit code 0
    Expected Result: Zero test regressions
    Failure Indicators: Any test failure or error
    Evidence: .sisyphus/evidence/task-6-tests.txt

  Scenario: Ruff passes
    Tool: Bash
    Steps:
      1. Run: ruff check pulumi/talos-cluster-baremetal/__main__.py
      2. Assert exit code 0
    Expected Result: Zero violations
    Evidence: .sisyphus/evidence/task-6-ruff.txt
  ```

  **Commit**: YES (commit 6)
  - Message: `feat(talos-baremetal): add Longhorn v1.9.1 Helm release`
  - Files: `pulumi/talos-cluster-baremetal/__main__.py`
  - Pre-commit: `pytest tests/ && ruff check pulumi/talos-cluster-baremetal/__main__.py`

- [x] 7. Add VolumeSnapshotClass (Phase 1)

  **What to do**:
  - After the `longhorn` Helm release in `pulumi/talos-cluster-baremetal/__main__.py`, add the VolumeSnapshotClass:
    ```python
    longhorn_snapshot_class = k8s.apiextensions.CustomResource(
        "longhorn-snapshot-class",
        api_version="snapshot.storage.k8s.io/v1",
        kind="VolumeSnapshotClass",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name="longhorn-snapshot-class",
        ),
        others={
            "driver": "driver.longhorn.io",
            "deletionPolicy": "Retain",
            "parameters": {
                "type": "snap",
            },
        },
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[longhorn, snapshot_crds],
        ),
    )
    ```
  - The VolumeSnapshotClass depends on both the Longhorn Helm release (for the driver) and the snapshot CRDs (for the CRD definition)
  - Run `ruff check`, `ruff format --check`, and `pytest tests/`

  **Must NOT do**:
  - Do NOT use `k8s.yaml.ConfigFile` or raw YAML — use `k8s.apiextensions.CustomResource` for type safety
  - Do NOT create additional VolumeSnapshotClasses — only `longhorn-snapshot-class`
  - Do NOT set this as a default VolumeSnapshotClass annotation — it's the only one, no annotation needed

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single CustomResource addition with known spec
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (fourth/final task, sequential)
  - **Blocks**: F1-F4
  - **Blocked By**: Task 6

  **References**:

  **Pattern References**:
  - `/Users/yamer003/Desktop/personal-projects/talos-fluxcd/infrastructure/base/longhorn/volumesnapshotclass/longhorn-volumesnapshotclass.yaml` — The exact VolumeSnapshotClass manifest from the Flux reference config. Fields: `driver: driver.longhorn.io`, `deletionPolicy: Retain`, `parameters.type: snap`.

  **API/Type References**:
  - `k8s.apiextensions.CustomResource` — Pulumi's generic CRD resource. Used for any custom Kubernetes resource. The `others` parameter holds spec fields that aren't part of the standard metadata/apiVersion/kind.

  **WHY Each Reference Matters**:
  - Flux reference — This is the source of truth for the VolumeSnapshotClass spec. 1:1 mapping required.
  - CustomResource API — The executor needs to know the Pulumi resource type and how to map YAML fields to Python args.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: VolumeSnapshotClass resource defined correctly
    Tool: Bash
    Preconditions: Tasks 5-6 completed
    Steps:
      1. Run: grep -n "longhorn-snapshot-class" pulumi/talos-cluster-baremetal/__main__.py
      2. Assert output shows CustomResource definition
      3. Run: grep -A 5 "longhorn-snapshot-class" pulumi/talos-cluster-baremetal/__main__.py | grep "driver.longhorn.io"
      4. Assert driver reference exists
    Expected Result: VolumeSnapshotClass with correct driver and parameters
    Failure Indicators: Missing resource or wrong driver
    Evidence: .sisyphus/evidence/task-7-snapshot-class.txt

  Scenario: Dependency chain correct
    Tool: Bash
    Preconditions: Resource defined
    Steps:
      1. Run: grep -A 10 "longhorn-snapshot-class" pulumi/talos-cluster-baremetal/__main__.py | grep "depends_on"
      2. Assert depends_on includes both longhorn and snapshot_crds
    Expected Result: VolumeSnapshotClass depends on Longhorn Helm release and snapshot CRDs
    Failure Indicators: Missing dependencies
    Evidence: .sisyphus/evidence/task-7-deps.txt

  Scenario: All 16 existing tests still pass + ruff clean
    Tool: Bash
    Steps:
      1. Run: cd pulumi/talos-cluster-baremetal && pytest tests/
      2. Assert "16 passed" and exit code 0
      3. Run: ruff check pulumi/talos-cluster-baremetal/__main__.py
      4. Assert exit code 0
      5. Run: ruff format --check pulumi/talos-cluster-baremetal/__main__.py
      6. Assert exit code 0
    Expected Result: All tests pass, zero lint/format violations
    Failure Indicators: Test failures or lint violations
    Evidence: .sisyphus/evidence/task-7-tests-ruff.txt
  ```

  **Commit**: YES (commit 7)
  - Message: `feat(talos-baremetal): add Longhorn VolumeSnapshotClass`
  - Files: `pulumi/talos-cluster-baremetal/__main__.py`
  - Pre-commit: `pytest tests/ && ruff check pulumi/talos-cluster-baremetal/__main__.py`

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run `pulumi preview`). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in `.sisyphus/evidence/`. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `ruff check .` + `ruff format --check .` in both `pulumi/` and `pulumi/talos-cluster-baremetal/`. Run `pytest tests/` in `pulumi/talos-cluster-baremetal/`. Review all changed files for: `as any`, empty catches, commented-out code, unused imports, AI slop (excessive comments, over-abstraction, generic names). Verify `k8s.helm.v3.Release` is used (not v4.Chart).
  Output: `Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Run `pulumi preview --stack dev` in `pulumi/talos-cluster-baremetal/` — verify Longhorn resources appear, existing resources unchanged. Run Python assertions for `cilium_pre_installed` field defaults. Run `pulumi preview --stack talos-baremetal` in `pulumi/` — verify Step 0 resources absent. Save all output to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (`git diff`). Verify 1:1 — everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance. Detect cross-task contamination. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

| # | Message | Files | Pre-commit |
|---|---------|-------|-----------|
| 1 | `feat(platform): add cilium_pre_installed field to PlatformProfile` | `pulumi/platforms/types.py` | `ruff check pulumi/platforms/types.py` |
| 2 | `feat(platform): set cilium_pre_installed=True for talos-baremetal` | `pulumi/platforms/talos_baremetal.py` | `ruff check pulumi/platforms/talos_baremetal.py` |
| 3 | `feat(openchoreo): skip Cilium install when pre-installed by Phase 1` | `pulumi/__main__.py` | `ruff check pulumi/__main__.py` |
| 4 | `feat(talos-baremetal): add longhorn-system namespace and config` | `pulumi/talos-cluster-baremetal/__main__.py`, `pulumi/talos-cluster-baremetal/Pulumi.dev.yaml` | `ruff check pulumi/talos-cluster-baremetal/__main__.py` |
| 5 | `feat(talos-baremetal): add external-snapshotter CRDs and controller` | `pulumi/talos-cluster-baremetal/__main__.py` | `ruff check pulumi/talos-cluster-baremetal/__main__.py` |
| 6 | `feat(talos-baremetal): add Longhorn v1.9.1 Helm release` | `pulumi/talos-cluster-baremetal/__main__.py` | `pytest tests/ && ruff check pulumi/talos-cluster-baremetal/__main__.py` |
| 7 | `feat(talos-baremetal): add Longhorn VolumeSnapshotClass` | `pulumi/talos-cluster-baremetal/__main__.py` | `pytest tests/ && ruff check pulumi/talos-cluster-baremetal/__main__.py` |

---

## Success Criteria

### Verification Commands
```bash
# Phase 1 — talos-cluster-baremetal
cd pulumi/talos-cluster-baremetal
pytest tests/                          # Expected: 16 passed
ruff check .                           # Expected: All checks passed
ruff format --check .                  # Expected: N files already formatted
PULUMI_CONFIG_PASSPHRASE="openchoreo-talos-baremetal-dev" pulumi preview --stack dev  # Expected: new Longhorn resources, zero changes to existing

# Phase 2 — OpenChoreo
cd pulumi
ruff check .                           # Expected: All checks passed
ruff format --check .                  # Expected: N files already formatted
python -c "from platforms.types import PlatformProfile; assert hasattr(PlatformProfile, 'cilium_pre_installed')"  # Expected: no error
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All 16 existing tests pass
- [ ] Ruff clean in both projects
- [ ] Pulumi preview shows correct resources
