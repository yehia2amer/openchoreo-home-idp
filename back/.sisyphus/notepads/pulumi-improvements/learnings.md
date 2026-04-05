# Learnings — Pulumi Improvements

## 2026-03-29 Research Phase
- Pulumi passphrase is `openchoreo` — use `PULUMI_CONFIG_PASSPHRASE=openchoreo` for all preview commands
- Two stacks: `dev` and `rancher-desktop`
- `is_dev_stack` list: `("dev", "rancher-desktop", "local", "test")`
- User wants E2E tests only, no unit tests
- Save reviews to `docs/pulumi-remediation-reviews/`
- All 9 component modules use plain `deploy()` functions + `*Result` dataclasses
- Zero ComponentResource, zero PolicyPack, zero template files currently exist
- ComponentResource conversion requires `aliases` to preserve URNs (critical)
- Project name is `openchoreo` (in Pulumi.yaml)
- OpenBao post-start script now lives in `pulumi/templates/openbao_post_start.sh.tpl` and is loaded with stdlib `string.Template`.
- `$$` in the template is required to preserve literal shell `$KUBERNETES_PORT_443_TCP_ADDR` during substitution.

## 2026-03-29 k3d Cilium entrypoint extraction
- Moved the static Cilium k3d entrypoint script into pulumi/templates/k3d_entrypoint_cilium.sh with no template placeholders.
- bootstrap_k3d.py now reads the script from PULUMI_DIR / "templates" before writing the temp entrypoint file.

## 2026-03-29 T3: CrossGuard PolicyPack
- Created `pulumi/policy/` with `PulumiPolicy.yaml`, `__main__.py`, `requirements.txt`
- PolicyPacks run in their own isolated virtualenv — LSP can't resolve `pulumi_policy` from the main project (expected)
- `pulumi_policy` SDK: `StackValidationArgs.resources` returns `List[PolicyResource]` with `.resource_type`, `.props`, `.urn`, `.name`, `.opts`
- `ResourceValidationArgs` has `.resource_type`, `.props`, `.opts` (with `.custom_timeouts`), `.urn`, `.name`
- `PolicyCustomTimeouts` exposes `.create_seconds`, `.update_seconds`, `.delete_seconds`
- URN format: `urn:pulumi:{stack}::{project}::{type}::{name}` — stack extractable from URN
- Insecure defaults found in config.py:212-227: `openbao_root_token="root"`, `opensearch_password="ThisIsTheOpenSearchPassword1"`
- Dev seed patterns: `"bao kv put secret/choreo-system-password"`, `"bao kv put secret/opensearch-password"`
- Helm Chart resource type: `kubernetes:helm.sh/v4:Chart`; K8s Namespace: `kubernetes:core/v1:Namespace`
- Added `pulumi-policy>=1.0.0` to dev dependency group in `pulumi/pyproject.toml`
- Invoke with: `pulumi preview --policy-pack ./policy` or `pulumi up --policy-pack ./policy`
- Commit created: `05df40b` with the requested policy pack files only; unrelated workspace files were left untouched.

## 2026-03-29 T4: Prerequisites ComponentResource conversion
- Converted `pulumi/components/prerequisites.py` from function-only deployment to `class Prerequisites(pulumi.ComponentResource)` while keeping `PrerequisitesResult` unchanged.
- Added `_child_opts()` helper to enforce alias-preserving reparenting for every child resource with:
  - `parent=self`
  - `aliases=[pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)]`
- Applied `_child_opts()` to all 21 resource creation sites in prerequisites to preserve existing URNs during tree restructure.
- Preserved backward compatibility by keeping `deploy()` as a thin wrapper returning `Prerequisites("prerequisites", ...).result`.
- Updated `pulumi/__main__.py` Step 1 to instantiate `Prerequisites` and then assign `prereqs = prereqs_component.result`, preserving downstream usage.
- `pulumi preview --stack dev --diff` execution in this environment reached stack graph creation but failed against unreachable Kubernetes API (`0.0.0.0:6550`), so zero create/delete validation must be confirmed in a reachable cluster environment.

## 2026-03-29 T6: DataPlane ComponentResource conversion
- Converted `pulumi/components/data_plane.py` from function-only deployment into `class DataPlane(pulumi.ComponentResource)` with type `openchoreo:components:DataPlane`.
- Kept `DataPlaneResult` unchanged and retained `deploy()` as a thin backward-compatible wrapper returning `DataPlane(...).result`.
- Added `_child_opts()` using `parent=self` and `aliases=[pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)]` and applied it to all Data Plane child resources.
- Updated helper integrations: `copy_ca(..., opts=self._child_opts(...))`, `register_plane(..., opts=self._child_opts(...))`, and `_allow_gateway_ingress(..., opts=...)` so ingress policy is also reparented.
- For Helm release options, used `pulumi.ResourceOptions.merge(self._child_opts(...), ResourceOptions(custom_timeouts=...))` to preserve timeout behavior while adding parent/alias metadata.
- Updated `pulumi/__main__.py` Step 3 to instantiate `DataPlane` component directly and read `.result` to match the newer component pattern used by prerequisites/control-plane.

## 2026-03-29 T7: WorkflowPlane ComponentResource conversion
- Converted `pulumi/components/workflow_plane.py` from `deploy()` to `class WorkflowPlane(pulumi.ComponentResource)` with type `openchoreo:components:WorkflowPlane`.
- Added `_child_opts()` exactly matching the DataPlane pattern and applied it to all 6 child creation sites to enforce `parent=self` and `aliases=[pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)]`.
- Kept `WorkflowPlaneResult` unchanged and retained a thin backward-compatible `deploy()` wrapper returning `WorkflowPlane("workflow-plane", ...).result`.
- Used `pulumi.ResourceOptions.merge()` at both Helm sites to preserve existing custom timeouts while adding parent+alias metadata.
- Updated `pulumi/__main__.py` Step 4 to instantiate `WorkflowPlane(...)` and then assign `wp = wp_component.result`.

