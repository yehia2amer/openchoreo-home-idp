# Pulumi IaC Remediation — Security, Reliability, Consistency & Cleanup

## TL;DR

> **Quick Summary**: Fix 15 verified issues across the Pulumi Python IaC codebase — hardcoded secrets, fragile dynamic providers, inconsistent patterns, and dead code — then scaffold an E2E pytest suite wrapping the existing `k8s_ops.check_*` functions.
> 
> **Deliverables**:
> - P0: Non-dev stacks fail-fast without configured secrets; dev seed data gated behind `is_dev_stack`
> - P1: All Helm resources have timeouts, dynamic providers return correct types, exception handling narrowed, port-forward cleanup safe, monotonic timers
> - P2: `values/data_plane.py` wired into component, return type hints on all values/helpers
> - P3: Unused imports removed, TYPE_CHECKING guards added
> - E2E: pytest infrastructure + E2E tests wrapping existing check functions
> 
> **Estimated Effort**: Medium (11 atomic commits)
> **Parallel Execution**: YES — 4 waves
> **Critical Path**: Task 1 → Task 2 → Task 3-7 (parallel) → Task 8-10 (parallel) → Task 11

---

## Context

### Original Request
Research Pulumi best practices from official docs, audit the entire `pulumi/` directory for issues, and create a remediation plan grounded in those best practices. E2E tests only — no unit testing.

### Interview Summary
**Key Discussions**:
- User wants all fixes grounded in official Pulumi documentation best practices
- E2E tests only — explicitly excluded unit tests
- All 20+ files in `pulumi/` were read and audited

**Research Findings**:
- Official Pulumi docs recommend: `pulumi.Output.secret()` for sensitive values, `ComponentResource` for reusable modules, `CustomTimeouts` on all long-running resources, proper `UpdateResult` returns from dynamic providers
- Existing codebase has strong foundation (typed config, ComponentResource usage, proper dependency chains) but accumulated tech debt in security defaults and dynamic provider implementations
- An integration test harness already exists in `components/integration_tests.py` with ~35 tests running as Pulumi dynamic resources, plus reusable check functions in `helpers/k8s_ops.py`

### Metis Review
**Identified Gaps** (addressed):
- `update()` methods returning `dict` instead of `UpdateResult` — added as P1-4
- Helm `wait_for_jobs` needs per-chart audit (not blind addition) — noted in Task 3
- P0-4 (secret serialization in dynamic provider inputs) too risky for this remediation — documented as known limitation
- Embedded bash script in `values/openbao.py` (46-line f-string) should NOT be extracted (scope creep) — only gating fix applied
- Verification triad: `ruff check` + `ty check` + `pulumi preview` on both stacks per commit

### Auto-Resolved Questions
- **Verification**: `pulumi preview -s dev` and `pulumi preview -s rancher-desktop` (local dev project)
- **root_token="root"**: Dev-only by design — `is_dev_stack` already gates warnings. Fix: escalate to `raise` on non-dev
- **values/data_plane.py**: Dead code — wire it into component (consistency fix, not deletion)
- **Pulumi versions**: `pulumi>=3.0.0,<4.0.0`, `pulumi-kubernetes>=4.0.0,<5.0.0`, Python `>=3.12`

---

## Work Objectives

### Core Objective
Harden the Pulumi IaC codebase against security misconfigurations, runtime failures, and inconsistent patterns — then add E2E test coverage to verify deployed infrastructure.

### Concrete Deliverables
- `config.py` — Non-dev stacks raise on missing secrets instead of warn-and-proceed
- `values/openbao.py` — Dev seed secrets gated behind `is_dev_stack`
- All Helm v4.Chart resources — `CustomTimeouts` added
- `dynamic_providers.py` — Correct `UpdateResult` returns, narrowed exceptions, safe port-forward cleanup
- `k8s_ops.py` — `time.monotonic()`, narrowed exceptions
- `values/data_plane.py` → wired into `components/data_plane.py`
- All `values/*.py` — Return type hints added
- `__main__.py`, 3 component files — Unused imports cleaned, TYPE_CHECKING guards
- `pyproject.toml` + `tests/` directory — pytest E2E infrastructure

### Definition of Done
- [ ] `uv run ruff check pulumi/` exits 0
- [ ] `uv run ty check` exits 0 (or only pre-existing warnings)
- [ ] `cd pulumi && pulumi preview -s dev` exits 0 with no unexpected changes
- [ ] `cd pulumi && pulumi preview -s rancher-desktop` exits 0 with no unexpected changes
- [ ] `cd pulumi && uv run pytest tests/ -m e2e --timeout=120` exits 0 (after stack is deployed)

### Must Have
- All 4 P0-Security fixes applied
- All 6 P1-Reliability fixes applied
- `pulumi preview` passes on both stacks after every commit
- E2E pytest infrastructure scaffolded with at least 5 tests wrapping existing `k8s_ops.check_*` functions

### Must NOT Have (Guardrails)
- **NO resource logical name changes** — would cause URN breakage (destroy + recreate)
- **NO Helm release name changes** — same risk as above
- **NO deployment dependency graph changes** — component ordering must remain identical
- **NO new features, resources, or configuration keys** — remediation only
- **NO unit tests** — user explicitly excluded these
- **NO CrossGuard / Policy-as-Code** — out of scope
- **NO Resource Transformations** — out of scope
- **NO converting plain functions to ComponentResource for aesthetics** — only fix real issues
- **NO extracting the openbao bash script to a template file** — scope creep
- **NO attempting to fix secret serialization in dynamic provider state (P0-4)** — documented as known limitation, too risky for this remediation

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (no pytest setup currently)
- **Automated tests**: YES (E2E tests-after — Task 11 adds pytest infrastructure)
- **Framework**: pytest + pytest-timeout (via uv)
- **Strategy**: Each commit verified by the **verification triad**, E2E tests added as final commit

### Verification Triad (per commit)
```bash
uv run ruff check pulumi/                    # Static lint
uv run ty check                               # Type checking
cd pulumi && pulumi preview -s dev            # IaC correctness (dev stack)
cd pulumi && pulumi preview -s rancher-desktop  # IaC correctness (rancher stack)
```

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **IaC changes**: Use Bash (`pulumi preview`, `ruff check`, `ty check`) — verify exit codes and diff output
- **Python changes**: Use Bash (`python -c "..."` or `uv run python -c "..."`) — import verification
- **E2E tests**: Use Bash (`uv run pytest`) — run the test suite

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — P0 Security):
├── Task 1: Fail-fast on non-dev stacks without configured secrets [quick]
└── Task 2: Gate dev seed secrets behind is_dev_stack (depends: 1) [quick]

Wave 2 (After Wave 1 — P1 Reliability, MAX PARALLEL):
├── Task 3: Add CustomTimeouts to all Helm v4.Chart resources [quick]
├── Task 4: Fix update() return types to UpdateResult [quick]
├── Task 5: Narrow exception handling in dynamic providers & k8s_ops [unspecified-high]
├── Task 6: Use time.monotonic() consistently [quick]
└── Task 7: Add safe port-forward process cleanup [unspecified-high]

Wave 3 (After Wave 2 — P2 Consistency + P3 Cleanup, PARALLEL):
├── Task 8: Wire values/data_plane.py into component [quick]
├── Task 9: Add return type hints to values and helpers [quick]
└── Task 10: Remove unused imports + add TYPE_CHECKING guards [quick]

Wave 4 (After ALL — E2E Tests):
└── Task 11: Scaffold pytest E2E infrastructure and initial tests [deep]

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
| 1 | — | 2 | 1 |
| 2 | 1 | 3-10 | 1 |
| 3 | 2 | 11 | 2 |
| 4 | 2 | 5, 7 | 2 |
| 5 | 4 | 7, 11 | 2 |
| 6 | 2 | 11 | 2 |
| 7 | 5 | 11 | 2 |
| 8 | 2 | 11 | 3 |
| 9 | 2 | 11 | 3 |
| 10 | 2 | 11 | 3 |
| 11 | 3-10 | F1-F4 | 4 |

### Agent Dispatch Summary

- **Wave 1**: **2** — T1 → `quick`, T2 → `quick`
- **Wave 2**: **5** — T3 → `quick`, T4 → `quick`, T5 → `unspecified-high`, T6 → `quick`, T7 → `unspecified-high`
- **Wave 3**: **3** — T8 → `quick`, T9 → `quick`, T10 → `quick`
- **Wave 4**: **1** — T11 → `deep`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## Known Limitations (Out of Scope)

