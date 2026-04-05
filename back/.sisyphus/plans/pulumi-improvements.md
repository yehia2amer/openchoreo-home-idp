# Pulumi Improvements Plan — Script Extraction, CrossGuard, ComponentResource

> **Project**: openchoreo-home-idp
> **Created**: 2026-03-29
> **Status**: Complete
> **Passphrase**: `PULUMI_CONFIG_PASSPHRASE=openchoreo`
> **Stacks**: `dev`, `rancher-desktop`

---

## Overview

Three improvements to the OpenChoreo Pulumi IaC codebase, ordered by risk (lowest first):

1. **Phase A — Script Extraction** (LOW RISK): Extract inline bash scripts to external template files
2. **Phase B — CrossGuard PolicyPack** (LOW RISK, additive): Add Pulumi's native policy-as-code framework
3. **Phase C — ComponentResource Conversion** (HIGH RISK): Refactor deploy() functions to ComponentResource classes

---

## TODOs

### Phase A — Script Extraction

- [x] **T1: Create templates directory and extract OpenBao post-start script**
  - Create `pulumi/templates/` directory
  - Extract the 48-line bash script from `pulumi/values/openbao.py:37-86` to `pulumi/templates/openbao_post_start.sh.tpl`
  - Use `string.Template` for variable interpolation (`$token`, `$os_user`, `$os_pass`, conditional `$dev_secrets_block`)
  - Update `_post_start_script()` in `openbao.py` to load from template file using `Path(__file__).resolve().parent.parent / "templates" / "openbao_post_start.sh.tpl"`
  - Keep `_post_start_script()` function signature unchanged (public API preserved)
  - **Files created**: `pulumi/templates/openbao_post_start.sh.tpl`
  - **Files modified**: `pulumi/values/openbao.py`
  - **Verification**: `cd pulumi && PULUMI_CONFIG_PASSPHRASE=openchoreo pulumi preview --stack dev 2>&1 | tail -20` exits cleanly
  - **Parallelizable with**: Nothing (first task)

- [x] **T2: Extract k3d entrypoint Cilium script from bootstrap_k3d.py**
  - Extract the 10-line static `K3D_ENTRYPOINT_CILIUM` script from `pulumi/scripts/bootstrap_k3d.py:35-45` to `pulumi/templates/k3d_entrypoint_cilium.sh`
  - This is a **static script** (no interpolation needed) — just move the string constant to a file
  - Update `bootstrap_k3d.py` to load from `PULUMI_DIR / "templates" / "k3d_entrypoint_cilium.sh"` using `Path.read_text()`
  - Remove the `K3D_ENTRYPOINT_CILIUM` string constant
  - **Files created**: `pulumi/templates/k3d_entrypoint_cilium.sh`
  - **Files modified**: `pulumi/scripts/bootstrap_k3d.py`
  - **Verification**: `python -c "from pathlib import Path; exec(open('pulumi/scripts/bootstrap_k3d.py').read().split('def main')[0]); print('OK')"` — module-level imports parse OK
  - **Parallelizable with**: T1

### Phase B — CrossGuard PolicyPack

