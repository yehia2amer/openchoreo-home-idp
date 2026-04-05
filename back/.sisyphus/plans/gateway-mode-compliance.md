# Gateway Mode Fix + OpenChoreo Compliance Audit

## TL;DR

> **Quick Summary**: Switch talos-baremetal's `gateway_mode` from `"cilium"` to `"kgateway"` so OpenChoreo uses the proper kgateway (agentgateway) for API routes, MCP/A2A/LLM routing, tool federation, AI guardrails, and AI-specific governance. Simultaneously fix all compliance gaps between our Phase 2 Pulumi code and the official OpenChoreo guide — including disabling Cilium's Gateway API in Phase 1, adding explicit TLS/CA chain resources, fixing k3d-specific workflow template URLs, and removing duplicate Gateway API CRDs from Phase 1.
>
> **Deliverables**:
> - `gateway_mode="kgateway"` in talos-baremetal profile
> - Cilium Gateway API disabled in Phase 1 (no GatewayClass competition)
> - Gateway API CRDs removed from Phase 1 (Phase 2 owns them)
> - Explicit TLS/CA chain (self-signed bootstrap → CA cert → CA issuer + per-plane wildcard certs)
> - Standard workflow template URLs (no k3d references)
> - Phase 2 exports updated for kgateway edition
> - All tests passing + clean `pulumi preview` for both stacks
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES — 3 waves
> **Critical Path**: T1 → T3 → T4 → T6 → T8 → T10 → F1-F4

---

## Context

### Original Request
User discovered from the official OpenChoreo guide that kgateway (agentgateway) must be the Gateway API implementation — not Cilium. Cilium should only serve as CNI. Additionally, user wants a full compliance audit of Phase 2 Pulumi code against the guide.

### Interview Summary
**Key Discussions**:
- **Gateway mode**: Must change from "cilium" to "kgateway" for bare-metal. kgateway handles MCP/A2A/LLM routing, tool federation, AI guardrails, AI-specific governance.
- **TLS strategy**: User chose to add explicit CA chain resources matching the guide exactly (self-signed bootstrap → CA cert → CA issuer + per-plane wildcard certs).
- **CRD duplication**: User chose to remove Gateway API CRDs from Phase 1, letting Phase 2 prerequisites own them.
- **Scope boundary**: Only talos-baremetal changes. Do NOT touch k3d, rancher-desktop, or other platform files.

**Research Findings**:
- **Cilium Gateway API is ENABLED in Phase 1** (`gatewayAPI.enabled: True` at `__main__.py:405-409`). This will compete with kgateway. MUST disable it.
- **Cilium depends_on Gateway API CRDs** (`__main__.py:430`). Cannot simply remove CRDs — must handle dependency.
- **`tls_enabled` defaults to `False`** (`config.py:185`). Not set in `Pulumi.talos-baremetal.yaml`. New TLS resources must be gated behind this flag.
- **Workflow template URLs** use k3d-specific variants globally (`config.py:264-268`). Must make platform-conditional.
- **kgateway code path already exists** in all Phase 2 components — just need to flip the switch.

### Metis Review
**Identified Gaps** (addressed in plan):
- Cilium Gateway API must be disabled in Phase 1 to avoid GatewayClass competition — **Added as T2**
- CRD removal must handle `depends_on` chain in Phase 1 Cilium — **T3 addresses via `retainOnDelete`**
- Workflow template URLs must be platform-conditional, not globally changed — **T6 adds field to PlatformProfile**
- TLS resources must be gated behind `tls_enabled` — **T7-T8 implement with conditional logic**
- `listenerName` may be missing from ClusterDataPlane registration — **T9 investigates and fixes**
- cert-manager → ClusterIssuer → Certificate dependency chain must be explicit — **T8 uses `depends_on`**

---

## Work Objectives

### Core Objective
Make the talos-baremetal deployment fully compliant with the official OpenChoreo guide by switching to kgateway for Gateway API and ensuring all TLS, workflow, and resource configurations match the guide exactly.

### Concrete Deliverables
- `pulumi/platforms/talos_baremetal.py` — `gateway_mode="kgateway"`
- `pulumi/talos-cluster-baremetal/__main__.py` — Cilium `gatewayAPI.enabled: False` + Gateway API CRDs removed (with `retainOnDelete`)
- `pulumi/components/tls_setup.py` — New component for CA chain + per-plane TLS certs
- `pulumi/config.py` — Platform-conditional workflow template URLs
- `pulumi/components/workflow_plane.py` — Updated sed patterns for standard templates
- `pulumi/__main__.py` — Updated exports for kgateway edition
- `pulumi/components/data_plane.py` — `listenerName` in plane registration (if needed)
- Updated unit tests for all changes
- Clean `pulumi preview` for both Phase 1 and Phase 2 stacks

### Definition of Done
- [ ] `pulumi preview --stack dev` (Phase 1) succeeds with 0 errors
- [ ] `pulumi preview --stack talos-baremetal` (Phase 2) succeeds with 0 errors
- [ ] `python -m pytest tests/ -v` passes for both stacks
- [ ] `ruff check .` passes for both stacks
- [ ] No `k3d` references in workflow template URLs for talos-baremetal platform
- [ ] No `gatewayAPI.enabled: True` in Phase 1 Cilium values
- [ ] No Gateway API CRD installation in Phase 1

### Must Have
- kgateway as Gateway API controller (not Cilium)
- Cilium Gateway API disabled in Phase 1
- TLS CA chain gated behind `tls_enabled` flag
- Standard (non-k3d) workflow template URLs for bare-metal
- All existing tests continue to pass (no regressions)

### Must NOT Have (Guardrails)
- ❌ DO NOT touch `k3d.py`, `rancher_desktop.py`, or any non-baremetal platform files
- ❌ DO NOT implement two-phase CP install — Pulumi knows domain upfront
- ❌ DO NOT apply `all.yaml` default resources — that's a Phase 3 FluxCD concern
- ❌ DO NOT add MetalLB or external LB configuration
- ❌ DO NOT refactor PlatformProfile dataclass beyond adding needed fields
- ❌ DO NOT add observability plane TLS certificates (only CP and DP gateways)
- ❌ DO NOT change k3d workflow template behavior — k3d must keep working
- ❌ DO NOT use `create_namespace=True` on Helm releases
- ❌ DO NOT use `k8s.helm.v4.Chart` in Phase 1 (use `k8s.helm.v3.Release`)
- ❌ DO NOT use `git commit` without `--no-gpg-sign`
- ❌ DO NOT forget to `git checkout -- .sisyphus/boulder.json` after subagent returns

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: YES (Tests-after, matching existing pattern)
- **Framework**: pytest (already configured in both stacks)
- **Test commands**:
  - Phase 1: `pulumi/talos-cluster-baremetal/.venv/bin/python -m pytest tests/ -v` (workdir: `pulumi/talos-cluster-baremetal`)
  - Phase 2: `pulumi/.venv/bin/python -m pytest tests/ -v` (workdir: `pulumi`)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Code changes**: Use `ruff check` + `pytest` + `pulumi preview`
- **Config verification**: Use `grep` to verify no stale values remain
- **Integration**: Use `pulumi preview` to verify Pulumi resource graph is valid

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — gateway mode flip + Phase 1 fixes):
├── T1: Gateway mode flip in talos_baremetal.py [quick]
├── T2: Disable Cilium gatewayAPI in Phase 1 [quick]
├── T3: Remove Gateway API CRDs from Phase 1 (retainOnDelete) [quick]
└── T4: Update Phase 2 exports for kgateway edition [quick]

Wave 2 (After Wave 1 — workflow templates + TLS):
├── T5: Add workflow_template_urls field to PlatformProfile [quick]
├── T6: Fix workflow template URLs + sed patterns [unspecified-high]
├── T7: Add TLS constants and tls_enabled stack config [quick]
└── T8: Create tls_setup.py component (CA chain + per-plane certs) [deep]

