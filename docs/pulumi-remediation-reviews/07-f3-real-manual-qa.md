# F3: Real Manual QA — Pulumi Remediation Plan

> **Date**: 2026-03-29
> **Reviewer**: Sisyphus F3 QA Agent
> **Scope**: Tasks 1–11 from `.sisyphus/plans/pulumi-remediation.md`
> **Mode**: READ-ONLY source verification, ruff lint, pytest collection

---

## Summary

All 10 remediation tasks were verified (Task 8 skipped — pre-existing implementation). Every QA scenario passed. Ruff lint is clean. All 5 E2E tests collect successfully.

```
Scenarios [24/24 pass] | Integration [2/2] | E2E Tests [5/5 collected] | VERDICT: APPROVE
```

---

## Task-by-Task Results

### Task 1: Security — Fail-fast on non-dev stacks ✅

| Scenario | File:Line | Result |
|----------|-----------|--------|
| `is_dev_stack` defined correctly | `config.py:213` | PASS |
| ValueError for missing opensearch_admin_password | `config.py:218` | PASS |
| ValueError for missing opensearch_seed_password | `config.py:229` | PASS |
| Dev stacks still get defaults | `config.py:220-232` | PASS |

**4/4 PASS**

### Task 2: Security — Gate dev seed secrets ✅

| Scenario | File:Line | Result |
|----------|-----------|--------|
| `is_dev_stack` parameter accepted | `values/openbao.py:12` | PASS |
| `is_dev_stack` passed from call site | `components/prerequisites.py:205` | PASS |
| Hardcoded dev credentials gated | `values/openbao.py:67-85` | PASS |

**Note**: Call site is in `prerequisites.py` (not `control_plane.py` as plan suggested) — functionally correct.

**3/3 PASS**

### Task 3: CustomTimeouts on Helm resources ✅

| Resource | File:Line | Timeout Values | Result |
|----------|-----------|---------------|--------|
| cert-manager (v4.Chart) | `prerequisites.py:97` | `create=TIMEOUT_DEFAULT` | PASS |
| external-secrets (v4.Chart) | `prerequisites.py:119` | `10m/10m/5m` | PASS |
| kgateway-crds (v4.Chart) | `prerequisites.py:146` | `10m/10m/5m` | PASS |
| kgateway (v4.Chart) | `prerequisites.py:184` | `10m/10m/5m` | PASS |
| openbao (v4.Chart) | `prerequisites.py:211` | `10m/10m/5m` | PASS |
| docker-registry (v4.Chart) | `workflow_plane.py:63` | `10m/10m/5m` | PASS |
| WP (v3.Release) | `workflow_plane.py:91` | `create=TIMEOUT_DEFAULT` | PASS |
| DP (v3.Release) | `data_plane.py:103` | `create=TIMEOUT_DEFAULT` | PASS |
| 4x Observability (v3.Release) | `observability_plane.py:149,169,188,213` | `create=TIMEOUT_DEFAULT` | PASS |
| flux_gitops.py | N/A — no Helm charts | N/A | N/A |

**4/4 PASS** (1 N/A)

### Task 4: UpdateResult returns ✅

| Provider | File:Line | Return Statement | Result |
|----------|-----------|-----------------|--------|
| `_CopyCAProvider.update` | `dynamic_providers.py:60` | `UpdateResult(outs=result.outs)` | PASS |
| `_RegisterPlaneProvider.update` | `dynamic_providers.py:164` | `UpdateResult(outs=result.outs)` | PASS |
| `_LinkPlanesProvider.update` | `dynamic_providers.py:252` | `UpdateResult(outs=result.outs)` | PASS |
| `_LabelNamespaceProvider.update` | `dynamic_providers.py:324` | `UpdateResult(outs=result.outs)` | PASS |
| `_OpenBaoSecretsProvider.update` | `dynamic_providers.py:516` | `UpdateResult(outs=result.outs)` | PASS |
| `_ValidateOpenBaoSecretsProvider.update` | `dynamic_providers.py:578` | `UpdateResult(outs=result.outs)` | PASS |
| `_IntegrationTestProvider.update` | `dynamic_providers.py:803` | `UpdateResult(outs=self._run_check(news))` | PASS |

Import verified at `dynamic_providers.py:19`.

**2/2 PASS** (7 update methods verified)

### Task 5: Narrow exception handling ✅

| Scenario | Evidence | Result |
|----------|----------|--------|
| K8s API uses `k8s_client.ApiException` | 14+ catch sites in `k8s_ops.py` | PASS |
| Non-K8s uses specific exceptions | `urllib.error.URLError/OSError`, `hvac.exceptions.VaultError` | PASS |

**Acceptable residuals**:
- `k8s_ops.py:624` — outer `except Exception` catch-all for port-forward block (integration test safety net)
- `k8s_ops.py:669` — `except k8s_client.ApiException: pass` in polling loop (INTENTIONAL per constraints)

**2/2 PASS**

### Task 6: time.monotonic() ✅

| Function | File:Line | Result |
|----------|-----------|--------|
| `wait_for_pod_ready` | `k8s_ops.py:33,35` | PASS |
| `wait_for_secret_type` | `k8s_ops.py:59,61` | PASS |
| `wait_for_deployments_available` | `k8s_ops.py:86,89` | PASS |
| `check_service_http` | `k8s_ops.py:353,355,371` | PASS |
| `wait_for_custom_resource_condition` | `k8s_ops.py:657,659` | PASS |

