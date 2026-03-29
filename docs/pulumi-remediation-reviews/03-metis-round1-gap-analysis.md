# Metis Round 1 — Gap Analysis

> **Agent**: Metis
> **Session**: `ses_2c6474a8cffeqHx3hfCk9tseV0`
> **Phase**: Pre-plan generation review
> **Objective**: Identify gaps, missing guardrails, unanswered questions, and edge cases before plan generation

---

## 1. Guardrails Review

### Identified Missing Guardrails
Metis flagged that the initial plan draft lacked explicit "Must NOT do" constraints. These were added:

- **NO resource logical name changes** — would cause URN breakage (destroy + recreate)
- **NO Helm release name changes** — same risk as above
- **NO deployment dependency graph changes** — component ordering must remain identical
- **NO new features, resources, or configuration keys** — remediation only
- **NO unit tests** — user explicitly excluded these
- **NO CrossGuard / Policy-as-Code** — out of scope
- **NO Resource Transformations** — out of scope
- **NO converting plain functions to ComponentResource for aesthetics** — only fix real issues
- **NO extracting the openbao bash script to a template file** — scope creep
- **NO attempting to fix secret serialization in dynamic provider state (P0-4)** — too risky

### Assessment
All guardrails accepted and incorporated into the final plan's "Must NOT Have" section.

---

## 2. Scope Lockdown

### Issues Metis Raised
1. **P0-4 (secret serialization) too risky**: The `root_token` passed as plain string through dynamic provider inputs is stored in Pulumi state unencrypted. Fixing requires structural changes to the dynamic provider pattern. Metis recommended deferring to a separate task.
2. **Embedded bash script extraction is scope creep**: The 46-line bash f-string in `values/openbao.py` should eventually be extracted, but doing so in this remediation risks complex merge conflicts.
3. **Shell-outs in components are working code**: `curl | sed | kubectl apply` patterns in workflow_plane, control_plane, observability_plane are common in IaC. Replacing with pure Python is a separate project.

### Resolution
All 3 items documented as "Known Limitations" in the plan — intentionally NOT fixed.

---

## 3. Open Questions Identified

### Questions Metis Flagged
1. **Which stacks to verify against?** — dev and rancher-desktop (local dev project)
2. **Is root_token="root" intentional?** — Yes, dev-only by design. Fix: escalate to `raise` on non-dev
3. **What to do with values/data_plane.py dead code?** — Wire it into component (consistency fix, not deletion)
4. **Pulumi version constraints?** — `pulumi>=3.0.0,<4.0.0`, `pulumi-kubernetes>=4.0.0,<5.0.0`
5. **Should update() parameter names be fixed too?** — Yes, `inputs` → `props` alongside return type fix

### Resolution
All 5 questions auto-resolved by Prometheus based on codebase evidence. No user input needed.

---

## 4. Acceptance Criteria Review

### Metis Feedback
- Each task MUST have a verification triad: `ruff check` + `ty check` + `pulumi preview` (both stacks)
- QA scenarios must be agent-executable with zero human intervention
- Evidence files must be captured for every scenario
- Pre-commit checks must run before each commit

### Resolution
Verification triad added to every task. All QA scenarios written as agent-executable with specific commands and expected outputs.

---

## 5. Edge Cases Identified

### Cases Metis Flagged
1. **Task 3 (CustomTimeouts)**: Don't blindly add `wait_for_jobs` — that's a v3.Release parameter, not v4.Chart. Audit per-chart instead.
2. **Task 4 (UpdateResult)**: Also fix parameter name `inputs` → `props` to match base class signature, not just return types.
3. **Task 5 (Exception narrowing)**: Must preserve existing control flow — if code currently swallows and continues, keep that behavior but add logging.
4. **Task 7 (Port-forward cleanup)**: Must use try/finally, not context manager, because subprocess doesn't support `with` statement.
5. **Task 11 (E2E tests)**: Tests must wrap EXISTING `k8s_ops.check_*` functions, not reinvent checks from scratch.

### Resolution
All 5 edge cases incorporated into task descriptions in the final plan.

---

## 6. Issue Catalog Refinement

### Before Metis Review
Initial issue count: ~20 raw findings from explore agent

### After Metis Review
Refined to 15 actionable issues by:
- Merging related issues (e.g., "bare except" in two files → single task)
- Deferring risky changes (P0-4 secret serialization)
- Excluding working-but-imperfect code (shell-outs)
- Confirming each remaining issue has file:line evidence

### Final Issue Distribution
| Priority | Count | Tasks |
|----------|-------|-------|
| P0 Security | 2 | Tasks 1-2 |
| P1 Reliability | 5 | Tasks 3-7 |
| P2 Consistency | 2 | Tasks 8-9 |
| P3 Cleanup | 1 | Task 10 |
| E2E Testing | 1 | Task 11 |
| **Total** | **11** | **11 commits** |
