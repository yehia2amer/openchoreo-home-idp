# Talos Bare-Metal One-Click Deployment

## TL;DR

> **Quick Summary**: Complete the bare-metal Talos cluster project (`talos-cluster-baremetal`) so it bootstraps a fully-configured Talos v1.12.5 cluster on `192.168.0.100` with all machine config patches — and extend the Cilium component in the root app stack to support L2 networking on bare-metal. Together, `pulumi up` on the bare-metal stack (Talos bootstrap) followed by `pulumi up` on the root app stack (Cilium, Longhorn, apps) replaces the old 3-step Terraform process.
>
> **Deliverables**:
> - Extended `PlatformProfile` with bare-metal Cilium L2 fields
> - Cilium component (in root app stack) with `bpf.hostLegacyRouting`, L2 announcements, IP pool + announcement policy CRDs
> - Complete `patches.py` with all 8 machine config patches (factory image, static network, storage, kernel, cluster settings, hostDNS, cloudflared, NVIDIA) + `__main__.py` wiring
> - `Pulumi.dev.yaml` with real bare-metal hardware values
> - Verified: `pulumi preview` passes for bare-metal stack with all Talos resources
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES — 3 waves
> **Critical Path**: Task 1 (PlatformProfile) → Task 3 (Cilium) → Task 5 (machine patches) → Task 6 (Pulumi.dev.yaml) → Task 7 (E2E verify)

---

## Context

### Original Request
User wants to deploy Talos v1.12.5 on a bare-metal server at `192.168.0.100` using Pulumi, replacing an old 3-step Terraform workflow. The full stack includes Longhorn storage, Cloudflared tunnel, NVIDIA GPU passthrough, and L2 LoadBalancer IPs. This is achieved via two Pulumi stacks: (1) **bare-metal stack** (`talos-cluster-baremetal/`) bootstraps the Talos cluster with all machine config patches, then (2) **root app stack** (`pulumi/`) deploys Cilium, Longhorn, and all apps onto the running cluster.

### Interview Summary
**Key Discussions**:
- **Server**: Same IP (`192.168.0.100`), reachable, currently running old Talos cluster — user will wipe to maintenance mode
- **Features**: Everything at once (Longhorn, Cloudflared, NVIDIA GPU, L2 networking, all features)
- **Cluster**: Wipe and fresh install (not upgrade)
- **Schematic**: Generate new for Talos v1.12.5 (old was for v1.11.0-beta.2)
- **Hardware**: Same disks (WWID `naa.5002538e7026fcb7` for install, SanDisk for Longhorn), same interfaces (`enp0s1`)
- **Cloudflared token**: Available
- **Server specs**: 2 CPUs, 20 cores, 128GB RAM

**Research Findings**:
- **talos-terraform-new** (proven working): 8 machine config patches, `apply_mode="auto"`, `node=endpoint=same_IP`, factory schematic images
- **talos-fluxcd** (proven working): CiliumLoadBalancerIPPool `192.168.0.10-99`, L2AnnouncementPolicy on 3 interfaces, internal gateway on `192.168.0.90`
- **Current bare-metal `__main__.py`**: Has correct resource chain (Secrets → ConfigApply → Bootstrap → Kubeconfig) but only 1 of 8 config patches, placeholder IPs

### Metis Review
**Identified Gaps** (addressed):
- Missing factory schematic/install image patch → Task 5 adds it
- Missing static network config (currently DHCP) → Task 5 adds it
- Missing Longhorn storage patches → Task 5 adds it
- Missing kernel modules (vfio_pci) → Task 5 adds it
- Missing hostDNS config → Task 5 adds it
- Missing max-pods/cluster settings → existing patch partial, Task 5 completes it
- Missing Cilium `bpf.hostLegacyRouting` → Task 3 adds it
- Missing L2 CRDs → Task 3 adds CiliumLoadBalancerIPPool + CiliumL2AnnouncementPolicy
- Install disk uses path `/dev/vda` instead of WWID → Task 6 fixes in config
- PlatformProfile missing bare-metal Cilium L2 fields → Task 1 adds them
- Network address discrepancy (192.168.0.x node IP vs 192.168.2.x static config) → **RESOLVED**: User confirmed `192.168.0.100/24` with gateway `192.168.0.1`. The old `192.168.2.x` config was stale/incorrect. Single subnet.

---

## Work Objectives

### Core Objective
Complete the bare-metal Talos cluster stack so `pulumi up` in `talos-cluster-baremetal/` bootstraps a fully-configured Talos v1.12.5 node with all 8 machine config patches (install, factory image, static network, storage, kernel, cluster settings, cloudflared, NVIDIA). Additionally, extend the Cilium component in the root app stack (`pulumi/components/cilium.py`) with `bpf.hostLegacyRouting`, L2 announcements, and L2 CRDs — so the root app stack can deploy Cilium with L2 networking onto the bare-metal cluster.

> **Two-stack workflow**:
> 1. `pulumi up` in `talos-cluster-baremetal/` → Talos secrets, config apply, bootstrap, kubeconfig
> 2. `pulumi up` in `pulumi/` (root app stack) → Cilium with L2, Longhorn, Gateway API, Cloudflared, all apps
>
> This plan covers BOTH stacks' changes. The "one-click deployment" is the full sequence: stack 1 then stack 2.

### Concrete Deliverables
- `pulumi/platforms/types.py` — 4 new fields on `PlatformProfile`
- `pulumi/platforms/talos_baremetal.py` — populated with bare-metal L2/BPF values
- `pulumi/components/cilium.py` — `bpf.hostLegacyRouting`, `l2announcements`, L2 CRD resources
- `pulumi/talos-cluster-baremetal/__main__.py` — orchestrator that imports patches and builds resource chain
- `pulumi/talos-cluster-baremetal/patches.py` — all 8 machine config patch functions (pure, testable, no Pulumi imports)
- `pulumi/talos-cluster-baremetal/Pulumi.dev.yaml` — real bare-metal IPs, disks, schematic ID

### Definition of Done

**Phase A — Bare-metal stack (`talos-cluster-baremetal/`):**
- [ ] `pulumi preview` passes with all Talos resources (Secrets, ConfigApply, Bootstrap, Kubeconfig)
- [ ] `pulumi up` on maintenance-mode server completes without errors
- [ ] `kubectl get nodes` shows Ready node (node is up, but no CNI yet — `NotReady` is expected until Cilium is deployed by root app stack)

**Phase B — Root app stack (`pulumi/`) on the bare-metal cluster:**
- [ ] `cilium status` shows healthy (Cilium deployed with L2 support)
- [ ] LoadBalancer service gets IP from `192.168.0.10-99` pool
- [ ] Longhorn manager pod running (deployed by existing app stack Helm/FluxCD, NOT by this plan directly — this plan provides the Talos disk/mount machine patches that Longhorn requires)

> **Scope note**: This plan implements Tasks 1-8 which cover BOTH stacks' code changes. Phase A verification is done by Task 7 (preview) and actual `pulumi up`. Phase B verification requires running the root app stack after Phase A, which uses the existing bootstrap scripts and Cilium component (modified by Task 3).

### Must Have
- All 8 machine config patches from proven Terraform config
- Cilium with `bpf.hostLegacyRouting: true` and `l2announcements.enabled: true`
- CiliumLoadBalancerIPPool for `192.168.0.10-99`
- CiliumL2AnnouncementPolicy on interfaces `enp7s0`, `enp0s1`, `enp0s25`
- Install disk by WWID (not path)
- Static network config (not DHCP)
- Factory schematic image for Talos v1.12.5