- [x] **T3: Create CrossGuard PolicyPack with policy enforcement**
  - Create `pulumi/policy/` directory
  - Create `pulumi/policy/PulumiPolicy.yaml` with `name: openchoreo-policy` and `runtime: python`
  - Create `pulumi/policy/requirements.txt` with `pulumi-policy>=1.0.0`
  - Create `pulumi/policy/__main__.py` with the following policies:
    1. **`require-secrets-on-prod`** — `StackValidationPolicy`: Verify that non-dev stacks have required secrets configured (mirrors `config.py:212-227` logic but as a policy)
    2. **`block-dev-seeds-on-prod`** — `StackValidationPolicy`: Verify that dev-only seed secrets (OpenBao kv puts) are not present in production resource config
    3. **`enforce-resource-labels`** — `ResourceValidationPolicy`: Ensure all Kubernetes Namespace resources have `openchoreo.dev` labels
    4. **`enforce-helm-timeouts`** — `ResourceValidationPolicy`: Ensure all Helm charts specify `timeout` in their `CustomTimeouts`
  - Add `pulumi-policy` to `pyproject.toml` dev dependencies (NOT main deps — PolicyPack is a separate program)
  - **Files created**: `pulumi/policy/PulumiPolicy.yaml`, `pulumi/policy/__main__.py`, `pulumi/policy/requirements.txt`
  - **Files modified**: `pulumi/pyproject.toml`
  - **Verification**: `cd pulumi && PULUMI_CONFIG_PASSPHRASE=openchoreo pulumi preview --stack dev --policy-pack ./policy 2>&1 | tail -30` runs policies without violations
  - **Parallelizable with**: T1, T2

### Phase C — ComponentResource Conversion

- [x] **T4: Convert prerequisites.py to ComponentResource**
  - Convert `deploy()` function to `class Prerequisites(pulumi.ComponentResource)` with type `"openchoreo:components:Prerequisites"`
  - Move all resources from `deploy()` into `__init__()` with `parent=self` on each child resource
  - Add `aliases=[pulumi.Alias(parent=pulumi.rootStackResource)]` to every child resource to preserve URNs
  - Expose results as `self.result` attribute (type `PrerequisitesResult`)
  - Update `__main__.py` line 54-58: `prereqs = Prerequisites("prerequisites", cfg=cfg, k8s_provider=k8s_provider, extra_depends=[...])` then `prereqs.result`
  - Keep `PrerequisitesResult` dataclass unchanged
  - **Files modified**: `pulumi/components/prerequisites.py`, `pulumi/__main__.py`
  - **Verification**: `cd pulumi && PULUMI_CONFIG_PASSPHRASE=openchoreo pulumi preview --stack dev --diff 2>&1 | grep -E '(create|delete|replace|update|same)' | head -20` shows zero create/delete (all same or update)
  - **Parallelizable with**: Nothing (must be first ComponentResource; __main__.py changes are sequential)

- [x] **T5: Convert control_plane.py to ComponentResource**
  - Convert `deploy()` function to `class ControlPlane(pulumi.ComponentResource)` with type `"openchoreo:components:ControlPlane"`
  - All child resources get `parent=self` + `aliases=[pulumi.Alias(parent=pulumi.rootStackResource)]`
  - Expose `self.result` as `ControlPlaneResult`
  - Update `__main__.py` line 61-65
  - **Files modified**: `pulumi/components/control_plane.py`, `pulumi/__main__.py`
  - **Verification**: `pulumi preview --stack dev --diff` shows zero create/delete
  - **Parallelizable with**: Nothing (sequential — depends on T4 __main__.py changes)

- [x] **T6: Convert data_plane.py to ComponentResource**
  - Convert `deploy()` to `class DataPlane(pulumi.ComponentResource)` with type `"openchoreo:components:DataPlane"`
  - Same alias pattern for all child resources
  - Update `__main__.py` line 68
  - **Files modified**: `pulumi/components/data_plane.py`, `pulumi/__main__.py`
  - **Verification**: `pulumi preview --stack dev --diff` shows zero create/delete
  - **Parallelizable with**: Nothing (sequential)

- [x] **T7: Convert workflow_plane.py to ComponentResource**
  - Convert `deploy()` to `class WorkflowPlane(pulumi.ComponentResource)` with type `"openchoreo:components:WorkflowPlane"`
  - Same alias pattern for all child resources
  - Update `__main__.py` line 71
  - **Files modified**: `pulumi/components/workflow_plane.py`, `pulumi/__main__.py`
  - **Verification**: `pulumi preview --stack dev --diff` shows zero create/delete
  - **Parallelizable with**: Nothing (sequential)

