# F1 Code Quality Review — Pulumi Improvements

## Verdict: REJECT

I reviewed all 18 requested files across T1-T9.

The ComponentResource migration is mostly disciplined and internally consistent: all reviewed component modules keep `deploy()` wrappers, expose `self.result`, use `_child_opts()` with `parent=self` plus `aliases=[pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)]`, avoid passing `provider` into the reviewed dynamic providers, and use `pulumi.ResourceOptions.merge()` where child opts must be combined with timeouts or replacement settings.

That said, there are correctness gaps that are large enough to block approval because they will either make the verification layer fail against healthy deployments or leave the new PolicyPack materially under-enforcing the intended rules.

---

## Scope reviewed

### Phase A — Script Extraction
- `pulumi/templates/openbao_post_start.sh.tpl`
- `pulumi/templates/k3d_entrypoint_cilium.sh`
- `pulumi/values/openbao.py`
- `pulumi/scripts/bootstrap_k3d.py`

### Phase B — CrossGuard PolicyPack
- `pulumi/policy/PulumiPolicy.yaml`
- `pulumi/policy/__main__.py`
- `pulumi/policy/requirements.txt`
- `pulumi/pyproject.toml`

### Phase C — ComponentResource Conversion
- `pulumi/components/prerequisites.py`
- `pulumi/components/control_plane.py`
- `pulumi/components/data_plane.py`
- `pulumi/components/workflow_plane.py`
- `pulumi/components/observability_plane.py`
- `pulumi/components/cilium.py`
- `pulumi/components/flux_gitops.py`
- `pulumi/components/link_planes.py`
- `pulumi/components/integration_tests.py`
- `pulumi/__main__.py`

---

## What is solid

### ComponentResource pattern checks
All six required migration patterns are present across the reviewed component modules.

1. **Child resource parenting/aliasing:** every reviewed ComponentResource module defines `_child_opts()` with `parent=self` and `aliases=[pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)]`.
2. **Resource creation sites:** reviewed child resource creation sites consistently use `_child_opts(...)`, including the helper-backed sites in `data_plane.py` and `cilium.py` where merged opts are passed into helper-created resources.
3. **Merged options:** `pulumi.ResourceOptions.merge()` is used where `_child_opts(...)` must be combined with `custom_timeouts`, `delete_before_replace`, or `replace_on_changes`.
4. **Dynamic providers:** reviewed uses of `WaitDeployments`, `WaitCustomResourceCondition`, `LinkPlanes`, and `IntegrationTest` correctly omit `provider=` and only pass dependency/options metadata.
5. **`self.result`:** every converted component exposes `self.result` and the result shape is consistent with its wrapper return type.
6. **Backward compatibility:** every reviewed component module still keeps a thin `deploy()` wrapper.

### Phase A
- `openbao_post_start.sh.tpl` correctly uses `$$` to preserve the shell variable in the rendered script.
- `bootstrap_k3d.py` cleanly externalizes the static Cilium entrypoint script and reads it from `pulumi/templates/`.

---

## Blocking findings

### 1. Flux integration tests target the wrong Kustomization names
**Severity:** High  
**Files:** `pulumi/components/flux_gitops.py`, `pulumi/components/integration_tests.py`

The Flux component creates these Kustomization resource names:
- `namespaces` (`flux_gitops.py:74`)
- `platform-shared` (`flux_gitops.py:88`)
- `oc-demo-platform` (`flux_gitops.py:102`)
- `oc-demo-projects` (`flux_gitops.py:118`)

But the integration tests check:
- `oc-namespaces`
- `oc-platform-shared`
- `oc-platform`
- `oc-demo-projects`
  (`integration_tests.py:397-408`)

So three of the four Flux E2E checks do not match the resources this code actually creates. On any stack with Flux enabled, those tests will fail even if Flux is healthy.

**Required fix:** make the test resource names match the actual Flux `metadata.name` values, or rename the created Kustomizations to match the test expectations.

### 2. External Secrets readiness tests use `v1beta1` while the deployed resources/waits use `v1`
**Severity:** High  
**Files:** `pulumi/components/prerequisites.py`, `pulumi/components/control_plane.py`, `pulumi/components/observability_plane.py`, `pulumi/components/integration_tests.py`