Wave 3 (After Wave 2 — integration fixes + validation):
├── T9: Fix listenerName in ClusterDataPlane registration [quick]
├── T10: Add unit tests for all changes [unspecified-high]
└── T11: Run pulumi preview for both stacks [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── F1: Plan Compliance Audit (oracle)
├── F2: Code Quality Review (unspecified-high)
├── F3: Real Manual QA (unspecified-high)
└── F4: Scope Fidelity Check (deep)
-> Present results -> Get explicit user okay
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| T1   | —         | T4, T5, T6, T8, T9, T10 | 1 |
| T2   | —         | T3, T10, T11 | 1 |
| T3   | T2        | T10, T11 | 1 |
| T4   | T1        | T10 | 1 |
| T5   | T1        | T6 | 2 |
| T6   | T5        | T10, T11 | 2 |
| T7   | —         | T8 | 2 |
| T8   | T7, T1    | T10, T11 | 2 |
| T9   | T1        | T10, T11 | 2 |
| T10  | T1-T9     | T11 | 3 |
| T11  | T1-T10    | F1-F4 | 3 |
| F1-F4| T11       | user okay | FINAL |

### Agent Dispatch Summary

- **Wave 1**: **4** — T1 → `quick`, T2 → `quick`, T3 → `quick`, T4 → `quick`
- **Wave 2**: **4** — T5 → `quick`, T6 → `unspecified-high`, T7 → `quick`, T8 → `deep`
- **Wave 3**: **3** — T9 → `quick`, T10 → `unspecified-high`, T11 → `quick`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Switch gateway_mode from "cilium" to "kgateway" in talos_baremetal.py

  **What to do**:
  - Open `pulumi/platforms/talos_baremetal.py`
  - Change line 13: `gateway_mode="cilium"` → `gateway_mode="kgateway"`
  - That's it — single line change

  **Must NOT do**:
  - Do NOT change `cni_mode` — it stays as `"cilium"`
  - Do NOT touch `talos.py`, `k3d.py`, `rancher_desktop.py`, or any other platform file
  - Do NOT change any other field in the PlatformProfile

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single-line config change in a known file
  - **Skills**: []
    - No skills needed for a trivial edit

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with T2, T3, T4)
  - **Blocks**: T4, T5, T6, T8, T9, T10
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `pulumi/platforms/k3d.py` — Reference for a platform that already uses `gateway_mode="kgateway"`. Compare structure.

  **API/Type References**:
  - `pulumi/platforms/types.py:PlatformProfile` — The dataclass with the `gateway_mode` field. Valid values: `"cilium"` or `"kgateway"`.

  **External References**:
  - `docs/OpenChoreo - Steps to run in Any k8s Environment.md` lines 85-99 — Official guide showing kgateway as the required Gateway API controller.

  **WHY Each Reference Matters**:
  - `k3d.py` proves `"kgateway"` is a valid, tested value for `gateway_mode`
  - `types.py` confirms the field type and available values
  - The guide is the authoritative source for why kgateway is required

  **Acceptance Criteria**:
  - [ ] `pulumi/platforms/talos_baremetal.py` line 13 reads `gateway_mode="kgateway"`
  - [ ] `cni_mode` still reads `"cilium"` (unchanged)
  - [ ] No other platform files modified

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Gateway mode is kgateway for talos-baremetal
    Tool: Bash (grep)
    Preconditions: File exists at pulumi/platforms/talos_baremetal.py
    Steps:
      1. Run: grep 'gateway_mode=' pulumi/platforms/talos_baremetal.py
      2. Assert output contains: gateway_mode="kgateway"
      3. Run: grep 'cni_mode=' pulumi/platforms/talos_baremetal.py
      4. Assert output contains: cni_mode="cilium"
    Expected Result: gateway_mode is "kgateway", cni_mode is "cilium"
    Failure Indicators: gateway_mode still says "cilium" or cni_mode changed
    Evidence: .sisyphus/evidence/task-1-gateway-mode-value.txt

  Scenario: No other platform files were modified
    Tool: Bash (git diff)
    Preconditions: Changes committed
    Steps:
      1. Run: git diff HEAD~1 --name-only
      2. Assert output contains ONLY: pulumi/platforms/talos_baremetal.py
      3. Assert output does NOT contain: k3d.py, rancher_desktop.py, talos.py
    Expected Result: Only talos_baremetal.py was modified
    Failure Indicators: Other platform files appear in diff
    Evidence: .sisyphus/evidence/task-1-no-other-platforms.txt
  ```

  **Commit**: YES (groups with T2, T3)
  - Message: `fix(platform): switch talos-baremetal to kgateway and disable Cilium Gateway API`
  - Files: `pulumi/platforms/talos_baremetal.py`
  - Pre-commit: `ruff check pulumi/platforms/talos_baremetal.py`

- [x] 2. Disable Cilium Gateway API in Phase 1

  **What to do**:
  - Open `pulumi/talos-cluster-baremetal/__main__.py`
  - Locate the `CILIUM_VALUES` dict (around line 370-416)
  - Change `"gatewayAPI"` section (lines 405-409) from:
    ```python
    "gatewayAPI": {
        "enabled": True,
        "enableAlpn": True,
        "enableAppProtocol": True,
    },
    ```
    to:
    ```python
    "gatewayAPI": {
        "enabled": False,
    },
    ```
  - This prevents Cilium from registering a competing GatewayClass controller
  - Cilium continues to function as CNI, network policy, service mesh, and Hubble — only Gateway API is disabled

  **Must NOT do**:
  - Do NOT remove the `"gatewayAPI"` key entirely — keep it with `enabled: False` for clarity
  - Do NOT change any other Cilium values (L2, hubble, kubeProxyReplacement, etc.)
  - Do NOT remove the `depends_on=gateway_api_crd_resources` from the Cilium Helm release yet — that's T3's job

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Small dict change in a known location
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with T1, T3, T4)
  - **Blocks**: T3, T10, T11
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `pulumi/talos-cluster-baremetal/__main__.py:370-432` — The CILIUM_VALUES dict and Helm release. Lines 405-409 are the gatewayAPI section to modify. Line 430 is the `depends_on=gateway_api_crd_resources` that T3 will address.

  **External References**:
  - `docs/OpenChoreo - Steps to run in Any k8s Environment.md` lines 85-99 — Shows kgateway (not Cilium) as the Gateway API controller
  - Cilium docs: `gatewayAPI.enabled=false` disables Cilium's Gateway API controller without affecting CNI functionality

  **WHY Each Reference Matters**:
  - `__main__.py:405-409` is the exact location to modify
  - The guide proves kgateway must be the sole Gateway API controller — Cilium's must be disabled

  **Acceptance Criteria**:
  - [ ] `CILIUM_VALUES` has `"gatewayAPI": {"enabled": False}`
  - [ ] No `"enableAlpn"` or `"enableAppProtocol"` keys remain (they're Cilium Gateway API-specific)
  - [ ] All other Cilium values unchanged
  - [ ] Phase 1 pytest passes: `cd pulumi/talos-cluster-baremetal && .venv/bin/python -m pytest tests/ -v`
  - [ ] Phase 1 ruff passes: `cd pulumi/talos-cluster-baremetal && .venv/bin/ruff check .`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Cilium Gateway API is disabled
    Tool: Bash (grep)
    Preconditions: File modified at pulumi/talos-cluster-baremetal/__main__.py
    Steps:
      1. Run: grep -A2 '"gatewayAPI"' pulumi/talos-cluster-baremetal/__main__.py
      2. Assert output contains: "enabled": False
      3. Assert output does NOT contain: "enableAlpn" or "enableAppProtocol"
    Expected Result: gatewayAPI section shows enabled: False with no sub-options
    Failure Indicators: enabled is True, or ALPN/AppProtocol keys still present
    Evidence: .sisyphus/evidence/task-2-cilium-gateway-disabled.txt

  Scenario: Other Cilium values untouched
    Tool: Bash (grep)
    Preconditions: File modified
    Steps:
      1. Run: grep '"l2announcements"' pulumi/talos-cluster-baremetal/__main__.py
      2. Assert output contains: "enabled": True
      3. Run: grep '"hubble"' pulumi/talos-cluster-baremetal/__main__.py
      4. Assert output contains: "enabled": True
      5. Run: grep '"kubeProxyReplacement"' pulumi/talos-cluster-baremetal/__main__.py
      6. Assert output contains: "true"
    Expected Result: L2 announcements, hubble, and kube-proxy replacement unchanged
    Failure Indicators: Any of these values changed
    Evidence: .sisyphus/evidence/task-2-cilium-other-values.txt

  Scenario: Phase 1 tests pass
    Tool: Bash
    Preconditions: Changes saved
    Steps:
      1. Run: cd pulumi/talos-cluster-baremetal && .venv/bin/python -m pytest tests/ -v
      2. Assert: all tests pass (0 failures)
    Expected Result: 20/20 tests pass
    Failure Indicators: Any test failure
    Evidence: .sisyphus/evidence/task-2-phase1-tests.txt
  ```

  **Commit**: YES (groups with T1, T3)
  - Message: `fix(platform): switch talos-baremetal to kgateway and disable Cilium Gateway API`
  - Files: `pulumi/talos-cluster-baremetal/__main__.py`
  - Pre-commit: Phase 1 `pytest` + `ruff check`