## 2026-03-29 T8: ObservabilityPlane ComponentResource conversion
- Converted `pulumi/components/observability_plane.py` from `deploy()` to `class ObservabilityPlane(pulumi.ComponentResource)` with type `openchoreo:components:ObservabilityPlane`.
- Added `_child_opts()` matching the established pattern and applied it to all 11 observability child creation sites with `parent=self` and `aliases=[pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)]`.
- For all Helm releases that had `custom_timeouts`, used `pulumi.ResourceOptions.merge(self._child_opts(...), pulumi.ResourceOptions(custom_timeouts=...))` to preserve timeout behavior while adding parent/alias metadata.
- Kept `ObservabilityPlaneResult` unchanged and retained a thin backward-compatible `deploy()` wrapper returning `ObservabilityPlane("observability-plane", ...).result`.
- Updated `pulumi/__main__.py` Step 5 to instantiate `ObservabilityPlane(...)` and assign `obs = obs_component.result`.

## 2026-03-29 T9: Remaining ComponentResource conversions
- Converted remaining modules to `ComponentResource` classes and retained thin `deploy()` wrappers for backward compatibility.
- Resource-site conversions in this task:
  - `cilium.py`: 2 sites (`bpf-mount-fix` Job helper via passed opts, `cilium` Helm Chart with merged custom timeout)
  - `flux_gitops.py`: 8 sites (ConfigGroup, 5 CustomResources, 2 dynamic waits)
  - `link_planes.py`: 1 site (dynamic `LinkPlanes` resource)
  - `integration_tests.py`: ~40 IntegrationTest dynamic resources via shared `base_opts = self._child_opts(depends_on=depends)`
- Edge cases handled:
  - Dynamic providers (`WaitDeployments`, `WaitCustomResourceCondition`, `LinkPlanes`, `IntegrationTest`) were wired with `_child_opts(depends_on=...)` only (no provider injection).
  - `cilium` preserved timeout semantics by merging `_child_opts(...)` with `custom_timeouts` for both the BPF fix Job and Helm chart.
  - `integration_tests` kept `pulumi.export()` calls inside the component initializer and reparented all generated tests through a single base opts object.
- Naming collision resolution:
  - Kept the dynamic provider import named `LinkPlanes` unchanged.
  - Introduced component class name `LinkPlanesComponent` with resource type `openchoreo:components:LinkPlanes` to avoid symbol collision while preserving component type naming.

## 2026-03-29 F4: Pulumi preview integration test
- `pulumi preview --stack dev` reached graph evaluation and failed at Kubernetes API schema fetch (`https://0.0.0.0:6550/openapi/v2` connection refused), which is expected when local k3d/rancher-desktop cluster is down.
- No Python import/syntax failures were observed in preview output before the Kubernetes connectivity failure.
- `python3 -m compileall -q components/ policy/ values/ scripts/ templates/ __main__.py` returned no output and no errors.
- `pulumi preview --stack dev --policy-pack ./policy` successfully loaded `openchoreo-policy@v0.0.1` before hitting the same expected Kubernetes connectivity failure.
- In this environment, alias migration cannot be conclusively validated end-to-end without a reachable cluster and existing state; preview showed `+ 10 to create` and no deletes before failure.


## 2026-03-29 F1: Code quality review findings
- ComponentResource migration pattern is consistently applied across the 9 reviewed component modules: `_child_opts()` includes `parent=self` plus `aliases=[pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)]`, dynamic providers avoid `provider=`, and merged options preserve custom timeouts/replacement flags.
- The most important defects are in verification/policy alignment rather than the ComponentResource wrapping itself.
- Flux E2E tests must use the actual Kustomization names created by `flux_gitops.py`: `namespaces`, `platform-shared`, `oc-demo-platform`, `oc-demo-projects`.
- External Secrets checks should be standardized on `external-secrets.io/v1` to match the created resources and existing prerequisite readiness waiter.
- The `block-dev-seeds-on-prod` policy must be kept in sync with the current OpenBao dev seed commands; stale pattern lists silently weaken enforcement.


## 2026-03-29 — F2 security review learnings
- `string.Template` is safer than raw f-strings for externalized bash templates, but it does not provide shell escaping. Treat substituted values as shell-sensitive unless they are explicitly quoted/escaped for shell context.
- CrossGuard stack policies should fail closed. `assume dev if stack cannot be determined` is not a safe default for prod enforcement.
- The ComponentResource alias pattern (`parent=self` + alias to root stack) did not introduce a new authz issue by itself; the meaningful risk lives in the resource payloads and command execution paths, not the wrapper class.

## 2026-03-29 F3: Architecture Review
- Reviewed `pulumi/__main__.py`, all 9 component modules, `pulumi/policy/__main__.py`, `pulumi/values/openbao.py`, and the extracted OpenBao template.
- No direct component-to-component imports were found; orchestration remains centralized in `pulumi/__main__.py`.
- The flat root-level component hierarchy, `ROOT_STACK_RESOURCE` alias migration strategy, `pulumi/templates/` layout, and Path-based template loading are architecturally sound.
- `self.result` is pragmatic for this repo-local Pulumi program, but less idiomatic than exposing component properties via `register_outputs(...)`.