These are documented but intentionally NOT fixed in this remediation:

1. **P0-4: Secret serialization in dynamic provider state** — `root_token` is passed as plain string through dynamic provider inputs and stored in Pulumi state unencrypted. Fixing requires structural changes to the dynamic provider pattern (wrapping in `pulumi.Output.secret()` at call sites AND handling secret inputs in providers). Risk of breaking state compatibility too high.

2. **Embedded bash script in values/openbao.py** — The 46-line bash f-string in the openbao postStart script should eventually be extracted to a template file, but doing so in this remediation risks scope creep and complex merge conflicts.

3. **Shell-outs in workflow_plane.py, control_plane.py, observability_plane.py** — `curl | sed | kubectl apply`, complex kubectl patch bash, docker exec commands. These work and are common in IaC for complex orchestration. Replacing with pure Python would be a separate project.

4. **Network call during plan phase (control_plane.py:31)** — `_fetch_yaml()` makes an HTTP request at module import time. Fixing requires lazy loading or caching. Not in scope for this remediation.

5. **Mixed Helm v3.Release vs v4.Chart** — The codebase uses both. Migration from v3→v4 requires careful Helm chart compatibility testing. Not in scope.

6. **Inconsistent protect=True** — Some resources have `protect=True`, others don't. Requires business decision on which resources are critical. Not in scope.

---

## TODOs

- [x] 1. Fail-fast on non-dev stacks without configured secrets

  **What to do**:
  - In `config.py`, change the warn-and-fallback pattern for `openbao_root_token` (lines 215-222) and `opensearch_password` (lines 226-233) to **raise a `pulumi.ConfigMissingError` on non-dev stacks** instead of just logging a warning and proceeding with insecure defaults
  - Keep the current `is_dev_stack` check at line 210: `is_dev_stack = stack_name in ("dev", "rancher-desktop", "local", "test")`
  - Dev stacks continue to use defaults (`"root"` and `"ThisIsTheOpenSearchPassword1"`) — this is intentional for local development
  - Non-dev stacks MUST fail with a clear error message telling the user how to set the secret: `pulumi config set --secret openbao_root_token <value>`

  **Must NOT do**:
  - Do NOT change the `is_dev_stack` list of stack names
  - Do NOT change the default values for dev stacks
  - Do NOT add new config keys or change existing key names
  - Do NOT touch `github_pat` or other config values

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single file, ~10 lines changed, straightforward conditional logic change
  - **Skills**: [`find-docs`]
    - `find-docs`: Look up `pulumi.ConfigMissingError` or equivalent error class in Pulumi Python SDK to use the correct exception type

  **Parallelization**:
  - **Can Run In Parallel**: NO (must be first — foundation for Task 2)
  - **Parallel Group**: Wave 1 (sequential with Task 2)
  - **Blocks**: Task 2, Tasks 3-10
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `pulumi/config.py:210-233` — Current warn-and-fallback pattern. Lines 210 defines `is_dev_stack`, lines 215-222 handle `openbao_root_token`, lines 226-233 handle `opensearch_password`
  - `pulumi/config.py:1-20` — Import section, check if `pulumi.ConfigMissingError` is available or if a plain `ValueError` / `RuntimeError` is more appropriate

  **API/Type References**:
  - `pulumi/config.py:29-46` — The `InfraConfig` dataclass that consumes these values. The function `load_config()` starts at line 105

  **External References**:
  - Pulumi Python SDK: Check `pulumi.Config` class for built-in secret/required config helpers. The `cfg.require_secret("key")` method may be more idiomatic than manual raise

  **WHY Each Reference Matters**:
  - `config.py:210-233`: This is the EXACT code to modify — executor needs to see the current if/else pattern to understand the minimal change required
  - `config.py:29-46`: InfraConfig shows how these values flow downstream — confirms no other code needs changing
  - Pulumi SDK docs: `cfg.require_secret()` may be more idiomatic than `raise RuntimeError`, and would automatically mark the value as secret in state

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Dev stack still works with defaults (happy path)
    Tool: Bash
    Preconditions: Current working directory is pulumi/, dev stack exists
    Steps:
      1. Run: cd pulumi && pulumi preview -s dev 2>&1
      2. Verify exit code is 0
      3. Verify output does NOT contain "ConfigMissingError" or "RuntimeError"
    Expected Result: Preview succeeds, no errors about missing secrets
    Failure Indicators: Non-zero exit code, error mentioning missing config
    Evidence: .sisyphus/evidence/task-1-dev-stack-preview.txt

  Scenario: Rancher-desktop stack still works with defaults (happy path)
    Tool: Bash
    Preconditions: Current working directory is pulumi/, rancher-desktop stack exists
    Steps:
      1. Run: cd pulumi && pulumi preview -s rancher-desktop 2>&1
      2. Verify exit code is 0
    Expected Result: Preview succeeds
    Evidence: .sisyphus/evidence/task-1-rancher-preview.txt

  Scenario: Non-dev stack fails without secrets (error path)
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: cd pulumi && python -c "
         import pulumi
         # Simulate non-dev stack by patching stack name
         from config import load_config
         # Verify the code path raises for non-dev stacks
         " 2>&1
      2. Alternatively, use ast_grep_search to verify: the `else` branch (non-dev) now raises instead of just warning
      3. Run: ast_grep_search pattern='raise $ERR' in config.py — should find 2 matches (one per secret)
    Expected Result: Two raise statements found in the non-dev code paths
    Failure Indicators: Zero raise statements found, or warn-only pattern still present
    Evidence: .sisyphus/evidence/task-1-raise-verification.txt

  Scenario: Ruff and ty pass (static analysis)
    Tool: Bash
    Preconditions: uv installed, .venv exists
    Steps:
      1. Run: cd pulumi && uv run ruff check config.py 2>&1
      2. Run: cd pulumi && uv run ty check 2>&1
    Expected Result: Both exit 0 (or only pre-existing warnings)
    Evidence: .sisyphus/evidence/task-1-static-analysis.txt
  ```

  **Commit**: YES (commit 1 of 11)
  - Message: `fix(security): fail on non-dev stacks without configured secrets`
  - Files: `pulumi/config.py`
  - Pre-commit: verification triad

- [x] 2. Gate dev seed secrets behind is_dev_stack check

  **What to do**:
  - In `values/openbao.py`, the `get_values()` function builds Helm values that include a `postStart` shell script (lines 24-69) containing hardcoded dev secrets like vault policies and secret engine seeds
  - Add the `is_dev_stack` parameter to `get_values()` (passed from config) and conditionally include the seed secrets ONLY when `is_dev_stack=True`
  - When NOT dev stack: the postStart script should still initialize OpenBao (unseal, enable engines) but NOT seed any default secrets/policies with hardcoded values
  - The calling code in `components/control_plane.py` already has access to config (which includes `is_dev_stack` or the stack name) — pass it through

  **Must NOT do**:
  - Do NOT extract the bash script to a separate file (scope creep)
  - Do NOT change the resource logical name or Helm release name for OpenBao
  - Do NOT modify any other values files
  - Do NOT change the OpenBao Helm chart version

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Two files, moderate change — add parameter and conditional in values, pass it from component
  - **Skills**: [`find-docs`]
    - `find-docs`: Reference Pulumi Helm chart values best practices if needed

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 1 for `is_dev_stack` pattern)
  - **Parallel Group**: Wave 1 (after Task 1)
  - **Blocks**: Tasks 3-10
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `pulumi/values/openbao.py:1-70` — The ENTIRE file. `get_values()` returns a dict with the Helm values. The postStart script at lines 24-69 contains the seed secrets
  - `pulumi/values/control_plane.py:1-64` — Example of how other values files accept and use config parameters. Follow this pattern for adding `is_dev_stack` parameter
  - `pulumi/components/control_plane.py:88-120` — Where `get_values()` from `values/openbao.py` is called. This is where `is_dev_stack` needs to be passed through

  **API/Type References**:
  - `pulumi/config.py:29-46` — `InfraConfig` dataclass. Check if `is_dev_stack` is already a field, or if it needs to be derived from `stack_name`
  - `pulumi/config.py:210` — Where `is_dev_stack` is defined: `is_dev_stack = stack_name in ("dev", "rancher-desktop", "local", "test")`

  **WHY Each Reference Matters**:
  - `values/openbao.py` — This is the file being modified. The executor MUST understand the full postStart script structure to know where to add the conditional
  - `components/control_plane.py:88-120` — The call site that needs updating to pass `is_dev_stack`
  - `config.py:210` — Source of truth for `is_dev_stack` — executor needs to verify this is accessible at the call site

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Dev stack preview passes with seed secrets (happy path)
    Tool: Bash
    Preconditions: Task 1 complete, dev stack available
    Steps:
      1. Run: cd pulumi && pulumi preview -s dev 2>&1
      2. Verify exit code is 0
    Expected Result: Preview succeeds, openbao values still include seed data for dev
    Evidence: .sisyphus/evidence/task-2-dev-preview.txt

  Scenario: Seed secrets are gated behind is_dev_stack (code verification)
    Tool: Bash
    Preconditions: Task implementation complete
    Steps:
      1. Run: grep -n "is_dev_stack" pulumi/values/openbao.py
      2. Verify at least 1 occurrence of `is_dev_stack` in the file
      3. Run: grep -n "is_dev_stack" pulumi/components/control_plane.py
      4. Verify `is_dev_stack` is passed to the openbao get_values call
    Expected Result: `is_dev_stack` parameter exists in values/openbao.py and is passed from control_plane.py
    Failure Indicators: No occurrences of `is_dev_stack` in either file
    Evidence: .sisyphus/evidence/task-2-gate-verification.txt

  Scenario: Static analysis passes
    Tool: Bash
    Steps:
      1. Run: cd pulumi && uv run ruff check values/openbao.py components/control_plane.py 2>&1
      2. Run: cd pulumi && uv run ty check 2>&1
    Expected Result: Both exit 0
    Evidence: .sisyphus/evidence/task-2-static-analysis.txt
  ```

  **Commit**: YES (commit 2 of 11)
  - Message: `fix(security): gate dev seed secrets behind is_dev_stack check`
  - Files: `pulumi/values/openbao.py`, `pulumi/components/control_plane.py`
  - Pre-commit: verification triad