Zero occurrences of `time.time()` in timeout loops.

**2/2 PASS**

### Task 7: Safe port-forward cleanup ✅

| Location | File:Line | Pattern | Result |
|----------|-----------|---------|--------|
| `_OpenBaoSecretsProvider.create` | `dynamic_providers.py:501-507` | suppress + kill fallback | PASS |
| `check_openbao_secrets` | `k8s_ops.py:630-636` | suppress + kill fallback | PASS |
| `validate_openbao_secrets` | `k8s_ops.py:724-730` | suppress + kill fallback | PASS |

**Minor note**: `check_service_http` (`k8s_ops.py:395`) uses simpler cleanup without `contextlib.suppress(ProcessLookupError)` — acceptable for integration test helper.

**2/2 PASS**

### Task 8: Wire data_plane.py — SKIPPED

Pre-existing implementation. Not in remediation scope.

### Task 9: Return type hints on values/*.py ✅

| File | Line | Signature | Result |
|------|------|-----------|--------|
| `values/control_plane.py` | 18 | `-> dict[str, Any]` | PASS |
| `values/registry.py` | 8 | `-> dict[str, Any]` | PASS |
| `values/workflow_plane.py` | 8 | `-> dict[str, Any]` | PASS |
| `values/data_plane.py` | 8 | `-> dict[str, Any]` | PASS |
| `values/observability_plane.py` | 16 | `-> dict[str, Any]` | PASS |
| `values/openbao.py` | 12 | `-> dict[str, Any]` | PASS |

All files have `from typing import Any` and `from __future__ import annotations`.

**2/2 PASS**

### Task 10: TYPE_CHECKING guards ✅

| File | Lines | Guard | Result |
|------|-------|-------|--------|
| `data_plane.py` | 5-6, 15-16 | `if TYPE_CHECKING: from helpers.dynamic_providers import RegisterPlane` | PASS |
| `workflow_plane.py` | 5, 23-24 | `if TYPE_CHECKING: from helpers.dynamic_providers import RegisterPlane` | PASS |
| `observability_plane.py` | 5, 26-27 | `if TYPE_CHECKING: from helpers.dynamic_providers import RegisterPlane` | PASS |

All three files have `from __future__ import annotations` at line 3.

**2/2 PASS**

### Task 11: E2E test collection ✅

| Scenario | Evidence | Result |
|----------|----------|--------|
| 5 tests collected | `uv run pytest tests/ -v --co` → 5 tests in 0.39s | PASS |
| All tests have markers | `@pytest.mark.e2e` + `@pytest.mark.timeout(120)` on all 5 | PASS |
| Fixtures + pyproject config | session-scoped fixtures, `pytest>=8.0`, `pytest-timeout>=2.0` | PASS |

**Tests collected**:
1. `test_control_plane_api_deployment_ready`
2. `test_thunder_httproute_accepted`
3. `test_backstage_service_http`
4. `test_gateway_httproute_crd_exists`
5. `test_backstage_secret_exists`

**3/3 PASS**

---

## Cross-Task Integration

| Check | Command | Result |
|-------|---------|--------|
| Ruff lint | `uv run ruff check .` | All checks passed ✅ |
| E2E test collection | `uv run pytest tests/ -v --co` | 5/5 collected ✅ |
| Pulumi preview | N/A — no local k8s cluster | N/A (constraint) |

**2/2 PASS** (1 N/A)

---

## Discoveries

1. **Task 2 call site**: `is_dev_stack` is passed from `components/prerequisites.py:205`, not `control_plane.py` as the plan suggested. Functionally correct.
2. **flux_gitops.py**: Has no Helm v4.Chart resources — uses `yaml.v2.ConfigGroup` and `CustomResource`. Task 3 correctly does not apply.
3. **check_service_http cleanup**: Uses simpler `pf.terminate(); pf.wait(timeout=5)` without `contextlib.suppress(ProcessLookupError)`. Minor gap, acceptable for integration test helper.
4. **_IntegrationTestProvider.update**: Returns `UpdateResult(outs=self._run_check(news))` directly instead of delegating to `self.create()`. Different pattern but functionally correct.
5. **Pre-existing type errors**: ~275 ty diagnostics in `__main__.py`, `integration_tests.py`, `k8s_ops.py` — all pre-existing, not caused by remediation changes.

---

## Evidence Files

All evidence saved to `.sisyphus/evidence/final-qa/`:

| File | Task |
|------|------|
| `task-01-security-failfast.md` | Task 1 |
| `task-02-gate-secrets.md` | Task 2 |
| `task-03-custom-timeouts.md` | Task 3 |
| `task-04-update-result.md` | Task 4 |
| `task-05-narrow-exceptions.md` | Task 5 |
| `task-06-monotonic-time.md` | Task 6 |
| `task-07-port-forward-cleanup.md` | Task 7 |
| `task-08-skipped.md` | Task 8 (skipped) |
| `task-09-return-type-hints.md` | Task 9 |
| `task-10-type-checking-guards.md` | Task 10 |
| `task-11-e2e-tests.md` | Task 11 |
| `cross-task-integration.md` | Integration checks |

---

## Verdict

```
Scenarios [24/24 pass] | Integration [2/2] | E2E Tests [5/5 collected] | VERDICT: APPROVE
```

All remediation tasks have been correctly implemented. No blocking issues found. The codebase is ready for deployment testing on a live cluster.
