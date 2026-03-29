# Explore Agent — Full Codebase Audit

> **Agent**: Explore
> **Session**: `ses_2c64bde78ffehNkTfayXOU2L4J`
> **Scope**: Every file in `pulumi/` directory (20+ files)
> **Objective**: Map the entire codebase, identify all issues with file:line references

---

## Codebase Map

### Project Root (`pulumi/`)

| File | Purpose | Lines |
|------|---------|-------|
| `__main__.py` | Pulumi entry point — loads config, instantiates all components in dependency order | ~50 |
| `config.py` | Configuration loading — `InfraConfig` dataclass, stack detection, secret handling | ~240 |
| `Pulumi.yaml` | Project definition — runtime (python), toolchain (uv), description | ~10 |
| `Pulumi.rancher-desktop.yaml` | Stack config for rancher-desktop — encrypted secrets, platform settings | ~30 |
| `pyproject.toml` | Python project config — dependencies, uv settings | ~40 |

### Components (`pulumi/components/`)

| File | Purpose | Key Resources |
|------|---------|---------------|
| `prerequisites.py` | Foundation layer — cert-manager, metrics-server, trust-manager, open-feature | Helm v4.Chart × 4+ |
| `control_plane.py` | Control plane — ArgoCD, OpenBao (Vault), Dex | Helm v3.Release, dynamic providers |
| `data_plane.py` | Data plane — OpenSearch, OpenSearch Dashboards | Helm v3.Release × 2 |
| `workflow_plane.py` | Workflow plane — Argo Workflows, Argo Events | Helm v4.Chart × 2 |
| `observability_plane.py` | Observability — OpenTelemetry Collector, Jaeger | Helm v4.Chart, Helm v3.Release |
| `flux_gitops.py` | GitOps — Flux CD | Helm v4.Chart |
| `cilium.py` | CNI — Cilium network plugin | Helm v3.Release |
| `link_planes.py` | Cross-plane wiring — connects components that depend on each other | Custom resources |
| `integration_tests.py` | E2E test harness — ~35 tests running as Pulumi dynamic resources | Dynamic providers |

### Helpers (`pulumi/helpers/`)

| File | Purpose | Key Functions |
|------|---------|---------------|
| `dynamic_providers.py` | Custom Pulumi dynamic providers — CRD wait, Helm OCI, kubectl apply, OpenBao secrets | 4 provider classes (~550 lines) |
| `k8s_ops.py` | Kubernetes operations — wait for pods, port-forward, check deployments, health checks | ~700 lines, heavily used by integration_tests |
| `wait.py` | Wait/retry utilities — poll until condition met | Generic retry with backoff |
| `utils.py` | Misc utilities — YAML loading, string helpers | Small utility functions |
| `__init__.py` | Package init | Barrel exports |

### Values (`pulumi/values/`)

| File | Purpose | Returns |
|------|---------|---------|
| `openbao.py` | OpenBao Helm values — includes 46-line postStart bash script with dev seed secrets | `dict` |
| `data_plane.py` | OpenSearch + Dashboards Helm values | `dict` (NOT wired into component) |
| `control_plane.py` | ArgoCD + Dex Helm values | `dict` |
| `workflow_plane.py` | Argo Workflows + Events Helm values | `dict` |
| `observability_plane.py` | OpenTelemetry + Jaeger Helm values | `dict` |
| `flux_gitops.py` | Flux CD Helm values | `dict` |
| `prerequisites.py` | cert-manager, metrics-server, etc. Helm values | `dict` |
| `__init__.py` | Package init | Barrel exports |

### Platforms (`pulumi/platforms/`)

| File | Purpose |
|------|---------|
| `resolver.py` | Platform detection — resolves which platform config to use |
| `k3d.py` | k3d-specific platform configuration |
| `rancher_desktop.py` | Rancher Desktop-specific platform configuration |
| `talos.py` | Talos-specific platform configuration |
| `register_plane.py` | Platform registration utilities |

### Scripts (`pulumi/scripts/`)