- [x] 3. Remove Gateway API CRDs from Phase 1 with retainOnDelete

  **What to do**:
  - Open `pulumi/talos-cluster-baremetal/__main__.py`
  - Locate Gateway API CRD installation (lines 354-371):
    ```python
    gateway_api_crds = { ... }  # 6 CRD URLs
    gateway_api_crd_resources: list[k8s.yaml.ConfigFile] = []
    for name, url in gateway_api_crds.items():
        crd = k8s.yaml.ConfigFile(...)
        gateway_api_crd_resources.append(crd)
    ```
  - Locate the `gateway_api_version` config var (line 54)
  - **Step 1**: Add `retain_on_delete=True` to each CRD's `ResourceOptions` so that running `pulumi up` won't delete existing CRDs from the cluster:
    ```python
    crd = k8s.yaml.ConfigFile(
        f"gateway-api-crd-{name}",
        file=url,
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            retain_on_delete=True,
        ),
    )
    ```
  - **Step 2**: Remove the CRD block entirely (lines 354-371) AND the `gateway_api_version` config var (line 54)
  - **Step 3**: Remove `depends_on=gateway_api_crd_resources` from Cilium Helm release (line 430). Since Gateway API is now disabled in Cilium (T2), it doesn't need the CRDs.
  - **Step 4**: Remove `gateway_api_version` from `Pulumi.dev.yaml` if present

  **IMPORTANT**: The two-step approach (add retainOnDelete first, THEN remove) ensures that:
  1. First `pulumi up` marks CRDs as "retain on delete"
  2. Second `pulumi up` (or same run) removes them from Pulumi state without deleting from cluster
  3. Phase 2 prerequisites will install Gateway API CRDs v1.4.1 fresh

  However, since we're modifying code (not running pulumi up between steps), the executor should:
  - Simply REMOVE the CRD block and Cilium depends_on in one commit
  - Add a comment explaining CRDs are now managed by Phase 2
  - The first `pulumi up` of Phase 1 will try to delete the CRDs — but since Phase 2 hasn't run yet, this is safe. OR: just use `pulumi state delete` for the CRD resources before running `pulumi up`.

  **Actually, safest approach**: Keep the CRD resources but add `retain_on_delete=True` and add a comment `# Retained for backward compatibility — Phase 2 prerequisites installs v1.4.1`. Then remove `depends_on` from Cilium. This way Phase 1 won't delete existing CRDs on update, and Phase 2 will overwrite them with newer versions.

  **FINAL APPROACH** (simplest): 
  1. Remove `depends_on=gateway_api_crd_resources` from Cilium release (since Gateway API is disabled)
  2. Add `retain_on_delete=True` to each CRD resource's `ResourceOptions`
  3. Add comment: `# Gateway API CRDs: retained for existing clusters, Phase 2 manages definitive versions`
  4. This is safe because: Cilium no longer needs CRDs (Gateway API disabled), existing clusters keep CRDs, Phase 2 will install its own version

  **Must NOT do**:
  - Do NOT delete CRDs from running cluster without retainOnDelete
  - Do NOT remove CRD resources if there's any risk of cascade deletion

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Known file, specific lines, clear instructions
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO — must wait for T2 (Cilium Gateway API disabled first)
  - **Parallel Group**: Wave 1 (sequential after T2)
  - **Blocks**: T10, T11
  - **Blocked By**: T2

  **References**:

  **Pattern References**:
  - `pulumi/talos-cluster-baremetal/__main__.py:354-371` — Gateway API CRD loop to modify
  - `pulumi/talos-cluster-baremetal/__main__.py:430` — Cilium `depends_on` to remove

  **API/Type References**:
  - Pulumi `ResourceOptions.retain_on_delete` — When True, Pulumi removes from state without deleting the actual resource

  **External References**:
  - `docs/OpenChoreo - Steps to run in Any k8s Environment.md` lines 57-59 — Phase 2 prerequisites install Gateway API CRDs via `experimental-install.yaml`

  **WHY Each Reference Matters**:
  - `__main__.py:354-371` is the exact code to modify
  - `retain_on_delete` prevents cascade deletion of Gateway/HTTPRoute resources
  - Guide confirms Phase 2 will install CRDs, making Phase 1 installation redundant

  **Acceptance Criteria**:
  - [ ] Each Gateway API CRD resource has `retain_on_delete=True` in ResourceOptions
  - [ ] Cilium Helm release has NO `depends_on=gateway_api_crd_resources`
  - [ ] Comment explains CRDs are retained for existing clusters, Phase 2 manages definitive versions
  - [ ] Phase 1 pytest passes
  - [ ] Phase 1 ruff passes

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: CRDs have retainOnDelete
    Tool: Bash (grep)
    Preconditions: File modified at pulumi/talos-cluster-baremetal/__main__.py
    Steps:
      1. Run: grep -c 'retain_on_delete=True' pulumi/talos-cluster-baremetal/__main__.py
      2. Assert output is: 6 (one per CRD)
    Expected Result: All 6 CRD resources have retain_on_delete=True
    Failure Indicators: Count is less than 6 or 0
    Evidence: .sisyphus/evidence/task-3-retain-on-delete.txt

  Scenario: Cilium has no CRD dependency
    Tool: Bash (grep)
    Preconditions: File modified
    Steps:
      1. Run: grep -n 'depends_on=gateway_api_crd_resources' pulumi/talos-cluster-baremetal/__main__.py
      2. Assert: no output (empty)
    Expected Result: No depends_on referencing gateway_api_crd_resources
    Failure Indicators: Line still exists
    Evidence: .sisyphus/evidence/task-3-no-depends-on.txt

  Scenario: Phase 1 tests still pass
    Tool: Bash
    Preconditions: Changes saved
    Steps:
      1. Run: cd pulumi/talos-cluster-baremetal && .venv/bin/python -m pytest tests/ -v
      2. Assert: all tests pass
    Expected Result: 20/20 tests pass
    Failure Indicators: Any test failure
    Evidence: .sisyphus/evidence/task-3-phase1-tests.txt
  ```

  **Commit**: YES (groups with T1, T2)
  - Message: `fix(platform): switch talos-baremetal to kgateway and disable Cilium Gateway API`
  - Files: `pulumi/talos-cluster-baremetal/__main__.py`
  - Pre-commit: Phase 1 `pytest` + `ruff check`

- [x] 4. Update Phase 2 exports for kgateway edition

  **What to do**:
  - Open `pulumi/__main__.py`
  - Lines 147, 150, 183-184 reference `gateway_mode == "cilium"` for exports
  - These are cosmetic/informational outputs — they will AUTOMATICALLY produce correct values when `gateway_mode` is `"kgateway"`:
    - Line 147: `edition` → "generic-cni" (correct for kgateway)
    - Line 150: `cilium_enabled` → False (correct — Cilium is CNI only, not Gateway API)
    - Line 183: `EDITION` → "generic-cni"
    - Line 184: `CILIUM_ENABLED` → "false"
  - **These lines DON'T NEED CODE CHANGES** — the logic already handles non-cilium gateway modes correctly
  - However, `cilium_enabled` is misleading since Cilium IS installed (just not as Gateway controller). Consider renaming to `cilium_gateway_enabled` for clarity.
  - **Actually**: Leave as-is. The export naming matches upstream OpenChoreo conventions. Document this in a comment if needed, but don't change the export names.
  - **The only action needed**: Verify these exports produce correct values with `gateway_mode="kgateway"`. Add a brief inline comment explaining the semantics.

  **Must NOT do**:
  - Do NOT rename exports — they may be consumed by downstream scripts
  - Do NOT change the export logic — it's already correct

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Comment addition, no logic change
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with T1, T2, T3) — but logically depends on T1
  - **Blocks**: T10
  - **Blocked By**: T1 (gateway_mode must be changed first to validate)

  **References**:

  **Pattern References**:
  - `pulumi/__main__.py:147-184` — Export section with gateway_mode conditional logic

  **WHY Each Reference Matters**:
  - These lines produce informational outputs — no code change needed, just verification

  **Acceptance Criteria**:
  - [ ] With `gateway_mode="kgateway"`, `edition` export would be "generic-cni"
  - [ ] With `gateway_mode="kgateway"`, `cilium_enabled` export would be False
  - [ ] Optional: brief comment added explaining `cilium_enabled` refers to Cilium-as-Gateway, not Cilium-as-CNI

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Exports produce correct values for kgateway
    Tool: Bash (grep)
    Preconditions: gateway_mode changed to "kgateway" in talos_baremetal.py
    Steps:
      1. Run: grep 'edition.*cilium.*generic-cni' pulumi/__main__.py
      2. Assert: logic reads "cilium" if gateway_mode == "cilium" else "generic-cni"
      3. With gateway_mode="kgateway", this evaluates to "generic-cni" — correct
    Expected Result: Export logic produces "generic-cni" for kgateway mode
    Failure Indicators: Logic hardcoded or broken
    Evidence: .sisyphus/evidence/task-4-exports-check.txt
  ```

  **Commit**: YES (groups with T1, T2, T3 — or standalone)
  - Message: `fix(openchoreo): update exports for kgateway edition`
  - Files: `pulumi/__main__.py`
  - Pre-commit: `ruff check pulumi/__main__.py`

