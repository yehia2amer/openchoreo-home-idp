# Fix kubectl Missing --kubeconfig Flags & Complete Phase 2 Deployment

## TL;DR

> **Quick Summary**: Fix 5 `kubectl` invocations across 4 files that are missing the `--kubeconfig` flag, causing failures on bare-metal clusters where the default kubeconfig doesn't point to the target cluster. Then re-deploy Phase 2 to complete the OpenChoreo installation.
> 
> **Deliverables**:
> - 3 `subprocess.Popen` calls in `k8s_ops.py` and `dynamic_providers.py` fixed with `--kubeconfig` + `--context` flags
> - 3 shell-string `kubectl apply` commands in `workflow_plane.py` fixed with `--kubeconfig` flag
> - 2 shell-string `kubectl` commands in `control_plane.py` fixed with `--kubeconfig` flag (defensive)
> - Successful Phase 2 `pulumi up` deploying all OpenChoreo workloads
> 
> **Estimated Effort**: Quick
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: T1 → T2 → T3

---

## Context

### Original Request
Phase 2 `pulumi up --stack talos-baremetal --yes` deployed 81/100 resources but failed on `validate-openbao-secrets` because `kubectl port-forward` couldn't reach the cluster — it was called without `--kubeconfig` or `--context` flags. On bare-metal, the default kubeconfig doesn't point to the Talos cluster.

### Investigation Findings
- **Root cause**: `kubeconfig_path` and `context` are passed as parameters but never forwarded to subprocess calls
- **3 subprocess.Popen calls** in helpers: missing `--kubeconfig` and `--context` on `kubectl port-forward`
- **3 shell-string commands** in workflow_plane.py: have `--context` but missing `--kubeconfig` on `kubectl apply`
- **2 shell-string commands** in control_plane.py: same pattern (guarded by `k3d-patch` mode, but fix defensively)
- **Correct pattern exists** in `check_service_http()` at k8s_ops.py:334 — uses both flags

### Metis Review
**Identified Gaps** (addressed):
- workflow_plane.py `kubectl apply` commands also missing `--kubeconfig` — would block re-deployment
- control_plane.py `kubectl` commands missing `--kubeconfig` — dormant but same root cause

---

## Work Objectives

### Core Objective
Fix all `kubectl` subprocess invocations that omit `--kubeconfig` so Phase 2 deploys successfully on bare-metal Talos clusters.

### Concrete Deliverables
- `pulumi/helpers/k8s_ops.py` — 2 port-forward calls fixed
- `pulumi/helpers/dynamic_providers.py` — 1 port-forward call fixed
- `pulumi/components/workflow_plane.py` — 3 kubectl apply commands fixed
- `pulumi/components/control_plane.py` — 2 kubectl commands fixed (defensive)
- Phase 2 fully deployed with all OpenChoreo pods running

### Definition of Done
- [ ] `pulumi up --stack talos-baremetal --yes` completes with 0 errors
- [ ] All OpenChoreo pods Running/Completed (control-plane, data-plane, workflow-plane)
- [ ] No `kubectl` calls anywhere in the codebase that use `--context` without `--kubeconfig`

### Must Have
- `--kubeconfig` flag on EVERY kubectl subprocess call that also uses `--context`
- `os.path.expanduser()` on kubeconfig paths in subprocess calls (matching existing pattern)
- All existing tests still pass after changes

### Must NOT Have (Guardrails)
- DO NOT touch k3d.py, rancher_desktop.py, or any non-baremetal platform files
- DO NOT change the logic or behavior of any function — only add missing flags
- DO NOT modify Helm chart values, namespaces, or any other deployment config
- DO NOT use `create_namespace=True` on Helm releases
- DO NOT use git commit without `--no-gpg-sign`
- DO NOT forget to `git checkout -- .sisyphus/boulder.json` after subagent returns

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (bun test via pulumi/.venv/bin/python -m pytest)
- **Automated tests**: YES (tests-after — verify grep assertions)
- **Framework**: pytest (existing test infrastructure)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — all code fixes in parallel):
├── Task 1: Fix kubectl port-forward calls in k8s_ops.py + dynamic_providers.py [quick]
├── Task 2: Fix kubectl apply calls in workflow_plane.py + control_plane.py [quick]

