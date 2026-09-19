# MARSEL ROAPP — MASTER PROJECT CONTROL

## Purpose
Единая контрольная точка проекта: техническое состояние RO App integration, качество данных, безопасность, бизнес-автоматизация, deployment и коммерческий контур MARSEL.

## Canonical state — 2026-09-20
- System: **MARSEL ROAPP** — единая каноническая система.
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Technical canonical branch: `main`
- Repository default branch: `main`.
- Current application/code checkpoint: **`2282ef546f755573fbbee8ea4c32e9ccf8ccacea`**.
- Canonical control plane: `.github/workflows/marsel-unified-control-plane.yml`
- Canonical control contract: `01_MASTER/MARSEL_ROAPP_CONTROL_PLANE_V2.md`
- ChatGPT operating protocol: `docs/MARSEL_CHATGPT_OPERATING_PROTOCOL.md`
- Repository validator: `scripts/marsel_control_plane_validate.py`
- Current integration mode: READ-ONLY.
- Owner MVP vertical slice is present in `web/index.html`, served at `/app`, with Supabase Auth/RLS integration.
- Production WRITE: DISABLED.

## Latest repository changes
Since the previously recorded application checkpoint `b29c80a9ec337111459ac22535ba67a529f251bb`, `main` advanced through four commits including the Gate A deployment verification workflow and Owner MVP contract tests. The current `main` checkpoint is `2282ef546f755573fbbee8ea4c32e9ccf8ccacea`.

## Latest verified CI evidence
- GitHub Actions run **35394220647**, workflow **MARSEL Unified Control Plane**, executed successfully on application/code checkpoint `3eae5f89317e0cc4e928f7c7331958baaa789bf8` on 2026-09-18.
- GitHub Actions run **35395707026**, workflow **MARSEL Execution Worker**, executed successfully on the same checkpoint; its READ-ONLY worker, RO App probe, auxiliary health probe, evidence upload and production-safety assertion succeeded.
- GitHub Actions run **35390149457**, MARSEL Production Gate, completed **skipped**. This is not production-readiness evidence.
- Railway production deployment for the previous `main` checkpoint `b29c80a9ec337111459ac22535ba67a529f251bb` is **VERIFIED**: deployment `c96d55ad-5966-48a4-9506-90ba20cd793c` completed `SUCCESS` on Railway production. The post-deployment Gate A smoke workflow has been merged but has not yet been run against the current deployment, so current `/health`, `/ready`, `/app` and `/app/config` end-to-end verification remains **NOT VERIFIED**.
- Owner UI `/app` end-to-end browser verification is still **NOT VERIFIED**.
- No production WRITE was executed.

## Branch state
- `main` is the only technical canonical branch.
- `Main` and `main-MARSEL-ROAPP` are non-canonical stale branches, each 2 commits behind current `main` and 0 commits ahead.
- `main-MARSEL-ROAPP-PROTECTION` is a non-canonical stale branch, 4 commits behind current `main` and 0 commits ahead.
- Compatibility/snapshot branches must not become independent development lines. Deletion/retirement is a separate destructive safety-gated action and was NOT performed.

## Mandatory execution sequence
1. READ current `main` and live project state.
2. Verify the latest checkpoint and do not restart from historical branches or closed stages.
3. ANALYZE only newly changed or currently unverified items.
4. Execute the highest-priority safe READ-ONLY correction available.
5. VERIFY with direct read-back/evidence.
6. QA: BEFORE → ACTION → AFTER → DIFF → INTEGRITY → EVIDENCE.
7. Record repository-state changes here.
8. Continue automatically to the next safe task.
9. Stop only at a safety gate requiring external authorization, secret access, irreversible WRITE, or unavailable account-level control; mark it BLOCKED/NOT VERIFIED.

## Status rules
- VERIFIED = current direct evidence.
- PARTIAL = some evidence exists but the gate is incomplete.
- BLOCKED = required external authorization/control is unavailable.
- NOT VERIFIED = no current direct evidence.
- PROPOSED = planned only.
- Historical, synthetic, repository-only or assumed evidence never becomes VERIFIED.

## Current verified repository state
- `main` is the technical canonical branch.
- GitHub default branch is `main`.
- Compatibility branches listed above are stale relative to current `main`; no branch content was modified or deleted in this audit.
- Production WRITE remains disabled and fail-closed.
- Existing backup/export and isolated restore/integrity evidence is not to be repeated without a reason.
- Observability/correlation is already recorded as verified under Issue #134.
- Unified-control-plane CI evidence is verified on an earlier application/code checkpoint; current Railway deployment is separately verified on `b29c80a9ec337111459ac22535ba67a529f251bb`.

## Hard blockers for production readiness
1. Fresh authorized RO App GET evidence for complete applicable API/entity coverage.
2. Fresh authoritative warehouse/stock contract evidence.
3. Current duplicate/reference reconciliation.
4. Credential-exposure remediation under Issue #23.
5. Official RO App MCP authorization.
6. Gmail OAuth user authorization if the integration remains in scope.
7. Verified production deployment target and direct health/end-to-end evidence.
8. Current Wix ↔ RO App reconciliation, mutation dry-run, idempotency and rollback evidence.
9. GitHub account-level security/branch administration under Issue #91.
10. Production WRITE remains disabled until every applicable safety gate passes and explicit authorization exists.

## Safety
Never claim backup, restore, reconciliation, security rotation, OAuth, MCP authorization, deployment, synchronization or WRITE readiness without direct evidence. Never guess an API endpoint or identifier. Never execute a production mutation merely to make a test green. Never expose or commit `ROAPP_API_KEY`.

## Continuation rule
Every execution starts from this file and the latest verified `main` checkpoint. Verify current evidence, fix the highest-priority safe defect, verify the result, update this checkpoint when repository state changes, and continue. If an external authorization or secret is required and unavailable to connected tools, mark the gate BLOCKED/NOT VERIFIED rather than simulating completion.
