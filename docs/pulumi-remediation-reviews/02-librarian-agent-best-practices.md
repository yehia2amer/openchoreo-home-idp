# Librarian Agent — Pulumi Best Practices Research

> **Agent**: Librarian
> **Session**: `ses_2c64babfbffeN85ZAdT3tbIsqX`
> **Sources**: Official Pulumi documentation, Pulumi blog, Pulumi examples repo
> **Objective**: Research Pulumi best practices to ground all remediation decisions in official guidance

---

## 1. ComponentResource Pattern

### Official Guidance
- ComponentResource is the recommended way to create reusable, multi-resource abstractions
- Always pass `opts=pulumi.ResourceOptions(parent=self)` to child resources
- Call `self.register_outputs({...})` at the end of `__init__` to expose outputs
- Use consistent naming: `{parent_name}-{child_purpose}`

### Codebase Assessment
- All major components use ComponentResource correctly
- Child resources pass `parent=self` via ResourceOptions
- Components call `register_outputs()`
- Some components don't expose all outputs (minor)

### Recommendation
No action needed — ComponentResource usage is solid.

---

## 2. Configuration & Secrets Management

### Official Guidance
- Use `pulumi.Config().require("key")` for mandatory config values
- Use `pulumi.Config().require_secret("key")` for sensitive values — this marks them as secret in state
- NEVER hardcode secrets in code — always use config or environment variables
- Use `pulumi.Output.secret(value)` to wrap values as secret in code
- Stack-specific config goes in `Pulumi.<stack>.yaml`

### Codebase Assessment
- Config values loaded via `pulumi.Config()` in `config.py`
- **CRITICAL**: Non-dev stacks fall back to hardcoded defaults for secrets (config.py:215-233)
- **CRITICAL**: Dev seed secrets in `values/openbao.py` not gated behind stack check
- `root_token="root"` passed as plain string through dynamic provider inputs (state unencrypted)
- Encrypted secrets in `Pulumi.rancher-desktop.yaml`

### Recommendations (applied to plan)
- **Task 1**: Change non-dev fallback to `raise` error — matches `require_secret()` behavior
- **Task 2**: Gate dev seed data behind `is_dev_stack` parameter
- **Known Limitation**: Dynamic provider state secret serialization deferred (too risky)

---

## 3. CustomTimeouts on Resources

### Official Guidance
- All long-running resources should have explicit `custom_timeouts`
- Default timeout is 10 minutes for create/update/delete
- Helm chart installations can take longer (CRD registration, webhook startup)
- Use `pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")` pattern
- Different resources may need different timeouts based on complexity

### Codebase Assessment
- No Helm v4.Chart resources have `custom_timeouts`
- Some Helm v3.Release resources have timeout-related settings
- Cert-manager and Flux are known to be slow — need generous timeouts

### Recommendations (applied to plan)
- **Task 3**: Add `CustomTimeouts` to all v4.Chart calls with 10m/10m/5m defaults
- Per-chart audit recommended (not blind `wait_for_jobs` addition)

---

## 4. Dynamic Resource Providers

### Official Guidance
- Dynamic providers implement `pulumi.dynamic.ResourceProvider`
- Required methods: `create(self, props)` → `CreateResult`, `delete(self, id, props)` → None
- Optional methods: `update(self, id, olds, news)` → `UpdateResult`, `diff(self, id, olds, news)` → `DiffResult`
- **CRITICAL**: `update()` MUST return `UpdateResult(outs=dict)`, NOT a plain `dict`
- Parameter naming: `props` (not `inputs`) for `create()`, `olds`/`news` for `update()`
- Exception handling: providers should catch specific exceptions and provide clear error messages

### Codebase Assessment
- **4 update() methods return `dict` instead of `UpdateResult`** — violates contract
- **Parameter names use `inputs` instead of `props`** in some create/update methods
- **Bare except blocks** swallow errors silently
- **Port-forward process leak** — no cleanup in exception paths
- CreateResult used correctly in create() methods
- DiffResult used correctly in diff() methods

### Recommendations (applied to plan)
- **Task 4**: Fix all `update()` return types to `UpdateResult`
- **Task 5**: Narrow exception handling to specific types + add logging
- **Task 7**: Add try/finally for port-forward process cleanup

---

## 5. Timing and Monotonic Clocks

