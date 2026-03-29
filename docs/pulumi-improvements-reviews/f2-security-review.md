# F2 Security Review — Pulumi Improvements (T1-T9)

Date: 2026-03-29  
Reviewer: Oracle / Security Review

## Scope
Reviewed all 18 files listed for the Pulumi Improvements project:

1. `pulumi/templates/openbao_post_start.sh.tpl`
2. `pulumi/templates/k3d_entrypoint_cilium.sh`
3. `pulumi/values/openbao.py`
4. `pulumi/scripts/bootstrap_k3d.py`
5. `pulumi/policy/PulumiPolicy.yaml`
6. `pulumi/policy/__main__.py`
7. `pulumi/policy/requirements.txt`
8. `pulumi/pyproject.toml`
9. `pulumi/components/prerequisites.py`
10. `pulumi/components/control_plane.py`
11. `pulumi/components/data_plane.py`
12. `pulumi/components/workflow_plane.py`
13. `pulumi/components/observability_plane.py`
14. `pulumi/components/cilium.py`
15. `pulumi/components/flux_gitops.py`
16. `pulumi/components/link_planes.py`
17. `pulumi/components/integration_tests.py`
18. `pulumi/__main__.py`

Method: full file read + targeted pattern search for secrets, shell/code injection, subprocess/command execution, policy bypass conditions, template loading, and dependency/version hygiene.

## Verdict
**REJECT**

This change set contains one **High** severity issue and multiple **Medium** severity issues. The most important blocker is shell injection in the newly externalized OpenBao post-start script path; the new CrossGuard policy pack also has a fail-open/partial-coverage bypass that weakens the stated production guardrail.

---

## Blocking Findings

### 1) HIGH — Shell injection in OpenBao post-start templating
**Files:**
- `pulumi/templates/openbao_post_start.sh.tpl:3,29`
- `pulumi/values/openbao.py:43-61,63`

**What is happening**
- The template exports the token as `export BAO_TOKEN=$token`.
- The dev-only seed block is injected as raw shell via `$dev_secrets_block`.
- That block is built with Python f-strings that place `os_user` and `os_pass` inside double-quoted shell arguments:
  - `bao kv put secret/opensearch-username value="{os_user}"`
  - `bao kv put secret/opensearch-password value="{os_pass}"`

**Why this is a vulnerability**
`string.Template` only substitutes text; it does **not** shell-escape values. In POSIX shell, assignment values and double-quoted strings still permit command substitution like `$(...)` and backticks. A malicious or malformed Pulumi config value can therefore execute arbitrary shell within the OpenBao pod during Helm postStart.

**Impact**
- Arbitrary shell execution in the OpenBao container at deploy/startup time.
- Secret seeding can be altered or additional commands can run under the OpenBao startup context.
- This affects the newly introduced template-based path directly.

**Why this blocks approval**
The extraction moved the post-start script into a template, but the current implementation still treats secret/config values as shell-safe text when they are not.

**Required fix before approval**
Use shell-safe quoting for every injected scalar (`token`, `os_user`, `os_pass`) or switch to a transport that avoids shell interpolation entirely (for example: generate a data-only file or pass values via a safer mechanism rather than inline shell text).

---

### 2) MEDIUM — CrossGuard prod protections can be bypassed / are incomplete
**File:** `pulumi/policy/__main__.py:35,45-48,70-77,133-166`

**What is happening**
- `_is_dev_stack_from_resources()` returns `True` when it cannot determine the stack name (`return True  # If we cannot determine the stack, assume dev`).
- `block-dev-seeds-on-prod` only scans for two literal patterns:
  - `bao kv put secret/choreo-system-password`
  - `bao kv put secret/opensearch-password`
- The actual dev seed block in `pulumi/values/openbao.py:45-60` contains many additional dev-only seeds (`npm-token`, `docker-password`, `github-pat`, `git-token`, `gitops-token`, `backstage-*`, `observer-oauth-client-secret`, `rca-oauth-client-secret`, etc.).