The created resources and prerequisite waiter are all aligned to `external-secrets.io/v1`:
- `ClusterSecretStore` uses `api_version="external-secrets.io/v1"` (`prerequisites.py:286`)
- prerequisite readiness waiter uses `version="v1"` (`prerequisites.py:317`)
- `ExternalSecret` resources in control plane and observability also use `api_version="external-secrets.io/v1"` (`control_plane.py:243`, `observability_plane.py:66`, `:83`, `:100`)

But the integration tests check those resources with `cr_version="v1beta1"` (`integration_tests.py:318`, `:332`, `:418`).

That mismatch is brittle at best and wrong at worst. If the cluster only serves the `v1` endpoint for these CRDs, the tests will 404 against healthy resources.

**Required fix:** standardize the integration tests on `external-secrets.io/v1` to match the deployed resources and the existing prerequisite waiter.

### 3. `block-dev-seeds-on-prod` is stale/incomplete relative to the actual OpenBao dev seed script
**Severity:** High  
**Files:** `pulumi/policy/__main__.py`, `pulumi/values/openbao.py`, `pulumi/templates/openbao_post_start.sh.tpl`

The policy only scans for two hard-coded seed patterns:
- `bao kv put secret/choreo-system-password`
- `bao kv put secret/opensearch-password`
  (`policy/__main__.py:45-48`)

But the actual dev-only seed block now emits a much larger set of seed commands, including:
- `secret/npm-token`
- `secret/docker-username`
- `secret/docker-password`
- `secret/github-pat`
- `secret/git-token`
- `secret/gitops-token`
- `secret/username`
- `secret/password`
- `secret/backstage-backend-secret`
- `secret/backstage-client-secret`
- `secret/backstage-jenkins-api-key`
- `secret/observer-oauth-client-secret`
- `secret/rca-oauth-client-secret`
- `secret/opensearch-username`
- `secret/opensearch-password`
  (`openbao.py:45-60`)

So the production guard no longer reflects the actual seed behavior. It would miss most of the dev-only secret seeding that this change set introduced/retained.

**Required fix:** update the policy to detect the current seed commands, preferably from a broader rule such as matching dev-only `bao kv put secret/...` patterns that are specific to the seeded set, instead of a stale two-entry allowlist/blocklist.

---

## Additional findings

### 4. `enforce-helm-timeouts` does not cover most Helm-backed resources in this change set
**Severity:** Medium  
**Files:** `pulumi/policy/__main__.py`, multiple component modules

`enforce-helm-timeouts` only checks `kubernetes:helm.sh/v4:Chart` (`policy/__main__.py:234`). But many of the actual Helm-backed deployments in the converted components are `kubernetes:helm.sh/v3:Release`, including Thunder, the control plane, data plane, workflow plane, and observability releases.

If the policy intent is really “all Helm deployments must define timeouts,” the current implementation under-enforces that rule.

**Suggested fix:** either broaden the policy to include `kubernetes:helm.sh/v3:Release` or narrow the policy description so it matches the actual enforcement scope.

### 5. Script extraction is correct, but `openbao.py` only partially moved interpolation into the template
**Severity:** Low  
**Files:** `pulumi/templates/openbao_post_start.sh.tpl`, `pulumi/values/openbao.py`

The extraction works, but `os_user` and `os_pass` are still interpolated inside Python (`openbao.py:59-60`) rather than being fully represented as template placeholders in `openbao_post_start.sh.tpl`. That is not a runtime bug, but it does leave some of the original script assembly logic embedded in Python.

---

## File-group summary

### Phase A — Script extraction
No blocking correctness issues found. The template/file loading approach is straightforward and maintainable.

### Phase B — CrossGuard PolicyPack
The pack is structurally sound, but two of the policies are not yet aligned with the current codebase:
- dev-seed detection is stale/incomplete
- Helm timeout enforcement is narrower than the codebase it is meant to govern

### Phase C — ComponentResource conversion
The conversion pattern itself is good. The main problems are in the verification layer around it, not in the parent/alias migration mechanics:
- Flux E2E names do not match actual Flux resources
- External Secrets E2E versioning is inconsistent with the deployed resources

---

## Final assessment

**REJECT**

This is close, but not ready to approve as-is. The ComponentResource migration pattern looks disciplined, however the new verification/policy surface has real correctness gaps that will either fail healthy deployments (`integration_tests.py`) or leave production-policy enforcement materially incomplete (`policy/__main__.py`).