### Must NOT Have (Guardrails)
- **NO changes to existing resource logical names**: `"machine-secrets"`, `"control-plane-config"`, `"bootstrap"`, `"kubeconfig"`, `"cilium"`
- **NO changes to `pulumi/__main__.py` dependency chain** (app-stack orchestrator)
- **NO changes to `pulumi/talos-cluster/__main__.py`** (local VM variant — separate path)
- **NO refactoring shared helpers** between `talos-cluster/` and `talos-cluster-baremetal/`
- **NO Helm release name changes** in the Cilium component
- **NO modifying non-bare-metal platform profiles** (k3d, rancher-desktop, talos)
- **NO over-abstraction** — config patch functions should be straightforward, not generic "patch builder" frameworks
- **NO excessive comments or documentation** — code should be self-evident; comments only for non-obvious decisions
- **NO `as any` / `# type: ignore` hacks** — proper typing throughout

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (no unit test framework in Pulumi projects currently)
- **Automated tests**: Tests-after (add basic config patch tests in Task 8)
- **Framework**: `pytest` (already available in Python environment)
- **QA approach**: Agent-Executed QA via `pulumi preview`, `ruff check`, `py_compile`, and eventually real `pulumi up`

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Pulumi resources**: Use `pulumi preview` to verify resource graph
- **Python code**: Use `ruff check` + `py_compile` for lint/syntax
- **Config patches**: Use `python -c "import json; ..."` to verify valid JSON
- **Deployment**: Use `kubectl` + `cilium status` for post-deploy verification

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation):
├── Task 1: Extend PlatformProfile with bare-metal Cilium L2 fields [quick]
├── Task 2: Update talos_baremetal profile with L2/BPF values [quick]
└── Task 4: Add certSANs config key to Pulumi.dev.yaml schema [quick]

Wave 2 (After Wave 1 — core implementation, MAX PARALLEL):
├── Task 3: Add Cilium bpf.hostLegacyRouting + L2 announcements + L2 CRDs (depends: 1, 2) [deep]
├── Task 5: Add ALL machine config patches to __main__.py (depends: 1) [deep]
└── Task 6: Update Pulumi.dev.yaml with real bare-metal values (depends: 4, 5) [quick]

