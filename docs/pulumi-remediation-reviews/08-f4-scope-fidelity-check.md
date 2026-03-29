# F4: Scope Fidelity Check

## Task-by-Task Compliance

### Task 1: MISSING
- Plan: Fail fast on non-dev stacks using `pulumi.ConfigMissingError` (or equivalent Pulumi config-missing behavior), keep `is_dev_stack` list and dev defaults unchanged.
- Actual: Added non-dev fail-fast logic and preserved `is_dev_stack` list/dev defaults, but raised `ValueError` in `pulumi/config.py` instead of `pulumi.ConfigMissingError`.
- Missing: `pulumi.ConfigMissingError`/Pulumi-native missing-config exception usage.
- Extra: none.

### Task 2: COMPLIANT
- Plan: Gate OpenBao dev seed secrets behind `is_dev_stack`; pass `is_dev_stack` from component call site; keep script embedded.
- Actual: `pulumi/values/openbao.py` now accepts `is_dev_stack` and gates seed-secret block; caller passes `is_dev_stack` from stack in `pulumi/components/prerequisites.py`; script remains embedded.
- Missing: none.
- Extra: `depends_on=base_depends + [kgateway_crds]` -> `depends_on=[*base_depends, kgateway_crds]` in `prerequisites.py` (allowed by inherited context as required ruff-safe rewrite, not treated as scope creep).

### Task 3: MISSING
- Plan: Add `custom_timeouts` to all Helm v4.Chart resources in `prerequisites.py`, `workflow_plane.py`, and `flux_gitops.py`.
- Actual: Added `custom_timeouts` to all v4.Chart calls in `prerequisites.py` and `workflow_plane.py`.
- Missing: No `flux_gitops.py` change in `003a3ec..HEAD` despite plan expecting Flux chart timeout coverage.
- Extra: none.

### Task 4: COMPLIANT
- Plan: Fix dynamic provider `update()` methods to return `UpdateResult(outs=...)` instead of dict; align signatures.
- Actual: All four targeted `update()` methods in `pulumi/helpers/dynamic_providers.py` now return `UpdateResult(outs=...)` with `-> UpdateResult` annotation.
- Missing: none.
- Extra: File-level pyright/ruff comment adjustments (non-functional).

### Task 5: COMPLIANT
- Plan: Narrow broad exception handling in `dynamic_providers.py` and `k8s_ops.py`; add visible warning logs; keep control flow.
- Actual: Replaced broad catches with narrower `k8s_client.ApiException`, `hvac.exceptions.VaultError`, and `(urllib.error.URLError, OSError)` where appropriate; added `pulumi.log.warn()`; flow preserved.
- Missing: none.
- Extra: none.

### Task 6: COMPLIANT
- Plan: Replace remaining timeout-related `time.time()` calls with `time.monotonic()` in `k8s_ops.py`.
- Actual: `deadline` and loop comparison in `wait_for_custom_resource_condition` switched to monotonic.
- Missing: none.
- Extra: none.

### Task 7: COMPLIANT
- Plan: Add exception-safe port-forward cleanup (`terminate` + `wait`, handle `ProcessLookupError`, kill on `TimeoutExpired`) in `dynamic_providers.py` and `k8s_ops.py`.
- Actual: Implemented `finally` cleanup pattern in all targeted blocks with `contextlib.suppress(ProcessLookupError)`, `wait(timeout=5)`, and kill fallback.
- Missing: none.
- Extra: none.

### Task 8: COMPLIANT
- Plan: Wire `values/data_plane.py` into `components/data_plane.py`.
- Actual: No remediation commit for T8 (explicitly skipped per plan/context because already implemented before baseline). Current code already uses `from values.data_plane import get_values as dp_values`.
- Missing: none (intentionally pre-satisfied).
- Extra: none.

### Task 9: COMPLIANT
- Plan: Add `-> dict[str, Any]` return types across values helpers and required typing imports.
- Actual: Added return annotations/imports across touched values modules (`control_plane`, `data_plane`, `observability_plane`, `openbao`, `registry`, `workflow_plane`).
- Missing: none material in changed scope.
- Extra: Included `values/registry.py` typing update (consistent with “all values helpers” intent).

### Task 10: MISSING
- Plan: Remove unused `Sequence` and `Path` imports from `pulumi/__main__.py`; add `TYPE_CHECKING` guards for type-only `RegisterPlane` imports in three component files.
- Actual: `TYPE_CHECKING` guards added in `data_plane.py`, `workflow_plane.py`, `observability_plane.py`.
- Missing: `pulumi/__main__.py` cleanup was not done; `Path` import remains.
- Extra: none.

### Task 11: MISSING
- Plan: Add pytest E2E scaffold and deps; tests should wrap existing checks and import from `helpers.k8s_ops` and `components.integration_tests`; no unrelated config expansion.
- Actual: Added test dep group, pytest config, `pulumi/tests/conftest.py`, `pulumi/tests/test_e2e_smoke.py`, and lockfile updates.
- Missing: `test_e2e_smoke.py` imports only `helpers.k8s_ops`; no import/wrapping from `components.integration_tests` as specified.
- Extra: Added `[tool.ruff.lint.per-file-ignores]` entries in `pulumi/pyproject.toml` (not in task spec).

## Must NOT Do Guardrails

- Resource logical name changes: **CLEAN** (no detected logical-name argument changes in remediation diff).
- Helm release name changes: **CLEAN** (no `release_name` changes in remediation diff).
- Dependency graph changes: **CLEAN (with known allowed formatting exception)** — one `depends_on` expression rewritten from concatenation to unpacked list in `prerequisites.py` (explicitly documented acceptable ruff-related rewrite).
- New features/resources/config: **FOUND** — added Ruff per-file ignore configuration (`[tool.ruff.lint.per-file-ignores]`) not requested by remediation plan tasks.
- Unit tests: **CLEAN** (only E2E pytest scaffold under `pulumi/tests`).
- CrossGuard / Policy-as-Code: **CLEAN**.
- Bash extraction: **CLEAN** (OpenBao postStart script remained embedded in `values/openbao.py`).

## Unaccounted Files

From `git diff --stat 003a3ec..HEAD`, all changed files map to tasks except below:

- `pulumi/pyproject.toml` — contains unplanned Ruff per-file ignores in addition to planned test config (partial unaccounted scope).

Known exceptions correctly ignored:
- `.sisyphus/notepads/pulumi-remediation/learnings.md`
- `pulumi/uv.lock`

## VERDICT: REJECT

Reasoning: multiple task/spec mismatches remain (T1 exception type mismatch, T3 missing Flux timeout coverage per plan, T10 missing `__main__.py` import cleanup, T11 missing `integration_tests` wrapping requirement) and one scope-creep config change (unplanned Ruff per-file ignores).

Tasks [7/11 compliant] | Scope Creep [1 issue] | Unaccounted [1 file] | VERDICT: REJECT
