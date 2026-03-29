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

## 2026-03-29
- Kept OpenBao auth/policy/role bootstrap unconditional while gating only fake dev seed secrets behind `is_dev_stack`.
- Derived `is_dev_stack` from `pulumi.get_stack()` at the chart call site so values builders stay stack-aware without changing config.
- Ruff flagged an unrelated `depends_on` concatenation in `prerequisites.py`; rewriting it as list unpacking kept checks clean.
Added CustomTimeouts to all Helm v4.Chart resources in prerequisites.py and workflow_plane.py; kept them inside pulumi.ResourceOptions and left existing cilium chart unchanged.
- Replaced the remaining `time.time()` timeout calculations in `helpers/k8s_ops.py` with `time.monotonic()` to avoid wall-clock drift during waits.
2026-03-29: Fixed the four dynamic provider update() methods in pulumi/helpers/dynamic_providers.py to return UpdateResult(outs=...) instead of raw dicts; UpdateResult was already imported so no import changes were needed.