Wave 3 (After Wave 2 — verification):
├── Task 7: End-to-end pulumi preview verification (depends: 3, 5, 6) [unspecified-high]
└── Task 8: Add pytest unit tests for config patch generation (depends: 5) [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA — pulumi preview + ruff (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay
```

### Dependency Matrix

| Task | Blocked By | Blocks |
|------|-----------|--------|
| 1 | — | 2, 3, 5 |
| 2 | 1 | 3 |
| 3 | 1, 2 | 7 |
| 4 | — | 6 |
| 5 | 1 | 6, 7, 8 |
| 6 | 4, 5 | 7 |
| 7 | 3, 5, 6 | F1-F4 |
| 8 | 5 | F1-F4 |

### Agent Dispatch Summary

- **Wave 1**: **3** — T1 → `quick`, T2 → `quick`, T4 → `quick`
- **Wave 2**: **3** — T3 → `deep`, T5 → `deep`, T6 → `quick`
- **Wave 3**: **2** — T7 → `unspecified-high`, T8 → `quick`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Extend PlatformProfile with bare-metal Cilium L2 fields

  **What to do**:
  - Add 4 new fields to the `PlatformProfile` dataclass in `pulumi/platforms/types.py`:
    - `cilium_bpf_host_legacy_routing: bool = False` — Enable BPF host legacy routing (required for bare-metal L2)
    - `cilium_l2_announcements_enabled: bool = False` — Enable Cilium L2 announcements for LoadBalancer IPs
    - `cilium_l2_ip_pool_cidrs: tuple[str, ...] = ()` — CIDR blocks for CiliumLoadBalancerIPPool (e.g. `("192.168.0.10-192.168.0.99",)`)
    - `cilium_l2_interfaces: tuple[str, ...] = ()` — Network interfaces for CiliumL2AnnouncementPolicy (e.g. `("enp7s0", "enp0s1", "enp0s25")`)
  - All fields MUST have defaults that preserve backward compatibility (existing profiles unchanged)
  - **CRITICAL dataclass ordering**: Add fields at the END of the dataclass (after `cluster_name_config_key: str`), under a new `# ── Bare-metal Cilium L2 ──` section comment. They MUST NOT be placed before any non-default fields — Python dataclasses require all non-default fields before defaulted fields. Since ALL existing fields are non-default (required), the new defaulted fields go last.
  - Add docstrings matching existing style

  **Must NOT do**:
  - Do NOT change any existing field names, types, or defaults
  - Do NOT reorder existing fields
  - Do NOT add fields to other platform profiles (k3d, rancher-desktop, talos) — they get the defaults

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple dataclass field additions, ~15 lines of code
  - **Skills**: []
    - No special skills needed for adding Python dataclass fields
  - **Skills Evaluated but Omitted**:
    - `senior-backend`: Overkill for dataclass field additions

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 4)
  - **Blocks**: Tasks 2, 3, 5
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `pulumi/platforms/types.py:1-69` — Full PlatformProfile dataclass. New fields go after line 55 (`cilium_cni_bin_path`) and before line 57 (`workflow_template_mode`). Follow the exact same pattern: field name, type annotation, default value, docstring.

  **API/Type References**:
  - `pulumi/platforms/talos.py:26-48` — Example of how platform profiles instantiate PlatformProfile. After adding new fields, existing profiles use defaults (no changes needed).
  - `pulumi/platforms/talos_baremetal.py:7-24` — The bare-metal profile that will set these new fields in Task 2.

  **WHY Each Reference Matters**:
  - `types.py` shows the exact docstring style, field ordering convention, and section comments — match them precisely
  - `talos.py` proves backward compatibility: existing profiles don't pass the new fields, so defaults must be safe (False/empty)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: New fields exist with correct defaults
    Tool: Bash (python -c)
    Preconditions: types.py has been modified
    Steps:
      1. Run (from repo root): cd pulumi && python -c "from platforms.types import PlatformProfile; p = PlatformProfile(name='test', gateway_mode='cilium', cni_mode='cilium', enable_kube_proxy_replacement=True, k8s_service_host='localhost', k8s_service_port=7445, requires_coredns_rewrite=False, requires_machine_id_fix=False, requires_bpf_mount_fix=False, cilium_auto_mount_bpf=False, cilium_host_network_gateway=False, cilium_cni_bin_path='', workflow_template_mode='default', local_registry=False, bootstrap_script='', cluster_name_config_key=''); print(p.cilium_bpf_host_legacy_routing, p.cilium_l2_announcements_enabled, p.cilium_l2_ip_pool_cidrs, p.cilium_l2_interfaces)"
      2. Assert output: `False False () ()`
    Expected Result: All 4 new fields exist and have correct default values
    Failure Indicators: ImportError, AttributeError, or wrong default values
    Evidence: .sisyphus/evidence/task-1-defaults-check.txt

  Scenario: Existing profiles still instantiate without changes
    Tool: Bash (python -c)
    Preconditions: types.py modified, talos.py NOT modified
    Steps:
      1. Run (from repo root): cd pulumi && python -c "from platforms.talos import talos; p = talos(); print(p.name, p.cilium_bpf_host_legacy_routing)"
      2. Assert output: `talos False`
    Expected Result: Existing talos profile works with new defaults
    Failure Indicators: TypeError about unexpected keyword arguments
    Evidence: .sisyphus/evidence/task-1-backward-compat.txt

  Scenario: Lint and compile pass
    Tool: Bash
    Preconditions: types.py modified
    Steps:
      1. Run: ruff check pulumi/platforms/types.py
      2. Run: python -m py_compile pulumi/platforms/types.py
    Expected Result: Both commands exit 0
    Failure Indicators: Non-zero exit code
    Evidence: .sisyphus/evidence/task-1-lint.txt
  ```

  **Commit**: YES (groups with Task 2)
  - Message: `feat(platforms): add bare-metal Cilium L2 fields to PlatformProfile`
  - Files: `pulumi/platforms/types.py`, `pulumi/platforms/talos_baremetal.py`
  - Pre-commit: `ruff check pulumi/platforms/types.py pulumi/platforms/talos_baremetal.py`

- [x] 2. Update talos_baremetal profile with L2/BPF values

  **What to do**:
  - In `pulumi/platforms/talos_baremetal.py`, add the 4 new fields to the `PlatformProfile(...)` constructor call:
    - `cilium_bpf_host_legacy_routing=True` — proven required for bare-metal (from talos-terraform-new Cilium values)
    - `cilium_l2_announcements_enabled=True` — proven required for LoadBalancer IPs on bare-metal
    - `cilium_l2_ip_pool_cidrs=("192.168.0.10-192.168.0.99",)` — from talos-fluxcd CiliumLoadBalancerIPPool
    - `cilium_l2_interfaces=("enp7s0", "enp0s1", "enp0s25")` — from talos-fluxcd CiliumL2AnnouncementPolicy
  - Add parameters to the `talos_baremetal()` function signature for IP pool and interfaces so they can be overridden:
    - `l2_ip_pool_cidrs: tuple[str, ...] = ("192.168.0.10-192.168.0.99",)`
    - `l2_interfaces: tuple[str, ...] = ("enp7s0", "enp0s1", "enp0s25")`

  **Must NOT do**:
  - Do NOT modify `talos.py` (local macOS profile)
  - Do NOT change the function name or existing parameters
  - Do NOT add fields that don't exist in PlatformProfile (Task 1 must complete first)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Small file, adding ~6 lines to existing constructor call
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (same Wave as Task 1, but depends on Task 1 completing)
  - **Parallel Group**: Wave 1 (sequential after Task 1 within the wave)
  - **Blocks**: Task 3
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `pulumi/platforms/talos_baremetal.py:6-24` — Current bare-metal profile constructor. Add new fields after `cluster_name_config_key` line 23.
  - `pulumi/platforms/talos.py:17-48` — Local Talos profile for comparison. Shows parameter pattern (`k8s_service_host: str = "localhost"`).

  **External References**:
  - `.sisyphus/drafts/talos-baremetal-repo-findings.md:88-91` — L2 networking config from talos-fluxcd: IP pool `192.168.0.10-99`, interfaces `enp7s0, enp0s1, enp0s25`

  **WHY Each Reference Matters**:
  - `talos_baremetal.py` is the file being modified — understand its current shape
  - `talos.py` shows the function signature pattern to follow
  - Draft findings confirm the exact values from the proven FluxCD deployment

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Bare-metal profile has L2 fields populated
    Tool: Bash (python -c)
    Preconditions: Both types.py and talos_baremetal.py modified
    Steps:
      1. Run (from repo root): cd pulumi && python -c "from platforms.talos_baremetal import talos_baremetal; p = talos_baremetal(); print(p.cilium_bpf_host_legacy_routing, p.cilium_l2_announcements_enabled, p.cilium_l2_ip_pool_cidrs, p.cilium_l2_interfaces)"
      2. Assert output: `True True ('192.168.0.10-192.168.0.99',) ('enp7s0', 'enp0s1', 'enp0s25')`
    Expected Result: All L2 fields set to bare-metal values
    Failure Indicators: Wrong values or AttributeError
    Evidence: .sisyphus/evidence/task-2-l2-fields.txt

  Scenario: Custom overrides work
    Tool: Bash (python -c)
    Preconditions: talos_baremetal.py modified with parameters
    Steps:
      1. Run (from repo root): cd pulumi && python -c "from platforms.talos_baremetal import talos_baremetal; p = talos_baremetal(l2_ip_pool_cidrs=('10.0.0.1-10.0.0.50',), l2_interfaces=('eth0',)); print(p.cilium_l2_ip_pool_cidrs, p.cilium_l2_interfaces)"
      2. Assert output: `('10.0.0.1-10.0.0.50',) ('eth0',)`
    Expected Result: Parameters override defaults
    Failure Indicators: TypeError or still showing default values
    Evidence: .sisyphus/evidence/task-2-overrides.txt
  ```

  **Commit**: YES (groups with Task 1)
  - Message: `feat(platforms): add bare-metal Cilium L2 fields to PlatformProfile`
  - Files: `pulumi/platforms/types.py`, `pulumi/platforms/talos_baremetal.py`
  - Pre-commit: `ruff check pulumi/platforms/types.py pulumi/platforms/talos_baremetal.py`

- [x] 3. Add Cilium bpf.hostLegacyRouting, L2 announcements, IP pool + announcement policy CRDs

  **What to do**:
  Modify the Cilium component (`pulumi/components/cilium.py`) that is used by the **root app stack** (`pulumi/__main__.py`), NOT by the bare-metal stack. The bare-metal stack only bootstraps the Talos cluster; the root app stack deploys Cilium onto it. These changes ensure Cilium is deployed with L2 networking when the platform profile has L2 fields enabled.

  - In `pulumi/components/cilium.py`, modify the `Cilium.__init__` method:
    1. **Add `bpf.hostLegacyRouting`**: In the `values` dict, within the existing `"bpf"` key, add `"hostLegacyRouting": p.cilium_bpf_host_legacy_routing`. This goes alongside the existing `"autoMount"` key.
    2. **Add `l2announcements`**: Add a new top-level key `"l2announcements": {"enabled": p.cilium_l2_announcements_enabled}` to the values dict.
    3. **Add `externalIPs.enabled`**: Add `"externalIPs": {"enabled": p.cilium_l2_announcements_enabled}` — required for L2 announcement policy to work with externalTrafficPolicy.
  - After the `cilium_chart` creation, **conditionally** create L2 CRD resources (only when `p.cilium_l2_announcements_enabled` is True):
    4. **CiliumLoadBalancerIPPool** — Kubernetes custom resource:
       ```yaml
       apiVersion: cilium.io/v2alpha1
       kind: CiliumLoadBalancerIPPool
       metadata:
         name: homelab-ip-pool
         namespace: kube-system
       spec:
         blocks:
           - start: "192.168.0.10"   # From p.cilium_l2_ip_pool_cidrs
             stop: "192.168.0.99"
       ```
       Use `k8s.apiextensions.CustomResource` with `depends_on=[cilium_chart]`.
    5. **CiliumL2AnnouncementPolicy** — Kubernetes custom resource:
       ```yaml
       apiVersion: cilium.io/v2alpha1
       kind: CiliumL2AnnouncementPolicy
       metadata:
         name: homelab-l2-policy
         namespace: kube-system
       spec:
         interfaces:
           - ^enp7s0$
           - ^enp0s1$
           - ^enp0s25$
         loadBalancerIPs: true
         externalIPs: true
       ```
       Use `k8s.apiextensions.CustomResource` with `depends_on=[cilium_chart]`.
  - Parse `p.cilium_l2_ip_pool_cidrs` entries: if entry contains `-`, split into `start`/`stop`; if entry contains `/`, use as `cidr`.

  **Must NOT do**:
  - Do NOT change the Helm release name `"cilium"`
  - Do NOT modify existing values that aren't related to L2/BPF
  - Do NOT add L2 CRDs when `cilium_l2_announcements_enabled` is False (breaks non-bare-metal)
  - Do NOT change `_child_opts` or `_ensure_bpf_shared_mount` functions
  - Do NOT change the `deploy()` function signature

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Modifying a shared component that affects all platforms; needs careful conditional logic and CRD creation
  - **Skills**: [`find-docs`]
    - `find-docs`: Look up Cilium L2 announcement CRD schema and CiliumLoadBalancerIPPool spec to confirm field names
  - **Skills Evaluated but Omitted**:
    - `senior-frontend`: Not relevant (backend/infra code)
    - `helm-chart-builder`: Not building a Helm chart, just modifying values and adding CRDs

  **Parallelization**:
  - **Can Run In Parallel**: YES (within Wave 2)
  - **Parallel Group**: Wave 2 (with Tasks 5, 6)
  - **Blocks**: Task 7
  - **Blocked By**: Tasks 1, 2

  **References**:

  **Pattern References**:
  - `pulumi/components/cilium.py:123-195` — Current Helm values dict. Add `hostLegacyRouting` inside the `"bpf"` dict at line 149. Add `l2announcements` as new top-level key after `"operator"` (line 190).
  - `pulumi/components/cilium.py:206-218` — Cilium chart creation. L2 CRDs must depend on this chart.
  - `pulumi/components/cilium.py:95-106` — `__init__` signature and platform profile access pattern (`p = cfg.platform`).

  **API/Type References**:
  - `pulumi/platforms/types.py` (after Task 1) — New fields: `cilium_bpf_host_legacy_routing`, `cilium_l2_announcements_enabled`, `cilium_l2_ip_pool_cidrs`, `cilium_l2_interfaces`

  **External References**:
  - `.sisyphus/drafts/talos-baremetal-repo-findings.md:60-75` — Proven Cilium values from Terraform post-install showing `bpf.hostLegacyRouting: true` and `l2announcements.enabled: true`
  - `.sisyphus/drafts/talos-baremetal-repo-findings.md:88-91` — CiliumLoadBalancerIPPool and CiliumL2AnnouncementPolicy specs from FluxCD

  **WHY Each Reference Matters**:
  - `cilium.py:123-195` is WHERE to insert the new values — must understand existing dict structure to merge cleanly
  - `cilium.py:206-218` is the chart resource that L2 CRDs depend on — wrong dependency = CRDs created before Cilium CRD definitions exist
  - Draft findings provide the EXACT proven values to use

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Cilium values include bpf.hostLegacyRouting for bare-metal
    Tool: Bash (ruff + py_compile)
    Preconditions: cilium.py modified
    Steps:
      1. Run: ruff check pulumi/components/cilium.py
      2. Run: python -m py_compile pulumi/components/cilium.py
      3. Grep for "hostLegacyRouting" in cilium.py — must appear exactly once
      4. Grep for "l2announcements" in cilium.py — must appear
    Expected Result: Lint passes, compile passes, both strings found
    Failure Indicators: Ruff errors, compile errors, or missing strings
    Evidence: .sisyphus/evidence/task-3-cilium-lint.txt

  Scenario: L2 CRDs NOT created for non-bare-metal profiles
    Tool: Bash (grep)
    Preconditions: cilium.py modified
    Steps:
      1. Verify that CiliumLoadBalancerIPPool and CiliumL2AnnouncementPolicy creation is gated behind a condition checking `p.cilium_l2_announcements_enabled`
      2. Grep for "if p.cilium_l2_announcements_enabled" or equivalent conditional
    Expected Result: L2 CRDs are conditionally created
    Failure Indicators: CRDs created unconditionally (would break k3d/rancher-desktop stacks)
    Evidence: .sisyphus/evidence/task-3-conditional-check.txt

  Scenario: No existing values modified
    Tool: Bash (git diff)
    Preconditions: cilium.py modified
    Steps:
      1. Run: git diff pulumi/components/cilium.py
      2. Verify no REMOVED lines in the Helm values dict (only additions)
      3. Verify Helm release name "cilium" unchanged
    Expected Result: Only additions, no deletions or renames in existing code
    Failure Indicators: Deleted lines in values dict or changed release name
    Evidence: .sisyphus/evidence/task-3-no-breakage.txt
  ```

  **Commit**: YES
  - Message: `feat(cilium): add bpf.hostLegacyRouting, L2 announcements, IP pool and announcement policy`
  - Files: `pulumi/components/cilium.py`
  - Pre-commit: `ruff check pulumi/components/cilium.py && python -m py_compile pulumi/components/cilium.py`

- [x] 4. Add bare-metal config keys to Pulumi.dev.yaml schema

  **What to do**:
  - Add new config keys to `pulumi/talos-cluster-baremetal/Pulumi.dev.yaml` that the __main__.py patches will read. These are PLACEHOLDER values for now (Task 6 fills in real values):
    - `openchoreo-talos-cluster-baremetal:schematic_id: REPLACE_WITH_NEW_SCHEMATIC_ID`
    - `openchoreo-talos-cluster-baremetal:network_interface: enp0s1`
    - `openchoreo-talos-cluster-baremetal:network_address: REPLACE_WITH_STATIC_IP/CIDR`
    - `openchoreo-talos-cluster-baremetal:network_gateway: REPLACE_WITH_GATEWAY`
    - `openchoreo-talos-cluster-baremetal:longhorn_disk: /dev/disk/by-id/ata-SanDisk_SDSSDHII960G_151740411937`
    - `openchoreo-talos-cluster-baremetal:cert_sans: '["192.168.0.100", "talos.amernas.work"]'`
    - `openchoreo-talos-cluster-baremetal:enable_cloudflared: "false"`
    - `openchoreo-talos-cluster-baremetal:cloudflared_token: ""`
    - `openchoreo-talos-cluster-baremetal:enable_nvidia: "false"`
  - This establishes the config schema so Task 5 can reference these keys in `cfg.get()`

  **Must NOT do**:
  - Do NOT remove existing config keys
  - Do NOT change the encryption salt line

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: YAML config file additions, ~10 lines
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Task 6
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `pulumi/talos-cluster-baremetal/Pulumi.dev.yaml:1-8` — Current config file with 6 keys. Add new keys following the same `openchoreo-talos-cluster-baremetal:key_name: value` pattern.

  **External References**:
  - `.sisyphus/drafts/talos-baremetal-repo-findings.md:11-22` — Proven config values from Terraform (IP, disk WWID, schematic ID, interface name)

  **WHY Each Reference Matters**:
  - `Pulumi.dev.yaml` is the file being modified — must match existing key naming convention
  - Draft findings provide the exact hardware identifiers from the working Terraform setup

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: YAML is valid and contains all new keys
    Tool: Bash (python -c)
    Preconditions: Pulumi.dev.yaml modified
    Steps:
      1. Run: python -c "import yaml; d = yaml.safe_load(open('pulumi/talos-cluster-baremetal/Pulumi.dev.yaml')); cfg = d['config']; keys = ['schematic_id', 'network_interface', 'network_address', 'network_gateway', 'longhorn_disk', 'cert_sans', 'enable_cloudflared', 'cloudflared_token', 'enable_nvidia']; missing = [k for k in keys if f'openchoreo-talos-cluster-baremetal:{k}' not in cfg]; print('PASS' if not missing else f'MISSING: {missing}')"
      2. Assert output: `PASS`
    Expected Result: All 9 new keys present in config
    Failure Indicators: MISSING output or YAML parse error
    Evidence: .sisyphus/evidence/task-4-yaml-keys.txt

  Scenario: Existing keys preserved
    Tool: Bash (python -c)
    Preconditions: Pulumi.dev.yaml modified
    Steps:
      1. Run: python -c "import yaml; d = yaml.safe_load(open('pulumi/talos-cluster-baremetal/Pulumi.dev.yaml')); cfg = d['config']; print(cfg.get('openchoreo-talos-cluster-baremetal:cluster_name'), cfg.get('openchoreo-talos-cluster-baremetal:talos_version'))"
      2. Assert output: `openchoreo v1.12.5`
    Expected Result: Original keys still present with correct values
    Evidence: .sisyphus/evidence/task-4-existing-keys.txt
  ```

  **Commit**: NO (groups with Task 6)

- [x] 5. Add ALL machine config patches to __main__.py

  **What to do**:
  This is the core task. Create a new `pulumi/talos-cluster-baremetal/patches.py` module with ALL config patch functions as pure functions (no Pulumi imports), and update `__main__.py` to import and use them. The machine config must match the proven Terraform deployment exactly.

  **Step 0 — Create `patches.py` module** (new file `pulumi/talos-cluster-baremetal/patches.py`):
  This module holds ALL `render_*_patch()` functions as pure functions. Module-level variables (set by `__main__.py` before calling functions) store config values. NO Pulumi imports in this file — only `json` and stdlib.

  **Step 1 — Define module-level config variables in `patches.py`** (plain defaults — `__main__.py` will override these at runtime):
  ```python
  # These are set by __main__.py before calling any render_*_patch() function.
  # Default values here are for type hints and testing only.
  schematic_id: str = ""
  talos_version: str = ""
  network_interface: str = "enp0s1"
  network_address: str = ""
  network_gateway: str = ""
  longhorn_disk: str = ""
  install_disk_wwid: str = ""  # Raw WWID (e.g. "naa.5002538e7026fcb7"), NOT a /dev path
  control_plane_node: str = ""
  cert_sans_extra: list[str] = []
  enable_cloudflared: bool = False
  cloudflared_token: str = ""
  enable_nvidia: bool = False
  ```

  **Step 1b — In `__main__.py`**, read config values from Pulumi and set them on the patches module:
  ```python
  schematic_id = cfg.get("schematic_id") or ""
  network_interface = cfg.get("network_interface") or "enp0s1"
  network_address = cfg.get("network_address") or ""
  network_gateway = cfg.get("network_gateway") or ""
  longhorn_disk = cfg.get("longhorn_disk") or ""
  install_disk_wwid = cfg.get("install_disk_wwid") or ""  # Raw WWID string, NOT a /dev path
  cert_sans_raw = cfg.get("cert_sans") or "[]"
  cert_sans_extra = json.loads(cert_sans_raw) if cert_sans_raw else []
  enable_cloudflared = cfg.get_bool("enable_cloudflared") or False
  cloudflared_token = cfg.get("cloudflared_token") or ""  # Use cfg.get(), NOT cfg.get_secret() — patches.py is pure Python
  enable_nvidia = cfg.get_bool("enable_nvidia") or False

  # Wire config into patches module
  import patches
  patches.schematic_id = schematic_id
  patches.talos_version = talos_version
  patches.install_disk_wwid = install_disk_wwid
  # ... (set all module vars as shown in Step 4)
  ```

  **Step 2 — Update `render_install_patch()`** to include certSANs from config:
  - Merge `cert_sans_extra` into the existing `cert_sans` list
  - **Remove** `machine.install.disk` from this function — disk selection is now handled by `render_storage_patch()` using `diskSelector.wwid` (see Step 3)

  **Step 3 — Add new patch functions** (each returns a JSON string):

  1. **`render_factory_image_patch()`** — Factory schematic install image (uses `metal-installer` for bare-metal, NOT `installer`):
     ```python
     def render_factory_image_patch() -> str:
         if not schematic_id:
             return ""
         return json.dumps({
             "machine": {
                 "install": {
                     "image": f"factory.talos.dev/metal-installer/{schematic_id}:{talos_version}",
                     "wipe": True,
                 }
             }
         })
     ```
     > **CRITICAL**: The URL is `factory.talos.dev/metal-installer/...` — verified from `locals.tf` line 6. Do NOT use `factory.talos.dev/installer/...` (that's for VMs, not bare-metal).

  2. **`render_network_patch()`** — Static network config + hostDNS:
     ```python
     def render_network_patch() -> str:
         patch: dict = {
             "machine": {
                 "network": {
                     "nameservers": ["1.1.1.1", "8.8.8.8"],
                 },
                 "features": {
                     "hostDNS": {
                         "enabled": True,
                         "forwardKubeDNSToHost": False,
                     }
                 },
             }
         }
         if network_interface and network_address and network_gateway:
             patch["machine"]["network"]["interfaces"] = [{
                 "interface": network_interface,
                 "addresses": [network_address],
                 "routes": [{"network": "0.0.0.0/0", "gateway": network_gateway}],
             }]
         return json.dumps(patch)
     ```

  3. **`render_storage_patch()`** — Longhorn kubelet extraMounts + disk + install disk selector by WWID:
     ```python
     def render_storage_patch() -> str:
         if not longhorn_disk:
             return ""
         patch: dict = {
             "machine": {
                 "kubelet": {
                     "extraMounts": [{
                         "destination": "/var/lib/longhorn",
                         "type": "bind",
                         "source": "/var/lib/longhorn",
                         "options": ["bind", "rshared", "rw"],
                     }]
                 },
                 "disks": [{
                     "device": longhorn_disk,
                     "partitions": [{
                         "mountpoint": "/var/lib/longhorn",
                     }],
                 }],
             }
         }
         # Install disk selection by WWID (proven from locals.tf lines 61-64)
         if install_disk_wwid:
             patch["machine"]["install"] = {
                 "diskSelector": {
                     "wwid": install_disk_wwid,
                 }
             }
         return json.dumps(patch)
     ```
     > **CRITICAL**: The install disk is selected via `machine.install.diskSelector.wwid` (verified from `locals.tf` lines 61-64), NOT `machine.install.disk` with a device path. The `install_disk_wwid` variable holds the raw WWID string (e.g., `"naa.5002538e7026fcb7"`), NOT a `/dev/disk/by-id/...` path.

  4. **`render_kernel_patch()`** — Kernel modules + containerd device ownership:
     ```python
     def render_kernel_patch() -> str:
         return json.dumps({
             "machine": {
                 "kernel": {
                     "modules": [
                         {"name": "vfio_pci"},
                         {"name": "vfio_iommu_type1"},
                     ]
                 },
                 "files": [{
                     "content": "containerd_device_ownership_from_security_context = true",
                     "path": "/etc/cri/conf.d/20-device-ownership.toml",
                     "op": "create",
                 }],
             }
         })
     ```

  5. **`render_cluster_settings_patch()`** — Max pods + scheduling on control plane:
     ```python
     def render_cluster_settings_patch() -> str:
         return json.dumps({
             "machine": {
                 "kubelet": {
                     "extraArgs": {"max-pods": "250"},
                 }
             },
             "cluster": {
                 "allowSchedulingOnControlPlanes": True,
             },
         })
     ```

  6. **`render_cloudflared_patch()`** — Conditional Cloudflared extension service config:
     ```python
     def render_cloudflared_patch() -> str:
         """Return a raw Talos ExtensionServiceConfig document (NOT JSON).
         
         This is a v1alpha1 document, not a machine config patch.
         It goes into config_patches as a raw YAML string.
         """
         if not enable_cloudflared or not cloudflared_token:
             return ""
         return (
             "---\n"
             "apiVersion: v1alpha1\n"
             "kind: ExtensionServiceConfig\n"
             "name: cloudflared\n"
             "environment:\n"
             f"  - TUNNEL_TOKEN={cloudflared_token}\n"
             "  - TUNNEL_METRICS=localhost:2000\n"
         )
     ```
     > **IMPORTANT**: This is a raw YAML v1alpha1 document, NOT a JSON machine config patch. The Talos config_patches field accepts both JSON and YAML documents. Verified from `locals.tf` line 134. The `cloudflared_token` MUST be a plain string (use `cfg.get()` in `__main__.py`, NOT `cfg.get_secret()`) since `patches.py` is pure Python with no Pulumi runtime.

  7. **`render_nvidia_patch()`** — Conditional NVIDIA GPU PCIDriverRebindConfig:
     ```python
     def render_nvidia_patch() -> str:
         """Return raw Talos PCIDriverRebindConfig documents (NOT JSON).
         
         These are v1alpha1 documents for GPU passthrough via vfio-pci.
         """
         if not enable_nvidia:
             return ""
         return (
             "---\n"
             "apiVersion: v1alpha1\n"
             "kind: PCIDriverRebindConfig\n"
             "name: 0000:03:00.0\n"
             "targetDriver: vfio-pci\n"
             "---\n"
             "apiVersion: v1alpha1\n"
             "kind: PCIDriverRebindConfig\n"
             "name: 0000:03:00.1\n"
             "targetDriver: vfio-pci"
         )
     ```
     > **NOTE**: The PCI device addresses (`0000:03:00.0`, `0000:03:00.1`) are from the user's specific GPU. Verified from `locals.tf` line 137. If the user changes GPUs, these addresses need updating. Consider making them configurable via Pulumi config in a future iteration.

  **Step 4 — Wire up in `__main__.py`**: Import from `patches.py` and assemble the patches list.
  In `__main__.py`, after reading config variables:
  ```python
  import patches
  # Set config vars on the patches module
  patches.schematic_id = schematic_id
  patches.talos_version = talos_version
  patches.network_interface = network_interface
  patches.network_address = network_address
  patches.network_gateway = network_gateway
  patches.longhorn_disk = longhorn_disk
  patches.install_disk_wwid = install_disk_wwid
  patches.control_plane_node = control_plane_node
  patches.cert_sans_extra = cert_sans_extra
  patches.enable_cloudflared = enable_cloudflared
  patches.cloudflared_token = cloudflared_token
  patches.enable_nvidia = enable_nvidia
  ```
  Then replace the current `config_patch = render_install_patch()` (line 153) with:
  ```python
  config_patches = [p for p in [
      patches.render_install_patch(),
      patches.render_factory_image_patch(),
      patches.render_network_patch(),
      patches.render_storage_patch(),
      patches.render_kernel_patch(),
      patches.render_cluster_settings_patch(),
      patches.render_cloudflared_patch(),
      patches.render_nvidia_patch(),
  ] if p]  # Filter out empty strings from conditional patches
  ```
  Then update line 162 from `config_patches=[config_patch]` to `config_patches=config_patches`.

  **Must NOT do**:
  - Do NOT change resource logical names: `"machine-secrets"`, `"control-plane-config"`, `"bootstrap"`, `"kubeconfig"`
  - Do NOT change the resource chain order (Secrets → ConfigApply → Bootstrap → Kubeconfig)
  - Do NOT modify helper functions `as_client_configuration`, `as_machine_client_configuration_input`, etc.
  - Do NOT put Pulumi imports in `patches.py` — it must remain pure Python (json + stdlib only) so Task 8 can import it without Pulumi runtime
  - Do NOT add logging/print statements
  - Do NOT over-abstract the patches into a "patch builder" framework

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Core implementation task touching ~150 lines of config patch logic. Needs careful JSON structure matching proven Terraform patterns.
  - **Skills**: [`find-docs`]
    - `find-docs`: Look up Talos machine config patch format for v1.12.5 (extensionServices, disks, kernel modules)
  - **Skills Evaluated but Omitted**:
    - `senior-backend`: The code is infrastructure config, not backend API design
    - `tdd-guide`: Tests are in Task 8, not here

  **Parallelization**:
  - **Can Run In Parallel**: YES (within Wave 2, independent of Task 3)
  - **Parallel Group**: Wave 2 (with Tasks 3, 6)
  - **Blocks**: Tasks 6, 7, 8
  - **Blocked By**: Task 1 (needs PlatformProfile fields to exist, though this task doesn't directly use them)

  **References**:

  **Pattern References**:
  - `pulumi/talos-cluster-baremetal/__main__.py:111-135` — Current `render_install_patch()` function. Follow the same pattern: function returns `json.dumps(dict)`.
  - `pulumi/talos-cluster-baremetal/__main__.py:149-163` — Current resource chain where patches are applied. The `config_patches` list feeds into `get_configuration_output()`.
  - `pulumi/talos-cluster-baremetal/__main__.py:11-21` — Current config variable pattern (`cfg.get("key") or "default"`).

  **External References (CRITICAL — proven working patches)**:
  - `/Users/yamer003/Desktop/personal-projects/talos-terraform-new/apply-bootstrap/locals.tf` — Contains ALL machine config patches as Terraform locals. The executor MUST read this file to get exact YAML/JSON structure for each patch. All 8 patches are defined as `local.config_patches_*` variables in this file.
  - `/Users/yamer003/Desktop/personal-projects/talos-terraform-new/apply-bootstrap/outputs/controlplane.yaml` — The RENDERED machine config output showing the final assembled config. Cross-reference this with `locals.tf` to verify patch structure correctness.
  - `/Users/yamer003/Desktop/personal-projects/talos-terraform-new/apply-bootstrap/variables.tf` — Variable definitions (schematic_id, network_interface, disk WWID, etc.) showing what's configurable.
  - `.sisyphus/drafts/talos-baremetal-repo-findings.md:25-46` — Summary of all 8 patches with key details

  **WHY Each Reference Matters**:
  - `__main__.py:111-135` establishes the EXACT pattern for patch functions (return type, JSON structure)
  - `locals.tf` is WHERE all proven patches live — the executor must read it to get exact field names, nesting, and structure (especially for cloudflared extensionServices and NVIDIA PCIDriverRebindConfig which are non-obvious)
  - `outputs/controlplane.yaml` is the RENDERED result — use it to verify your patches produce the same structure
  - Draft findings provide a quick summary but the executor should verify against `locals.tf` for exactness

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All patch functions return valid JSON
    Tool: Bash (python -c)
    Preconditions: patches.py created with all patch functions, config variables set as module-level attributes
    Steps:
      1. Run (from repo root): cd pulumi/talos-cluster-baremetal && python -c "
         import json
         import patches as p
         # Set required module-level config vars for non-conditional patches
         p.schematic_id = 'test-schematic-abc123'
         p.talos_version = 'v1.12.5'
         p.network_interface = 'enp0s1'
         p.network_address = '192.168.0.100/24'
         p.network_gateway = '192.168.0.1'
         p.longhorn_disk = '/dev/disk/by-id/ata-test-disk'
         p.control_plane_install_disk = '/dev/disk/by-id/wwn-0xtest'
         p.control_plane_node = '192.168.0.100'
         p.cert_sans_extra = ['192.168.0.100', 'talos.amernas.work']
         p.enable_cloudflared = False
         p.enable_nvidia = False
         fns = [p.render_install_patch, p.render_factory_image_patch, p.render_network_patch, p.render_storage_patch, p.render_kernel_patch, p.render_cluster_settings_patch]
         for fn in fns:
             result = fn()
             if result:
                 json.loads(result)
                 print(f'{fn.__name__}: valid JSON')
         print('ALL PASS')"
      2. Assert output ends with: `ALL PASS`
    Expected Result: Every non-empty patch is valid JSON
    Failure Indicators: json.JSONDecodeError, ImportError, AttributeError
    Evidence: .sisyphus/evidence/task-5-json-valid.txt

  Scenario: Conditional patches return empty string when disabled
    Tool: Bash (python -c)
    Preconditions: patches.py created with conditional patch functions
    Steps:
      1. Run (from repo root): cd pulumi/talos-cluster-baremetal && python -c "
         import patches as p
         p.schematic_id = ''
         p.enable_cloudflared = False
         p.enable_nvidia = False
         assert p.render_factory_image_patch() == '', f'factory expected empty, got {p.render_factory_image_patch()!r}'
         assert p.render_cloudflared_patch() == '', f'cloudflared expected empty, got {p.render_cloudflared_patch()!r}'
         assert p.render_nvidia_patch() == '', f'nvidia expected empty, got {p.render_nvidia_patch()!r}'
         print('ALL CONDITIONAL PASS')"
      2. Assert output: `ALL CONDITIONAL PASS`
    Expected Result: All three return empty string when disabled
    Failure Indicators: AssertionError with actual value shown
    Evidence: .sisyphus/evidence/task-5-conditional.txt

  Scenario: Lint and compile pass
    Tool: Bash
    Preconditions: __main__.py and patches.py modified/created
    Steps:
      1. Run: ruff check pulumi/talos-cluster-baremetal/__main__.py pulumi/talos-cluster-baremetal/patches.py
      2. Run: python -m py_compile pulumi/talos-cluster-baremetal/__main__.py
      3. Run: python -m py_compile pulumi/talos-cluster-baremetal/patches.py
    Expected Result: All commands exit 0
    Evidence: .sisyphus/evidence/task-5-lint.txt

  Scenario: Config patches list filters empty strings
    Tool: Bash (grep)
    Preconditions: __main__.py modified
    Steps:
      1. Grep for "if p]" or equivalent filter in the config_patches assembly
      2. Verify empty-string patches from conditional functions are excluded
    Expected Result: Filter pattern exists
    Evidence: .sisyphus/evidence/task-5-filter.txt
  ```

  **Commit**: YES
  - Message: `feat(talos-baremetal): add all machine config patches (factory, network, storage, kernel, cluster, cloudflared, nvidia)`
  - Files: `pulumi/talos-cluster-baremetal/__main__.py`, `pulumi/talos-cluster-baremetal/patches.py`
  - Pre-commit: `ruff check pulumi/talos-cluster-baremetal/__main__.py pulumi/talos-cluster-baremetal/patches.py && python -m py_compile pulumi/talos-cluster-baremetal/__main__.py && python -m py_compile pulumi/talos-cluster-baremetal/patches.py`

- [x] 6. Update Pulumi.dev.yaml with real bare-metal values

  **What to do**:
  - Replace placeholder values in `pulumi/talos-cluster-baremetal/Pulumi.dev.yaml`:
    - `control_plane_node: 127.0.0.1` → `control_plane_node: "192.168.0.100"`
    - `control_plane_endpoint: 127.0.0.1` → `control_plane_endpoint: "192.168.0.100"`
    - `control_plane_install_disk: /dev/vda` → `control_plane_install_disk: /dev/disk/by-id/wwn-0x5002538e7026fcb7`
    - `network_interface: enp0s1` (already set from Task 4)
    - `longhorn_disk: /dev/disk/by-id/ata-SanDisk_SDSSDHII960G_151740411937` (already set from Task 4)
    - `cert_sans: '["192.168.0.100", "talos.amernas.work"]'` (already set from Task 4)
  - **[DECISION RESOLVED: Network address and gateway]** — User confirmed: `192.168.0.100/24` with gateway `192.168.0.1`. The old Terraform `192.168.2.x` config was stale. Set:
    - `network_address: "192.168.0.100/24"`
    - `network_gateway: "192.168.0.1"`
  - `schematic_id` remains `REPLACE_WITH_NEW_SCHEMATIC_ID` — user must generate this at factory.talos.dev before `pulumi up`

  **Must NOT do**:
  - Do NOT remove the encryption salt line
  - Do NOT change the project name prefix `openchoreo-talos-cluster-baremetal:`

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: YAML value replacements, ~15 lines
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 4 and 5 for config key names)
  - **Parallel Group**: Wave 2 (sequential after Tasks 4, 5)
  - **Blocks**: Task 7
  - **Blocked By**: Tasks 4, 5

  **References**:

  **Pattern References**:
  - `pulumi/talos-cluster-baremetal/Pulumi.dev.yaml:1-8` — Current file with placeholder values
  - `pulumi/talos-cluster-baremetal/__main__.py:11-21` (after Task 5) — Config variable names that must match YAML keys

  **External References**:
  - `.sisyphus/drafts/talos-baremetal-repo-findings.md:11-22` — Proven hardware values: node IP `192.168.0.100`, disk WWID `naa.5002538e7026fcb7`, interface `enp0s1`, certSANs

  **WHY Each Reference Matters**:
  - Current `Pulumi.dev.yaml` shows placeholder format to replace
  - `__main__.py` config variables show the exact key names that must match
  - Draft findings provide the proven hardware identifiers

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Real IP addresses in config
    Tool: Bash (python -c)
    Preconditions: Pulumi.dev.yaml updated
    Steps:
      1. Run: python -c "import yaml; d = yaml.safe_load(open('pulumi/talos-cluster-baremetal/Pulumi.dev.yaml')); cfg = d['config']; print(cfg['openchoreo-talos-cluster-baremetal:control_plane_node'])"
      2. Assert output: `192.168.0.100`
    Expected Result: Real IP, not 127.0.0.1
    Evidence: .sisyphus/evidence/task-6-real-ip.txt

  Scenario: Install disk uses WWID, not path
    Tool: Bash (grep)
    Preconditions: Pulumi.dev.yaml updated
    Steps:
      1. Grep Pulumi.dev.yaml for "control_plane_install_disk"
      2. Assert value contains "by-id" or "wwn-" (not "/dev/vda")
    Expected Result: Disk identified by WWID
    Failure Indicators: Still shows "/dev/vda"
    Evidence: .sisyphus/evidence/task-6-disk-wwid.txt

  Scenario: YAML remains valid
    Tool: Bash (python -c)
    Preconditions: Pulumi.dev.yaml updated
    Steps:
      1. Run: python -c "import yaml; yaml.safe_load(open('pulumi/talos-cluster-baremetal/Pulumi.dev.yaml')); print('VALID')"
      2. Assert output: `VALID`
    Expected Result: YAML parses without error
    Evidence: .sisyphus/evidence/task-6-yaml-valid.txt
  ```

  **Commit**: YES (groups with Task 4)
  - Message: `chore(talos-baremetal): update Pulumi.dev.yaml with real bare-metal values`
  - Files: `pulumi/talos-cluster-baremetal/Pulumi.dev.yaml`
  - Pre-commit: `python -c "import yaml; yaml.safe_load(open('pulumi/talos-cluster-baremetal/Pulumi.dev.yaml'))"`

- [x] 7. End-to-end pulumi preview verification

  **What to do**:
  - Run `pulumi preview --stack dev` in `pulumi/talos-cluster-baremetal/` directory
  - Verify the resource graph includes the Talos lifecycle resources:
    - `talos:machine:Secrets` (machine-secrets)
    - `talos:machine:ConfigurationApply` (control-plane-config)
    - `talos:machine:Bootstrap` (bootstrap)
    - `talos:cluster:Kubeconfig` (kubeconfig)
  - Note: This preview covers the **bare-metal stack only**. Cilium L2 CRDs (Task 3) are deployed by the root app stack — verify those via `ruff check` and `py_compile` on `cilium.py`, NOT via this preview.
  - Verify NO errors in preview output
  - Verify config patches are being used (check for multiple patches in preview details)
  - Run `ruff check` across ALL modified files in `pulumi/` (including `components/cilium.py` from Task 3) to catch any cross-file issues
  - Verify `talos-cluster/` (local path) is UNCHANGED — run `git diff pulumi/talos-cluster/` and confirm empty

  **Must NOT do**:
  - Do NOT run `pulumi up` (that's a user action after server wipe)
  - Do NOT modify any files in this task — verification only

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Integration verification across multiple files, needs careful output analysis
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (must verify after all implementation tasks)
  - **Parallel Group**: Wave 3
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 3, 5, 6

  **References**:

  **Pattern References**:
  - `pulumi/talos-cluster-baremetal/Pulumi.yaml` — Project definition with runtime/name
  - `pulumi/talos-cluster-baremetal/Pulumi.dev.yaml` — Stack config (after Task 6)
  - `pulumi/talos-cluster-baremetal/__main__.py` — Full program (after Task 5)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Pulumi preview succeeds
    Tool: Bash (pulumi)
    Preconditions: All implementation tasks complete
    Steps:
      1. cd pulumi/talos-cluster-baremetal
      2. Run: PULUMI_CONFIG_PASSPHRASE="openchoreo-talos-baremetal-dev" pulumi preview --stack dev 2>&1
      3. Check exit code is 0
      4. Check output contains resource creation plan (not "no changes")
    Expected Result: Preview completes with resource plan, exit 0
    Failure Indicators: Non-zero exit, error messages, missing resources
    Evidence: .sisyphus/evidence/task-7-preview.txt

  Scenario: Local talos-cluster unchanged
    Tool: Bash (git diff)
    Preconditions: All tasks complete
    Steps:
      1. Run: git diff --stat pulumi/talos-cluster/
      2. Assert output is empty (no changes)
    Expected Result: Zero changes to local talos-cluster directory
    Failure Indicators: Any diff output
    Evidence: .sisyphus/evidence/task-7-no-local-changes.txt

  Scenario: Full lint pass across all modified files
    Tool: Bash (ruff)
    Preconditions: All tasks complete
    Steps:
      1. Run: ruff check pulumi/platforms/types.py pulumi/platforms/talos_baremetal.py pulumi/components/cilium.py pulumi/talos-cluster-baremetal/__main__.py pulumi/talos-cluster-baremetal/patches.py
      2. Assert exit 0
    Expected Result: All files pass lint
    Evidence: .sisyphus/evidence/task-7-full-lint.txt
  ```

  **Commit**: NO (verification only)

- [x] 8. Add pytest unit tests for config patch generation

  **What to do**:
  - Create `pulumi/talos-cluster-baremetal/tests/test_config_patches.py` with pytest tests for each patch function
  - Tests should:
    1. Import each `render_*_patch()` function
    2. Verify each returns valid JSON (json.loads doesn't throw)
    3. Verify conditional patches return empty string when conditions not met
    4. Verify key structure of each patch (e.g., factory image patch has `machine.install.image`)
    5. Verify certSANs merging works correctly
  - Create `pulumi/talos-cluster-baremetal/tests/__init__.py` (empty)
  - Create `pulumi/talos-cluster-baremetal/tests/conftest.py` with any needed fixtures (e.g., mock config values)
  - **Add `pytest` to `pulumi/talos-cluster-baremetal/pyproject.toml`** under `[dependency-groups] dev` (it is NOT currently listed — only `ruff` and `ty` are there). Then run `uv sync --group dev` to install it.
  - Tests must be runnable with: `cd pulumi/talos-cluster-baremetal && uv run python -m pytest tests/ -v`

  **Must NOT do**:
  - Do NOT test Pulumi resource creation (that requires Pulumi runtime)
  - Do NOT test the full `__main__.py` module (it has side effects at import — Pulumi runtime dependency)
  - Import patch functions from `patches.py` (created in Task 5), NOT from `__main__.py`. Example: `from patches import render_install_patch, render_network_patch, ...`
  - Use `conftest.py` to set module-level config variables on the `patches` module before calling functions (e.g., `patches.schematic_id = "test-id"`).

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Straightforward pytest tests for pure functions
  - **Skills**: [`tdd-guide`]
    - `tdd-guide`: Pytest test patterns and fixtures
  - **Skills Evaluated but Omitted**:
    - `senior-qa`: Overkill for simple unit tests

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 7, in Wave 3)
  - **Parallel Group**: Wave 3
  - **Blocks**: F1-F4
  - **Blocked By**: Task 5

  **References**:

  **Pattern References**:
  - `pulumi/talos-cluster-baremetal/patches.py` (created in Task 5) — All `render_*_patch()` functions to test. Import directly: `from patches import render_install_patch, ...`. Set module-level config vars before calling functions.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All tests pass
    Tool: Bash (pytest)
    Preconditions: Test files created, pytest added to pyproject.toml, uv sync --group dev run
    Steps:
      1. cd pulumi/talos-cluster-baremetal
      2. Run: uv run python -m pytest tests/ -v
      3. Assert exit 0
      4. Assert all tests collected and passed
    Expected Result: All tests pass, 0 failures
    Failure Indicators: Any test failures or collection errors
    Evidence: .sisyphus/evidence/task-8-pytest.txt

  Scenario: Test file passes lint
    Tool: Bash (ruff)
    Preconditions: Test file created
    Steps:
      1. Run: ruff check pulumi/talos-cluster-baremetal/tests/test_config_patches.py
      2. Assert exit 0
    Expected Result: Clean lint
    Evidence: .sisyphus/evidence/task-8-lint.txt
  ```

  **Commit**: YES
  - Message: `test(talos-baremetal): add pytest unit tests for config patch generation`
  - Files: `pulumi/talos-cluster-baremetal/pyproject.toml`, `pulumi/talos-cluster-baremetal/tests/test_config_patches.py`, `pulumi/talos-cluster-baremetal/tests/__init__.py`, `pulumi/talos-cluster-baremetal/tests/conftest.py`
  - Pre-commit: `cd pulumi/talos-cluster-baremetal && uv run python -m pytest tests/ -v`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run `pulumi preview`). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in `.sisyphus/evidence/`. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `ruff check pulumi/` + `py_compile` on all modified files. Review changed files for: `# type: ignore`, empty catches, `print()` in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Ruff [PASS/FAIL] | Compile [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Run `pulumi preview` in `talos-cluster-baremetal/` dir. Verify expected resource count matches plan. Check that all config patches render valid JSON. Verify no changes to `talos-cluster/` (local path). Run `ruff check` across entire `pulumi/` tree.
  Output: `Preview [PASS/FAIL] | Resources [N expected/N actual] | JSON [PASS/FAIL] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git diff). Verify 1:1 — everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance. Detect cross-task contamination: Task N touching Task M's files. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

| Commit | Scope | Message | Files | Pre-commit |
|--------|-------|---------|-------|------------|
| 1 | PlatformProfile + bare-metal profile | `feat(platforms): add bare-metal Cilium L2 fields to PlatformProfile` | `types.py`, `talos_baremetal.py` | `ruff check`, `py_compile` |
| 2 | Cilium component | `feat(cilium): add bpf.hostLegacyRouting, L2 announcements, IP pool + announcement policy` | `cilium.py` | `ruff check`, `py_compile` |
| 3 | Machine config patches | `feat(talos-baremetal): add all machine config patches (factory, network, storage, kernel, hostDNS, cloudflared, nvidia)` | `__main__.py`, `patches.py` | `ruff check`, `py_compile` |
| 4 | Config values | `chore(talos-baremetal): update Pulumi.dev.yaml with real bare-metal values` | `Pulumi.dev.yaml` | `pulumi preview` |
| 5 | Tests | `test(talos-baremetal): add pytest unit tests for config patch generation` | `tests/test_config_patches.py` | `pytest` |

---

## Success Criteria

### Verification Commands

**Pre-deploy (agent-verifiable — bare-metal stack code quality):**
```bash
# Syntax/lint
ruff check pulumi/platforms/types.py pulumi/platforms/talos_baremetal.py pulumi/components/cilium.py pulumi/talos-cluster-baremetal/__main__.py pulumi/talos-cluster-baremetal/patches.py
python -m py_compile pulumi/platforms/types.py
python -m py_compile pulumi/platforms/talos_baremetal.py
python -m py_compile pulumi/components/cilium.py
python -m py_compile pulumi/talos-cluster-baremetal/__main__.py
python -m py_compile pulumi/talos-cluster-baremetal/patches.py

# Preview (bare-metal stack — Talos resources only)
cd pulumi/talos-cluster-baremetal && PULUMI_CONFIG_PASSPHRASE="openchoreo-talos-baremetal-dev" pulumi preview --stack dev  # Expected: ~5 Talos resources, no errors
```

**Post-deploy Phase A (after user wipes server and runs `pulumi up` on bare-metal stack):**
```bash
kubectl --kubeconfig ~/.kube/config-openchoreo-talos-baremetal get nodes  # Expected: 1 node (may be NotReady until Cilium deployed)
```

**Post-deploy Phase B (after running root app stack on the bare-metal cluster):**
```bash
cilium status  # Expected: OK (Cilium with L2 support)
kubectl get pods -n longhorn-system  # Expected: longhorn-manager running (deployed by root app stack)
kubectl get svc -A | grep LoadBalancer  # Expected: IPs from 192.168.0.10-99 pool
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] `ruff check` passes on all modified files
- [ ] `py_compile` passes on all modified files
- [ ] `pulumi preview` passes for bare-metal stack with Talos resources
- [ ] `cilium.py` compiles and lints (L2 changes verified structurally; runtime verified when root app stack runs)
- [ ] No changes to `talos-cluster/` directory
- [ ] No changes to `pulumi/__main__.py`
- [ ] Config patches render valid JSON