### Official Guidance (Python stdlib, not Pulumi-specific)
- `time.time()` returns wall clock time — affected by NTP corrections, DST, manual changes
- `time.monotonic()` returns monotonically increasing time — immune to clock adjustments
- **Always use `time.monotonic()` for elapsed-time calculations and timeouts**
- `time.time()` is only appropriate for timestamps that need to be human-readable or stored

### Codebase Assessment
- `k8s_ops.py:646,648` uses `time.time()` for timeout calculations
- Other timeout loops in the same file already use `time.monotonic()`

### Recommendations (applied to plan)
- **Task 6**: Replace `time.time()` with `time.monotonic()` at the two identified locations

---

## 6. Testing Strategies

### Official Guidance
- **Unit tests**: Test resource definitions without deploying (mock Pulumi runtime)
- **Integration tests**: Deploy to real infrastructure and verify
- **Policy-as-code (CrossGuard)**: Enforce rules on all Pulumi operations
- **Property testing**: Verify resource properties before deployment

### User Decision
- **E2E tests ONLY** — user explicitly excluded unit tests
- **No CrossGuard** — out of scope for this remediation

### Codebase Assessment
- Integration test harness exists in `components/integration_tests.py` (~35 tests)
- Reusable check functions in `helpers/k8s_ops.py` (check_deployment, check_pod, etc.)
- No pytest infrastructure — tests run as Pulumi dynamic resources only
- No `tests/` directory, no pytest config in `pyproject.toml`

### Recommendations (applied to plan)
- **Task 11**: Scaffold pytest + pytest-timeout, create `tests/` directory, wrap existing `k8s_ops.check_*` functions as E2E pytest tests

---

## 7. Project Structure Best Practices

### Official Guidance
- Separate concerns: components, helpers, config
- Use ComponentResource for reusable modules
- Keep values/configuration separate from resource definitions
- Use `__all__` exports for clean public APIs
- Organize by domain (not by resource type)

### Codebase Assessment
- Clean separation: `components/`, `helpers/`, `values/`, `platforms/`, `scripts/`
- Domain-organized: control_plane, data_plane, workflow_plane, etc.
- One deviation: `values/data_plane.py` not wired into `components/data_plane.py`
- Unused imports in several files

### Recommendations (applied to plan)
- **Task 8**: Wire `values/data_plane.py` into its component
- **Task 9**: Add return type hints to values files for consistency
- **Task 10**: Clean unused imports + add TYPE_CHECKING guards

---

## 8. Resource Protection and State Management

### Official Guidance
- Use `protect=True` on stateful resources to prevent accidental deletion
- Never change resource logical names — causes URN breakage (destroy + recreate)
- Use `aliases` when renaming resources
- Import existing resources with `pulumi import`

### Codebase Assessment
- Inconsistent `protect=True` usage (some resources have it, others don't)
- Resource names are consistent and stable

### Recommendations
- **Out of scope**: `protect=True` consistency requires business decision on which resources are critical
- **Guardrail**: Plan explicitly forbids resource logical name changes and Helm release name changes

---

## 9. Error Handling Best Practices

### Official Guidance
- Use specific exception types, not bare `except:`
- Log caught exceptions with `pulumi.log.warn()` or `pulumi.log.error()`
- Resource creation failures should propagate clearly
- Use `pulumi.log.info()` for operational messages, `.warn()` for non-fatal issues

### Codebase Assessment
- Multiple bare `except:` blocks in dynamic_providers.py and k8s_ops.py
- Some exception blocks swallow errors without logging
- Happy paths generally log well with `pulumi.log.info()`

### Recommendations (applied to plan)
- **Task 5**: Narrow all exception handling, add `pulumi.log.warn()` to caught exceptions

---

## 10. Key Pulumi Python SDK References

### Import Paths Confirmed
```python
from pulumi.dynamic import ResourceProvider, CreateResult, UpdateResult, DiffResult
from pulumi import CustomTimeouts, ResourceOptions, ComponentResource
import pulumi
```

### Version Constraints (from pyproject.toml)
- `pulumi>=3.0.0,<4.0.0`
- `pulumi-kubernetes>=4.0.0,<5.0.0`
- Python `>=3.12`
- Toolchain: `uv`

### Verification Commands
```bash
uv run ruff check pulumi/       # Static lint
uv run ty check                  # Type checking
cd pulumi && pulumi preview -s dev            # IaC preview (dev)
cd pulumi && pulumi preview -s rancher-desktop  # IaC preview (rancher)
```