| File | Purpose |
|------|---------|
| `openbao_init.py` | OpenBao initialization script — unseal, configure |
| `openbao_setup.py` | OpenBao setup — create policies, secret engines |
| `argocd_setup.py` | ArgoCD setup — configure repos, projects |
| `__init__.py` | Package init |

---

## Issues Identified (15 Actionable)

### P0 — Security (2 issues)

#### Issue 1: Non-dev stacks silently use insecure defaults
- **File**: `config.py:215-233`
- **Severity**: P0 (Security)
- **Description**: When `openbao_root_token` and `opensearch_password` are not configured, the code logs a warning and falls back to hardcoded defaults (`"root"`, `"ThisIsTheOpenSearchPassword1"`). This happens for ALL stacks, including production. Non-dev stacks should FAIL, not silently proceed with insecure defaults.
- **Evidence**: Lines 215-222 (openbao_root_token), lines 226-233 (opensearch_password) both have `pulumi.log.warn()` followed by fallback assignment
- **Fix**: Change the `else` branch (non-dev stacks) from warn-and-fallback to `raise` with clear error message

#### Issue 2: Dev seed secrets not gated behind is_dev_stack
- **File**: `values/openbao.py:24-69`
- **Severity**: P0 (Security)
- **Description**: The OpenBao Helm values `get_values()` function returns a postStart script containing hardcoded dev secrets (vault policies, secret engine seeds) for ALL stacks. These should only be included when running on a dev stack.
- **Evidence**: Lines 24-69 contain a bash f-string with hardcoded secrets that always gets included in Helm values
- **Fix**: Accept `is_dev_stack` parameter, conditionally include seed data

### P1 — Reliability (5 issues)

#### Issue 3: Helm v4.Chart resources missing CustomTimeouts
- **Files**: `components/prerequisites.py`, `components/workflow_plane.py`, `components/flux_gitops.py`
- **Severity**: P1 (Reliability)
- **Description**: All Helm v4.Chart resource calls lack `custom_timeouts`, meaning they use Pulumi's default (10min create, 10min update, 10min delete). Long-running Helm installations (cert-manager CRDs, Flux) can hit these defaults and fail intermittently.
- **Evidence**: `ast_grep_search` for `k8s.helm.v4.Chart(` finds 6+ calls, none with `custom_timeouts`
- **Fix**: Add `custom_timeouts=pulumi.CustomTimeouts(create="10m", update="10m", delete="5m")` to each

#### Issue 4: update() returns dict instead of UpdateResult
- **File**: `helpers/dynamic_providers.py:55,247,317,502`
- **Severity**: P1 (Reliability)
- **Description**: Four `update()` methods in dynamic provider classes return `dict[str, Any]` (via `result.outs`) instead of `pulumi.dynamic.UpdateResult`. This violates the Pulumi ResourceProvider contract and may cause silent failures.
- **Evidence**: LSP diagnostics confirm type errors at all 4 lines. Also confirmed: parameter name `inputs` should be `props` to match base class signature.
- **Fix**: Wrap returns in `UpdateResult(outs=...)`, fix parameter names

#### Issue 5: Bare except / broad Exception handling
- **Files**: `helpers/dynamic_providers.py:~265`, `helpers/k8s_ops.py:~616,~658`
- **Severity**: P1 (Reliability)
- **Description**: Several try/except blocks catch bare `except:` or `except Exception:` without logging, silently swallowing errors. This makes debugging infrastructure failures extremely difficult.
- **Fix**: Narrow to specific exception types (`ApiException`, `CalledProcessError`, `VaultError`), add `pulumi.log.warn()`

#### Issue 6: time.time() vs time.monotonic() inconsistency
- **File**: `helpers/k8s_ops.py:646,648`
- **Severity**: P1 (Reliability)
- **Description**: Timeout calculations use `time.time()` which can be affected by system clock changes (NTP corrections). `time.monotonic()` is the correct choice for elapsed-time calculations.
- **Evidence**: Lines 646 and 648 use `time.time()` while other timeout loops in the same file already use `time.monotonic()`
- **Fix**: Replace `time.time()` with `time.monotonic()` at the identified locations

