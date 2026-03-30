# F3: Manual QA Results

**Date**: 2026-03-29
**Executor**: Sisyphus-Junior (QA Agent)

---

## Part A: Task Scenario Results (11/11 PASS)

### Task 1 — Fail-fast on non-dev stacks ✅ PASS
- `config.py` line 213: `is_dev_stack = stack_name in ("dev", "rancher-desktop", "local", "test")`
- Lines 218, 226: Non-dev stacks raise `pulumi.ConfigMissingError` for `openbao_root_token` and `opensearch_password`
- **Note**: Uses `ConfigMissingError` (Pulumi-native) instead of `ValueError`. Functionally equivalent fail-fast behavior.

### Task 2 — Gate dev seed secrets ✅ PASS
- `values/openbao.py` line 14: `get_values()` accepts `is_dev_stack: bool`
- `_post_start_script()` line 43: Dev secrets wrapped in `if is_dev_stack:` guard
- `prerequisites.py` line 208: passes `is_dev_stack=pulumi.get_stack() in ("dev", "rancher-desktop", "local", "test")`
- Auth/policy/role bootstrap NOT gated (correct — only fake seed secrets are gated)

### Task 3 — CustomTimeouts on Helm charts ✅ PASS
- `prerequisites.py`: All `v4.Chart` calls have `custom_timeouts`:
  - external-secrets (line 122)
  - openbao (line 213)
  - kgateway-crds (line 148)
  - kgateway (line 186)
- `workflow_plane.py`: docker-registry `v4.Chart` (line 66) has `custom_timeouts`
- `flux_gitops.py`: No `v4.Chart` calls — uses `yaml.v2.ConfigGroup` and dynamic providers. N/A.
- Cilium uses `v3.Release` — not in scope (confirmed)

### Task 4 — UpdateResult return types ✅ PASS
All 7 `def update()` methods in `dynamic_providers.py` return `UpdateResult(outs=...)`:
- `_CopyCAProvider.update` (line 58-60)
- `_RegisterPlaneProvider.update` (line 162-164)
- `_LinkPlanesProvider.update` (line 250-252)
- `_LabelNamespaceProvider.update` (line 322-324)
- `_OpenBaoSecretsProvider.update` (line 514-516)
- `_ValidateOpenBaoSecretsProvider.update` (line 576-578)
- `_IntegrationTestProvider.update` (line 802-803)

### Task 5 — Narrowed exception handling ✅ PASS
- `dynamic_providers.py`: `_LinkPlanesProvider.delete` catches `k8s_client.ApiException` (line 268)
- `k8s_ops.py`: Most except blocks catch `k8s_client.ApiException`
- **Note**: `k8s_ops.py` line 624 has `except Exception as e:` in `check_openbao_secrets()` — pre-existing, NOT a regression per inherited constraints.

### Task 6 — time.monotonic() ✅ PASS
- `k8s_ops.py`: 0 matches for `time.time()`, 10 matches for `time.monotonic()` at lines 33, 35, 59, 61, 86, 89, 353, 355, 371, 657, 659
- Verified via bash grep commands

### Task 7 — Safe port-forward cleanup ✅ PASS
- `dynamic_providers.py` `_OpenBaoSecretsProvider.create` (lines 498-507): `contextlib.suppress(ProcessLookupError)` + `subprocess.TimeoutExpired` with kill escalation
- `k8s_ops.py` `validate_openbao_secrets` (lines 722-730): Same pattern
- `k8s_ops.py` `check_openbao_secrets` (lines 628-636): Same pattern
- **Note**: `check_service_http` (lines 394-396) uses simpler `terminate()+wait()` — pre-existing, NOT a regression.

### Task 8 — Wire data_plane values ✅ PASS
- `data_plane.py` line 13: `from values.data_plane import get_values as dp_values`
- Line 96: `values=dp_values(dp_http_port=cfg.dp_http_port, dp_https_port=cfg.dp_https_port, tls_enabled=cfg.tls_enabled)`

### Task 9 — Return type hints ✅ PASS
All `get_values` functions have `-> dict[str, Any]`:
- `values/data_plane.py` line 8
- `values/workflow_plane.py` line 8
- `values/observability_plane.py` line 10
- `values/control_plane.py` line 10
- `values/registry.py` line 8
- `values/openbao.py` line 10
- `_post_start_script() -> str` confirmed at `values/openbao.py` line 38

