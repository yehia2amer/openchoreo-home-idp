# F3: Architecture Review

Date: 2026-03-29

## Scope

Reviewed the architecture across:
- `pulumi/__main__.py`
- `pulumi/components/data_plane.py`
- `pulumi/components/prerequisites.py`
- `pulumi/components/integration_tests.py`
- `pulumi/components/control_plane.py`
- `pulumi/components/workflow_plane.py`
- `pulumi/components/observability_plane.py`
- `pulumi/components/flux_gitops.py`
- `pulumi/components/link_planes.py`
- `pulumi/components/cilium.py`
- `pulumi/policy/__main__.py`
- `pulumi/values/openbao.py`
- `pulumi/templates/openbao_post_start.sh.tpl`
- `pulumi/config.py`

## Executive Summary

**VERDICT: REJECT**

The overall direction is good: the project now has a clean stage-oriented component structure, a sensible flat top-level orchestration model, a reasonable template layout, and a separate policy pack. However, there are still two architectural correctness gaps: `IntegrationTests` is not ordered behind `FluxGitOps` even though it creates Flux-specific tests, and the CrossGuard pack only partially covers the actual risk surface because it misses most dev-seed cases, ignores `helm.v3.Release`, and defaults to a fail-open dev classification when stack detection fails.

## A. ComponentResource Design (T4-T9)

### What is sound

- **`_child_opts()` helper pattern:** Sound within a component. It consistently applies `parent=self`, carries optional `provider` / `depends_on`, and centralizes the alias rule that matters for URN migration.
- **Alias strategy:** `aliases=[pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)]` is the right architectural move for function → `ComponentResource` migration as long as child logical names and types stay unchanged.
- **Component type names:** `"openchoreo:components:{ClassName}"` is consistent and readable across all nine components. `LinkPlanesComponent` using the type `openchoreo:components:LinkPlanes` is a reasonable collision-avoidance compromise.
- **Thin `deploy()` wrappers:** Sustainable for backward compatibility because they remain thin pass-throughs that just instantiate the component and return `.result`.
- **`ResourceOptions.merge()` usage:** Correct where used. It preserves parent/provider/alias metadata from `_child_opts()` while layering in `custom_timeouts` or replacement settings.
- **Flat top-level hierarchy:** This is the right choice for this codebase. The components represent deployment phases, not deeply nested reusable domains, and a flat layout keeps orchestration obvious while minimizing URN migration complexity.

### What is acceptable but not ideal

- **`self.result` pattern:** Pragmatic and workable for a repo-local Pulumi application, but only partly idiomatic. A more idiomatic Pulumi component would expose properties and call `register_outputs(...)` with real outputs. Here, `self.result` is fine for internal Python-to-Python handoff, but it makes the component abstraction less reusable outside this stack program.
- **`_child_opts()` duplication:** The pattern itself is good, but it is duplicated across all components. That is not a current correctness problem, but it does create drift risk if alias/provider behavior ever needs to change globally.

### Blocking concern

- **Inter-component dependency wiring is incomplete for Flux.** In `pulumi/__main__.py`, `IntegrationTests` depends on control plane, data plane, workflow plane, and optional observability resources, but not on any `FluxGitOps` readiness handle. In `pulumi/components/integration_tests.py`, the component conditionally creates Flux controller and Flux Kustomization tests when Flux is enabled. That means Pulumi can schedule the test resources before Flux installation/reconciliation is complete, which makes the final validation stage architecturally unsound.

## B. CrossGuard PolicyPack Design (T3)

### What is sound

- **Policy choice is directionally right for this repo.** Secrets enforcement, dev-seed leakage detection, namespace hygiene, and Helm timeout discipline all match real risks in this stack.
- **Policy structure is extensible.** Each validator is isolated, constants are grouped at the top, and the split between stack-level and resource-level validation is clear.
- **Enforcement levels are mostly appropriate.** Mandatory for secret leakage and Helm timeout discipline makes sense; advisory for namespace labels is reasonable given the current resource state.

### Architectural concerns

- **URN-based stack detection is only partially robust.** `_extract_stack_name()` is fine for normal Pulumi URNs, but `_is_dev_stack_from_resources()` returns `True` when it cannot determine the stack. That is a fail-open security posture.
- **Policy/data drift already exists.** `_DEV_STACKS` is defined in multiple places (`config.py`, `prerequisites.py`, and `policy/__main__.py`), which increases the chance of environment classification drifting over time.

### Blocking concerns

1. **Dev-seed policy coverage is stale/incomplete.**
   `pulumi/values/openbao.py` currently emits many dev-only `bao kv put secret/...` commands in the dev block, but `pulumi/policy/__main__.py` only scans for two patterns. One of those patterns (`secret/choreo-system-password`) does not match the current template content at all. So the policy does not actually guard the full dev-seed surface it claims to protect.

2. **Helm timeout policy misses a large part of the project.**
   `enforce-helm-timeouts` only validates `kubernetes:helm.sh/v4:Chart`. In the component set I reviewed, the project currently uses both Helm resource models, including **8 `k8s.helm.v3.Release` usages** and **6 `k8s.helm.v4.Chart` usages**. For this project's real risk profile, the mandatory policy misses the majority of chart installs.

## C. Script Template Extraction (T1-T2)

### Assessment

- **`string.Template` is the right choice** for the OpenBao post-start script. It is stdlib, low-complexity, and sufficient for a small number of placeholders.
- **`pulumi/templates/` is a good structure** for extracted shell assets. Using `.sh.tpl` for templated scripts and `.sh` for static scripts is clean and understandable.
- **Path-based loading is appropriate** for a Pulumi repo executed from different working directories. `Path(__file__).resolve().parent.parent / "templates" / ...` is stable for this source-layout project.

### Caveat

- Bash templating always carries `$`-escaping hazards, but the current template already handles this correctly with `$$KUBERNETES_PORT_443_TCP_ADDR`. For this level of templating, the solution is architecturally simple and sufficient.

## D. Overall Project Structure

### What is sound

- The `pulumi/` directory is cleanly partitioned into `components/`, `helpers/`, `values/`, `policy/`, `templates/`, and `scripts/`.
- Component boundaries are understandable for a project of this size: prerequisites, planes, optional infrastructure, GitOps, and tests.
- I did not find direct component-to-component imports. Orchestration remains centralized in `pulumi/__main__.py`, which is a good way to avoid circular component coupling.
- Shared coupling through `OpenChoreoConfig` and a small helper layer is appropriate for a single-stack infrastructure program.

### Minor concern

- `IntegrationTests` exports stack outputs from inside the component. That is workable because the component is only used at the top level, but it does blur the boundary between stack orchestration and component internals.

## Approval Conditions

Approve after these issues are addressed:

1. Add an explicit Flux dependency from `IntegrationTests` to a Flux readiness signal when Flux-backed tests are enabled.
2. Align CrossGuard coverage with the current codebase by expanding dev-seed detection and covering both Helm resource styles used in the stack, or narrow the documented claims to match actual enforcement.
3. Change policy stack detection so an unknown stack classification does not silently downgrade to dev behavior.

## Final Verdict

**REJECT**

Reason: the componentization and template extraction are architecturally sound, and the overall project structure is good. But the missing Flux → integration-test dependency and the partial/fail-open CrossGuard coverage are real architecture gaps, not minor cleanup items.
