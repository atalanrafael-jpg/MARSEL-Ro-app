# MARSEL ROAPP — MASTER PROJECT CONTROL

## Purpose
Единая контрольная точка проекта: техническое состояние RO App integration, качество данных, безопасность, бизнес-автоматизация, deployment и коммерческий контур MARSEL.

## Canonical state — 2026-09-18
- System: **MARSEL ROAPP** — единая каноническая система.
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Technical canonical branch: `main`
- Current main HEAD observed before this control-document commit: **`0e26c00b488ccbc02144765c4388090f20516dda`**
- Repository default branch reported by GitHub: `main-MARSEL-ROAPP` (legacy/default branch; no longer canonical).
- Canonical control plane: `.github/workflows/marsel-unified-control-plane.yml`
- Canonical control contract: `01_MASTER/MARSEL_ROAPP_CONTROL_PLANE_V2.md`
- ChatGPT operating protocol: `docs/MARSEL_CHATGPT_OPERATING_PROTOCOL.md`
- Repository validator: `scripts/marsel_control_plane_validate.py`
- Current integration mode: READ-ONLY.
- Production WRITE: DISABLED.

## Latest verified action
- Corrected the unified workflow evidence builder so a PASS status is emitted only when the quality gate succeeds and all required evidence files exist.
- Corrected canonical self-check/branch semantics so the technical canonical branch is `main`.
- Verified the corrected workflow and canonical self-check content on `main`.
- Added the ChatGPT operating protocol defining request routing, evidence hierarchy, tool/app roles, launch stages and owner-vs-agent responsibilities.
- Corrected the control-plane validator to accept the canonical `Technical canonical branch: main` wording.
- The current `main` HEAD is `0e26c00...`; GitHub Actions shows successful push-triggered workflow executions for this commit, but the available evidence has not yet directly verified a fresh successful execution of the specific `MARSEL Unified Control Plane` workflow.

## Mandatory execution sequence
1. READ current `main` and live project state.
2. Verify the latest checkpoint and do not restart from historical branches or closed stages.
3. ANALYZE only newly changed or currently unverified items.
4. Execute the highest-priority safe READ-ONLY correction available.
5. VERIFY with direct read-back/evidence.
6. QA: BEFORE → ACTION → AFTER → DIFF → INTEGRITY → EVIDENCE.
7. Record the new checkpoint here when the repository state changes.
8. Continue automatically to the next safe task.
9. Stop only at a safety gate requiring external authorization, secret access, irreversible WRITE, or unavailable account-level control; mark it BLOCKED/NOT VERIFIED.

## Status rules
- VERIFIED = current direct evidence.
- PARTIAL = some evidence exists but the gate is incomplete.
- BLOCKED = required external authorization/control is unavailable.
- NOT VERIFIED = no current direct evidence.
- PROPOSED = planned only.
- Never convert historical, synthetic, repository-only or assumed evidence into VERIFIED.

## Verified current repository state
- `main` is the technical canonical branch of the MARSEL ROAPP system.
- `main-MARSEL-ROAPP` is retained as a legacy branch pending administrative cleanup.
- GitHub currently reports `main-MARSEL-ROAPP` as the repository default branch; changing the default to `main` remains an account/repository administration action not exposed by the available connector.
- `main` and `main-MARSEL-ROAPP` currently point to the same observed commit `0e26c00...`.
- Production WRITE remains disabled and fail-closed.
- Existing backup/export and isolated restore/integrity evidence is not to be repeated without a reason.
- Observability/correlation is already recorded as verified under Issue #134.
- CI PASS must be based on actual current workflow evidence, not repository configuration alone.

## Hard blockers for production readiness
1. Fresh authorized RO App GET evidence for complete applicable API/entity coverage.
2. Fresh authoritative warehouse/stock contract evidence.
3. Current duplicate/reference reconciliation.
4. Credential-exposure remediation under Issue #23.
5. Official RO App MCP authorization.
6. Gmail OAuth user authorization if the integration remains in scope.
7. Verified production deployment target if required.
8. Current Wix ↔ RO App reconciliation, mutation dry-run, idempotency and rollback evidence.
9. GitHub account-level security/branch administration under Issue #91.
10. Production WRITE remains disabled until every applicable safety gate passes and explicit authorization exists.

## Safety
Never claim backup, restore, reconciliation, security rotation, OAuth, MCP authorization, deployment, synchronization or WRITE readiness without direct evidence. Never guess an API endpoint or identifier. Never execute a production mutation merely to make a test green. Never expose or commit `ROAPP_API_KEY`.

## Continuation rule
Every execution starts from this file and the latest verified `main` checkpoint. Verify current evidence, fix the highest-priority safe defect, verify the result, update this checkpoint, and continue. If an external authorization or secret is required and unavailable to connected tools, mark the gate BLOCKED/NOT VERIFIED rather than simulating completion.
