# Documentation Phase: Lessons Learned & Bridge Bug RFC

## TL;DR

> **Quick Summary**: Create two comprehensive documentation deliverables capturing the full journey of the Pulumi/Talos bare-metal Kubernetes project — a Lessons Learned document covering all bugs, workarounds, and pro tips, and a standalone RFC documenting the `pulumi-terraform-bridge` state serialization bug for upstream contribution.
> 
> **Deliverables**:
> - `docs/lessons-learned.md` — Project lessons learned (4 bugs, workarounds, known issue status, pro tips)
> - `docs/bridge-bug-rfc.md` — Technical RFC for the `pulumi-terraform-bridge` rawstate bug (suitable for PR/issue submission)
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Task 1 (extract patches) -> Task 2 & Task 3 (write docs in parallel) -> F1-F4 (verification)

---

## Context

### Original Request
The user wants a "Documentation Phase" capturing:
1. What was wrong, what was unexpected, workarounds used, known issue status, and pro tips
2. A separate "full blown documentation" on the bridge bug — what the bug was, whether recompiling fixed it, and a PR/RFC for future developers

### Interview Summary
**Key Discussions**:
- Scope: Focus on bugs + workarounds + pro tips (user's exact words)
- RFC target: `pulumi-terraform-bridge` repo (root cause) with mention of `pulumiverse-talos`
- Audience: Intermediate Pulumi/Talos users (Doc 1); upstream maintainers (Doc 2)
- Format: Concise callout-style pro tips; standard RFC structure for Doc 2

**Research Findings**:
- 4 distinct bugs documented across project notepads and source files
- Patched `rawstate.go` confirmed at `/tmp/bridge-v3.116.0-patched/pkg/tfbridge/rawstate.go` (29968 bytes)
- 3 previous execution plans with 176+ lines of accumulated learnings
- All implementation files verified and project fully deployed/healthy

### Metis Review
**Identified Gaps** (addressed):
- Document locations: Resolved to `docs/lessons-learned.md` and `docs/bridge-bug-rfc.md`
- RFC target repo: Resolved to `pulumi-terraform-bridge` (root cause)
- Scope: Resolved to bugs + workarounds + pro tips per user's words
- Pro tips format: Resolved to concise callout-style bullets
- Audience: Resolved to intermediate users (Doc 1) / upstream maintainers (Doc 2)

---

## Work Objectives

### Core Objective
Produce two high-quality markdown documents that preserve the project's hard-won knowledge for future reference and community contribution.

### Concrete Deliverables
- `docs/lessons-learned.md` — Comprehensive lessons learned document
- `docs/bridge-bug-rfc.md` — Technical RFC for the bridge state serialization bug

### Definition of Done
- [ ] Both documents exist and are well-structured markdown
- [ ] Lessons learned covers all 4 bugs with: symptom, root cause, fix, known issue status
- [ ] RFC includes: reproduction steps, root cause analysis, patch diffs, proposed fix
- [ ] Pro tips section provides actionable reference for future deployments
- [ ] All code references are accurate (verified against actual source files)

### Must Have
- All 4 bugs documented (bridge rawstate, TLS 1.3 false positive, /readyz 401, TCP port float)
- macOS code signing discovery
- Actual patch code from rawstate.go (not paraphrased)
- Reproduction steps for the bridge bug
- Build environment details

### Must NOT Have (Guardrails)
- No speculation about bugs — only document what was actually observed and fixed
- No secrets, passwords, or IP addresses in documents
- No auto-generated filler text or generic "best practices" padding
- No documenting things that weren't actually encountered
- Do NOT include the full 925-line rawstate.go — only the relevant diff sections

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest exists but irrelevant for docs)
- **Automated tests**: None (documentation task — no code to test)
- **Framework**: N/A

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Documentation**: Use Bash (grep/wc) — Verify section presence, word count, code block accuracy
- **Code References**: Use Read tool — Verify quoted code matches actual source files

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — extract source material):
├── Task 1: Extract bridge patches from rawstate.go [quick]
├── Task 2: Read all source files for bug details [quick]

Wave 2 (After Wave 1 — write documents in parallel):
├── Task 3: Write Lessons Learned document [writing]
├── Task 4: Write Bridge Bug RFC document [writing]