#### Issue 7: Port-forward process leak on exception
- **Files**: `helpers/dynamic_providers.py:469-494`, `helpers/k8s_ops.py:598-625`
- **Severity**: P1 (Reliability)
- **Description**: Port-forward subprocess creation doesn't use proper cleanup in exception paths. If an exception occurs between process creation and the cleanup code, the subprocess leaks (stays running indefinitely).
- **Fix**: Use try/finally or context manager pattern to ensure `process.terminate()` is always called

### P2 — Consistency (2 issues)

#### Issue 8: values/data_plane.py is dead code / pattern deviation
- **File**: `values/data_plane.py` (entire file), `components/data_plane.py:81-87`
- **Severity**: P2 (Consistency)
- **Description**: Unlike all other components, `data_plane.py` component does NOT call its corresponding `values/data_plane.py`. Instead, Helm values are built inline in the component. This deviates from the established pattern and makes `values/data_plane.py` dead code.
- **Fix**: Wire `values/data_plane.py` into `components/data_plane.py` following the same pattern as other components

#### Issue 9: Missing type hints on get_values() returns
- **Files**: All `values/*.py` files
- **Severity**: P2 (Consistency)
- **Description**: No values file has return type annotations on `get_values()` functions. All return `dict` but none declare it.
- **Fix**: Add `-> dict[str, Any]` return type hints to all `get_values()` functions

### P3 — Cleanup (1 issue)

#### Issue 10: Unused imports + missing TYPE_CHECKING guards
- **Files**: `__main__.py:3-4`, `components/data_plane.py:10`, `components/workflow_plane.py:15`, `components/observability_plane.py:19`
- **Severity**: P3 (Cleanup)
- **Description**: Several files import modules that are only used for type annotations but aren't guarded behind `if TYPE_CHECKING:`. Other files have completely unused imports.
- **Fix**: Remove unused imports, add `from __future__ import annotations` and `TYPE_CHECKING` guards where needed

### E2E — Testing (1 issue)

#### Issue 11: No pytest infrastructure for E2E tests
- **Files**: `pyproject.toml` (no test deps), `tests/` (directory doesn't exist)
- **Severity**: E2E (New capability)
- **Description**: The project has no pytest setup. An integration test harness exists in `components/integration_tests.py` with ~35 tests and reusable `k8s_ops.check_*` functions, but no standard pytest infrastructure to run them independently.
- **Fix**: Add pytest + pytest-timeout to dev dependencies, create `tests/` directory, scaffold E2E tests wrapping existing `check_*` functions

---

## Architecture Observations

### Strengths
- **Typed config**: `InfraConfig` dataclass provides type-safe configuration
- **ComponentResource pattern**: All major components use Pulumi's `ComponentResource` for modularity
- **Dependency chains**: Components declare explicit dependencies via `pulumi.ResourceOptions(depends_on=[...])`
- **Platform abstraction**: `platforms/` directory cleanly separates platform-specific config
- **Values separation**: `values/` files keep Helm values separate from component logic (except data_plane)

### Debt Areas
- **Dynamic providers**: The most complex code with the most issues. 4 provider classes in one 550-line file.
- **k8s_ops.py**: 700+ lines of Kubernetes operations with 197+ pre-existing LSP errors. Heavy shell-out usage.
- **integration_tests.py**: 35+ tests run as dynamic Pulumi resources (unusual pattern). 20+ pre-existing LSP errors.
- **Shell-outs**: Multiple components use `subprocess.run()` for curl, kubectl, docker exec. Works but fragile.

### Pre-existing Issues (NOT in remediation scope)
- `k8s_ops.py`: 197+ LSP errors (pre-existing, mostly type-related)
- `integration_tests.py`: 20+ LSP errors (pre-existing)
- Mixed Helm v3.Release vs v4.Chart (requires separate migration project)
- Shell-outs in workflow_plane, control_plane, observability_plane (working, not worth refactoring)
- Network call during plan phase in control_plane.py:31 (_fetch_yaml at import time)
- Inconsistent `protect=True` usage (requires business decision)
