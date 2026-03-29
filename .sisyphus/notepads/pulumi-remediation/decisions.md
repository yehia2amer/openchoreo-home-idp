# Decisions — Pulumi Remediation

## 2026-03-29 Session Start
- E2E tests ONLY — no unit tests (user explicit constraint)
- NO resource logical name changes (would cause URN breakage)
- NO Helm release name changes
- NO new features, resources, or config keys
- P0-4 (secret serialization in dynamic provider state) is OUT OF SCOPE — too risky
- Embedded bash script in values/openbao.py stays as-is (scope creep to extract)