- [x] 5. Add workflow_template_urls field to PlatformProfile

  **What to do**:
  - Open `pulumi/platforms/types.py`
  - Add a new optional field to `PlatformProfile`:
    ```python
    workflow_template_urls: tuple[str, ...] | None = None
    ```
  - This allows each platform to specify its own workflow template URLs
  - When `None`, fall back to the default URLs in `config.py` (k3d URLs for backward compatibility)
  - Open `pulumi/platforms/talos_baremetal.py` and set the field to standard URLs:
    ```python
    workflow_template_urls=(
        "checkout-source.yaml",
        "workflow-templates.yaml",  # This is the coordinator, at wt_base level
        "publish-image.yaml",
        "generate-workload.yaml",
    ),
    ```
    (These are just filenames — `config.py` will prepend the base URL)
  - Do NOT change `k3d.py` or any other platform — they continue using defaults (k3d URLs)

  **Must NOT do**:
  - Do NOT change default behavior for k3d or other platforms
  - Do NOT add full URLs to the platform profile — keep it DRY with base URL in config.py

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Adding a field + setting it in one platform
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with T6, T7, T8)
  - **Blocks**: T6
  - **Blocked By**: T1

  **References**:

  **Pattern References**:
  - `pulumi/platforms/types.py:1-79` — PlatformProfile dataclass. Look at how existing optional fields are declared (e.g., `cilium_cni_bin_path: str = ""`).
  - `pulumi/platforms/talos_baremetal.py:1-33` — Platform profile to add field to.
  - `pulumi/platforms/k3d.py` — Reference platform that uses k3d templates (do NOT modify).

  **API/Type References**:
  - `pulumi/config.py:263-269` — Where `workflow_templates_urls` is currently constructed. T6 will modify this to use the platform field.

  **External References**:
  - `docs/OpenChoreo - Steps to run in Any k8s Environment.md` lines 696-722 — Standard workflow template URLs

  **WHY Each Reference Matters**:
  - `types.py` shows existing field patterns to follow for consistency
  - `config.py` is where this field will be consumed (in T6)
  - Guide provides the correct standard URLs

  **Acceptance Criteria**:
  - [ ] `PlatformProfile` has `workflow_template_urls: tuple[str, ...] | None = None`
  - [ ] `talos_baremetal.py` sets the field with standard template filenames
  - [ ] No other platform files modified
  - [ ] Phase 2 ruff passes

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: PlatformProfile has workflow_template_urls field
    Tool: Bash (grep)
    Preconditions: types.py modified
    Steps:
      1. Run: grep 'workflow_template_urls' pulumi/platforms/types.py
      2. Assert: field exists with type tuple[str, ...] | None and default None
    Expected Result: Field declared with correct type and default
    Failure Indicators: Field missing or wrong type
    Evidence: .sisyphus/evidence/task-5-platform-field.txt

  Scenario: talos_baremetal has standard template URLs
    Tool: Bash (grep)
    Preconditions: talos_baremetal.py modified
    Steps:
      1. Run: grep -A5 'workflow_template_urls' pulumi/platforms/talos_baremetal.py
      2. Assert: contains "publish-image.yaml" (not "publish-image-k3d.yaml")
      3. Assert: contains "generate-workload.yaml" (not "generate-workload-k3d.yaml")
    Expected Result: Standard (non-k3d) template filenames
    Failure Indicators: k3d-specific filenames present
    Evidence: .sisyphus/evidence/task-5-standard-urls.txt
  ```

  **Commit**: YES (groups with T6)
  - Message: `fix(workflow): use standard template URLs for bare-metal`
  - Files: `pulumi/platforms/types.py`, `pulumi/platforms/talos_baremetal.py`
  - Pre-commit: `ruff check`

- [x] 6. Fix workflow template URLs and sed patterns in config.py and workflow_plane.py

  **What to do**:
  - **In `pulumi/config.py` (lines 263-269)**:
    - If `platform.workflow_template_urls` is set, use those (resolving filenames against `wt_base`)
    - If `None`, fall back to current k3d URLs (backward compatible)
    - Implementation:
      ```python
      wt_base = f"{raw_base}/samples/getting-started"
      if platform.workflow_template_urls:
          workflow_templates_urls = []
          for filename in platform.workflow_template_urls:
              if "/" not in filename:
                  # Simple filename like "publish-image.yaml" → under workflow-templates/
                  workflow_templates_urls.append(f"{wt_base}/workflow-templates/{filename}")
              else:
                  # Already includes path like "workflow-templates.yaml"
                  workflow_templates_urls.append(f"{wt_base}/{filename}")
      else:
          # Default: k3d-specific URLs (backward compatible)
          workflow_templates_urls = [
              f"{wt_base}/workflow-templates/checkout-source.yaml",
              f"{wt_base}/workflow-templates.yaml",
              f"{wt_base}/workflow-templates/publish-image-k3d.yaml",
              f"{wt_base}/workflow-templates/generate-workload-k3d.yaml",
          ]
      ```
    
    **WAIT** — looking at the guide more carefully:
    - `checkout-source.yaml` is under `workflow-templates/`
    - `workflow-templates.yaml` is at the `wt_base` level (NOT under `workflow-templates/`)
    - `publish-image.yaml` is under `workflow-templates/`
    - `generate-workload.yaml` is under `workflow-templates/`
    
    So the PlatformProfile should store **relative paths from wt_base**:
    ```python
    workflow_template_urls=(
        "workflow-templates/checkout-source.yaml",
        "workflow-templates.yaml",
        "workflow-templates/publish-image.yaml",
        "workflow-templates/generate-workload.yaml",
    ),
    ```
    And config.py just prepends `wt_base`:
    ```python
    if platform.workflow_template_urls:
        workflow_templates_urls = [f"{wt_base}/{path}" for path in platform.workflow_template_urls]
    ```

  - **In `pulumi/components/workflow_plane.py` (lines 109-123)**:
    - The `k3d_templates` set and sed patterns need updating for standard templates
    - For **standard** (non-k3d) templates:
      - `publish-image.yaml` uses `ttl.sh` directly — NO sed needed
      - `generate-workload.yaml` has `host.k3d.internal` references that need sed replacement:
        - `https://host.k3d.internal:8080/oauth2/token` → `https://thunder.{domain_base}/oauth2/token`
        - `http://host.k3d.internal:8080` → `https://api.{domain_base}`
    - Update the sed logic to handle BOTH k3d and standard templates:
      ```python
      # Templates needing URL patching (k3d-specific host references)
      needs_patching = {
          "publish-image-k3d.yaml",     # k3d: registry endpoint
          "generate-workload-k3d.yaml", # k3d: gateway + thunder
          "generate-workload.yaml",     # standard: gateway + thunder (same k3d placeholders)
      }
      ```
    - The sed commands should also add thunder URL replacement:
      ```python
      thunder_url = f"https://thunder.{cfg.domain_base}"
      api_url = f"https://api.{cfg.domain_base}"
      
      if any(url.endswith(t) for t in needs_patching):
          sed_parts = [f"curl -sL {url}"]
          if "k3d" in url:
              # k3d templates: replace registry + gateway endpoints
              sed_parts.append(f"sed 's|host.k3d.internal:10082|{registry_endpoint}|g'")
              sed_parts.append(f"sed 's|host.k3d.internal:8080|{gateway_endpoint}|g'")
          else:
              # Standard templates: replace thunder + api endpoints
              sed_parts.append(f"sed 's|https://host.k3d.internal:8080/oauth2/token|{thunder_url}/oauth2/token|g'")
              sed_parts.append(f"sed 's|http://host.k3d.internal:8080|{api_url}|g'")
          sed_parts.append(f"kubectl apply --context {cfg.kubeconfig_context} -f -")
          apply_cmds.append(" | ".join(sed_parts))
      ```

  **Must NOT do**:
  - Do NOT break k3d workflow templates — they must continue working with existing sed patterns
  - Do NOT hardcode domain names — use `cfg.domain_base`
  - Do NOT add sed to `publish-image.yaml` — it uses ttl.sh directly, no patching needed

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Multi-file change with conditional logic and URL pattern matching
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO — depends on T5 (field must exist first)
  - **Parallel Group**: Wave 2 (sequential after T5)
  - **Blocks**: T10, T11
  - **Blocked By**: T5

  **References**:

  **Pattern References**:
  - `pulumi/config.py:255-269` — Current workflow template URL construction. Lines 264-268 are the URLs to make platform-conditional.
  - `pulumi/components/workflow_plane.py:97-128` — Workflow template application with sed logic. Lines 109-123 are the template matching and sed replacement.

  **API/Type References**:
  - `pulumi/platforms/types.py:PlatformProfile.workflow_template_urls` — New field from T5
  - `pulumi/config.py:OpenChoreoConfig.workflow_templates_urls` — The config attribute that consumers read

  **External References**:
  - `docs/OpenChoreo - Steps to run in Any k8s Environment.md` lines 696-722 — Official template URLs and sed patterns:
    - `checkout-source.yaml`: no sed
    - `workflow-templates.yaml`: no sed
    - `publish-image.yaml`: no sed (uses ttl.sh)
    - `generate-workload.yaml`: sed to replace `host.k3d.internal:8080` with real URLs

  **WHY Each Reference Matters**:
  - `config.py:264-268` is the exact location to add platform branching
  - `workflow_plane.py:109-123` is the sed logic that needs updating for standard templates
  - Guide provides the correct sed patterns for standard templates

  **Acceptance Criteria**:
  - [ ] `config.py` uses `platform.workflow_template_urls` when set, falls back to k3d URLs when `None`
  - [ ] `workflow_plane.py` correctly seds `generate-workload.yaml` with thunder/api URLs
  - [ ] `publish-image.yaml` is applied WITHOUT sed (just kubectl apply)
  - [ ] k3d templates still work with existing sed patterns
  - [ ] No `k3d` string appears in any URL for talos-baremetal platform
  - [ ] Phase 2 ruff passes

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Standard templates used for talos-baremetal
    Tool: Bash (grep)
    Preconditions: config.py and workflow_plane.py modified
    Steps:
      1. Run: grep -n 'workflow_template_urls' pulumi/config.py
      2. Assert: platform-conditional logic exists (if platform.workflow_template_urls)
      3. Run: grep 'k3d' pulumi/platforms/talos_baremetal.py
      4. Assert: no output (no k3d references in talos-baremetal)
    Expected Result: talos-baremetal uses standard URLs, no k3d references
    Failure Indicators: k3d URLs used for talos-baremetal, or conditional logic missing
    Evidence: .sisyphus/evidence/task-6-standard-templates.txt

  Scenario: generate-workload.yaml gets thunder/api sed replacement
    Tool: Bash (grep)
    Preconditions: workflow_plane.py modified
    Steps:
      1. Run: grep -A5 'generate-workload.yaml' pulumi/components/workflow_plane.py
      2. Assert: sed patterns include thunder URL replacement
      3. Assert: sed patterns include api URL replacement
    Expected Result: Standard generate-workload.yaml is sed-patched with real URLs
    Failure Indicators: Missing sed for standard template, or wrong URL patterns
    Evidence: .sisyphus/evidence/task-6-sed-patterns.txt

  Scenario: publish-image.yaml is applied without sed
    Tool: Bash (grep)
    Preconditions: workflow_plane.py modified
    Steps:
      1. Run: grep -B2 -A2 'publish-image.yaml' pulumi/components/workflow_plane.py
      2. Assert: standard publish-image.yaml is NOT in the needs_patching set
    Expected Result: publish-image.yaml applied via plain kubectl apply
    Failure Indicators: publish-image.yaml appears in needs_patching/k3d_templates set
    Evidence: .sisyphus/evidence/task-6-publish-no-sed.txt

  Scenario: k3d templates still work (backward compatibility)
    Tool: Bash (grep)
    Preconditions: workflow_plane.py modified
    Steps:
      1. Run: grep 'publish-image-k3d.yaml' pulumi/components/workflow_plane.py
      2. Assert: k3d template name still referenced in needs_patching set
      3. Run: grep 'host.k3d.internal:10082' pulumi/components/workflow_plane.py
      4. Assert: k3d registry sed pattern still present
    Expected Result: k3d-specific sed logic preserved for k3d platforms
    Failure Indicators: k3d sed patterns removed or broken
    Evidence: .sisyphus/evidence/task-6-k3d-compat.txt
  ```

  **Commit**: YES (groups with T5)
  - Message: `fix(workflow): use standard template URLs for bare-metal`
  - Files: `pulumi/config.py`, `pulumi/components/workflow_plane.py`
  - Pre-commit: `ruff check`

- [x] 7. Add TLS constants and tls_enabled to stack config

  **What to do**:
  - **In `pulumi/Pulumi.talos-baremetal.yaml`**:
    - Add `openchoreo:tls_enabled: "true"` to the `config:` section
    - Add `openchoreo:domain_base: "openchoreo.local"` if not already present (needed for TLS cert dnsNames — bare-metal needs a real domain, not `openchoreo.localhost`)
  - **In `pulumi/config.py`**:
    - Verify existing constants are sufficient for TLS setup. The following already exist and are reusable:
      - `NS_CERT_MANAGER = "cert-manager"` (line 32) — namespace for CA certificate
      - `TIMEOUT_TLS_WAIT = 240` (line 61) — timeout for certificate readiness
      - `SECRET_AGENT_TLS = "cluster-agent-tls"` (line 39)
    - Add new constants for TLS resource names used in `tls_setup.py`:
      ```python
      # TLS CA chain resource names (matches official guide Step 2)
      ISSUER_SELFSIGNED_BOOTSTRAP = "selfsigned-bootstrap"
      CERT_OPENCHOREO_CA = "openchoreo-ca"
      SECRET_OPENCHOREO_CA = "openchoreo-ca-secret"
      ISSUER_OPENCHOREO_CA = "openchoreo-ca"
      CERT_CP_GATEWAY_TLS = "cp-gateway-tls"
      CERT_DP_GATEWAY_TLS = "dp-gateway-tls"
      ```
  - These constants will be consumed by `tls_setup.py` (T8)

  **Must NOT do**:
  - Do NOT change `tls_enabled` default value in `config.py` — it stays `False` for other platforms
  - Do NOT add TLS resource creation logic here — that's T8's job
  - Do NOT add observability plane TLS constants

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Adding constants to config file + one line to YAML stack config
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with T5, T6, T8)
  - **Blocks**: T8
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `pulumi/config.py:30-67` — Existing constant declarations. Follow the same naming pattern (UPPER_SNAKE_CASE, grouped by concern with comments).
  - `pulumi/config.py:185` — Where `tls_enabled` is read from Pulumi config. Confirms the config key is `openchoreo:tls_enabled`.
  - `pulumi/Pulumi.talos-baremetal.yaml:1-7` — Current stack config. Add new keys under `config:`.

  **External References**:
  - `docs/OpenChoreo - Steps to run in Any k8s Environment.md` lines 164-195 — CA chain resource names: `selfsigned-bootstrap`, `openchoreo-ca`, `openchoreo-ca-secret`
  - `docs/OpenChoreo - Steps to run in Any k8s Environment.md` lines 284-299 — CP TLS cert name: `cp-gateway-tls`
  - `docs/OpenChoreo - Steps to run in Any k8s Environment.md` lines 540-556 — DP TLS cert name: `dp-gateway-tls`

  **WHY Each Reference Matters**:
  - `config.py:30-67` shows the naming convention for constants so T7 stays consistent
  - `config.py:185` confirms the Pulumi config key name for `tls_enabled`
  - Guide provides the exact resource names that must match (TLS setup depends on these names)

  **Acceptance Criteria**:
  - [ ] `Pulumi.talos-baremetal.yaml` has `openchoreo:tls_enabled: "true"`
  - [ ] `config.py` has constants: `ISSUER_SELFSIGNED_BOOTSTRAP`, `CERT_OPENCHOREO_CA`, `SECRET_OPENCHOREO_CA`, `ISSUER_OPENCHOREO_CA`, `CERT_CP_GATEWAY_TLS`, `CERT_DP_GATEWAY_TLS`
  - [ ] Constants match official guide resource names exactly
  - [ ] Phase 2 ruff passes

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Stack config has tls_enabled set to true
    Tool: Bash (grep)
    Preconditions: Pulumi.talos-baremetal.yaml modified
    Steps:
      1. Run: grep 'tls_enabled' pulumi/Pulumi.talos-baremetal.yaml
      2. Assert output contains: openchoreo:tls_enabled: "true"
    Expected Result: tls_enabled is set to "true" for talos-baremetal stack
    Failure Indicators: Key missing or value is "false"
    Evidence: .sisyphus/evidence/task-7-tls-enabled-config.txt

  Scenario: TLS constants exist in config.py
    Tool: Bash (grep)
    Preconditions: config.py modified
    Steps:
      1. Run: grep 'ISSUER_SELFSIGNED_BOOTSTRAP' pulumi/config.py
      2. Assert: output contains the constant declaration
      3. Run: grep 'SECRET_OPENCHOREO_CA' pulumi/config.py
      4. Assert: output contains "openchoreo-ca-secret"
      5. Run: grep 'CERT_CP_GATEWAY_TLS' pulumi/config.py
      6. Assert: output contains "cp-gateway-tls"
      7. Run: grep 'CERT_DP_GATEWAY_TLS' pulumi/config.py
      8. Assert: output contains "dp-gateway-tls"
    Expected Result: All 6 TLS constants declared with correct values
    Failure Indicators: Any constant missing or misspelled
    Evidence: .sisyphus/evidence/task-7-tls-constants.txt

  Scenario: Ruff passes after changes
    Tool: Bash
    Preconditions: Changes saved
    Steps:
      1. Run: cd pulumi && .venv/bin/ruff check config.py
      2. Assert: 0 errors
    Expected Result: Clean lint
    Failure Indicators: Any ruff error
    Evidence: .sisyphus/evidence/task-7-ruff.txt
  ```

  **Commit**: YES (groups with T8)
  - Message: `feat(tls): add explicit CA chain and per-plane certificates`
  - Files: `pulumi/config.py`, `pulumi/Pulumi.talos-baremetal.yaml`
  - Pre-commit: `ruff check`