**Why this is a vulnerability**
This is a **policy bypass** problem. The policy is meant to be a mandatory backstop for prod stacks, but it:
1. **fails open** when stack detection is unavailable, and
2. only covers a narrow subset of the dev seed commands it claims to block.

**Impact**
- If stack detection fails, both mandatory stack policies short-circuit and skip enforcement.
- If a dev-seed leak does not include one of the two hardcoded patterns, the policy will not catch it.
- The direct `is_dev_stack` gate in `prerequisites.py:204-209` is currently correct, but the new policy layer is not reliable enough to serve as a strong compensating control.

**Why this blocks approval**
The new PolicyPack is being added specifically as security enforcement. In its current form it gives a stronger safety signal than it actually provides.

**Required fix before approval**
- Fail closed when stack identification is unavailable.
- Expand detection to match the full dev seed surface actually emitted by `openbao.py`, or validate the specific OpenBao postStart payload structurally instead of matching two literals.

---

## Additional Findings

### 3) MEDIUM — Local shell-command injection surface in `command.local.Command`
**Files:**
- `pulumi/components/workflow_plane.py:117-123,124-127`
- `pulumi/components/control_plane.py:314-320`
- `pulumi/components/observability_plane.py:121-125`

**What is happening**
These resources build shell command strings with direct interpolation of config-derived values such as `cfg.kubeconfig_context`, `cfg.k3d_cluster_name`, and remote URLs.

Examples:
- `curl -sL {url} | ... | kubectl apply --context {cfg.kubeconfig_context} -f -`
- `docker exec k3d-{cfg.k3d_cluster_name}-server-0 sh -c ...`

**Risk**
If those config values contain shell metacharacters, a local operator machine can execute unintended commands during `pulumi up`. This was already a risk surface in the affected files; the ComponentResource conversion does not introduce a new authorization flaw, but the changed files still contain this injection class.

**Recommendation**
Treat these as shell-sensitive inputs: quote/escape them correctly or replace shell pipelines with argument-vector subprocess execution where possible.

---

### 4) LOW — Dependency specs are range-based, not exact-pinned
**Files:**
- `pulumi/policy/requirements.txt:1`
- `pulumi/pyproject.toml:7-13,18-24`

**What is happening**
The new policy dependency is declared as `pulumi-policy>=1.0.0`, and the wider project also uses broad version ranges.

**Risk**
This is mainly a supply-chain/reproducibility concern rather than an immediate exploitable vulnerability. I did **not** verify CVE status from this review alone, so I am not asserting a known vulnerable package here.

**Recommendation**
Pin exact versions for reproducible policy-pack execution, or at minimum constrain ranges more tightly in the lock/update process.

---

## Checks Requested in the Task

### Template injection (`openbao_post_start.sh.tpl`)
**Result: FAIL**
- Structural template loading is okay.
- Actual shell safety is **not** okay because substituted values are not escaped for shell context.

### Secrets exposure
**Result: PARTIAL FAIL**
- No new hardcoded production secrets were introduced.
- Dev placeholder secrets remain dev-only and are gated by `is_dev_stack`.
- However, the OpenBao postStart path still embeds sensitive values into shell text, and the changed files still pass `root_token` through dynamic-resource inputs (`prerequisites.py:242-268`, `integration_tests.py:304-308`), which is an existing secret-handling concern in those files.

### Policy bypass (`pulumi/policy/__main__.py`)
**Result: FAIL**
- The policy pack can be bypassed by fail-open stack detection.
- The dev-seed matcher is incomplete relative to the actual dev seed payload.

### Path traversal (template loading)
**Result: PASS**
- `pulumi/values/openbao.py:39` and `pulumi/scripts/bootstrap_k3d.py:78` load from fixed repository-relative paths.
- No user-controlled path join or traversal was introduced in this change set.

