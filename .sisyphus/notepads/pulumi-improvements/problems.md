# Problems — Pulumi Improvements

(none yet)


## 2026-03-29 Open issues from F1 review
- Fix integration test mismatches before relying on `IntegrationTests` as the final gate for Flux-enabled or External-Secrets-dependent stacks.
- Tighten `pulumi/policy/__main__.py` so the policy pack enforces the current codebase rather than an older seed/Helm footprint.


## 2026-03-29 — F2 unresolved problems
- Existing secret-handling debt remains in changed component files where `root_token` is passed into Pulumi dynamic-resource inputs (`prerequisites.py`, `integration_tests.py`). This review did not treat it as a new T1-T9 regression, but it remains worth addressing separately.