- [x] 8. Create tls_setup.py component (CA chain + per-plane wildcard certs)

  **What to do**:
  - Create a new file: `pulumi/components/tls_setup.py`
  - Implement a `TlsSetup` ComponentResource that creates the full CA chain and per-plane TLS certificates
  - **Resources to create** (matching guide Step 2 + Step 3/5 TLS):

    1. **`selfsigned-bootstrap` ClusterIssuer** (selfSigned):
       ```yaml
       apiVersion: cert-manager.io/v1
       kind: ClusterIssuer
       metadata:
         name: selfsigned-bootstrap
       spec:
         selfSigned: {}
       ```

    2. **`openchoreo-ca` Certificate** (isCA, ECDSA P256, in cert-manager namespace):
       ```yaml
       apiVersion: cert-manager.io/v1
       kind: Certificate
       metadata:
         name: openchoreo-ca
         namespace: cert-manager
       spec:
         isCA: true
         commonName: openchoreo-ca
         secretName: openchoreo-ca-secret
         privateKey:
           algorithm: ECDSA
           size: 256
         issuerRef:
           name: selfsigned-bootstrap
           kind: ClusterIssuer
       ```

    3. **`openchoreo-ca` ClusterIssuer** (backed by CA secret):
       ```yaml
       apiVersion: cert-manager.io/v1
       kind: ClusterIssuer
       metadata:
         name: openchoreo-ca
       spec:
         ca:
           secretName: openchoreo-ca-secret
       ```

    4. **`cp-gateway-tls` Certificate** (wildcard, in openchoreo-control-plane namespace):
       ```yaml
       apiVersion: cert-manager.io/v1
       kind: Certificate
       metadata:
         name: cp-gateway-tls
         namespace: openchoreo-control-plane
       spec:
         secretName: cp-gateway-tls
         issuerRef:
           name: openchoreo-ca
           kind: ClusterIssuer
         dnsNames:
           - "*.{domain_base}"
           - "{domain_base}"
         privateKey:
           rotationPolicy: Always
       ```

    5. **`dp-gateway-tls` Certificate** (wildcard, in openchoreo-data-plane namespace):
       ```yaml
       apiVersion: cert-manager.io/v1
       kind: Certificate
       metadata:
         name: dp-gateway-tls
         namespace: openchoreo-data-plane
       spec:
         secretName: dp-gateway-tls
         issuerRef:
           name: openchoreo-ca
           kind: ClusterIssuer
         dnsNames:
           - "*.{dp_domain}"
           - "{dp_domain}"
         privateKey:
           rotationPolicy: Always
       ```
       Where `dp_domain` is `cfg.domain_base` (same domain for DP in bare-metal setup).

  - **Implementation approach**: Use `k8s.apiextensions.CustomResource` for ClusterIssuer and Certificate CRDs (they are cert-manager custom resources)
  - **Dependency chain** (CRITICAL — must use `depends_on`):
    ```
    cert-manager (from prerequisites) → selfsigned-bootstrap ClusterIssuer
    → openchoreo-ca Certificate → openchoreo-ca ClusterIssuer
    → cp-gateway-tls Certificate (parallel with dp-gateway-tls)
    → dp-gateway-tls Certificate
    ```
  - **Gate behind `tls_enabled`**: The entire TlsSetup component should only be instantiated when `cfg.tls_enabled is True`
  - **Wire into `pulumi/__main__.py`**:
    - Import `tls_setup` from components
    - After prerequisites (Step 1) and before control_plane (Step 2), add:
      ```python
      # ─── Step 1.5: TLS Setup (optional — bare-metal self-signed CA) ───
      tls_resources = None
      if cfg.tls_enabled:
          from components import tls_setup
          tls_component = tls_setup.TlsSetup(
              "tls-setup",
              cfg=cfg,
              k8s_provider=k8s_provider,
              depends=[prereqs.cert_manager],
          )
          tls_resources = tls_component.result
      ```
    - Add `tls_resources` to control_plane and data_plane `depends` if not None
  - **Follow existing component patterns**: Look at `prerequisites.py` for how to structure a `ComponentResource` with `_child_opts`, `register_outputs`, etc.

  **Must NOT do**:
  - Do NOT add observability plane TLS (`obs-gateway-tls`) — explicitly out of scope per Metis directive
  - Do NOT hardcode domain names — use `cfg.domain_base` for dnsNames
  - Do NOT create the component when `tls_enabled` is False
  - Do NOT use `k8s.yaml.v2.ConfigGroup` with `yaml=` for these — use `CustomResource` for proper dependency tracking
  - Do NOT skip the `depends_on` chain — cert-manager must be ready before ClusterIssuers

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: New file creation with complex dependency chain, multiple Kubernetes custom resources, conditional wiring into main entry point
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `find-docs`: Not needed — guide provides exact YAML specs
    - `senior-backend`: Python code is simple dataclass + Pulumi resources, not backend API design

  **Parallelization**:
  - **Can Run In Parallel**: NO — depends on T7 (constants must exist)
  - **Parallel Group**: Wave 2 (sequential after T7)
  - **Blocks**: T10, T11
  - **Blocked By**: T7 (TLS constants), T1 (gateway_mode for domain resolution)

  **References**:

  **Pattern References**:
  - `pulumi/components/prerequisites.py:1-370` — ComponentResource pattern to follow. Look at class structure, `_child_opts`, `register_outputs`, import style. Especially lines 70-80 for Gateway API CRD creation and lines 140-170 for kgateway Helm deployment — these show how to create cert-manager resources with proper dependencies.
  - `pulumi/components/prerequisites.py:218-228` — How `WaitCustomResourceCondition` is used to wait for cert-manager resources to be ready. The TLS certificates need the same wait pattern.
  - `pulumi/__main__.py:60-76` — Where prerequisites and control_plane are wired. TLS setup goes between them (after line 67, before line 70).

  **API/Type References**:
  - `pulumi/config.py:70-93` — `OpenChoreoConfig` dataclass. Access `cfg.tls_enabled`, `cfg.domain_base`, `cfg.platform.gateway_mode`.
  - `pulumi/config.py:T7-constants` — Constants from T7: `ISSUER_SELFSIGNED_BOOTSTRAP`, `CERT_OPENCHOREO_CA`, `SECRET_OPENCHOREO_CA`, `ISSUER_OPENCHOREO_CA`, `CERT_CP_GATEWAY_TLS`, `CERT_DP_GATEWAY_TLS`, `NS_CERT_MANAGER`, `NS_CONTROL_PLANE`, `NS_DATA_PLANE`.

  **External References**:
  - `docs/OpenChoreo - Steps to run in Any k8s Environment.md` lines 159-195 — Full Step 2 TLS setup (CA chain: selfsigned-bootstrap → openchoreo-ca cert → openchoreo-ca issuer)
  - `docs/OpenChoreo - Steps to run in Any k8s Environment.md` lines 278-305 — CP TLS certificate (`cp-gateway-tls`) with exact spec
  - `docs/OpenChoreo - Steps to run in Any k8s Environment.md` lines 537-559 — DP TLS certificate (`dp-gateway-tls`) with exact spec
  - Pulumi Kubernetes `k8s.apiextensions.CustomResource` — For creating cert-manager ClusterIssuer and Certificate resources

  **WHY Each Reference Matters**:
  - `prerequisites.py` provides the exact code pattern to replicate (ComponentResource with child opts, dependency chains)
  - `prerequisites.py:218-228` shows how to wait for cert-manager readiness — critical for the dependency chain
  - `__main__.py:60-76` is the insertion point for TLS setup wiring
  - Guide sections provide exact YAML specs that must be converted to Pulumi `CustomResource` calls
  - `config.py` constants ensure resource names match between TLS creation and consumers (helm values, register_plane)

  **Acceptance Criteria**:
  - [ ] `pulumi/components/tls_setup.py` exists and is importable
  - [ ] Creates 5 resources: selfsigned-bootstrap ClusterIssuer, openchoreo-ca Certificate, openchoreo-ca ClusterIssuer, cp-gateway-tls Certificate, dp-gateway-tls Certificate
  - [ ] Dependency chain is correct: each resource depends on its predecessor
  - [ ] dnsNames use `cfg.domain_base` (not hardcoded)
  - [ ] `pulumi/__main__.py` conditionally instantiates `TlsSetup` when `cfg.tls_enabled`
  - [ ] Control plane depends on TLS resources (when TLS enabled)
  - [ ] Component is NOT created when `tls_enabled` is False
  - [ ] Phase 2 ruff passes
  - [ ] Phase 2 pytest passes (no import errors)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: tls_setup.py creates all 5 TLS resources
    Tool: Bash (grep)
    Preconditions: pulumi/components/tls_setup.py created
    Steps:
      1. Run: grep -c 'CustomResource' pulumi/components/tls_setup.py
      2. Assert: count is 5 (one per resource)
      3. Run: grep 'selfsigned-bootstrap' pulumi/components/tls_setup.py
      4. Assert: ClusterIssuer with selfSigned spec
      5. Run: grep 'openchoreo-ca-secret' pulumi/components/tls_setup.py
      6. Assert: referenced in both Certificate and ClusterIssuer
      7. Run: grep 'cp-gateway-tls' pulumi/components/tls_setup.py
      8. Assert: Certificate in control-plane namespace
      9. Run: grep 'dp-gateway-tls' pulumi/components/tls_setup.py
      10. Assert: Certificate in data-plane namespace
    Expected Result: All 5 resources created with correct names and specs
    Failure Indicators: Missing resources or wrong names
    Evidence: .sisyphus/evidence/task-8-tls-resources.txt

  Scenario: Dependency chain is correct
    Tool: Bash (grep)
    Preconditions: tls_setup.py created
    Steps:
      1. Run: grep -n 'depends_on' pulumi/components/tls_setup.py
      2. Assert: multiple depends_on chains exist
      3. Verify ordering: bootstrap_issuer → ca_cert → ca_issuer → plane_certs
    Expected Result: Sequential dependency chain from bootstrap to plane certs
    Failure Indicators: Missing depends_on or wrong ordering
    Evidence: .sisyphus/evidence/task-8-dependency-chain.txt

  Scenario: TLS gated behind tls_enabled in __main__.py
    Tool: Bash (grep)
    Preconditions: __main__.py modified
    Steps:
      1. Run: grep -A3 'tls_enabled' pulumi/__main__.py
      2. Assert: conditional import and instantiation of tls_setup
      3. Run: grep 'tls_setup' pulumi/__main__.py
      4. Assert: import and usage present
    Expected Result: TLS component only created when tls_enabled is True
    Failure Indicators: Unconditional TLS setup or missing gate
    Evidence: .sisyphus/evidence/task-8-tls-gated.txt

  Scenario: No observability plane TLS (scope guard)
    Tool: Bash (grep)
    Preconditions: tls_setup.py created
    Steps:
      1. Run: grep -i 'observability\|obs-gateway' pulumi/components/tls_setup.py
      2. Assert: no output (empty)
    Expected Result: No observability plane TLS references
    Failure Indicators: Any observability TLS resource found
    Evidence: .sisyphus/evidence/task-8-no-obs-tls.txt

  Scenario: Phase 2 lint and import check
    Tool: Bash
    Preconditions: All files saved
    Steps:
      1. Run: cd pulumi && .venv/bin/ruff check components/tls_setup.py
      2. Assert: 0 errors
      3. Run: cd pulumi && .venv/bin/python -c "from components import tls_setup"
      4. Assert: no import errors
    Expected Result: Clean lint and successful import
    Failure Indicators: Ruff errors or import failures
    Evidence: .sisyphus/evidence/task-8-lint-import.txt
  ```

  **Commit**: YES (groups with T7)
  - Message: `feat(tls): add explicit CA chain and per-plane certificates`
  - Files: `pulumi/components/tls_setup.py`, `pulumi/__main__.py`, `pulumi/config.py`
  - Pre-commit: Phase 2 `ruff check` + `python -c "from components import tls_setup"`

- [x] 9. Add listenerName to ClusterDataPlane registration in data_plane.py

  **What to do**:
  - Open `pulumi/components/data_plane.py`
  - Locate the `extra_spec` dict (lines 109-127)
  - Add `listenerName` to both `http` and `https` entries in the gateway ingress spec:
    ```python
    extra_spec = {
        "gateway": {
            "ingress": {
                "external": {
                    "name": "gateway-default",
                    "namespace": NS_DATA_PLANE,
                    "http": {
                        "host": cfg.domain_base,
                        "listenerName": "http",
                        "port": cfg.dp_http_port,
                    },
                    "https": {
                        "host": cfg.domain_base,
                        "listenerName": "https",
                        "port": cfg.dp_https_port,
                    },
                },
            },
        },
        "secretStoreRef": {"name": "default"},
    }
    ```
  - The `listenerName` field tells OpenChoreo which Gateway listener to bind each route to. Without it, routes may not bind correctly to the kgateway listeners.

  **Must NOT do**:
  - Do NOT change any other fields in `extra_spec`
  - Do NOT modify the `_allow_gateway_ingress` Cilium policy section
  - Do NOT touch the `register_plane` call arguments

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Adding two key-value pairs to an existing dict
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (can run with T5, T6, T7, T8 — only depends on T1 for gateway_mode)
  - **Blocks**: T10, T11
  - **Blocked By**: T1

  **References**:

  **Pattern References**:
  - `pulumi/components/data_plane.py:109-127` — Exact location of `extra_spec` dict to modify. Add `listenerName` inside `http` and `https` sub-dicts.

  **External References**:
  - `docs/OpenChoreo - Steps to run in Any k8s Environment.md` lines 608-625 — Official ClusterDataPlane spec showing `listenerName: http` (line 617) and `listenerName: https` (line 621) as required fields.

  **WHY Each Reference Matters**:
  - `data_plane.py:109-127` is the exact code to modify
  - Guide lines 612-625 prove `listenerName` is required — our code is missing it, which is a compliance gap

  **Acceptance Criteria**:
  - [ ] `extra_spec["gateway"]["ingress"]["external"]["http"]` contains `"listenerName": "http"`
  - [ ] `extra_spec["gateway"]["ingress"]["external"]["https"]` contains `"listenerName": "https"`
  - [ ] All other fields in `extra_spec` unchanged
  - [ ] Phase 2 ruff passes

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: listenerName present in both http and https
    Tool: Bash (grep)
    Preconditions: data_plane.py modified
    Steps:
      1. Run: grep -c 'listenerName' pulumi/components/data_plane.py
      2. Assert: count is 2 (one for http, one for https)
      3. Run: grep -A1 '"http":' pulumi/components/data_plane.py | grep 'listenerName'
      4. Assert: contains "listenerName": "http"
      5. Run: grep -A1 '"https":' pulumi/components/data_plane.py | grep 'listenerName'
      6. Assert: contains "listenerName": "https"
    Expected Result: Both http and https have correct listenerName values
    Failure Indicators: Missing listenerName or wrong values
    Evidence: .sisyphus/evidence/task-9-listener-name.txt

  Scenario: No other extra_spec fields changed
    Tool: Bash (grep)
    Preconditions: data_plane.py modified
    Steps:
      1. Run: grep '"gateway-default"' pulumi/components/data_plane.py
      2. Assert: name field still present
      3. Run: grep 'secretStoreRef' pulumi/components/data_plane.py
      4. Assert: still has {"name": "default"}
    Expected Result: All other extra_spec fields unchanged
    Failure Indicators: Missing or modified fields
    Evidence: .sisyphus/evidence/task-9-extra-spec-unchanged.txt
  ```

  **Commit**: YES (standalone)
  - Message: `fix(dataplane): add listenerName to ClusterDataPlane registration`
  - Files: `pulumi/components/data_plane.py`
  - Pre-commit: `ruff check pulumi/components/data_plane.py`

