## Openbao Portforward Fix — Learnings

(Initialized — no learnings yet)

- Added `--kubeconfig {cfg.kubeconfig_path}` before `--context` for every affected kubectl shell string to keep template patching bound to the intended config.
- Verified the targeted Pulumi files stayed formatter-clean and ruff-clean after the flag-only change.

- OpenBao port-forward subprocess calls now follow the existing service helper pattern by expanding `kubeconfig_path` with `os.path.expanduser()` and passing both `--kubeconfig` and `--context`.
- `pulumi/.venv/bin/ruff check` and `ruff format --check` pass on the two edited helper files.
- Pyright still reports pre-existing environment/import issues in these files, but the edited port-forward call sites are updated correctly.
- Changed `registry.py` and `workflow_plane.py` service types from `LoadBalancer` to `ClusterIP` for bare-metal compatibility.
- Verified `ruff check`, `ruff format --check`, and LSP diagnostics stayed clean after the change.

- `prerequisites.py` needed to mirror `config.py`'s dev-stack tuple so `talos-baremetal` gets fake OpenBao secrets during init.
- `validate-openbao-secrets` now skips GitHub PAT secret validation unless `github_pat` is present or the stack is one of the dev stacks that synthesize fake tokens.
- `pulumi/.venv/bin/ruff check pulumi/components/prerequisites.py` passed after the targeted fix.

## [2026-04-01T01:20:08Z] Task: T3 — Phase 2 Deployment
- Re-ran `pulumi up --stack talos-baremetal --yes` with the fixed kubeconfig-aware kubectl calls.
- Deployment still fails at `validate-openbao-secrets` (exit code 1), but failure cause changed from kubeconfig/context issue to missing OpenBao secrets.
- Blocking errors: `secret/git-token: does not exist` and `secret/gitops-token: does not exist`.
- Because `pulumi up` failed, pod/CRD/service verification steps were not executed per task rules.
- Evidence captured in `.sisyphus/evidence/task-3-pulumi-up.txt`.

## [2026-04-01T01:38:43Z] Task: T3 — Phase 2 Deployment Retry
- Re-ran `pulumi up --stack talos-baremetal --yes` after commit `3e1a24a`.
- Pulumi updated `openbao` StatefulSet (`~ 1 updated`) but deployment still failed at `validate-openbao-secrets`.
- Blocking errors remain unchanged: `secret/git-token: does not exist` and `secret/gitops-token: does not exist`.
- Captured retry evidence in `.sisyphus/evidence/task-3-pulumi-up.txt` (overwritten) with `EXIT_CODE:1`.
- Collected post-run cluster snapshots:
  - `.sisyphus/evidence/task-3-pod-health.txt`
  - `.sisyphus/evidence/task-3-services.txt`
- Current OpenChoreo pod state remains partial: only `kgateway` exists in `openchoreo-control-plane`; no pods in `openchoreo-data-plane` or `openchoreo-workflow-plane`.

## [2026-04-01T00:00:00Z] Task: TLS Gateway Values Fix
- Added conditional `gateway.tls.hostname` and `gateway.tls.certificateRefs` to both control-plane and data-plane Helm value builders so TLS-enabled releases include real hostnames and cert refs.
- Passed `domain_base` through the data-plane values builder call site to keep the hostname derivation consistent with the stack config.
- Ruff lint and format checks passed on `pulumi/values/control_plane.py`, `pulumi/values/data_plane.py`, and `pulumi/components/data_plane.py`.
## 2026-04-01
- Talos clusters enforcing PodSecurity baseline require explicit namespace labels for workloads using AppArmor `Unconfined` annotations.
- Use the same three-label privileged pattern (`enforce`, `audit`, `warn`) consistently across OpenChoreo namespaces; no extra imports or logic changes were needed.

- Updated the Plane Registration E2E checks to assert `condition_type="Created"` for ClusterDataPlane, ClusterWorkflowPlane, and ClusterObservabilityPlane because the OpenChoreo v1.0 controller-manager sets `Created` only and never emits `Ready` for these CRs.
- Verified `pulumi/.venv/bin/ruff check pulumi/components/integration_tests.py` and `pulumi/.venv/bin/ruff format --check pulumi/components/integration_tests.py` both pass after the test-only change.