- [x] **T8: Convert observability_plane.py to ComponentResource**
  - Convert `deploy()` to `class ObservabilityPlane(pulumi.ComponentResource)` with type `"openchoreo:components:ObservabilityPlane"`
  - Same alias pattern for all child resources
  - Update `__main__.py` lines 75-76
  - **Files modified**: `pulumi/components/observability_plane.py`, `pulumi/__main__.py`
  - **Verification**: `pulumi preview --stack dev --diff` shows zero create/delete
  - **Parallelizable with**: Nothing (sequential)

- [x] **T9: Convert remaining components (cilium, flux_gitops, link_planes, integration_tests)**
  - Convert `cilium.py` deploy() → `class Cilium(pulumi.ComponentResource)` type `"openchoreo:components:Cilium"`
  - Convert `flux_gitops.py` deploy() → `class FluxGitOps(pulumi.ComponentResource)` type `"openchoreo:components:FluxGitOps"`
  - Convert `link_planes.py` deploy() → `class LinkPlanes(pulumi.ComponentResource)` type `"openchoreo:components:LinkPlanes"`
  - Convert `integration_tests.py` deploy() → `class IntegrationTests(pulumi.ComponentResource)` type `"openchoreo:components:IntegrationTests"`
  - All child resources get `parent=self` + `aliases=[pulumi.Alias(parent=pulumi.rootStackResource)]`
  - Update `__main__.py` for all four (lines 42-51, 79-89, 92-95)
  - **Files modified**: `pulumi/components/cilium.py`, `pulumi/components/flux_gitops.py`, `pulumi/components/link_planes.py`, `pulumi/components/integration_tests.py`, `pulumi/__main__.py`
  - **Verification**: `pulumi preview --stack dev --diff` shows zero create/delete
  - **Parallelizable with**: Nothing (depends on T4-T8 __main__.py state)

### Final Verification Wave

- [x] **F1: Code Quality Review** — Oracle agent reviews all changes for correctness, patterns, and best practices
- [x] **F2: Security Review** — Oracle agent reviews for security issues (policy bypass, template injection, etc.)
- [x] **F3: Architecture Review** — Oracle agent reviews ComponentResource design, alias strategy, and overall structure
- [x] **F4: Pulumi Preview Integration Test** — Run `pulumi preview --stack dev` to verify zero unexpected changes

---

## Conventions

- **Template files**: Use `.sh.tpl` extension for bash templates with placeholders, `.sh` for static scripts
- **Template loading**: Use `string.Template` for variable substitution (not f-strings) in template files
- **ComponentResource type format**: `"openchoreo:components:{ClassName}"`
- **Alias pattern**: Every child resource gets `aliases=[pulumi.Alias(parent=pulumi.rootStackResource)]`
- **Result exposure**: ComponentResource classes expose results via `self.result` property
- **PolicyPack**: Separate `pulumi/policy/` directory with its own `requirements.txt` (standard Pulumi convention)

---

## Risk Mitigation

### ComponentResource URN Changes
The most dangerous change. When wrapping resources in a ComponentResource, Pulumi changes their URN from:
```
urn:pulumi:dev::openchoreo::kubernetes:core/v1:Namespace::prereq-ns
```
to:
```
urn:pulumi:dev::openchoreo::openchoreo:components:Prerequisites$kubernetes:core/v1:Namespace::prereq-ns
```

This triggers destroy+recreate unless we add aliases. The alias strategy:
```python
opts=pulumi.ResourceOptions(
    parent=self,
    aliases=[pulumi.Alias(parent=pulumi.rootStackResource)],
)
```
tells Pulumi: "this resource used to have the root stack as parent" → it matches the old URN.

### Verification Protocol
After EACH ComponentResource conversion:
1. `pulumi preview --stack dev --diff` — must show zero creates/deletes
2. If any create/delete appears → alias is missing or wrong → fix immediately