- [x] 10. Add unit tests for gateway mode, TLS, workflow URLs, and listenerName

  **What to do**:
  - Create a new test file: `pulumi/tests/test_config_compliance.py`
  - Add tests that verify the configuration produces correct values for talos-baremetal:

    **Test 1: Gateway mode is kgateway for talos-baremetal**
    ```python
    def test_talos_baremetal_gateway_mode():
        from platforms.talos_baremetal import talos_baremetal
        assert talos_baremetal.gateway_mode == "kgateway"
        assert talos_baremetal.cni_mode == "cilium"
    ```

    **Test 2: TLS constants match official guide**
    ```python
    def test_tls_constants_match_guide():
        from config import (
            ISSUER_SELFSIGNED_BOOTSTRAP,
            CERT_OPENCHOREO_CA,
            SECRET_OPENCHOREO_CA,
            CERT_CP_GATEWAY_TLS,
            CERT_DP_GATEWAY_TLS,
        )
        assert ISSUER_SELFSIGNED_BOOTSTRAP == "selfsigned-bootstrap"
        assert CERT_OPENCHOREO_CA == "openchoreo-ca"
        assert SECRET_OPENCHOREO_CA == "openchoreo-ca-secret"
        assert CERT_CP_GATEWAY_TLS == "cp-gateway-tls"
        assert CERT_DP_GATEWAY_TLS == "dp-gateway-tls"
    ```

    **Test 3: workflow_template_urls field exists in PlatformProfile**
    ```python
    def test_platform_profile_has_workflow_template_urls():
        from platforms.types import PlatformProfile
        p = PlatformProfile(name="test", gateway_mode="kgateway", cni_mode="cilium")
        assert p.workflow_template_urls is None  # default is None
    ```

    **Test 4: talos-baremetal has standard (non-k3d) workflow templates**
    ```python
    def test_talos_baremetal_standard_workflow_urls():
        from platforms.talos_baremetal import talos_baremetal
        assert talos_baremetal.workflow_template_urls is not None
        for url in talos_baremetal.workflow_template_urls:
            assert "k3d" not in url, f"k3d reference in talos-baremetal URL: {url}"
    ```

    **Test 5: Edition export logic for kgateway**
    ```python
    def test_kgateway_edition_is_generic_cni():
        # The export logic: "cilium" if gateway_mode == "cilium" else "generic-cni"
        gateway_mode = "kgateway"
        edition = "cilium" if gateway_mode == "cilium" else "generic-cni"
        assert edition == "generic-cni"
    ```

    **Test 6: k3d platform still uses k3d default (backward compat)**
    ```python
    def test_k3d_workflow_urls_default():
        from platforms.k3d import k3d
        # k3d should NOT set workflow_template_urls (uses default k3d URLs)
        assert k3d.workflow_template_urls is None
    ```

  - These are pure Python unit tests — no Pulumi runtime, no cluster required
  - Follow existing test patterns from `pulumi/talos-cluster-baremetal/tests/test_config_patches.py`

  **Must NOT do**:
  - Do NOT write tests that require a running cluster or Pulumi runtime
  - Do NOT import Pulumi SDK in tests (it requires a running engine)
  - Do NOT modify existing test files
  - Do NOT test TLS resource creation (that requires Pulumi mocking — out of scope)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Multiple test cases across different modules, needs careful import handling
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `tdd-guide`: Tests are written AFTER implementation, not TDD workflow
    - `senior-qa`: Tests are simple assertions, not complex E2E

  **Parallelization**:
  - **Can Run In Parallel**: NO — depends on all prior tasks (T1-T9)
  - **Parallel Group**: Wave 3 (sequential after Wave 2)
  - **Blocks**: T11
  - **Blocked By**: T1, T2, T3, T4, T5, T6, T7, T8, T9

  **References**:

  **Pattern References**:
  - `pulumi/talos-cluster-baremetal/tests/test_config_patches.py` — Existing test file showing test structure, assertions, and import patterns for Pulumi config testing.
  - `pulumi/tests/test_e2e_smoke.py` — Phase 2 e2e tests. These require a running cluster (`@pytest.mark.e2e`). Our new tests should NOT be e2e — they should be pure unit tests.
  - `pulumi/tests/conftest.py` — Phase 2 test configuration. May need to add non-e2e fixture support.

  **API/Type References**:
  - `pulumi/platforms/types.py:PlatformProfile` — Dataclass to test field existence and defaults
  - `pulumi/platforms/talos_baremetal.py` — Platform instance to test gateway_mode and workflow_template_urls
  - `pulumi/platforms/k3d.py` — Platform instance for backward compatibility test
  - `pulumi/config.py` — TLS constants to test

  **WHY Each Reference Matters**:
  - `test_config_patches.py` shows how to test config without Pulumi runtime — critical for avoiding engine dependency
  - Platform files provide the concrete instances to assert against
  - `config.py` constants must match official guide values exactly

  **Acceptance Criteria**:
  - [ ] `pulumi/tests/test_config_compliance.py` exists with 6+ test functions
  - [ ] All tests pass: `cd pulumi && .venv/bin/python -m pytest tests/test_config_compliance.py -v`
  - [ ] No test requires Pulumi runtime or running cluster
  - [ ] Tests cover: gateway_mode, cni_mode, TLS constants, workflow_template_urls, edition logic, k3d backward compat
  - [ ] Phase 2 ruff passes on test file

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All compliance tests pass
    Tool: Bash
    Preconditions: test_config_compliance.py created, all prior tasks complete
    Steps:
      1. Run: cd pulumi && .venv/bin/python -m pytest tests/test_config_compliance.py -v
      2. Assert: all tests pass (6+ tests, 0 failures)
    Expected Result: 6/6 tests pass
    Failure Indicators: Any test failure or import error
    Evidence: .sisyphus/evidence/task-10-tests-pass.txt

  Scenario: Tests don't require Pulumi runtime
    Tool: Bash
    Preconditions: test file created
    Steps:
      1. Run: grep -c 'import pulumi' pulumi/tests/test_config_compliance.py
      2. Assert: count is 0 (no Pulumi imports in unit tests)
    Expected Result: No Pulumi SDK imported
    Failure Indicators: Pulumi import found (would fail without engine)
    Evidence: .sisyphus/evidence/task-10-no-pulumi-import.txt

  Scenario: Test file passes ruff
    Tool: Bash
    Preconditions: test file created
    Steps:
      1. Run: cd pulumi && .venv/bin/ruff check tests/test_config_compliance.py
      2. Assert: 0 errors
    Expected Result: Clean lint
    Failure Indicators: Any ruff error
    Evidence: .sisyphus/evidence/task-10-ruff.txt
  ```

  **Commit**: YES (standalone)
  - Message: `test: add compliance tests for gateway mode, TLS, workflow URLs`
  - Files: `pulumi/tests/test_config_compliance.py`
  - Pre-commit: `cd pulumi && .venv/bin/python -m pytest tests/test_config_compliance.py -v`

- [x] 11. Run pulumi preview for both stacks (validation)

  **What to do**:
  - Run `pulumi preview` for **Phase 1** (talos-cluster-baremetal):
    ```bash
    cd pulumi/talos-cluster-baremetal && \
    PATH="/opt/homebrew/bin:$PATH" \
    PULUMI_CONFIG_PASSPHRASE="openchoreo-talos-baremetal-dev" \
    pulumi preview --stack dev 2>&1 | tee /tmp/phase1-preview.txt
    ```
  - Run `pulumi preview` for **Phase 2** (openchoreo):
    ```bash
    cd pulumi && \
    PATH="/opt/homebrew/bin:$PATH" \
    pulumi preview --stack talos-baremetal 2>&1 | tee /tmp/phase2-preview.txt
    ```
  - **Analyze output**: Look for errors, warnings, and unexpected resource changes
  - **If errors occur**: Document them and fix. Common issues:
    - Missing provider configuration → check kubeconfig path
    - Import errors → check Python imports in new files
    - Resource conflicts → check for duplicate resource names
  - **Expected Phase 1 changes**: Cilium gatewayAPI disabled, CRD retainOnDelete added, depends_on removed
  - **Expected Phase 2 changes**: New TLS resources (if tls_enabled), updated workflow URLs, listenerName in data plane
  - Save preview outputs as evidence

  **Must NOT do**:
  - Do NOT run `pulumi up` — only `pulumi preview` (dry run)
  - Do NOT change any code based on preview — just document findings
  - Do NOT expose secrets in evidence files

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Running two commands and analyzing output
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO — depends on all prior tasks (T1-T10)
  - **Parallel Group**: Wave 3 (sequential after T10)
  - **Blocks**: F1-F4
  - **Blocked By**: T1-T10

  **References**:

  **Pattern References**:
  - `pulumi/talos-cluster-baremetal/Pulumi.dev.yaml` — Phase 1 stack config (stack name: `dev`)
  - `pulumi/Pulumi.talos-baremetal.yaml` — Phase 2 stack config (stack name: `talos-baremetal`)

  **Environment References**:
  - Pulumi binary: `/opt/homebrew/bin/pulumi` (must set PATH)
  - uv binary: `/opt/homebrew/bin/uv` (must be in PATH for Pulumi Python)
  - Phase 1 PULUMI_CONFIG_PASSPHRASE: `"openchoreo-talos-baremetal-dev"`
  - Phase 2 PULUMI_CONFIG_PASSPHRASE: check `pulumi/Pulumi.talos-baremetal.yaml` encryptionsalt or env

  **WHY Each Reference Matters**:
  - Stack configs determine which stack to preview and what config values are used
  - PATH must include homebrew for pulumi and uv binaries
  - Passphrase is required to decrypt stack config

  **Acceptance Criteria**:
  - [ ] `pulumi preview --stack dev` (Phase 1) completes with 0 errors
  - [ ] `pulumi preview --stack talos-baremetal` (Phase 2) completes with 0 errors
  - [ ] Phase 1 preview shows: Cilium gatewayAPI changes, CRD retainOnDelete
  - [ ] Phase 2 preview shows: TLS resources (if tls_enabled), updated workflow URLs
  - [ ] No unexpected resource deletions in either preview
  - [ ] Preview outputs saved as evidence

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Phase 1 pulumi preview succeeds
    Tool: Bash
    Preconditions: All Phase 1 code changes complete (T2, T3)
    Steps:
      1. Run: cd pulumi/talos-cluster-baremetal && PATH="/opt/homebrew/bin:$PATH" PULUMI_CONFIG_PASSPHRASE="openchoreo-talos-baremetal-dev" pulumi preview --stack dev 2>&1
      2. Assert: exit code 0
      3. Assert: no "error" lines in output (case-insensitive, excluding expected warnings)
    Expected Result: Clean preview with expected changes only
    Failure Indicators: Non-zero exit code, error messages
    Evidence: .sisyphus/evidence/task-11-phase1-preview.txt

  Scenario: Phase 2 pulumi preview succeeds
    Tool: Bash
    Preconditions: All Phase 2 code changes complete (T1, T4-T9)
    Steps:
      1. Run: cd pulumi && PATH="/opt/homebrew/bin:$PATH" pulumi preview --stack talos-baremetal 2>&1
      2. Assert: exit code 0
      3. Assert: no "error" lines in output
    Expected Result: Clean preview with TLS + workflow + listenerName changes
    Failure Indicators: Non-zero exit code, error messages
    Evidence: .sisyphus/evidence/task-11-phase2-preview.txt

  Scenario: No unexpected resource deletions
    Tool: Bash (grep)
    Preconditions: Preview output captured
    Steps:
      1. Run: grep -i 'delete\|destroy' /tmp/phase1-preview.txt
      2. Analyze: any deletions should be expected (CRD state changes)
      3. Run: grep -i 'delete\|destroy' /tmp/phase2-preview.txt
      4. Analyze: no unexpected deletions
    Expected Result: No surprising resource deletions
    Failure Indicators: Resources being deleted that shouldn't be
    Evidence: .sisyphus/evidence/task-11-no-unexpected-deletes.txt
  ```

  **Commit**: NO (validation only — no code changes)

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
>
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, check resource). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in `.sisyphus/evidence/`. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `ruff check .` + `ruff format --check .` + `python -m pytest tests/ -v` for BOTH stacks. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names.
  Output: `Phase 1 Tests [PASS/FAIL] | Phase 2 Tests [PASS/FAIL] | Lint [PASS/FAIL] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Run `pulumi preview` for both stacks. Verify no k3d references in talos-baremetal workflow URLs. Verify Cilium gatewayAPI disabled. Verify TLS resources gated behind tls_enabled.
  Output: `Scenarios [N/N pass] | Preview Phase1 [PASS/FAIL] | Preview Phase2 [PASS/FAIL] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built, nothing beyond spec. Check "Must NOT do" compliance. Detect cross-task contamination. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