Wave FINAL (After ALL tasks — verification):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
├── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 3, 4 | 1 |
| 2 | — | 3, 4 | 1 |
| 3 | 1, 2 | F1-F4 | 2 |
| 4 | 1, 2 | F1-F4 | 2 |
| F1-F4 | 3, 4 | — | FINAL |

### Agent Dispatch Summary

- **Wave 1**: **2** — T1 `quick`, T2 `quick`
- **Wave 2**: **2** — T3 `writing`, T4 `writing`
- **FINAL**: **4** — F1 `oracle`, F2 `unspecified-high`, F3 `unspecified-high`, F4 `deep`

---

## TODOs

- [x] 1. Extract Bridge Patches from rawstate.go

  **What to do**:
  - Run `diff` between the original and patched rawstate.go to produce the exact diff:
    - Original: `/Users/yamer003/go/pkg/mod/github.com/pulumi/pulumi-terraform-bridge/v3@v3.116.0/pkg/tfbridge/rawstate.go`
    - Patched: `/tmp/bridge-v3.116.0-patched/pkg/tfbridge/rawstate.go`
  - The diff reveals **4 logical patches** (not 5 — the original plan's count was inaccurate):
    1. **Conditional timeouts handling** in `inferRawStateDelta` — don't unconditionally strip `timeouts`; check if timeouts are part of the provider data model first. Also fix timeouts delta at path-level-1 and object-type-level to return `objDelta{PropertyDeltas: ...}` instead of empty `RawStateDelta{}`
    2. **Null normalization for turnaround check** in `turnaroundCheck` — add `stripNullsFromJSON` + `stripNulls` helper functions, perform a secondary comparison after normalizing both sides to strip null map entries dropped during PropertyValue round-trip
    3. **Enhanced error messages** — add delta and PropertyValue context to the turnaround check error, add `os.WriteFile` debug dumps to `/tmp/rawstate-{original,recovered}.json`
    4. **Import addition** — `"os"` package for debug file writing
  - For each patch, extract:
    - The function name where the patch lives
    - The exact diff hunks (from the `diff` output)
    - A 1-2 sentence explanation of what the patch fixes
  - Save extracted patches to `.sisyphus/evidence/task-1-bridge-patches.md` as structured notes
  - The full diff output should also be saved for inclusion in the RFC

  **Must NOT do**:
  - Do NOT copy the entire 29968-byte rawstate.go into evidence — only the relevant sections
  - Do NOT speculate about patches — only document what's actually in the file

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: This is a read-and-extract task — no code writing, just reading files and noting sections
  - **Skills**: []
    - No specialized skills needed — file reading and note-taking only

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Tasks 3, 4
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `/tmp/bridge-v3.116.0-patched/pkg/tfbridge/rawstate.go` — The patched bridge source (29968 bytes). Contains all patches in `inferRawStateDelta` (line ~496), `turnaroundCheck` (line ~517), `deltaAt` (line ~641, ~834), plus new `stripNullsFromJSON`/`stripNulls` functions (line ~562).
  - `/Users/yamer003/go/pkg/mod/github.com/pulumi/pulumi-terraform-bridge/v3@v3.116.0/pkg/tfbridge/rawstate.go` — The ORIGINAL unpatched source from Go module cache. Run `diff` between this and the patched version to produce the exact diff for the RFC.
  - `/tmp/pulumi-talos-fork/provider/go.mod` — Shows the `replace` directive that points to the patched bridge.

  **WHY Each Reference Matters**:
  - The diff between original and patched rawstate.go is the ONLY source of truth for what patches were applied. The RFC document must quote exact diffs.
  - The go.mod `replace` directive documents how the patched bridge was wired into the provider build.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Patches extracted completely
    Tool: Bash (grep)
    Preconditions: Evidence file exists at .sisyphus/evidence/task-1-bridge-patches.md
    Steps:
      1. Run: test -f .sisyphus/evidence/task-1-bridge-patches.md && echo "EXISTS"
      2. Run: grep -c "Patch" .sisyphus/evidence/task-1-bridge-patches.md
      3. Run: grep -c "inferRawStateDelta\|turnaroundCheck\|stripNulls" .sisyphus/evidence/task-1-bridge-patches.md
    Expected Result: File exists, contains >= 4 patch descriptions (4 logical patches), references key functions
    Failure Indicators: File missing, fewer than 4 patches documented, missing function references
    Evidence: .sisyphus/evidence/task-1-patches-verified.txt

  Scenario: No full file dump in evidence
    Tool: Bash (wc)
    Preconditions: Evidence file exists
    Steps:
      1. Run: wc -l .sisyphus/evidence/task-1-bridge-patches.md
    Expected Result: Less than 500 lines (extracted sections only, not full 900+ line file)
    Failure Indicators: More than 500 lines suggests full file was dumped
    Evidence: .sisyphus/evidence/task-1-size-check.txt
  ```

  **Evidence to Capture:**
  - [ ] `.sisyphus/evidence/task-1-bridge-patches.md` — Structured patch extractions
  - [ ] `.sisyphus/evidence/task-1-patches-verified.txt` — Grep verification output
  - [ ] `.sisyphus/evidence/task-1-size-check.txt` — Line count verification

  **Commit**: NO (evidence file only, committed with final docs)

- [x] 2. Read All Source Files for Bug Details

  **What to do**:
  - Read the following source files to extract exact bug details, error messages, and fix implementations:
    1. `pulumi/talos-cluster-baremetal/check_node_state.py` — TLS 1.3 false positive bug (Bug 2)
    2. `pulumi/talos-cluster-baremetal/wait_for_k8s_api.py` — /readyz 401 bug (Bug 3)
    3. `pulumi/talos-cluster-baremetal/wait_for_talos_node.py` — TCP port float type bug (Bug 4)
    4. `pulumi/talos-cluster-baremetal/__main__.py` — Overall architecture reference
    5. `pulumi/talos-cluster-baremetal/COMPARISON-AND-ALIGNMENT-PLAN.md` — 12-step alignment context
  - Also read all sisyphus notepads for accumulated learnings:
    1. `.sisyphus/notepads/talos-baremetal-deploy/learnings.md`
    2. `.sisyphus/notepads/pulumi-improvements/learnings.md`
    3. `.sisyphus/notepads/pulumi-improvements/issues.md`
    4. `.sisyphus/notepads/pulumi-improvements/decisions.md`
    5. `.sisyphus/notepads/pulumi-remediation/learnings.md`
    6. `.sisyphus/notepads/pulumi-remediation/decisions.md`
  - Gather bridge bug, macOS codesign, and build environment facts from **verifiable sources** (NOT from `.sisyphus/plans/talos-baremetal-deploy.md` — that plan does not contain these details). Use:
    - **Bridge bug patches**: The diff output from Task 1 (`.sisyphus/evidence/task-1-bridge-patches.md`)
    - **Build environment**: Run `go version` (expected: go1.26.1 darwin/arm64), `sw_vers` (expected: macOS 26.x), `pulumi version` (expected: v3.228.0)
    - **macOS codesign discovery**: Run `codesign -dv ~/.pulumi/plugins/resource-talos-v0.7.1/pulumi-resource-talos` to verify the binary is ad-hoc signed. The workaround command is: `codesign --force --sign - --timestamp=none <binary>` — this is needed after copying any Go-compiled binary on macOS (quarantine/Gatekeeper blocks unsigned binaries).
    - **Recompilation confirmation**: Run `file ~/.pulumi/plugins/resource-talos-v0.7.1/pulumi-resource-talos` (expected: Mach-O 64-bit arm64) and `ls -la ~/.pulumi/plugins/resource-talos-v0.7.1/` to confirm the patched binary exists
    - **Fork build wiring**: Read `/tmp/pulumi-talos-fork/provider/go.mod` to see the `replace` directive pointing to the patched bridge
  - For each bug, extract: exact symptom, root cause, the fix applied (with code references), and any relevant error messages
  - Save structured notes to `.sisyphus/evidence/task-2-bug-details.md`

  **Must NOT do**:
  - Do NOT copy entire files — extract only the relevant sections
  - Do NOT include IP addresses or secrets from config files

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Read-and-extract task across multiple files — straightforward file reading
  - **Skills**: []
    - No specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Tasks 3, 4
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `pulumi/talos-cluster-baremetal/check_node_state.py` — Lines containing `ssl.CERT_NONE`, `talosctl get machinestatus`, and the TLS 1.3 detection logic
  - `pulumi/talos-cluster-baremetal/wait_for_k8s_api.py` — Lines containing `/readyz`, HTTP status check logic, and the "< 500" acceptance fix
  - `pulumi/talos-cluster-baremetal/wait_for_talos_node.py` — Lines containing `int(port)` casting fix
  - `pulumi/talos-cluster-baremetal/__main__.py` — Overall pipeline structure showing how dynamic resources connect
   **NOTE**: `.sisyphus/plans/talos-baremetal-deploy.md` does NOT contain bridge bug, codesign, or recompilation details. Do not search it for those topics. The verifiable sources for those facts are shell commands and the diff from Task 1 — see "What to do" above.

  **Build Environment Verification Commands** (run these to capture exact versions — these ARE the sources):
  - `go version` — expected: `go1.26.1 darwin/arm64`
  - `sw_vers` — expected: macOS 26.x
  - `pulumi version` — expected: `v3.228.0`
  - `ls -la ~/.pulumi/plugins/resource-talos-v0.7.1/` — expected: patched binary exists
  - `file ~/.pulumi/plugins/resource-talos-v0.7.1/pulumi-resource-talos` — expected: Mach-O 64-bit arm64
  - `codesign -dv ~/.pulumi/plugins/resource-talos-v0.7.1/pulumi-resource-talos` — expected: ad-hoc signed (Signature=adhoc)

  **WHY Each Reference Matters**:
  - Each source file contains the actual implementation of a bug fix. The lessons learned document must reference real code, not vague descriptions.
  - The notepads contain additional context (error messages, debugging steps) that may not be in the final source code.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All 4 bugs documented with details
    Tool: Bash (grep)
    Preconditions: Evidence file exists at .sisyphus/evidence/task-2-bug-details.md
    Steps:
      1. Run: test -f .sisyphus/evidence/task-2-bug-details.md && echo "EXISTS"
      2. Run: grep -c "Bug\|bug" .sisyphus/evidence/task-2-bug-details.md
      3. Run: grep -c "TLS\|readyz\|float\|rawstate\|bridge" .sisyphus/evidence/task-2-bug-details.md
    Expected Result: File exists, references all 4 bugs with technical keywords
    Failure Indicators: File missing, any bug not documented
    Evidence: .sisyphus/evidence/task-2-bugs-verified.txt

  Scenario: No secrets or IPs in evidence
    Tool: Bash (grep)
    Preconditions: Evidence file exists
    Steps:
      1. Run: grep -cE "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" .sisyphus/evidence/task-2-bug-details.md
    Expected Result: 0 matches (no IP addresses)
    Failure Indicators: Any IP address found in the evidence
    Evidence: .sisyphus/evidence/task-2-secrets-check.txt
  ```

  **Evidence to Capture:**
  - [ ] `.sisyphus/evidence/task-2-bug-details.md` — Structured bug details from all source files
  - [ ] `.sisyphus/evidence/task-2-bugs-verified.txt` — Bug coverage verification
  - [ ] `.sisyphus/evidence/task-2-secrets-check.txt` — Secrets scan result

  **Commit**: NO (evidence file only, committed with final docs)

- [x] 3. Write Project Lessons Learned Document

  **What to do**:
  - Create `docs/lessons-learned.md` with the following structure:
    ```
    # Pulumi/Talos Bare-Metal Kubernetes: Lessons Learned
    ## Project Overview (brief — 3-4 sentences)
    ## Bug 1: Pulumi-Terraform Bridge State Serialization Crash
      - Symptom / Root Cause / Fix / Known Issue Status
    ## Bug 2: Pre-Flight Node Detection TLS 1.3 False Positive
      - Symptom / Root Cause / Fix / Known Issue Status
    ## Bug 3: Kubernetes /readyz Returns 401 on Talos Clusters
      - Symptom / Root Cause / Fix / Known Issue Status
    ## Bug 4: TCP Port Float Type Mismatch in Dynamic Resources
      - Symptom / Root Cause / Fix / Known Issue Status
    ## Unexpected Discovery: macOS Code Signing for Go Binaries
      - What happened / The fix
    ## Terraform Post-Install Superseded
      - What happened / Why it's expected
    ## Pro Tips
      - Callout-style bullets for quick reference
    ## Build Environment
      - Exact versions used
    ```
  - For each bug section, use the evidence from Task 2 (`.sisyphus/evidence/task-2-bug-details.md`)
  - Include actual code snippets showing the fix (not just descriptions)
  - Pro tips should be concise, actionable, and formatted as callout blocks or bullet points
  - Include the build environment details: Go 1.26.1 darwin/arm64, macOS 26.3.1, Pulumi v3.228.0, pulumiverse-talos v0.7.1, pulumi-kubernetes v4.28.0
  - Keep Bug 1 (bridge bug) summary-level here — point to `docs/bridge-bug-rfc.md` for the deep dive

  **Must NOT do**:
  - Do NOT include IP addresses, passwords, or the PULUMI_CONFIG_PASSPHRASE value
  - Do NOT pad with generic Kubernetes/Pulumi best practices not encountered in this project
  - Do NOT over-document Bug 1 here — the RFC is the detailed document for that
  - Do NOT use filler phrases like "it's worth noting that" or "it should be mentioned that"

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: This is a documentation/writing task — structured technical writing from gathered evidence
  - **Skills**: []
    - No specialized skills needed — straightforward technical documentation

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 4)
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 1, 2 (need extracted evidence)

  **References**:

  **Pattern References**:
  - `.sisyphus/evidence/task-2-bug-details.md` — Extracted bug details from source files (created by Task 2)
  - `pulumi/talos-cluster-baremetal/check_node_state.py:1-50` — TLS 1.3 fix implementation (for code snippet)
  - `pulumi/talos-cluster-baremetal/wait_for_k8s_api.py:1-50` — /readyz 401 fix (for code snippet)
  - `pulumi/talos-cluster-baremetal/wait_for_talos_node.py` — Port casting fix (search for `int(port)`)
  **NOTE**: `.sisyphus/plans/talos-baremetal-deploy.md` does NOT contain bridge bug, codesign, or recompilation details — do not search it for those topics. Those facts come from Task 1 evidence, Task 2 evidence, and shell commands (see Tasks 1 & 2).

  **macOS/Build Facts Source** (gathered by Task 2 into its evidence file):
  - macOS codesign workaround: `codesign --force --sign - --timestamp=none <binary>` — required after copying Go binaries to Pulumi plugin directory on macOS
  - Build environment: Go 1.26.1 darwin/arm64, macOS 26.3.1, Pulumi v3.228.0

  **External References**:
  - `docs/bridge-bug-rfc.md` — Reference this from Bug 1 section as "see RFC for detailed analysis"

  **WHY Each Reference Matters**:
  - Evidence file has structured notes ready to be turned into prose
  - Source files provide exact code snippets to include
  - Cross-reference to RFC keeps Bug 1 section appropriately brief

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Document has all required sections
    Tool: Bash (grep)
    Preconditions: docs/lessons-learned.md exists
    Steps:
      1. Run: grep -c "## Bug" docs/lessons-learned.md
      2. Run: grep -c "## Pro Tips" docs/lessons-learned.md
      3. Run: grep -c "## Build Environment" docs/lessons-learned.md
      4. Run: grep "macOS" docs/lessons-learned.md | head -3
      5. Run: grep "bridge-bug-rfc" docs/lessons-learned.md | head -1
    Expected Result: >= 4 bug sections, Pro Tips section present, Build Environment present, macOS discovery present, cross-reference to RFC present
    Failure Indicators: Missing sections, no cross-reference, no macOS mention
    Evidence: .sisyphus/evidence/task-3-sections-verified.txt

  Scenario: Document has substantive content (not filler)
    Tool: Bash (wc)
    Preconditions: docs/lessons-learned.md exists
    Steps:
      1. Run: wc -w docs/lessons-learned.md
      2. Run: grep -c '```' docs/lessons-learned.md
    Expected Result: >= 1500 words, >= 4 code blocks (one per bug fix)
    Failure Indicators: < 1500 words or < 4 code blocks suggests thin content
    Evidence: .sisyphus/evidence/task-3-content-depth.txt

  Scenario: No secrets or IPs leaked
    Tool: Bash (grep)
    Preconditions: docs/lessons-learned.md exists
    Steps:
      1. Run: grep -cE "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" docs/lessons-learned.md
      2. Run: grep -ci "passphrase\|password\|secret" docs/lessons-learned.md
    Expected Result: 0 IP matches, 0 password/secret value matches (the word "secrets" in context is fine, actual values are not)
    Failure Indicators: Any actual IP address or credential value
    Evidence: .sisyphus/evidence/task-3-secrets-check.txt
  ```

  **Evidence to Capture:**
  - [ ] `.sisyphus/evidence/task-3-sections-verified.txt` — Section presence verification
  - [ ] `.sisyphus/evidence/task-3-content-depth.txt` — Word count and code block count
  - [ ] `.sisyphus/evidence/task-3-secrets-check.txt` — Secrets scan

  **Commit**: YES (group with Task 4)
  - Message: `docs: add project lessons learned and bridge bug RFC`
  - Files: `docs/lessons-learned.md`, `docs/bridge-bug-rfc.md`
  - Pre-commit: `test -f docs/lessons-learned.md && test -f docs/bridge-bug-rfc.md`

- [x] 4. Write Bridge Bug RFC Document

  **What to do**:
  - Create `docs/bridge-bug-rfc.md` with the following RFC structure:
    ```
    # RFC: Fix Timeouts Handling and Null Normalization in turnaroundCheck for pulumi-terraform-bridge
    ## Summary (2-3 sentences)
    ## Affected Versions
      - pulumi-terraform-bridge v3.116.0
      - pulumiverse-talos v0.7.1
      - Go 1.26.1 darwin/arm64
    ## Problem Statement
      - What happens: ConfigurationApply applies config successfully but crashes during state serialization
      - The error: `recovered raw state does not byte-for-byte match the original raw state` from turnaroundCheck
      - Secondary error when Object values reach rawStateRecoverNatural: `rawStateRecoverNatural cannot process Object values due to map vs object confusion`
      - Impact: Resource never saved to state, re-applied on every `pulumi up`
    ## Root Cause Analysis
      - Root cause 1: `inferRawStateDelta` unconditionally strips `timeouts` from the cty.Value before turnaroundCheck, but some providers include timeouts in their data model — the stripped state no longer matches the recovered state
      - Root cause 2: Null values in maps may be dropped during the PropertyValue round-trip — turnaroundCheck does byte-for-byte comparison which fails on semantically identical states that differ only in null representation
      - Root cause 3: Timeouts delta at path-level-1 and object-type-level returns empty `RawStateDelta{}` instead of a proper `objDelta`, causing downstream mismatches
      - Note: The `rawStateRecoverNatural` Object error (line 262-265) is NOT patched — it remains as-is because the delta recovery path handles objects via `d.Obj` in `recoverRepr`, bypassing `rawStateRecoverNatural`
      - Detailed code walkthrough of the failing path
    ## Reproduction Steps
      - Minimal reproduction case using pulumiverse-talos ConfigurationApply
      - Environment setup
      - Expected vs actual behavior
    ## Proposed Fix (4 logical patches)
      - Patch A: Conditional timeouts handling in inferRawStateDelta + fix timeouts delta returns (with diff)
      - Patch B: Null normalization for turnaround check with stripNullsFromJSON helper (with diff)
      - Patch C: Enhanced error messages for debugging (with diff)
      - Patch D: Debug file writing for inspection (with diff)
    ## Workaround (Current)
      - Recompile provider with patched bridge
      - Step-by-step build instructions (generic paths, no personal directories)
    ## Testing
      - How the fix was validated in production
      - Suggested test cases for upstream
    ## Impact Assessment
      - Which other providers could be affected
      - Severity level
    ## References
      - Links to relevant code, issues, PRs
    ```
  - Use the evidence from Task 1 (`.sisyphus/evidence/task-1-bridge-patches.md`) for exact patch code
  - Include the actual Go code patches — not paraphrased descriptions
  - Write reproduction steps that an upstream maintainer could follow
  - Include build/install instructions (Go version, codesign step, plugin installation)
  - Tone: professional, technical, suitable for submission as a GitHub issue or RFC

  **Must NOT do**:
  - Do NOT include the full rawstate.go file — only the patched functions/sections
  - Do NOT include personal paths (e.g., /Users/yamer003) — use generic placeholders
  - Do NOT include angry or frustrated tone — keep it professional and constructive
  - Do NOT speculate about why the bug exists — only document observable behavior and the fix
  - Do NOT include IP addresses or cluster-specific configuration

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: Technical RFC writing requiring structured prose + code blocks — writing-focused task
  - **Skills**: []
    - No specialized skills needed — technical writing from gathered evidence

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 3)
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 1, 2 (need extracted evidence, especially Task 1's patch extractions)

  **References**:

  **Pattern References**:
  - `.sisyphus/evidence/task-1-bridge-patches.md` — Extracted patch diffs from rawstate.go (created by Task 1)
  - `/tmp/bridge-v3.116.0-patched/pkg/tfbridge/rawstate.go` — Full patched source (for additional context if evidence is incomplete)
  - `/Users/yamer003/go/pkg/mod/github.com/pulumi/pulumi-terraform-bridge/v3@v3.116.0/pkg/tfbridge/rawstate.go` — Original unpatched source for before/after comparison
  - `/tmp/pulumi-talos-fork/provider/go.mod` — Shows the `replace` directive wiring patched bridge into provider build
  **NOTE**: `.sisyphus/plans/talos-baremetal-deploy.md` does NOT contain bridge bug investigation context, error messages, recompilation process, or codesign workaround — do not search it for those topics.
  - **Bridge bug facts** come from: Task 1 evidence (`.sisyphus/evidence/task-1-bridge-patches.md`) which has the exact diffs, and the original/patched rawstate.go files referenced above.
  - **Error messages** come from: grepping the original rawstate.go for the error strings listed below (under "Known Error Messages").
  - **Recompilation confirmation** comes from: `file ~/.pulumi/plugins/resource-talos-v0.7.1/pulumi-resource-talos` (Mach-O 64-bit arm64 = successfully compiled).
  - **Codesign workaround**: `codesign --force --sign - --timestamp=none <binary>` — required on macOS after any `cp` of a Go binary.
  - `.sisyphus/evidence/task-2-bug-details.md` — Additional bug details extracted by Task 2

  **Build/Repro Verification Commands** (run these to capture facts for the RFC):
  - `go version` — Go version used for recompilation
  - `sw_vers` — macOS version for codesign context
  - `file ~/.pulumi/plugins/resource-talos-v0.7.1/pulumi-resource-talos` — Confirm patched binary architecture
  - `diff <original> <patched>` — Full diff for inclusion in RFC (already computed, but Task 1 captures it)

  **Known Error Messages** (from the code, for the Problem Statement):
  - Primary: `"recovered raw state does not byte-for-byte match the original raw state"` (rawstate.go turnaroundCheck)
  - Secondary: `"rawStateRecoverNatural cannot process Object values due to map vs object confusion"` (rawstate.go line 263-264)
  - These error strings are in the source code and can be verified by grepping the original rawstate.go

  **External References**:
  - `https://github.com/pulumi/pulumi-terraform-bridge` — Upstream bridge repo (RFC target)
  - `https://github.com/pulumiverse/pulumi-talos` — Affected provider repo
  - `pulumi-terraform-bridge v3.116.0` source on GitHub — for linking to specific lines in the unpatched code

  **WHY Each Reference Matters**:
  - Task 1 evidence provides the exact patch code to include in the RFC
  - Upstream repo links are needed for the References section
  - The RFC must be self-contained enough for a maintainer to understand and act on

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: RFC has all required sections
    Tool: Bash (grep)
    Preconditions: docs/bridge-bug-rfc.md exists
    Steps:
      1. Run: grep -c "## " docs/bridge-bug-rfc.md
      2. Run: grep "Root Cause" docs/bridge-bug-rfc.md | head -1
      3. Run: grep "Reproduction" docs/bridge-bug-rfc.md | head -1
      4. Run: grep "Proposed Fix" docs/bridge-bug-rfc.md | head -1
      5. Run: grep "Workaround" docs/bridge-bug-rfc.md | head -1
    Expected Result: >= 8 sections, Root Cause present, Reproduction present, Proposed Fix present, Workaround present
    Failure Indicators: Missing critical sections
    Evidence: .sisyphus/evidence/task-4-sections-verified.txt

  Scenario: RFC contains actual Go code patches
    Tool: Bash (grep)
    Preconditions: docs/bridge-bug-rfc.md exists
    Steps:
      1. Run: grep -c '```go' docs/bridge-bug-rfc.md
      2. Run: grep -c "inferRawStateDelta\|turnaroundCheck\|stripNulls" docs/bridge-bug-rfc.md
      3. Run: grep -c "timeouts\|timeout" docs/bridge-bug-rfc.md
    Expected Result: >= 3 Go code blocks, references key functions, mentions timeouts handling
    Failure Indicators: No Go code blocks, missing function references, no mention of root cause
    Evidence: .sisyphus/evidence/task-4-code-verified.txt

  Scenario: RFC has substantive depth (not a stub)
    Tool: Bash (wc)
    Preconditions: docs/bridge-bug-rfc.md exists
    Steps:
      1. Run: wc -w docs/bridge-bug-rfc.md
    Expected Result: >= 2000 words
    Failure Indicators: < 2000 words suggests insufficient depth for an RFC
    Evidence: .sisyphus/evidence/task-4-depth-check.txt

  Scenario: No personal paths or secrets
    Tool: Bash (grep)
    Preconditions: docs/bridge-bug-rfc.md exists
    Steps:
      1. Run: grep -c "yamer003\|/Users/" docs/bridge-bug-rfc.md
      2. Run: grep -cE "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" docs/bridge-bug-rfc.md
    Expected Result: 0 personal path matches, 0 IP address matches
    Failure Indicators: Any personal paths or IP addresses found
    Evidence: .sisyphus/evidence/task-4-secrets-check.txt
  ```

  **Evidence to Capture:**
  - [ ] `.sisyphus/evidence/task-4-sections-verified.txt` — Section presence verification
  - [ ] `.sisyphus/evidence/task-4-code-verified.txt` — Code block and function reference verification
  - [ ] `.sisyphus/evidence/task-4-depth-check.txt` — Word count check
  - [ ] `.sisyphus/evidence/task-4-secrets-check.txt` — Personal path and secrets scan

  **Commit**: YES (group with Task 3)
  - Message: `docs: add project lessons learned and bridge bug RFC`
  - Files: `docs/lessons-learned.md`, `docs/bridge-bug-rfc.md`
  - Pre-commit: `test -f docs/lessons-learned.md && test -f docs/bridge-bug-rfc.md`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify content exists in the documents (grep for key terms). For each "Must NOT Have": search documents for forbidden patterns. Check evidence files exist in `.sisyphus/evidence/`.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Content Quality Review** — `unspecified-high`
  Read both documents end-to-end. Check: accurate technical details, no hand-wavy descriptions, code blocks are syntactically valid, all sections have substantive content (not filler), markdown renders correctly. Check for AI slop: excessive hedging, generic advice, unnecessary caveats.
  Output: `Lessons Learned [PASS/FAIL] | RFC [PASS/FAIL] | Quality Issues [N] | VERDICT`

- [x] F3. **Source Accuracy QA** — `unspecified-high`
  For every code snippet in both documents: read the actual source file and verify the snippet matches. For every file path referenced: verify the file exists. For every claim about behavior: verify against the actual implementation.
  Output: `Code Snippets [N/N accurate] | File Paths [N/N valid] | Claims [N/N verified] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  Verify: All 4 bugs are covered in lessons learned. Bridge bug RFC has reproduction steps, root cause, patches, and proposed fix. Pro tips section exists with actionable bullets. No scope creep (documenting things not requested). macOS discovery is included.
  Output: `Bugs Covered [4/4] | RFC Sections [N/N] | Pro Tips [present/missing] | Scope [CLEAN/CREEP] | VERDICT`

---

## Commit Strategy

- **1**: `docs: add project lessons learned and bridge bug RFC` — `docs/lessons-learned.md`, `docs/bridge-bug-rfc.md`

---

## Success Criteria

### Verification Commands
```bash
test -f docs/lessons-learned.md && echo "EXISTS" || echo "MISSING"  # Expected: EXISTS
test -f docs/bridge-bug-rfc.md && echo "EXISTS" || echo "MISSING"   # Expected: EXISTS
grep -c "## Bug" docs/lessons-learned.md                             # Expected: >= 4
grep -c "## " docs/bridge-bug-rfc.md                                 # Expected: >= 5 (sections)
wc -w docs/lessons-learned.md                                        # Expected: >= 1500 words
wc -w docs/bridge-bug-rfc.md                                         # Expected: >= 2000 words
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] Both documents are well-structured, accurate, and useful