Wave 2 (After Wave 1 — deploy):
└── Task 3: Re-deploy Phase 2 and verify all pods running [deep]

Wave FINAL (After ALL tasks — verification):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay
```

### Dependency Matrix
- **T1**: None → T3
- **T2**: None → T3
- **T3**: T1, T2 → F1-F4

### Agent Dispatch Summary
- **Wave 1**: 2 tasks — T1 `quick`, T2 `quick`
- **Wave 2**: 1 task — T3 `deep`
- **FINAL**: 4 tasks — F1 `oracle`, F2 `unspecified-high`, F3 `unspecified-high`, F4 `deep`

---

## TODOs

- [x] 1. Fix kubectl port-forward calls in helpers (k8s_ops.py + dynamic_providers.py)

  **What to do**:
  - In `pulumi/helpers/k8s_ops.py`, find the TWO `subprocess.Popen` calls that run `kubectl port-forward pod/...` (around lines 600-602 and 698-700). Both are missing `--kubeconfig` and `--context` flags. Add them following the EXACT pattern from `check_service_http()` at line 334-341 of the same file.
  - In `pulumi/helpers/dynamic_providers.py`, find the ONE `subprocess.Popen` call in `_OpenBaoSecretsProvider.create()` (around lines 474-482). Add `--kubeconfig` and `--context` flags using `inputs["kubeconfig_path"]` and `inputs["context"]` (both already available in the `inputs` dict). Also add `import os` at the function level and use `os.path.expanduser()` on the kubeconfig path.
  - Use `os.path.expanduser(kubeconfig_path)` on all paths (matching the pattern at k8s_ops.py line 327).
  - Run ruff lint and format checks after changes.

  **Must NOT do**:
  - DO NOT change any function signatures — `kubeconfig_path` and `context` are already parameters
  - DO NOT change logic, error handling, or timeouts
  - DO NOT touch k3d.py, rancher_desktop.py, or any non-helper files
  - DO NOT modify check_service_http — it's already correct

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple, targeted edits — adding flags to existing subprocess calls
  - **Skills**: []
    - No special skills needed — straightforward code edit

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Task 3
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL):

  **Pattern References** (existing code to follow):
  - `pulumi/helpers/k8s_ops.py:327-341` — `check_service_http()` is the CORRECT reference pattern. Copy exactly how it uses `os.path.expanduser(kubeconfig_path)`, `--context`, and `--kubeconfig` flags in the Popen call.

  **Files to modify**:
  - `pulumi/helpers/k8s_ops.py:598-605` — First port-forward call (in `check_openbao_secrets` helper). Change `["kubectl", "port-forward", f"pod/{pod_name}", f"{port}:8200", "-n", namespace]` to include `"--kubeconfig", os.path.expanduser(kubeconfig_path), "--context", context` before the `-n` flag.
  - `pulumi/helpers/k8s_ops.py:696-703` — Second port-forward call (in `validate_openbao_secrets`). Same fix.
  - `pulumi/helpers/dynamic_providers.py:472-485` — Third port-forward call (in `_OpenBaoSecretsProvider.create`). Same pattern but use `inputs["kubeconfig_path"]` and `inputs["context"]`.

  **Acceptance Criteria**:

  - [ ] `grep -n 'port-forward.*pod/' pulumi/helpers/k8s_ops.py` → both lines include `--kubeconfig` and `--context`
  - [ ] `grep -n 'port-forward.*pod/' pulumi/helpers/dynamic_providers.py` → line includes `--kubeconfig` and `--context`
  - [ ] `pulumi/.venv/bin/ruff check pulumi/helpers/k8s_ops.py pulumi/helpers/dynamic_providers.py` → no errors
  - [ ] `pulumi/.venv/bin/ruff format --check pulumi/helpers/k8s_ops.py pulumi/helpers/dynamic_providers.py` → no changes needed

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Verify all port-forward calls have --kubeconfig flag
    Tool: Bash (grep)
    Preconditions: Files have been edited
    Steps:
      1. Run: grep -n 'port-forward.*pod/' pulumi/helpers/k8s_ops.py pulumi/helpers/dynamic_providers.py
      2. For each matching line, verify it also contains '--kubeconfig'
      3. Run: grep -c '\-\-kubeconfig' pulumi/helpers/k8s_ops.py — expect at least 3 (1 in check_service_http + 2 new)
      4. Run: grep -c '\-\-kubeconfig' pulumi/helpers/dynamic_providers.py — expect at least 1
    Expected Result: All port-forward subprocess calls include --kubeconfig and --context flags
    Evidence: .sisyphus/evidence/task-1-portforward-flags.txt

  Scenario: Verify ruff passes on modified files
    Tool: Bash
    Preconditions: Files edited
    Steps:
      1. Run: pulumi/.venv/bin/ruff check pulumi/helpers/k8s_ops.py pulumi/helpers/dynamic_providers.py
      2. Run: pulumi/.venv/bin/ruff format --check pulumi/helpers/k8s_ops.py pulumi/helpers/dynamic_providers.py
    Expected Result: Both commands exit 0 with no errors
    Evidence: .sisyphus/evidence/task-1-ruff-check.txt
  ```

  **Commit**: YES (groups with T2)
  - Message: `fix(helpers): add --kubeconfig to all kubectl subprocess calls for bare-metal support`
  - Files: `pulumi/helpers/k8s_ops.py`, `pulumi/helpers/dynamic_providers.py`, `pulumi/components/workflow_plane.py`, `pulumi/components/control_plane.py`
  - Pre-commit: `pulumi/.venv/bin/ruff check pulumi/helpers/ pulumi/components/`