| # | Scope | Message | Files | Pre-commit |
|---|-------|---------|-------|------------|
| 1 | Gateway mode + Phase 1 Cilium fixes | `fix(platform): switch talos-baremetal to kgateway and disable Cilium Gateway API` | `talos_baremetal.py`, `talos-cluster-baremetal/__main__.py` | Phase 1 pytest ✅, ruff ✅ |
| 2 | Phase 2 exports | `fix(openchoreo): update exports for kgateway edition` | `pulumi/__main__.py` | Phase 2 ruff ✅ |
| 3 | Workflow templates | `fix(workflow): use standard template URLs for bare-metal` | `platforms/types.py`, `config.py`, `workflow_plane.py` | Phase 2 pytest ✅, ruff ✅ |
| 4 | TLS setup | `feat(tls): add explicit CA chain and per-plane certificates` | `tls_setup.py`, `config.py`, `Pulumi.talos-baremetal.yaml`, `__main__.py` | Phase 2 pytest ✅, ruff ✅ |
| 5 | Data plane listenerName | `fix(dataplane): add listenerName to ClusterDataPlane registration` | `data_plane.py` | Phase 2 ruff ✅ |
| 6 | Unit tests | `test: add coverage for gateway mode, TLS, workflow URLs` | `tests/` | Phase 2 pytest ✅ |

