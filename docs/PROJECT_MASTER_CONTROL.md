# MARSEL ROAPP — MASTER PROJECT CONTROL

## Purpose
Единая контрольная точка проекта: техническое состояние RO App integration, качество данных, безопасность, бизнес-автоматизация, deployment и коммерческий контур MARSEL.

## Canonical state — 2026-09-14
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Canonical branch: `main-MARSEL-ROAPP`
- Current canonical HEAD: `b8056ab440a084d31ccd6b6e5b4b1a9cb8a9dd2c`
- Canonical control plane: `.github/workflows/marsel-unified-control-plane.yml`
- Current integration mode: READ-ONLY.
- Production WRITE: DISABLED.

## Verified current state
- Repository structure self-check: PASS.
- GitHub ruleset `main MARSEL ROAPP PROTECTION` (ID `21230907`): active and targets `refs/heads/main-MARSEL-ROAPP`.
- Required ruleset checks include `test`, `CodeQL`, secret guard, RO App API V2 guard, MCP production readiness, release readiness and Unified Control Plane.
- Current `test` run on HEAD `b8056ab` succeeded.
- Current `MARSEL Language Quality` run on HEAD `b8056ab` succeeded.
- Current `MARSEL release readiness` run `34813759927` failed closed because `backup_evidence.json` is absent.
- Current `MARSEL Unified Control Plane` run `34813759796` failed at `Verify RO App secret`; subsequent live audits were correctly skipped.
- Current backup-evidence producer run `34813780085` was skipped because its prerequisite Unified Control Plane run did not succeed.
- Supabase project `wdbytmvzuensuuoquvav` is `ACTIVE_HEALTHY`; security advisor currently reports no findings. Performance advisor reports 12 unused-index informational findings; no index is removed automatically.
- No Vercel project is currently visible in the connected Vercel account.
- No Railway project is currently visible in the connected Railway account.

## Hard blockers for 100% production readiness
1. `ROAPP_API_KEY` is not available to the canonical GitHub Actions workflow at current HEAD. The workflow therefore cannot perform fresh authorized RO App GET audits. The secret must be rotated/verified through approved secret storage; the value must never be committed or sent in chat.
2. Full current RO App backup/export and independent restore/integrity evidence are not proven.
3. Complete current API/entity coverage is not proven.
4. Warehouse/stock live contract is not proven with fresh authoritative evidence.
5. Current duplicate/reference reconciliation is not closed.
6. Credential-exposure remediation remains open under Issue #23.
7. Official RO App MCP authorization is not independently verified.
8. Gmail OAuth requires actual user authorization if this integration remains in scope.
9. A production deployment target is not configured in Vercel or Railway; therefore application installation/deployment is NOT VERIFIED.
10. Production WRITE remains disabled until every applicable safety gate passes and explicit authorization exists.

## Safety
Never claim backup, restore, reconciliation, security rotation, OAuth, MCP authorization, deployment, synchronization or WRITE readiness without direct evidence. Never guess an API endpoint or identifier. Never execute a production mutation merely to make a test green. Never expose or commit `ROAPP_API_KEY`.

## Continuation rule
Every execution starts from this file and the current `main-MARSEL-ROAPP` checkpoint. Verify current CI/live evidence, fix the highest-priority safe defect, verify the result, document the checkpoint, and continue. If an external authorization or secret is required and unavailable to the connected tools, mark the gate `BLOCKED` rather than simulating completion.