- [x] 2. Fix kubectl apply calls in workflow_plane.py + control_plane.py

  **What to do**:
  - In `pulumi/components/workflow_plane.py`, find the 3 `kubectl apply` shell-string commands (lines 126, 134, 137). Each has `--context {cfg.kubeconfig_context}` but is missing `--kubeconfig {cfg.kubeconfig_path}`. Add `--kubeconfig {cfg.kubeconfig_path}` to each.
  - In `pulumi/components/control_plane.py`, find the 2 `kubectl` shell-string commands in the `k3d-patch` block (lines 314 and 318). Each has `--context {cfg.kubeconfig_context}` but is missing `--kubeconfig {cfg.kubeconfig_path}`. Add `--kubeconfig {cfg.kubeconfig_path}` to each.
  - Run ruff lint and format checks after changes.

  **Must NOT do**:
  - DO NOT change sed patterns, URLs, or any logic — only add the missing flag
  - DO NOT change the k3d-patch guard condition
  - DO NOT touch any other components

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple string interpolation additions
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 3
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL):

  **Files to modify**:
  - `pulumi/components/workflow_plane.py:126` — Change `kubectl apply --context {cfg.kubeconfig_context} -f -` to `kubectl apply --kubeconfig {cfg.kubeconfig_path} --context {cfg.kubeconfig_context} -f -`
  - `pulumi/components/workflow_plane.py:134` — Same change
  - `pulumi/components/workflow_plane.py:137` — Change `kubectl apply --context {cfg.kubeconfig_context} -f {url}` to `kubectl apply --kubeconfig {cfg.kubeconfig_path} --context {cfg.kubeconfig_context} -f {url}`
  - `pulumi/components/control_plane.py:314-315` — Change `kubectl get workflow.openchoreo.dev --all-namespaces -o yaml --context {cfg.kubeconfig_context}` to include `--kubeconfig {cfg.kubeconfig_path}`
  - `pulumi/components/control_plane.py:318` — Same pattern for `kubectl apply`

  **Acceptance Criteria**:

  - [ ] `grep -n 'kubectl.*--context' pulumi/components/workflow_plane.py` → all 3 lines also contain `--kubeconfig`
  - [ ] `grep -n 'kubectl.*--context' pulumi/components/control_plane.py` → all 2 lines also contain `--kubeconfig`
  - [ ] `pulumi/.venv/bin/ruff check pulumi/components/workflow_plane.py pulumi/components/control_plane.py` → no errors
  - [ ] `pulumi/.venv/bin/ruff format --check pulumi/components/workflow_plane.py pulumi/components/control_plane.py` → no changes needed

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Verify all kubectl apply calls have --kubeconfig flag
    Tool: Bash (grep)
    Preconditions: Files have been edited
    Steps:
      1. Run: grep -n 'kubectl.*--context' pulumi/components/workflow_plane.py
      2. Verify all 3 matching lines contain '--kubeconfig'
      3. Run: grep -n 'kubectl.*--context' pulumi/components/control_plane.py
      4. Verify all 2 matching lines contain '--kubeconfig'
    Expected Result: Every kubectl call with --context also has --kubeconfig
    Evidence: .sisyphus/evidence/task-2-kubectl-flags.txt

  Scenario: No kubectl calls with --context but without --kubeconfig anywhere in components/helpers
    Tool: Bash (grep)
    Preconditions: All edits complete
    Steps:
      1. Run: grep -rn '\-\-context' pulumi/helpers/ pulumi/components/ | grep -v '\-\-kubeconfig' | grep -v '.pyc' | grep -v __pycache__
      2. Assert output is empty (no lines match)
    Expected Result: Zero lines — every --context is paired with --kubeconfig
    Evidence: .sisyphus/evidence/task-2-no-orphan-context.txt
  ```

  **Commit**: YES (groups with T1)
  - Message: `fix(helpers): add --kubeconfig to all kubectl subprocess calls for bare-metal support`
  - Files: `pulumi/components/workflow_plane.py`, `pulumi/components/control_plane.py`
  - Pre-commit: `pulumi/.venv/bin/ruff check pulumi/components/`

- [x] 3. Re-deploy Phase 2 and verify all OpenChoreo pods running

  **What to do**:
  - Pre-flight: Verify kubeconfig exists and openbao-0 pod is Running
  - Run `pulumi up --stack talos-baremetal --yes` from `pulumi/` workdir with environment:
    - `PATH="/opt/homebrew/bin:$PATH"`
    - `PULUMI_CONFIG_PASSPHRASE="openchoreo-talos-baremetal"`
  - Wait for completion (timeout: 15 minutes)
  - Verify all pods are Running/Completed
  - Verify OpenChoreo CRDs exist (components, projects, environments, clusterdataplanes, clusterworkflowplanes)
  - Verify control plane services (thunder, backstage, openchoreo-api, controller-manager) have pods
  - Verify data plane agent has pods
  - Verify workflow plane (argo-server) has pods

  **Must NOT do**:
  - DO NOT modify any code — this is deploy-only
  - DO NOT run `pulumi destroy`
  - DO NOT change stack config

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Deployment requires patience, monitoring, and multi-step verification
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (sequential after Wave 1)
  - **Blocks**: F1-F4
  - **Blocked By**: T1, T2

  **References** (CRITICAL):

  **Environment References**:
  - Pulumi binary: `/opt/homebrew/bin/pulumi`
  - Python venv: `pulumi/.venv/bin/python` (workdir: `pulumi/`)
  - PULUMI_CONFIG_PASSPHRASE: `openchoreo-talos-baremetal`
  - Kubeconfig: `pulumi/talos-cluster-baremetal/outputs/kubeconfig`
  - Kubeconfig context: `admin@openchoreo`

  **Acceptance Criteria**:

  - [ ] `pulumi up --stack talos-baremetal --yes` exits with 0 errors
  - [ ] `kubectl get pods -A | grep -v -E 'Running|Completed|NAME'` → empty (all pods healthy)
  - [ ] `kubectl get pods -n openchoreo-control-plane` → shows thunder, backstage, openchoreo-api, controller-manager, kgateway pods
  - [ ] `kubectl get pods -n openchoreo-data-plane` → shows data-plane-agent pod
  - [ ] `kubectl get pods -n openchoreo-workflow-plane` → shows argo-server pod
  - [ ] `kubectl get crds | grep openchoreo` → shows components, projects, environments, etc.

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Phase 2 deployment completes successfully
    Tool: Bash
    Preconditions: T1+T2 committed, openbao-0 pod Running
    Steps:
      1. Run pre-flight: KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig kubectl get pod openbao-0 -n openbao -o jsonpath='{.status.phase}' — expect "Running"
      2. Run: PATH="/opt/homebrew/bin:$PATH" PULUMI_CONFIG_PASSPHRASE="openchoreo-talos-baremetal" pulumi up --stack talos-baremetal --yes (workdir: pulumi/, timeout: 900s)
      3. Check exit code is 0
      4. Run: pulumi stack --stack talos-baremetal — check for "0 errored" or no errors in output
    Expected Result: Deployment completes with 0 errors, remaining resources created
    Failure Indicators: "errored" in output, non-zero exit code, timeout
    Evidence: .sisyphus/evidence/task-3-pulumi-up.txt

  Scenario: All OpenChoreo pods are healthy after deployment
    Tool: Bash
    Preconditions: pulumi up completed successfully
    Steps:
      1. Run: KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig kubectl get pods -A --no-headers
      2. Run: KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig kubectl get pods -A --no-headers | grep -v -E 'Running|Completed'
      3. Assert step 2 output is empty
      4. Run: KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig kubectl get pods -n openchoreo-control-plane --no-headers | wc -l — expect >= 5
      5. Run: KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig kubectl get crds | grep openchoreo | wc -l — expect >= 5
    Expected Result: All pods Running/Completed, control plane has 5+ pods, 5+ OpenChoreo CRDs exist
    Failure Indicators: Pods in CrashLoopBackOff/Pending/Error, missing CRDs, empty namespaces
    Evidence: .sisyphus/evidence/task-3-pod-health.txt

  Scenario: OpenChoreo services are accessible
    Tool: Bash
    Preconditions: All pods running
    Steps:
      1. Run: KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig kubectl get svc -n openchoreo-control-plane --no-headers
      2. Verify thunder, backstage, openchoreo-api services exist
      3. Run: KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig kubectl get clusterissuer — verify all Ready
      4. Run: KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig kubectl get clustersecretstore — verify Ready
    Expected Result: All services exist, ClusterIssuers Ready, ClusterSecretStore Ready
    Evidence: .sisyphus/evidence/task-3-services.txt
  ```

  **Commit**: NO (deploy-only, no code changes)

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (grep for `--kubeconfig` in all kubectl calls). For each "Must NOT Have": search codebase for forbidden patterns. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run ruff lint (`pulumi/.venv/bin/ruff check pulumi/`), ruff format check (`pulumi/.venv/bin/ruff format --check pulumi/`), and existing tests (`pulumi/.venv/bin/python -m pytest pulumi/tests/ -v`). Check for unused imports, style violations.
  Output: `Lint [PASS/FAIL] | Format [PASS/FAIL] | Tests [N pass/N fail] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Verify all OpenChoreo pods running: `KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig kubectl get pods -A`. Check no non-Running/non-Completed pods. Verify ClusterIssuers Ready. Verify ClusterSecretStore Ready.
  Output: `Pods [N/N healthy] | ClusterIssuers [READY] | ClusterSecretStore [READY] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  Verify ONLY kubectl flag additions were made. No logic changes. No config changes. No new files beyond evidence. Check git diff for unexpected changes.
  Output: `Files Changed [N] | Only Flag Additions [YES/NO] | VERDICT`

---

## Commit Strategy

- **Commit 1** (after T1+T2): `fix(helpers): add --kubeconfig to all kubectl subprocess calls for bare-metal support` — helpers/k8s_ops.py, helpers/dynamic_providers.py, components/workflow_plane.py, components/control_plane.py

---

## Success Criteria

### Verification Commands
```bash
# All kubectl calls with --context also have --kubeconfig
grep -rn -- '--context' pulumi/helpers/ pulumi/components/ | grep -v '--kubeconfig'  # Expected: empty (no matches)

# Phase 2 deployment
PATH="/opt/homebrew/bin:$PATH" PULUMI_CONFIG_PASSPHRASE="openchoreo-talos-baremetal" pulumi up --stack talos-baremetal --yes  # Expected: 0 errors

# All pods healthy
KUBECONFIG=pulumi/talos-cluster-baremetal/outputs/kubeconfig kubectl get pods -A | grep -v -E 'Running|Completed|NAME'  # Expected: empty
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
- [ ] Phase 2 deployment complete with 0 errors
- [ ] All OpenChoreo workloads running