### Code injection (`eval`, `exec`, subprocess usage)
**Result: PARTIAL FAIL**
- No `eval()` / `exec()` found in the reviewed files.
- `bootstrap_k3d.py` uses list-based `subprocess.run(...)`, which is the safer pattern.
- `command.local.Command` usage in changed component files still builds shell strings from interpolated values and remains injection-sensitive.

### Dependency security
**Result: LOW-RISK NOTE**
- No known-vulnerable package claim from this review.
- Exact pinning is not used for the new policy dependency.

### Access control / privilege escalation (ComponentResource pattern)
**Result: PASS WITH NOTE**
- I found **no new privilege escalation risk caused by the ComponentResource conversion itself**. The `parent=self` / alias pattern changes resource ownership metadata, not runtime authorization.
- `pulumi/components/cilium.py` still creates a privileged host-level Job (`privileged=True`, `host_pid=True`, `host_network=True`), but that is an existing intentional platform operation rather than a new privilege-escalation bug introduced by the refactor.

### Information disclosure
**Result: PASS WITH NOTE**
- I did not find newly added logging that prints secret values in these changes.
- `pulumi/scripts/bootstrap_k3d.py` correctly points users to `pulumi stack output --show-secrets` instead of printing the secrets directly.

---

## File-by-File Coverage

### Phase A — Script Extraction
- `pulumi/templates/openbao_post_start.sh.tpl` — **Issue**: shell injection risk from unescaped template variables (`$token`, `$dev_secrets_block`).
- `pulumi/templates/k3d_entrypoint_cilium.sh` — **No issue found**: static script, no variable interpolation, no secret material.
- `pulumi/values/openbao.py` — **Issue**: unescaped values embedded into shell; `is_dev_stack` gate itself is correct.
- `pulumi/scripts/bootstrap_k3d.py` — **No blocking issue found**: fixed-path template loading and list-based subprocess calls are good; no secret values logged.

### Phase B — CrossGuard PolicyPack
- `pulumi/policy/PulumiPolicy.yaml` — **No issue found**: minimal config only.
- `pulumi/policy/__main__.py` — **Issue**: fail-open stack detection + incomplete dev-seed coverage.
- `pulumi/policy/requirements.txt` — **Low-risk note**: dependency not exact-pinned.
- `pulumi/pyproject.toml` — **Low-risk note**: range-based dependency constraints.

### Phase C — ComponentResource Conversion
- `pulumi/components/prerequisites.py` — **No new ComponentResource access-control issue**; dev gate matches config; existing secret-handling concern remains where `root_token` is passed to dynamic resources.
- `pulumi/components/control_plane.py` — **Issue**: interpolated shell command in `command.local.Command`; otherwise Job security context is reasonably hardened (`allow_privilege_escalation=False`, `run_as_non_root=True`, dropped capabilities).
- `pulumi/components/data_plane.py` — **No issue found** related to the refactor.
- `pulumi/components/workflow_plane.py` — **Issue**: interpolated shell command built from URLs/context.
- `pulumi/components/observability_plane.py` — **Issue**: interpolated shell command built from cluster name.
- `pulumi/components/cilium.py` — **No new refactor issue found**; privileged node-fix Job is intentional but high-trust.
- `pulumi/components/flux_gitops.py` — **No issue found** related to the refactor.
- `pulumi/components/link_planes.py` — **No issue found** related to the refactor.
- `pulumi/components/integration_tests.py` — **No new refactor issue found**; existing secret-handling concern remains where `root_token` is passed into a dynamic test resource.
- `pulumi/__main__.py` — **No new ComponentResource security issue found** in orchestration; credential exports are still marked secret at Pulumi output level.

---

## Approval Conditions
Approval should wait for these minimum fixes:

1. Make OpenBao post-start generation shell-safe for every substituted value.
2. Make CrossGuard stack detection fail closed and cover the full dev-seed payload.
3. Harden or constrain the `command.local.Command` shell interpolations in changed component files.

Once those are addressed, I would rerun the same review and expect this to move much closer to **APPROVE**.