- [x] 3. Add CustomTimeouts to all Helm v4.Chart resources

  **What to do**:
  - Find ALL `k8s.helm.v4.Chart(...)` calls in the codebase using `ast_grep_search`
  - Add `custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")` to each Chart resource that doesn't already have it
  - The Helm v4 Chart resources are in: `components/prerequisites.py`, `components/workflow_plane.py`, `components/flux_gitops.py`
  - Import `pulumi.CustomTimeouts` if not already imported
  - Do NOT add timeouts to Helm v3.Release resources (different API, different task scope)

  **Must NOT do**:
  - Do NOT change any Chart resource names or chart versions
  - Do NOT add `wait_for_jobs` to v4.Chart (that's a v3.Release parameter)
  - Do NOT modify chart values or any other Chart parameters

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Adding one parameter to 3-6 resource calls, mechanical change
  - **Skills**: [`find-docs`]
    - `find-docs`: Look up `pulumi_kubernetes.helm.v4.Chart` to verify `custom_timeouts` parameter name and type

  **Parallelization**:
  - **Can Run In Parallel**: YES (independent of Tasks 4-7)
  - **Parallel Group**: Wave 2 (with Tasks 4, 5, 6, 7)
  - **Blocks**: Task 11
  - **Blocked By**: Task 2

  **References**:

  **Pattern References**:
  - `pulumi/components/prerequisites.py` — Contains Helm v4.Chart calls for cert-manager, metrics-server, etc. Search for `k8s.helm.v4.Chart(`
  - `pulumi/components/workflow_plane.py` — Contains Helm v4.Chart for Argo Workflows
  - `pulumi/components/flux_gitops.py` — Contains Helm v4.Chart for Flux

  **External References**:
  - Pulumi Kubernetes v4 Helm Chart docs: `pulumi_kubernetes.helm.v4.Chart` — verify parameter name is `custom_timeouts` and accepts `pulumi.CustomTimeouts`

  **WHY Each Reference Matters**:
  - The 3 component files are the EXACT files to modify — executor needs to find every Chart call in each
  - Pulumi docs confirm the correct parameter name/type to avoid typos

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All Helm v4.Chart resources have CustomTimeouts (verification)
    Tool: Bash
    Preconditions: Implementation complete
    Steps:
      1. Run: ast_grep_search pattern='k8s.helm.v4.Chart($$$)' lang=python
      2. For each match, verify `custom_timeouts` appears in the arguments
      3. Run: grep -rn "custom_timeouts" pulumi/components/ | wc -l
      4. Compare count against number of Chart calls found in step 1
    Expected Result: Every v4.Chart call includes custom_timeouts parameter
    Failure Indicators: Any Chart call without custom_timeouts
    Evidence: .sisyphus/evidence/task-3-timeout-verification.txt

  Scenario: Preview passes on both stacks
    Tool: Bash
    Steps:
      1. Run: cd pulumi && pulumi preview -s dev 2>&1
      2. Run: cd pulumi && pulumi preview -s rancher-desktop 2>&1
    Expected Result: Both exit 0
    Evidence: .sisyphus/evidence/task-3-preview.txt

  Scenario: Static analysis passes
    Tool: Bash
    Steps:
      1. Run: cd pulumi && uv run ruff check components/prerequisites.py components/workflow_plane.py components/flux_gitops.py 2>&1
    Expected Result: Exit 0
    Evidence: .sisyphus/evidence/task-3-ruff.txt
  ```

  **Commit**: YES (commit 3 of 11)
  - Message: `fix(reliability): add CustomTimeouts to all Helm v4.Chart resources`
  - Files: `pulumi/components/prerequisites.py`, `pulumi/components/workflow_plane.py`, `pulumi/components/flux_gitops.py`
  - Pre-commit: verification triad

- [x] 4. Fix update() return types to UpdateResult

  **What to do**:
  - In `helpers/dynamic_providers.py`, find ALL `update()` methods that return `dict[str, Any]` instead of `UpdateResult`
  - There are 4 methods confirmed by LSP diagnostics at lines 55, 247, 317, 502: `_CRDWaitProvider.update()`, `_HelmOCIProvider.update()`, `_KubeApplyProvider.update()`, `_OpenBaoSecretsProvider.update()`
  - Change each from `return result.outs` (dict) to `return UpdateResult(outs=result.outs)` 
  - Import `UpdateResult` from `pulumi.dynamic` if not already imported (check existing imports at top of file)
  - Also fix the parameter name mismatch: `inputs` → `props` to match the base `ResourceProvider` class signature (confirmed by LSP errors)

  **Must NOT do**:
  - Do NOT change the `create()`, `diff()`, or `delete()` methods in this task
  - Do NOT change any business logic inside the methods
  - Do NOT rename variables or change the internal implementation

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Mechanical return type fixes, 4 methods, same pattern each time
  - **Skills**: [`find-docs`]
    - `find-docs`: Look up `pulumi.dynamic.ResourceProvider` to confirm `UpdateResult` import path and `update()` expected signature

  **Parallelization**:
  - **Can Run In Parallel**: YES (independent of Tasks 3, 6)
  - **Parallel Group**: Wave 2 (with Tasks 3, 5, 6, 7)
  - **Blocks**: Task 5 (same file — avoid merge conflicts)
  - **Blocked By**: Task 2

  **References**:

  **Pattern References**:
  - `pulumi/helpers/dynamic_providers.py:55` — `_CRDWaitProvider.update()` returning dict
  - `pulumi/helpers/dynamic_providers.py:247` — `_HelmOCIProvider.update()` returning dict
  - `pulumi/helpers/dynamic_providers.py:317` — `_KubeApplyProvider.update()` returning dict
  - `pulumi/helpers/dynamic_providers.py:502` — `_OpenBaoSecretsProvider.update()` returning dict
  - `pulumi/helpers/dynamic_providers.py:1-20` — Import section, check for existing `UpdateResult` import

  **External References**:
  - Pulumi Python SDK: `pulumi.dynamic.ResourceProvider.update()` — Expected signature: `def update(self, id: str, olds: dict, news: dict) -> UpdateResult`
  - Pulumi Python SDK: `pulumi.dynamic.UpdateResult` — Constructor: `UpdateResult(outs=dict)`

  **WHY Each Reference Matters**:
  - Lines 55, 247, 317, 502 — These are the exact 4 lines to change
  - Import section — Need to verify `UpdateResult` is imported or add it
  - SDK docs — Confirm correct return type and constructor

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: No more UpdateResult LSP errors (verification)
    Tool: Bash
    Preconditions: Implementation complete
    Steps:
      1. Run: cd pulumi && uv run ty check 2>&1 | grep -i "UpdateResult" | wc -l
      2. Alternatively: ast_grep_search for 'def update($$$) -> dict' in dynamic_providers.py — should find 0 matches
      3. Run: grep -n "UpdateResult" pulumi/helpers/dynamic_providers.py | wc -l
      4. Verify at least 5 occurrences (1 import + 4 return statements)
    Expected Result: Zero ty errors about UpdateResult, 5+ occurrences of UpdateResult in file
    Failure Indicators: Any remaining "override returns type dict" ty errors
    Evidence: .sisyphus/evidence/task-4-updateresult-verification.txt

  Scenario: Preview passes on both stacks
    Tool: Bash
    Steps:
      1. Run: cd pulumi && pulumi preview -s dev 2>&1
      2. Run: cd pulumi && pulumi preview -s rancher-desktop 2>&1
    Expected Result: Both exit 0
    Evidence: .sisyphus/evidence/task-4-preview.txt
  ```

  **Commit**: YES (commit 4 of 11)
  - Message: `fix(reliability): fix update() return types to UpdateResult`
  - Files: `pulumi/helpers/dynamic_providers.py`
  - Pre-commit: verification triad

- [x] 5. Narrow exception handling in dynamic providers and k8s_ops

  **What to do**:
  - In `helpers/dynamic_providers.py`, find all bare `except:` or `except Exception:` blocks that swallow errors silently. Known locations: line ~265 (HelmOCI), and any others found via `ast_grep_search`
  - In `helpers/k8s_ops.py`, find similar patterns at lines ~616, ~658 where exceptions are caught broadly
  - For each: narrow to specific exception types (`kubernetes.client.ApiException`, `subprocess.CalledProcessError`, `hvac.exceptions.VaultError`, etc.) and add `pulumi.log.warn()` for the caught exception so it's visible in Pulumi output
  - Do NOT change the control flow — if the code currently swallows and continues, it should still continue after logging. If it re-raises, it should still re-raise.

  **Must NOT do**:
  - Do NOT change business logic or control flow
  - Do NOT add new error recovery mechanisms
  - Do NOT change function signatures
  - Do NOT modify the happy path code

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires careful analysis of each except block to determine correct specific exception type. Must not break error recovery.
  - **Skills**: [`find-docs`]
    - `find-docs`: Look up `kubernetes.client.ApiException`, `hvac.exceptions` to get correct exception class names

  **Parallelization**:
  - **Can Run In Parallel**: YES (but should run after Task 4 to avoid merge conflicts in dynamic_providers.py)
  - **Parallel Group**: Wave 2 (after Task 4 completes)
  - **Blocks**: Task 7
  - **Blocked By**: Task 4

  **References**:

  **Pattern References**:
  - `pulumi/helpers/dynamic_providers.py:260-270` — HelmOCI exception handling area
  - `pulumi/helpers/k8s_ops.py:610-625` — Port-forward related exception handling
  - `pulumi/helpers/k8s_ops.py:650-665` — Another broad exception block

  **API/Type References**:
  - `kubernetes.client.exceptions.ApiException` — The standard K8s client exception
  - `hvac.exceptions.VaultError` — Base vault error class (for OpenBao operations)
  - `subprocess.CalledProcessError` — For shell-out error handling
  - `pulumi.log.warn()` — For logging caught exceptions visibly

  **WHY Each Reference Matters**:
  - The exception handling locations are where changes happen — executor must read the full try/except block context
  - Specific exception classes ensure we narrow correctly without missing legitimate errors

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: No bare except blocks remain (verification)
    Tool: Bash
    Preconditions: Implementation complete
    Steps:
      1. Run: ast_grep_search pattern='except:' lang=python in dynamic_providers.py and k8s_ops.py
      2. Run: ast_grep_search pattern='except Exception:' lang=python in same files
      3. Verify matches are 0 for bare except, and any remaining Exception catches have pulumi.log.warn
    Expected Result: Zero bare `except:` blocks. Any `except Exception:` includes logging.
    Failure Indicators: Bare except blocks still present
    Evidence: .sisyphus/evidence/task-5-exception-verification.txt

  Scenario: Preview passes on both stacks
    Tool: Bash
    Steps:
      1. Run: cd pulumi && pulumi preview -s dev 2>&1
      2. Run: cd pulumi && pulumi preview -s rancher-desktop 2>&1
    Expected Result: Both exit 0
    Evidence: .sisyphus/evidence/task-5-preview.txt
  ```

  **Commit**: YES (commit 5 of 11)
  - Message: `fix(reliability): narrow exception handling in dynamic providers and k8s_ops`
  - Files: `pulumi/helpers/dynamic_providers.py`, `pulumi/helpers/k8s_ops.py`
  - Pre-commit: verification triad

- [x] 6. Use `time.monotonic()` consistently for timeout calculations

  **What to do**:
  - In `helpers/k8s_ops.py`, locate the two `time.time()` calls used for timeout tracking (~lines 646 and 648)
  - Replace both with `time.monotonic()` — monotonic clocks are immune to system clock adjustments (NTP jumps, DST) and are the correct choice for measuring elapsed durations
  - The rest of the file already uses `time.monotonic()` (e.g., the `wait_for_*` functions) — this is a consistency fix for 2 missed call sites
  - Verify: `import time` is already present; no new imports needed
  - Run verification triad

  **Must NOT do**:
  - Do NOT change any timeout values or logic — only swap the clock source
  - Do NOT refactor surrounding code
  - Do NOT touch any other functions in k8s_ops.py

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Two-line change, mechanical substitution, no design decisions
  - **Skills**: []
    - No specialized skills needed for a find-and-replace
  - **Skills Evaluated but Omitted**:
    - `senior-backend`: Overkill for a 2-line clock source swap

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 3, 4, 5, 7)
  - **Blocks**: Task 11 (E2E tests depend on all fixes)
  - **Blocked By**: Task 1 (config.py changes must land first for clean preview)

  **References** (CRITICAL — Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `pulumi/helpers/k8s_ops.py:~580-590` — Existing `time.monotonic()` usage in the same file's `wait_for_pod_ready()` function. Shows the correct pattern already in use.

  **API/Type References** (contracts to implement against):
  - Python stdlib `time.monotonic()` — Returns float of fractional seconds from an unspecified epoch; cannot go backwards. Exact same interface as `time.time()` for arithmetic.

  **External References** (libraries and frameworks):
  - Python docs: `https://docs.python.org/3/library/time.html#time.monotonic` — "The reference point of the returned value is undefined, so that only the difference between the results of two calls is valid."

  **WHY Each Reference Matters**:
  - The k8s_ops.py pattern reference proves monotonic is already the convention in this file — these 2 lines are the outliers
  - Python docs confirm monotonic() is a drop-in replacement for time() when only elapsed duration matters (which is the case for timeout checks)

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: No time.time() calls remain in timeout logic
    Tool: Bash (grep)
    Preconditions: Task 6 changes applied
    Steps:
      1. Run: grep -n "time\.time()" pulumi/helpers/k8s_ops.py
      2. Verify output is empty (no matches)
    Expected Result: Exit code 1 (grep finds nothing), zero output lines
    Failure Indicators: Any line containing time.time() in k8s_ops.py
    Evidence: .sisyphus/evidence/task-6-no-time-time.txt

  Scenario: time.monotonic() is used in the port-forward timeout block
    Tool: Bash (grep)
    Preconditions: Task 6 changes applied
    Steps:
      1. Run: grep -n "time\.monotonic()" pulumi/helpers/k8s_ops.py | wc -l
      2. Count should be >= previous count + 2 (the two replaced calls)
    Expected Result: All timeout calculations in the file use monotonic()
    Failure Indicators: Count is less than expected
    Evidence: .sisyphus/evidence/task-6-monotonic-count.txt

  Scenario: Verification triad passes
    Tool: Bash
    Preconditions: Task 6 changes applied
    Steps:
      1. Run: uv run ruff check pulumi/
      2. Run: uv run ty check
      3. Run: pulumi preview -s dev
      4. Run: pulumi preview -s rancher-desktop
    Expected Result: All four commands exit 0 with no new errors
    Failure Indicators: Any command exits non-zero or shows new diagnostics
    Evidence: .sisyphus/evidence/task-6-preview.txt
  ```

  **Commit**: YES (commit 6 of 11)
  - Message: `fix(reliability): use time.monotonic() for timeout calculations in k8s_ops`
  - Files: `pulumi/helpers/k8s_ops.py`
  - Pre-commit: verification triad

- [x] 7. Add safe port-forward process cleanup with try/finally

  **What to do**:
  - In `helpers/dynamic_providers.py` (~lines 469-494): The `subprocess.Popen` port-forward process is started but cleanup on exception is fragile. Wrap the port-forward usage block in a `try/finally` that:
    1. Calls `pf.terminate()` in the `finally` block
    2. Catches `ProcessLookupError` around `terminate()` (process may have already exited)
    3. Adds `pf.wait(timeout=5)` after terminate to reap the zombie process
    4. Catches `subprocess.TimeoutExpired` on the wait and calls `pf.kill()` as last resort
  - In `helpers/k8s_ops.py` (~lines 598-625): Same pattern — port-forward process cleanup. Apply identical try/finally pattern.
  - Both files already have port-forward cleanup code, but it's not exception-safe. The fix wraps existing cleanup in proper try/finally guards.
  - Run verification triad

  **Must NOT do**:
  - Do NOT change port-forward connection logic, timeouts, or retry behavior
  - Do NOT abstract port-forward into a context manager (scope creep — that's a future refactor)
  - Do NOT change the port numbers, kubectl arguments, or readiness checks
  - Do NOT modify any code outside the port-forward lifecycle blocks

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires understanding subprocess lifecycle, exception safety, and zombie process prevention — needs careful implementation across two files
  - **Skills**: [`senior-backend`]
    - `senior-backend`: Process management and exception-safe resource cleanup is core backend engineering
  - **Skills Evaluated but Omitted**:
    - `senior-devops`: This is Python subprocess management, not infrastructure automation

  **Parallelization**:
  - **Can Run In Parallel**: YES (but coordinate with Task 5 on same files)
  - **Parallel Group**: Wave 2 (with Tasks 3, 4, 5, 6) — Task 5 and 7 both touch `dynamic_providers.py` and `k8s_ops.py` but different code sections (Task 5: exception clauses; Task 7: port-forward blocks). Agent should verify no merge conflicts.
  - **Blocks**: Task 11 (E2E tests depend on all fixes)
  - **Blocked By**: Task 1 (config.py changes must land first for clean preview)

  **References** (CRITICAL — Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `pulumi/helpers/dynamic_providers.py:469-494` — Current port-forward block in `ArgocdRepoSyncProvider.create()`. Shows `pf = subprocess.Popen(...)` followed by usage, then `pf.terminate()` and `pf.wait()` — but NOT in a finally block, so exceptions skip cleanup.
  - `pulumi/helpers/k8s_ops.py:598-625` — Current port-forward block in `create_argocd_application()`. Same pattern: Popen, use, terminate/wait — not exception-safe.

  **API/Type References** (contracts to implement against):
  - `subprocess.Popen.terminate()` — Sends SIGTERM. Raises `ProcessLookupError` if PID doesn't exist.
  - `subprocess.Popen.wait(timeout=N)` — Waits for process exit. Raises `subprocess.TimeoutExpired` if timeout exceeded.
  - `subprocess.Popen.kill()` — Sends SIGKILL. Last resort after terminate+wait fails.

  **External References** (libraries and frameworks):
  - Python docs: `https://docs.python.org/3/library/subprocess.html#popen-objects` — Popen lifecycle: terminate → wait → kill pattern

  **WHY Each Reference Matters**:
  - The two source files show the CURRENT code that needs wrapping — executor must understand what's there before adding try/finally
  - subprocess API docs are critical because the executor needs to handle `ProcessLookupError` (already-exited process) and `TimeoutExpired` (hung process) — these are the two failure modes

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Port-forward in dynamic_providers.py has try/finally cleanup
    Tool: Bash (python -c)
    Preconditions: Task 7 changes applied
    Steps:
      1. Run: python -c "
      import ast, sys
      with open('pulumi/helpers/dynamic_providers.py') as f:
          tree = ast.parse(f.read())
      for node in ast.walk(tree):
          if isinstance(node, ast.Try) and node.finalbody:
              for stmt in ast.walk(node):
                  if isinstance(stmt, ast.Call) and hasattr(stmt.func, 'attr') and stmt.func.attr == 'terminate':
                      print('PASS: try/finally with terminate() found')
                      sys.exit(0)
      print('FAIL: no try/finally with terminate()')
      sys.exit(1)
      "
    Expected Result: "PASS: try/finally with terminate() found", exit code 0
    Failure Indicators: "FAIL" message or exit code 1
    Evidence: .sisyphus/evidence/task-7-dynamic-providers-finally.txt

  Scenario: Port-forward in k8s_ops.py has try/finally cleanup
    Tool: Bash (python -c)
    Preconditions: Task 7 changes applied
    Steps:
      1. Run: python -c "
      import ast, sys
      with open('pulumi/helpers/k8s_ops.py') as f:
          tree = ast.parse(f.read())
      for node in ast.walk(tree):
          if isinstance(node, ast.Try) and node.finalbody:
              for stmt in ast.walk(node):
                  if isinstance(stmt, ast.Call) and hasattr(stmt.func, 'attr') and stmt.func.attr == 'terminate':
                      print('PASS: try/finally with terminate() found')
                      sys.exit(0)
      print('FAIL: no try/finally with terminate()')
      sys.exit(1)
      "
    Expected Result: "PASS: try/finally with terminate() found", exit code 0
    Failure Indicators: "FAIL" message or exit code 1
    Evidence: .sisyphus/evidence/task-7-k8s-ops-finally.txt

  Scenario: ProcessLookupError is caught around terminate()
    Tool: Bash (grep)
    Preconditions: Task 7 changes applied
    Steps:
      1. Run: grep -c "ProcessLookupError" pulumi/helpers/dynamic_providers.py
      2. Run: grep -c "ProcessLookupError" pulumi/helpers/k8s_ops.py
    Expected Result: Both return >= 1 (ProcessLookupError is handled in both files)
    Failure Indicators: Either file returns 0
    Evidence: .sisyphus/evidence/task-7-process-lookup-error.txt

  Scenario: Verification triad passes
    Tool: Bash
    Preconditions: Task 7 changes applied
    Steps:
      1. Run: uv run ruff check pulumi/
      2. Run: uv run ty check
      3. Run: pulumi preview -s dev
      4. Run: pulumi preview -s rancher-desktop
    Expected Result: All four commands exit 0 with no new errors
    Failure Indicators: Any command exits non-zero or shows new diagnostics
    Evidence: .sisyphus/evidence/task-7-preview.txt
  ```

  **Commit**: YES (commit 7 of 11)
  - Message: `fix(reliability): add exception-safe port-forward process cleanup`
  - Files: `pulumi/helpers/dynamic_providers.py`, `pulumi/helpers/k8s_ops.py`
  - Pre-commit: verification triad

- [x] 8. Wire `values/data_plane.py` into `components/data_plane.py` *(already implemented in current code — plan was stale)*

  **What to do**:
  - Currently `values/data_plane.py` exists with a `get_values()` function that builds Helm values for the data plane, but `components/data_plane.py` (~line 81-87) inlines the values dict directly instead of importing from the values module. This is the ONLY component that doesn't follow the `values/*.py → components/*.py` pattern.
  - In `components/data_plane.py`:
    1. Add import: `from ..values.data_plane import get_values as get_data_plane_values` (follow the exact import pattern used in other components like `components/control_plane.py`)
    2. Replace the inlined values dict (~lines 81-87) with a call to `get_data_plane_values(config)` (or whatever parameters the function expects)
    3. Pass the returned dict to the Helm Chart resource
  - In `values/data_plane.py`: Verify the function signature matches what the component needs. If the function needs config parameters not currently passed, add them. Look at `values/control_plane.py` as the canonical reference for function signature.
  - Verify: The Helm values produced are IDENTICAL before and after (no behavior change — this is purely a structural refactor)
  - Run verification triad

  **Must NOT do**:
  - Do NOT change the actual Helm values content — only move WHERE they're defined
  - Do NOT rename the values function or change its return type
  - Do NOT refactor other components' values patterns
  - Do NOT delete the inlined dict without confirming values/data_plane.py produces equivalent output

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Structural refactor following an established pattern — import a module, call a function, replace an inlined dict
  - **Skills**: []
    - No specialized skills needed — pattern is clearly visible in adjacent files
  - **Skills Evaluated but Omitted**:
    - `senior-frontend`: Not frontend work
    - `senior-backend`: Pattern is trivial once you see the other components

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 9, 10)
  - **Blocks**: Task 11 (E2E tests depend on all fixes)
  - **Blocked By**: Tasks 1-7 (Wave 2 must complete — especially Task 4 which touches dynamic_providers.py used by data plane)

  **References** (CRITICAL — Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `pulumi/components/control_plane.py:~45-60` — Shows the canonical pattern: imports `get_values` from `values/control_plane.py`, calls it with config, passes result to Helm Chart. THIS IS THE EXACT PATTERN TO REPLICATE.
  - `pulumi/components/workflow_plane.py:~50-65` — Another example of the same values import pattern for cross-reference.
  - `pulumi/components/data_plane.py:81-87` — The CURRENT inlined values dict that must be replaced with the function call.

  **API/Type References** (contracts to implement against):
  - `pulumi/values/data_plane.py` — The existing `get_values()` function. Executor must read its full signature and return type to wire it correctly.
  - `pulumi/values/__init__.py` — Check if data_plane is already exported here; if not, may need to add it.

  **External References** (libraries and frameworks):
  - No external references needed — this is an internal codebase consistency fix.

  **WHY Each Reference Matters**:
  - `components/control_plane.py` is the GOLDEN REFERENCE — it shows exact import path, function call pattern, and how return value feeds into Helm Chart. Executor should mirror this exactly.
  - `components/data_plane.py:81-87` shows what's being replaced — executor must verify the values dict in `values/data_plane.py` produces equivalent output.
  - `values/__init__.py` may need updating if it has explicit exports — executor must check.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: components/data_plane.py imports from values module
    Tool: Bash (grep)
    Preconditions: Task 8 changes applied
    Steps:
      1. Run: grep -n "from.*values.*data_plane.*import" pulumi/components/data_plane.py
    Expected Result: At least one line showing import from values.data_plane (or ..values.data_plane)
    Failure Indicators: No import found; values are still inlined
    Evidence: .sisyphus/evidence/task-8-import-check.txt

  Scenario: No inlined values dict remains in component
    Tool: Bash (python -c)
    Preconditions: Task 8 changes applied
    Steps:
      1. Run: python -c "
      with open('pulumi/components/data_plane.py') as f:
          content = f.read()
      # The old inlined dict had specific keys - check they're gone as inline
      # Instead, a function call should be present
      if 'get_values' in content or 'get_data_plane_values' in content:
          print('PASS: values function call found')
      else:
          print('FAIL: no values function call found')
          exit(1)
      "
    Expected Result: "PASS: values function call found", exit code 0
    Failure Indicators: "FAIL" message
    Evidence: .sisyphus/evidence/task-8-function-call.txt

  Scenario: Verification triad passes (proves Helm values are equivalent)
    Tool: Bash
    Preconditions: Task 8 changes applied
    Steps:
      1. Run: uv run ruff check pulumi/
      2. Run: uv run ty check
      3. Run: pulumi preview -s dev
      4. Run: pulumi preview -s rancher-desktop
    Expected Result: All four commands exit 0. Critically, pulumi preview must show NO unexpected changes to data plane resources — confirming values are equivalent.
    Failure Indicators: Preview shows data plane resources being updated/replaced (values changed), or any command exits non-zero
    Evidence: .sisyphus/evidence/task-8-preview.txt
  ```

  **Commit**: YES (commit 8 of 11)
  - Message: `refactor(consistency): wire values/data_plane.py into data plane component`
  - Files: `pulumi/components/data_plane.py`, `pulumi/values/data_plane.py` (if signature changes needed)
  - Pre-commit: verification triad

- [x] 9. Add return type hints to all values and helper functions

  **What to do**:
  - Add `-> dict[str, Any]` return type annotations to ALL `get_values()` functions across `values/*.py` files:
    - `values/openbao.py` — `get_values()`
    - `values/control_plane.py` — `get_values()`
    - `values/workflow_plane.py` — `get_values()`
    - `values/observability_plane.py` — `get_values()`
    - `values/flux_gitops.py` — `get_values()`
    - `values/prerequisites.py` — `get_values()`
    - `values/data_plane.py` — `get_values()`
  - Add `from typing import Any` import to each file if not already present
  - For helper functions in `helpers/*.py`: Add return type hints where missing. Focus on public functions that return dicts. Do NOT annotate every private helper — only functions called from outside the module.
  - Run verification triad

  **Must NOT do**:
  - Do NOT change function bodies or logic — type hints ONLY
  - Do NOT add parameter type hints (that's a separate concern and risks scope creep)
  - Do NOT add type hints to internal/private functions (prefixed with `_`)
  - Do NOT introduce `TypedDict` or complex types — simple `dict[str, Any]` is sufficient

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Mechanical addition of return type annotations across multiple files — no design decisions, just `-> dict[str, Any]`
  - **Skills**: []
    - No specialized skills — pattern is identical across all files
  - **Skills Evaluated but Omitted**:
    - `senior-backend`: Type annotations are trivial here; no complex typing needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 8, 10)
  - **Blocks**: Task 11 (E2E tests depend on all fixes)
  - **Blocked By**: Tasks 1-7 (Wave 2 must complete — Task 2 modifies values/openbao.py, Task 8 may modify values/data_plane.py)

  **References** (CRITICAL — Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `pulumi/values/control_plane.py` — Read the function signature. If ANY values file already has a return type hint, use that as the canonical pattern. If none do, the standard is `def get_values(...) -> dict[str, Any]:`.
  - `pulumi/helpers/k8s_ops.py` — Check existing type hints on helper functions to match the style.

  **API/Type References** (contracts to implement against):
  - `typing.Any` — Standard library import for `dict[str, Any]`
  - Python 3.12+ — `dict[str, Any]` is valid without `from __future__ import annotations` (lowercase dict generics available since 3.9)

  **External References** (libraries and frameworks):
  - Python typing docs: `https://docs.python.org/3/library/typing.html` — confirms `dict[str, Any]` syntax
  - Pulumi best practices: Return types on all exported functions for IDE support and type checking

  **WHY Each Reference Matters**:
  - Existing values files show current function signatures — executor needs to see what's there to add the return type
  - Python 3.12 confirmation means no `from __future__` import needed — just `dict[str, Any]` directly
  - `typing.Any` import is required in each file — executor must check if it's already imported

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All get_values() functions have return type hints
    Tool: Bash (grep)
    Preconditions: Task 9 changes applied
    Steps:
      1. Run: for f in pulumi/values/*.py; do echo "=== $f ==="; grep -n "def get_values" "$f"; done
      2. Verify every get_values function definition includes "-> dict[str, Any]:" or similar return type
    Expected Result: Every get_values definition line includes a return type annotation
    Failure Indicators: Any get_values line without "->" in its signature
    Evidence: .sisyphus/evidence/task-9-return-types.txt

  Scenario: All values files import Any (or don't need to)
    Tool: Bash (grep)
    Preconditions: Task 9 changes applied
    Steps:
      1. Run: for f in pulumi/values/*.py; do echo "=== $f ==="; grep -n "from typing import\|import typing" "$f" || echo "NO TYPING IMPORT"; done
    Expected Result: Every values file with dict[str, Any] return type has a corresponding typing import
    Failure Indicators: A file uses Any in type hint but has no typing import
    Evidence: .sisyphus/evidence/task-9-typing-imports.txt

  Scenario: Verification triad passes
    Tool: Bash
    Preconditions: Task 9 changes applied
    Steps:
      1. Run: uv run ruff check pulumi/
      2. Run: uv run ty check
      3. Run: pulumi preview -s dev
      4. Run: pulumi preview -s rancher-desktop
    Expected Result: All four commands exit 0 — type checker may even show FEWER errors now
    Failure Indicators: Any command exits non-zero or shows new diagnostics
    Evidence: .sisyphus/evidence/task-9-preview.txt
  ```

  **Commit**: YES (commit 9 of 11)
  - Message: `refactor(consistency): add return type hints to values and helper functions`
  - Files: all `pulumi/values/*.py`, select `pulumi/helpers/*.py`
  - Pre-commit: verification triad

- [x] 10. Remove unused imports and add `TYPE_CHECKING` guards

  **What to do**:
  - In `__main__.py` (lines 3-4): Remove unused imports `Sequence` and `Path` — these are imported but never used in the file.
  - In `components/data_plane.py` (~line 10): The `RegisterPlane` import (from `platforms/`) is only used for type annotations. Wrap it in `if TYPE_CHECKING:` guard to prevent circular imports and reduce runtime import overhead:
    ```python
    from __future__ import annotations
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from ..platforms.register_plane import RegisterPlane
    ```
  - In `components/workflow_plane.py` (~line 15): Same pattern — `RegisterPlane` import used only for type hints. Apply identical `TYPE_CHECKING` guard.
  - In `components/observability_plane.py` (~line 19): Same pattern — apply `TYPE_CHECKING` guard.
  - Verify: `from __future__ import annotations` is added at the top of each file that gets a `TYPE_CHECKING` guard (required for string-based forward references at runtime)
  - Run verification triad

  **Must NOT do**:
  - Do NOT remove imports that ARE used at runtime — only move type-only imports behind TYPE_CHECKING
  - Do NOT add TYPE_CHECKING guards to imports used in isinstance checks, function calls, or any runtime code
  - Do NOT reorganize import order beyond the specific changes listed
  - Do NOT touch any imports in files not listed above

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Mechanical import cleanup with a well-defined pattern — remove 2 unused imports and wrap 3 type-only imports
  - **Skills**: []
    - No specialized skills needed
  - **Skills Evaluated but Omitted**:
    - `senior-backend`: Import cleanup is trivial when the specific lines are identified

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 8, 9)
  - **Blocks**: Task 11 (E2E tests depend on all fixes)
  - **Blocked By**: Tasks 1-7 (Wave 2 must complete)

  **References** (CRITICAL — Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `pulumi/__main__.py:3-4` — Lines to remove: `from collections.abc import Sequence` and `from pathlib import Path`. Verify neither symbol appears elsewhere in the file before deleting.
  - `pulumi/components/data_plane.py:~10` — Current `from ..platforms.register_plane import RegisterPlane`. Used only in type annotation for `__init__` parameter. Must move behind TYPE_CHECKING.
  - `pulumi/components/workflow_plane.py:~15` — Same RegisterPlane import pattern.
  - `pulumi/components/observability_plane.py:~19` — Same RegisterPlane import pattern.

  **API/Type References** (contracts to implement against):
  - `typing.TYPE_CHECKING` — Boolean that is `True` only during static type checking (mypy, pyright, ty), `False` at runtime. Imports behind this guard are never executed.
  - `from __future__ import annotations` — Makes ALL annotations string-based (PEP 563), required when using TYPE_CHECKING guards so the type name resolves during checking but doesn't fail at runtime.

  **External References** (libraries and frameworks):
  - Python docs: `https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING` — TYPE_CHECKING usage pattern
  - PEP 563: `https://peps.python.org/pep-0563/` — Postponed evaluation of annotations

  **WHY Each Reference Matters**:
  - The 4 source file references show EXACT lines to modify — executor needs to verify no runtime usage before applying TYPE_CHECKING guard
  - `from __future__ import annotations` is REQUIRED when adding TYPE_CHECKING — without it, the type hint string won't resolve and will cause `NameError` at runtime if the class is instantiated

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Unused imports removed from __main__.py
    Tool: Bash (grep)
    Preconditions: Task 10 changes applied
    Steps:
      1. Run: grep -n "Sequence\|from pathlib" pulumi/__main__.py
    Expected Result: No matches — both unused imports are gone
    Failure Indicators: Either Sequence or Path import still present
    Evidence: .sisyphus/evidence/task-10-unused-imports.txt

  Scenario: TYPE_CHECKING guards present in component files
    Tool: Bash (grep)
    Preconditions: Task 10 changes applied
    Steps:
      1. Run: grep -l "TYPE_CHECKING" pulumi/components/data_plane.py pulumi/components/workflow_plane.py pulumi/components/observability_plane.py
    Expected Result: All three files listed (all contain TYPE_CHECKING)
    Failure Indicators: Any file missing from output
    Evidence: .sisyphus/evidence/task-10-type-checking.txt

  Scenario: __future__ annotations imported in guarded files
    Tool: Bash (grep)
    Preconditions: Task 10 changes applied
    Steps:
      1. Run: grep -l "from __future__ import annotations" pulumi/components/data_plane.py pulumi/components/workflow_plane.py pulumi/components/observability_plane.py
    Expected Result: All three files listed
    Failure Indicators: Any file missing — would cause NameError at runtime
    Evidence: .sisyphus/evidence/task-10-future-annotations.txt

  Scenario: Verification triad passes
    Tool: Bash
    Preconditions: Task 10 changes applied
    Steps:
      1. Run: uv run ruff check pulumi/
      2. Run: uv run ty check
      3. Run: pulumi preview -s dev
      4. Run: pulumi preview -s rancher-desktop
    Expected Result: All four commands exit 0 — ruff may show FEWER warnings now (unused imports gone)
    Failure Indicators: Any command exits non-zero or shows new diagnostics
    Evidence: .sisyphus/evidence/task-10-preview.txt
  ```

  **Commit**: YES (commit 10 of 11)
  - Message: `chore(cleanup): remove unused imports and add TYPE_CHECKING guards`
  - Files: `pulumi/__main__.py`, `pulumi/components/data_plane.py`, `pulumi/components/workflow_plane.py`, `pulumi/components/observability_plane.py`
  - Pre-commit: verification triad

- [x] 11. Scaffold pytest E2E infrastructure and initial tests

  **What to do**:
  - **Add test dependencies** to `pyproject.toml`:
    - Add `[dependency-groups]` section (if not present) with `test = ["pytest>=8.0", "pytest-timeout>=2.0"]`
    - Or append to existing dependency-groups if the section exists
  - **Create test conftest** at `pulumi/tests/conftest.py`:
    - Import and configure pytest markers: `@pytest.mark.e2e`, `@pytest.mark.slow`
    - Add shared fixtures:
      - `kubeconfig` fixture that reads `KUBECONFIG` env var (or defaults to `~/.kube/config`)
      - `pulumi_stack` fixture that reads `PULUMI_STACK` env var (for stack-aware tests)
    - Add `pytest.ini_options` in pyproject.toml: `testpaths = ["pulumi/tests"]`, `markers = ["e2e: end-to-end tests", "slow: long-running tests"]`
  - **Create E2E test file** at `pulumi/tests/test_e2e_smoke.py`:
    - Wrap EXISTING `k8s_ops.check_*` functions in pytest test cases — do NOT rewrite the check logic
    - Example: `def test_cert_manager_ready(): assert k8s_ops.check_cert_manager_crds()` (adapt to actual function signatures)
    - Import the check functions from `helpers.k8s_ops` and `components.integration_tests`
    - Add `@pytest.mark.e2e` decorator to all tests
    - Add `@pytest.mark.timeout(120)` for tests that hit the cluster
    - Each test should be a thin wrapper: call the check function → assert truthy result
  - **Do NOT rewrite check logic** — the existing ~35 integration test functions in `components/integration_tests.py` and the check helpers in `helpers/k8s_ops.py` contain the actual assertions. Your job is to make them runnable via `pytest`.
  - Run: `uv run pytest pulumi/tests/ -v --co` (collect only — verifies tests are discovered without running them)

  **Must NOT do**:
  - Do NOT write unit tests — E2E only
  - Do NOT rewrite or modify the existing check functions in `k8s_ops.py` or `integration_tests.py`
  - Do NOT add mocking — E2E tests hit real cluster
  - Do NOT make tests depend on Pulumi stack being deployed in CI — tests are for local dev verification against an already-deployed stack
  - Do NOT install test frameworks other than pytest
  - Do NOT create a separate test directory outside `pulumi/` — keep tests co-located

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Requires understanding the full test function inventory across two modules, designing the pytest scaffold to wrap them without rewriting logic, and handling import paths correctly within the Pulumi project structure
  - **Skills**: [`tdd-guide`, `senior-qa`]
    - `tdd-guide`: pytest scaffold patterns, conftest design, marker configuration
    - `senior-qa`: Test infrastructure setup, fixture design, test discovery configuration
  - **Skills Evaluated but Omitted**:
    - `playwright-pro`: Not browser testing
    - `senior-backend`: QA-specific skills are more relevant here

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4 (sequential — after ALL other tasks)
  - **Blocks**: Final Verification Wave
  - **Blocked By**: Tasks 1-10 (ALL must complete — tests verify the fixed codebase)

  **References** (CRITICAL — Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `pulumi/components/integration_tests.py` — The ENTIRE file is a reference. Contains ~35 integration test functions implemented as Pulumi dynamic resource providers. Each test function follows the pattern: check something on the cluster → return pass/fail. EXECUTOR MUST READ THIS ENTIRE FILE to inventory all test functions.
  - `pulumi/helpers/k8s_ops.py:check_*` functions — Reusable check functions like `check_cert_manager_crds()`, `check_helm_release()`, etc. These are the functions to wrap in pytest.
  - `pulumi/pyproject.toml` — Current dependency configuration. Executor must understand the existing structure to add test dependencies correctly.

  **API/Type References** (contracts to implement against):
  - `pytest.mark.e2e` — Custom marker for E2E tests (must be registered in pyproject.toml or conftest.py)
  - `pytest.mark.timeout(N)` — From `pytest-timeout` package; kills test after N seconds
  - `pytest.fixture` — For shared test fixtures (kubeconfig, stack name)

  **External References** (libraries and frameworks):
  - pytest docs: `https://docs.pytest.org/en/stable/` — Fixture patterns, marker registration, test discovery
  - pytest-timeout: `https://pypi.org/project/pytest-timeout/` — Timeout decorator usage
  - Pulumi testing docs: `https://www.pulumi.com/docs/using-pulumi/testing/` — While we're NOT doing Pulumi unit tests, the E2E section shows patterns for testing against deployed infrastructure

  **WHY Each Reference Matters**:
  - `integration_tests.py` is the SINGLE MOST IMPORTANT REFERENCE — it contains all the test logic that must be wrapped. Without reading it fully, the executor will miss test functions or misunderstand signatures.
  - `k8s_ops.py` check functions are the lower-level helpers — some integration tests call these, some implement their own checks. Executor needs both files.
  - `pyproject.toml` structure determines WHERE to add dependencies — wrong placement means `uv` won't install them.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: pytest discovers E2E tests without errors
    Tool: Bash
    Preconditions: Task 11 changes applied, test dependencies installed
    Steps:
      1. Run: uv sync --group test
      2. Run: uv run pytest pulumi/tests/ -v --co 2>&1
    Expected Result: pytest collects tests (shows "collected N items"), exit code 0. N should be >= 5 (minimum meaningful test count).
    Failure Indicators: ImportError, ModuleNotFoundError, "no tests ran", or exit code non-zero
    Evidence: .sisyphus/evidence/task-11-test-collection.txt

  Scenario: Test file uses existing check functions (no reimplementation)
    Tool: Bash (grep)
    Preconditions: Task 11 changes applied
    Steps:
      1. Run: grep -n "from.*k8s_ops\|from.*integration_tests\|import.*k8s_ops\|import.*integration_tests" pulumi/tests/test_e2e_smoke.py
    Expected Result: At least one import from k8s_ops or integration_tests (proves wrapping, not reimplementing)
    Failure Indicators: No imports from existing modules — tests might be reimplementing logic
    Evidence: .sisyphus/evidence/task-11-imports.txt

  Scenario: All tests have @pytest.mark.e2e decorator
    Tool: Bash (grep)
    Preconditions: Task 11 changes applied
    Steps:
      1. Run: grep -c "pytest.mark.e2e" pulumi/tests/test_e2e_smoke.py
      2. Run: grep -c "def test_" pulumi/tests/test_e2e_smoke.py
      3. Compare counts — e2e markers should equal or exceed test function count (class-level decorators count once for multiple tests)
    Expected Result: marker count >= 1 and reasonable relative to test count
    Failure Indicators: Zero e2e markers
    Evidence: .sisyphus/evidence/task-11-markers.txt

  Scenario: conftest.py has required fixtures
    Tool: Bash (grep)
    Preconditions: Task 11 changes applied
    Steps:
      1. Run: grep -n "def kubeconfig\|def pulumi_stack\|pytest.fixture" pulumi/tests/conftest.py
    Expected Result: At least kubeconfig fixture present with @pytest.fixture decorator
    Failure Indicators: No fixtures defined, or conftest.py doesn't exist
    Evidence: .sisyphus/evidence/task-11-conftest.txt

  Scenario: pyproject.toml has test dependencies
    Tool: Bash (grep)
    Preconditions: Task 11 changes applied
    Steps:
      1. Run: grep -A5 "\[dependency-groups\]" pulumi/pyproject.toml || grep "pytest" pulumi/pyproject.toml
    Expected Result: pytest>=8.0 and pytest-timeout>=2.0 are listed in test dependency group
    Failure Indicators: No pytest dependency found in pyproject.toml
    Evidence: .sisyphus/evidence/task-11-deps.txt

  Scenario: Verification triad passes
    Tool: Bash
    Preconditions: Task 11 changes applied
    Steps:
      1. Run: uv run ruff check pulumi/
      2. Run: uv run ty check
      3. Run: pulumi preview -s dev
      4. Run: pulumi preview -s rancher-desktop
    Expected Result: All four commands exit 0 (new test files pass linting)
    Failure Indicators: Any command exits non-zero
    Evidence: .sisyphus/evidence/task-11-preview.txt
  ```

  **Commit**: YES (commit 11 of 11)
  - Message: `feat(testing): scaffold pytest E2E infrastructure wrapping existing check functions`
  - Files: `pulumi/pyproject.toml`, `pulumi/tests/conftest.py` (new), `pulumi/tests/test_e2e_smoke.py` (new)
  - Pre-commit: verification triad + `uv run pytest pulumi/tests/ -v --co`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
>
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `uv run ruff check pulumi/` + `uv run ty check` + `pulumi preview -s dev` + `pulumi preview -s rancher-desktop`. Review all changed files for: bare `except:`, `time.time()` in timeout loops, `dict` return from `update()`, hardcoded secrets outside `is_dev_stack` gates. Check for AI slop: excessive comments, over-abstraction, generic variable names.
  Output: `Ruff [PASS/FAIL] | Ty [PASS/FAIL] | Preview dev [PASS/FAIL] | Preview rancher [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration (security + reliability fixes working together). Run all E2E tests. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | E2E Tests [N/N] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance: no resource logical name changes, no Helm release name changes, no new features. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Scope Creep [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

| Order | Message | Files | Pre-commit |
|-------|---------|-------|-----------|
| 1 | `fix(security): fail on non-dev stacks without configured secrets` | config.py | verification triad |
| 2 | `fix(security): gate dev seed secrets behind is_dev_stack check` | values/openbao.py | verification triad |
| 3 | `fix(reliability): add CustomTimeouts to all Helm v4.Chart resources` | prerequisites.py, workflow_plane.py, flux_gitops.py | verification triad |
| 4 | `fix(reliability): fix update() return types to UpdateResult` | dynamic_providers.py | verification triad |
| 5 | `fix(reliability): narrow exception handling in dynamic providers and k8s_ops` | dynamic_providers.py, k8s_ops.py | verification triad |
| 6 | `fix(reliability): use time.monotonic() consistently for timeouts` | k8s_ops.py | verification triad |
| 7 | `fix(reliability): add safe port-forward process cleanup` | dynamic_providers.py, k8s_ops.py | verification triad |
| 8 | `refactor(consistency): wire values/data_plane.py into component` | components/data_plane.py, values/data_plane.py | verification triad |
| 9 | `refactor(types): add precise return type hints to values and helpers` | values/*.py, helpers/*.py | verification triad |
| 10 | `chore(cleanup): remove unused imports and add TYPE_CHECKING guards` | __main__.py, data_plane.py, workflow_plane.py, observability_plane.py | verification triad |
| 11 | `test(e2e): scaffold pytest infrastructure and initial E2E tests` | pyproject.toml, tests/conftest.py, tests/test_*.py | verification triad + pytest |

---

## Success Criteria

### Verification Commands
```bash
uv run ruff check pulumi/                       # Expected: All checks passed!
uv run ty check                                   # Expected: No errors (or only pre-existing)
cd pulumi && pulumi preview -s dev               # Expected: no changes (or only expected)
cd pulumi && pulumi preview -s rancher-desktop   # Expected: no changes (or only expected)
cd pulumi && uv run pytest tests/ -m e2e --timeout=120  # Expected: all pass (requires deployed stack)
```

### Final Checklist
- [ ] All 4 "Must Have" P0 security fixes present
- [ ] All 6 "Must Have" P1 reliability fixes present
- [ ] All "Must NOT Have" guardrails verified (no logical name changes, no release name changes, no new features)
- [ ] All tests pass
- [ ] Verification triad passes on both stacks
