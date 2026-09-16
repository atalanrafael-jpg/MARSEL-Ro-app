# MARSEL ROAPP — MASTER PROJECT CONTROL

## Purpose
Единая контрольная точка проекта: техническое состояние RO App integration, качество данных, безопасность, бизнес-автоматизация, deployment и коммерческий контур MARSEL.

## Canonical state — 2026-09-16
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Canonical branch: `main-MARSEL-ROAPP`
- Canonical code HEAD before this control-document sync: `ec5876ecb44891b0d468a73d1ad7888d8ccfa783`
- Latest control-document sync commit: `5d06460d202897dbfc91484a9110d58c9b132606`
- Canonical control plane: `.github/workflows/marsel-unified-control-plane.yml`
- Current integration mode: READ-ONLY.
- Production WRITE: DISABLED.

## Verified current state
- Canonical branch `main-MARSEL-ROAPP` is the repository default branch.
- The code state immediately before this documentation-only sync was `ec5876ecb44891b0d468a73d1ad7888d8ccfa783`, whose parent canonical update was PR #173: OpenAI Python requirement `>=3.13.0,<4`.
- `README.md` identifies `main-MARSEL-ROAPP` as the canonical branch and the unified control plane as the canonical control mechanism.
- GitHub ruleset `main MARSEL ROAPP PROTECTION` (ID `21230907`) is documented as active and targeting `refs/heads/main-MARSEL-ROAPP`; account-level enforcement controls still require independent administration verification.
- Production WRITE remains disabled.
- Backup/export and isolated restore/integrity are recorded as already verified in the project control issues; they are not repeated merely because other gates remain open.
- Supabase project health and external deployment status remain subject to their connected-account evidence and are not treated as production deployment proof.

## Hard blockers for 100% production readiness
1. `ROAPP_API_KEY` is not available to the canonical GitHub Actions workflow for fresh authorized RO App GET audits. The secret must be rotated/verified through approved secret storage; the value must never be committed or sent in chat.
2. Complete current API/entity coverage is not proven with fresh authorized evidence.
3. Warehouse/stock live contract is not proven with fresh authoritative evidence.
4. Current duplicate/reference reconciliation is not closed.
5. Credential-exposure remediation remains open under Issue #23.
6. Official RO App MCP authorization is not independently verified.
7. Gmail OAuth requires actual user authorization if this integration remains in scope.
8. A production deployment target is not verified as configured in Vercel or Railway.
9. Current Wix ↔ RO App reconciliation, mutation dry-run, idempotency and rollback evidence remain open under the production-gate issues.
10. GitHub account-level security controls and branch hygiene requiring administration remain open under Issue #91.
11. Production WRITE remains disabled until every applicable safety gate passes and explicit authorization exists.

## Safety
Never claim backup, restore, reconciliation, security rotation, OAuth, MCP authorization, deployment, synchronization or WRITE readiness without direct evidence. Never guess an API endpoint or identifier. Never execute a production mutation merely to make a test green. Never expose or commit `ROAPP_API_KEY`.

## Continuation rule
Every execution starts from this file and the current `main-MARSEL-ROAPP` checkpoint. Verify current CI/live evidence, fix the highest-priority safe defect, verify the result, document the checkpoint, and continue. If an external authorization or secret is required and unavailable to the connected tools, mark the gate `BLOCKED` rather than simulating completion.