---

## Success Criteria

### Verification Commands
```bash
# Phase 1 tests
cd pulumi/talos-cluster-baremetal && .venv/bin/python -m pytest tests/ -v
# Expected: all tests pass (20+ tests)

# Phase 1 lint
cd pulumi/talos-cluster-baremetal && .venv/bin/ruff check .
# Expected: 0 errors

# Phase 2 tests
cd pulumi && .venv/bin/python -m pytest tests/ -v
# Expected: all tests pass

# Phase 2 lint
cd pulumi && .venv/bin/ruff check .
# Expected: 0 errors

# Phase 1 pulumi preview
cd pulumi/talos-cluster-baremetal && PATH="/opt/homebrew/bin:$PATH" PULUMI_CONFIG_PASSPHRASE="openchoreo-talos-baremetal-dev" pulumi preview --stack dev
# Expected: 0 errors

# Phase 2 pulumi preview
cd pulumi && PATH="/opt/homebrew/bin:$PATH" pulumi preview --stack talos-baremetal
# Expected: 0 errors
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass (both stacks)
- [ ] Pulumi preview clean (both stacks)
- [ ] No k3d references in talos-baremetal workflow URLs
- [ ] Cilium gatewayAPI disabled in Phase 1
- [ ] TLS gated behind tls_enabled flag