### Task 10 — Unused imports + TYPE_CHECKING ✅ PASS
- `data_plane.py` lines 5-6, 15-16: `TYPE_CHECKING` guard for `RegisterPlane`
- `workflow_plane.py` lines 5, 23-24: Same pattern
- `observability_plane.py` lines 5-6, 26-27: Same pattern
- `__main__.py`: No unused imports detected; all component imports used

### Task 11 — E2E test scaffold ✅ PASS
- **Pytest collection**: 5 tests collected successfully (`uv run --group test pytest tests/ -v --co`)
- **Test file**: `test_e2e_smoke.py` — 5 tests, all marked `@pytest.mark.e2e` and `@pytest.mark.timeout(120)`
- **Conftest**: `conftest.py` — 3 session-scoped fixtures (`kubeconfig`, `pulumi_stack`, `kube_context`) + `pytest_configure` for markers
- **pyproject.toml**: `pytest>=8.0` and `pytest-timeout>=2.0` in `[dependency-groups] test`; `[tool.pytest.ini_options]` with `testpaths = ["tests"]` and markers
- **Imports from modified helpers**: `check_crd_exists`, `check_deployment_ready`, `check_httproute_accepted`, `check_secret_exists`, `check_service_http` from `helpers.k8s_ops`

---

## Part B: Cross-Task Integration (4/4 PASS)

### Integration 1: T1+T2 consistency ✅ PASS
- `config.py` line 213 and `prerequisites.py` line 208 both use identical dev stack set: `("dev", "rancher-desktop", "local", "test")`
- `config.py` raises `ConfigMissingError` for non-dev; `openbao.py` gates secrets via `is_dev_stack` bool

### Integration 2: T5+T7 compatibility ✅ PASS
- Narrowed exceptions (T5) target `k8s_client.ApiException` for API calls
- Safe cleanup (T7) uses `contextlib.suppress(ProcessLookupError)` + `subprocess.TimeoutExpired` for process management
- These are orthogonal concerns — no interference

### Integration 3: T10 doesn't break T4/T5/T7 ✅ PASS
- `TYPE_CHECKING` guards only wrap `RegisterPlane` import (used for type hints only)
- Runtime imports in `dynamic_providers.py` (used by T4/T5/T7) are NOT behind `TYPE_CHECKING`
- No runtime import removed

### Integration 4: T11 imports from T5/T6 modified helpers ✅ PASS
- `test_e2e_smoke.py` imports 5 functions from `helpers.k8s_ops` (modified in T5/T6)
- Pytest collection succeeded with 5 tests collected — all imports resolve

---

## Part C: E2E Test Collection

```
$ uv run --group test pytest tests/ -v --co
============================= test session starts ==============================
platform darwin -- Python 3.12.12, pytest-9.0.2, pluggy-1.6.0
plugins: timeout-2.4.0
collecting ... collected 5 items

<Dir pulumi>
  <Package tests>
    <Module test_e2e_smoke.py>
      <Function test_control_plane_api_deployment_ready>
      <Function test_thunder_httproute_accepted>
      <Function test_backstage_service_http>
      <Function test_gateway_httproute_crd_exists>
      <Function test_backstage_secret_exists>

========================== 5 tests collected in 0.54s ==========================
```

---

## Notes & Observations

1. **ConfigMissingError vs ValueError**: Task 1 uses `pulumi.ConfigMissingError` instead of `ValueError`. This is arguably better (Pulumi-native error), functionally equivalent for fail-fast.
2. **Pre-existing broad catches**: `k8s_ops.py:624` (`except Exception`) and `check_service_http` simple cleanup — both pre-existing, not regressions per inherited constraints.
3. **Dual `is_dev_stack` computation**: Defined in `config.py` (line 213) and re-computed in `prerequisites.py` (line 208) with identical logic. Minor DRY opportunity but not a defect.
4. **`importlib.import_module("pytest")`**: Used in test files instead of direct `import pytest` — likely to avoid import errors when pytest isn't installed in non-test environments.

---

## Final Verdict

```
Scenarios [11/11 pass] | Integration [4/4 pass] | E2E Tests [5/5 collected] | VERDICT: APPROVE
```
