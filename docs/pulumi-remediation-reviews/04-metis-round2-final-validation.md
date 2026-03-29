# Metis Round 2 — Final Validation

> **Agent**: Metis
> **Session**: `ses_2c619433bffeN40ei3hnLk5O1Q`
> **Phase**: Post-plan generation validation
> **Objective**: Final check on plan completeness, consistency, and readiness for execution

---

## 1. Issue Catalog Validation

### Confirmed: 15 → 11 Tasks (no gaps)
Metis confirmed that the 15 issues are correctly mapped to 11 tasks:
- Some tasks address multiple related issues (e.g., Task 5 covers exception narrowing in both `dynamic_providers.py` and `k8s_ops.py`)
- No issues were dropped or forgotten in the mapping

### Verified File References
Every file:line reference in the plan was cross-checked against the actual codebase:
- `config.py:215-233` — confirmed warn-and-fallback pattern exists
- `values/openbao.py:24-69` — confirmed hardcoded secrets in postStart script
- `dynamic_providers.py:55,247,317,502` — confirmed `update()` returns dict
- `k8s_ops.py:646,648` — confirmed `time.time()` usage
- All other references verified

---

## 2. Auto-Resolved Questions (Validated)

Metis confirmed all auto-resolutions from Prometheus were correct:

| Question | Resolution | Evidence |
|----------|-----------|----------|
| Verification stacks | `dev` + `rancher-desktop` | Both exist in project (`Pulumi.rancher-desktop.yaml`) |
| root_token="root" intent | Dev-only by design | `is_dev_stack` check at config.py:210 |
| values/data_plane.py strategy | Wire, don't delete | Maintains pattern consistency across all components |
| Pulumi versions | `>=3.0.0,<4.0.0` | Confirmed in `pyproject.toml` |
| update() param names | Fix alongside return types | LSP diagnostics confirm mismatch |

---

## 3. Commit Ordering Validation

### Verified Dependency Chain
```
Task 1 (config.py) → Task 2 (values/openbao.py + control_plane.py)
  → Tasks 3-7 (parallel, P1 reliability)
    → Tasks 8-10 (parallel, P2/P3 consistency + cleanup)
      → Task 11 (E2E tests)
        → F1-F4 (final verification)
```

### Conflict Analysis
- **Task 4 → Task 5**: Both touch `dynamic_providers.py` — Task 5 must run after Task 4 to avoid merge conflicts. Correctly ordered in Wave 2 dependency matrix.
- **Task 5 → Task 7**: Task 7 (port-forward cleanup) depends on Task 5 (exception narrowing) because the cleanup changes interact with exception handling. Correctly ordered.
- **Tasks 8, 9, 10**: All touch different files — safe to run in parallel. Verified no file overlap.

---

## 4. Verification Triad Compliance

### Confirmed: Every Task Has Full Triad
Each of the 11 tasks includes:
1. `uv run ruff check pulumi/` — static lint
2. `uv run ty check` — type checking
3. `cd pulumi && pulumi preview -s dev` — IaC correctness (dev stack)
4. `cd pulumi && pulumi preview -s rancher-desktop` — IaC correctness (rancher stack)

### Pre-commit Enforcement
Every commit message includes `Pre-commit: verification triad` notation, ensuring the executing agent runs all 4 checks before committing.

---

## 5. E2E Test Directives (Validated)

### Confirmed Requirements
- **E2E ONLY** — no unit tests (user directive)
- **pytest + pytest-timeout** — test framework choice
- **Wrap existing functions** — use `k8s_ops.check_*` functions, don't reinvent
- **Minimum 5 tests** — covering deployment health, pod status, service availability
- **Mark with `@pytest.mark.e2e`** — for selective test execution
- **Timeout 120s per test** — infrastructure tests can be slow

### Test Infrastructure Plan (Task 11)
1. Add `pytest>=7.0.0` and `pytest-timeout>=2.0.0` to `pyproject.toml` dev dependencies
2. Create `pulumi/tests/` directory
3. Create `pulumi/tests/conftest.py` with K8s client setup
4. Create `pulumi/tests/test_e2e_infrastructure.py` with 5+ tests
5. Configure pytest in `pyproject.toml` with `[tool.pytest.ini_options]`

---

## 6. Known Limitations (Validated)

### Confirmed 6 Out-of-Scope Items
1. P0-4: Secret serialization in dynamic provider state — **too risky**
2. Embedded bash script in values/openbao.py — **scope creep**
3. Shell-outs in 3 component files — **working code, separate project**
4. Network call during plan phase (control_plane.py:31) — **requires lazy loading**
5. Mixed Helm v3.Release vs v4.Chart — **requires migration project**
6. Inconsistent protect=True — **requires business decision**

### Metis Verdict
All limitations are correctly documented, reasonably deferred, and do not block the current remediation scope.

---

## 7. Final Readiness Assessment

### Metis Checklist
| Item | Status |
|------|--------|
| All 15 issues mapped to tasks | ✅ |
| All file:line references verified | ✅ |
| No critical ambiguities remaining | ✅ |
| Guardrails comprehensive | ✅ |
| Verification triad per commit | ✅ |
| E2E-only directive enforced | ✅ |
| Known limitations documented | ✅ |
| Commit ordering valid | ✅ |
| Wave parallelization correct | ✅ |
| No user decisions pending | ✅ |

### Verdict: READY FOR EXECUTION
The plan is complete and validated. Proceed to `/start-work`.
