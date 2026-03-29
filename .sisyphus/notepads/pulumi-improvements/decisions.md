# Decisions — Pulumi Improvements

## 2026-03-29 Implementation Order
- Script Extraction first (lowest risk)
- CrossGuard second (additive, low risk)
- ComponentResource last (highest risk due to URN changes)


## 2026-03-29 — F2 security review decision
- Verdict for Pulumi Improvements F2: **REJECT**.
- Blocking rationale: (1) shell injection in the new OpenBao post-start templating path, and (2) incomplete / fail-open CrossGuard prod enforcement.

## 2026-03-29 F3 Architecture Review Position
- Keep the flat top-level `ComponentResource` hierarchy; for this stack, phase-oriented orchestration is a better fit than nesting components into each other.
- Keep alias-based child reparenting via `pulumi.Alias(parent=pulumi.ROOT_STACK_RESOURCE)` as the correct URN migration approach for the function-to-component conversion.
- Do not approve the improvement set until the Flux/test dependency gap and CrossGuard coverage gaps are closed.
