# Learnings — Pulumi Remediation

## 2026-03-29 Session Start
- Project uses `uv` as toolchain (confirmed in Pulumi.yaml and pyproject.toml)
- Verification triad: `uv run ruff check pulumi/` + `uv run ty check` + `pulumi preview -s dev` + `pulumi preview -s rancher-desktop`
- Pre-existing LSP errors in k8s_ops.py (197+) and integration_tests.py (20+) — NOT in scope
- Python >=3.12, Pulumi >=3.0.0,<4.0.0, pulumi-kubernetes >=4.0.0,<5.0.0
- `is_dev_stack` defined at config.py:210 as `is_dev_stack = stack_name in ("dev", "rancher-desktop", "local", "test")`
- Integration test harness already exists in components/integration_tests.py with ~35 tests
- Reusable check functions exist in helpers/k8s_ops.py
- For non-dev Pulumi stacks, insecure credential defaults should fail fast with `ValueError`, not warn-and-continue.
- `cfg.get()` stays appropriate here because these values need to remain plain strings for dynamic providers.
- Updated all `pulumi/values/*.py` `get_values()` helpers to return `dict[str, Any]` and added `from typing import Any` where needed.
- `openbao.py`'s `_post_start_script()` already had the correct `-> str` annotation and was left unchanged.
- Repository-wide `ruff check pulumi/` and `ty check` still surface unrelated pre-existing issues in `pulumi/__main__.py`, `pulumi/components/*.py`, and `pulumi/scripts/*.py`; the values files themselves stayed clean.

## 2026-03-29
- Kept OpenBao auth/policy/role bootstrap unconditional while gating only fake dev seed secrets behind `is_dev_stack`.
- Derived `is_dev_stack` from `pulumi.get_stack()` at the chart call site so values builders stay stack-aware without changing config.
- Ruff flagged an unrelated `depends_on` concatenation in `prerequisites.py`; rewriting it as list unpacking kept checks clean.
Added CustomTimeouts to all Helm v4.Chart resources in prerequisites.py and workflow_plane.py; kept them inside pulumi.ResourceOptions and left existing cilium chart unchanged.
- Replaced the remaining `time.time()` timeout calculations in `helpers/k8s_ops.py` with `time.monotonic()` to avoid wall-clock drift during waits.
2026-03-29: Fixed the four dynamic provider update() methods in pulumi/helpers/dynamic_providers.py to return UpdateResult(outs=...) instead of raw dicts; UpdateResult was already imported so no import changes were needed.

## 2026-03-29: Exception Handling Narrowing
- Narrowed 5 broad `except Exception:` blocks across `dynamic_providers.py` and `k8s_ops.py`:
  - K8s API calls → `k8s_client.ApiException` (dynamic_providers.py delete method)
  - urllib HTTP retry → `(urllib.error.URLError, OSError)` (k8s_ops.py check_service_http)
  - hvac/OpenBao calls → `hvac.exceptions.VaultError` (k8s_ops.py check_openbao_secrets and validate_openbao_secrets)
  - Top-level error boundaries → kept as `Exception` but added `pulumi.log.warn()` for visibility
- Added `pulumi.log.warn()` to ALL narrowed except blocks so errors surface in Pulumi output
- Removed stale `# ruff: noqa: SIM105` from dynamic_providers.py — it was only needed for the old `except Exception: pass` pattern which triggered "use contextlib.suppress" rule. After narrowing to `k8s_client.ApiException` + adding warn logging, it's no longer a bare pass.
- Import ordering matters: `kubernetes` is a third-party lib, so it sorts with `pulumi` imports, not after `from helpers` (first-party).
- `hvac` is imported locally inside function bodies (not at module level) but `hvac.exceptions.VaultError` is accessible after `import hvac`.

## 2026-03-29: Exception-Safe Port-Forward Cleanup
- Replaced bare `pf.terminate(); pf.wait(timeout=5)` in all 3 port-forward finally blocks with exception-safe pattern
- Used `contextlib.suppress(ProcessLookupError)` for terminate (process may already be dead)
- Used explicit `try/except subprocess.TimeoutExpired` for wait — calls `pf.kill(); pf.wait()` as escalation
- Ruff SIM105 rule flags `try/except/pass` and requires `contextlib.suppress` — applied `import contextlib` locally inside each finally block (matching the existing pattern of local imports in function bodies)
- `ProcessLookupError` is a Python built-in — no import needed
- `subprocess.TimeoutExpired` is available from the local `import subprocess` already present in each function body
- 3 blocks total: dynamic_providers.py (OpenBaoSecretsProvider.create), k8s_ops.py (check_openbao_secrets, validate_openbao_secrets)

## 2026-03-29: TYPE_CHECKING cleanup
- Wrapped `RegisterPlane` imports in `TYPE_CHECKING` blocks in data_plane.py, workflow_plane.py, and observability_plane.py since the type is only used in annotations.
- `pulumi/__main__.py` needed `cast(...)` on `register_cmd` values to satisfy Pyright/ty because `RegisterPlane` is a `pulumi.dynamic.Resource`, not just a generic `Resource`.
- Ruff passed on the touched Pulumi files; repo-wide `ty check` still reports unrelated missing third-party modules under `docs/reference-project-docs/openchoreo/rca-agent/`.

## 2026-03-29: Pytest E2E scaffold (Task 11)
- Added a dedicated `test` dependency group in `pulumi/pyproject.toml` with only `pytest>=8.0` and `pytest-timeout>=2.0`.
- Added `[tool.pytest.ini_options]` with `testpaths=["tests"]` and registered `e2e`/`slow` markers to avoid unknown-marker warnings.
- Created `pulumi/tests/conftest.py` with session fixtures for `KUBECONFIG`, `PULUMI_STACK`, and derived `KUBE_CONTEXT` defaults.
- Created `pulumi/tests/test_e2e_smoke.py` as thin wrappers over existing `helpers.k8s_ops.check_*` functions (deployment, httproute, service HTTP, CRD, secret).
- Kept wrappers environment-driven (`E2E_*` overrides) while defaulting to current platform namespaces/constants so `--co` works without live-cluster execution.
