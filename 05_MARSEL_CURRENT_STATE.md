# 05_MARSEL_CURRENT_STATE

**Role:** single living project checkpoint. Update after every material verified change.

## DATE
2026-08-30

## CURRENT VERSION
MARSEL/ROAPP unified control plane with production-safety hardening, canonical GitHub governance, automated evidence orchestration, and fail-closed production gating.

## CONTROL CHECKPOINT
Current `main` checkpoint: `1ee6e6027fea72ffafbd9044c6253666ebadbe55` — `ci: automate MARSEL evidence collection and fail-closed inventory` (merged PR #72).

## SYSTEM MODEL
**MARSEL = business contour + ROAPP = technical contour → one unified system → one canonical `main` control plane.**

## VERIFIED LIVE / REPOSITORY FACTS
- Repository `atalanrafael-jpg/Ro-app` is accessible with admin/maintain/push permissions through the connected GitHub integration.
- The repository is public, active, and `main` is the default branch.
- The Unified Control Plane is configured for push to `main`, pull requests, manual dispatch, and a 6-hour schedule.
- The Production Gate is fail-closed and runs automatically only after a successful Unified Control Plane run, or manually when an explicit upstream run ID is supplied.
- The Evidence Orchestrator is now automated and fail-closed; it requires eight named evidence artifacts and verifies read-only invariants before accepting production evidence.

## RO APP STATUS
🟢 **VERIFIED HISTORICAL LIVE ACCESS**
- `GET /v2/orders` has previously returned HTTP 200 in a real read-only smoke test.
- Historical order audit: 4,373 orders; 4,373 unique IDs; 0 duplicate IDs; 0 missing IDs; 0 missing client IDs; 0 missing statuses for that run.
- Historical V20.8 detail audit: 6,820 detail requests; 0 detail failures; 0 writes.

🟡 **PARTIAL**
- Historical API inventory: 124 operations / 45 GET probes.
- Full current API/entity completeness is not yet proven by a fresh complete evidence set.
- Product-code collision review remains a data-quality classification task; historical audit identified 11 duplicate-code groups without assuming uniqueness or performing deletion.

🔴 **BLOCKED / NOT VERIFIED**
- Complete production backup is not proven.
- Restore test is not proven.
- Production WRITE is not authorized.
- Credential-exposure remediation in Issue #23 is not closed until direct rotation and repository/history/log/artifact verification is proven.
- Fresh live warehouse evidence for the current control-plane revision is not yet verified.
- Gmail OAuth user-authorized verification is not complete.
- Official RO App MCP authorization is not complete.

## SAFETY
- Production mutation remains explicitly disabled: `MARSEL_WRITE_APPROVED=false` in the Production Gate.
- Unified Control Plane live checks are GET-only/read-only.
- Production Gate requires a successful upstream Unified Control Plane run and fail-closed evidence validation.
- Evidence Orchestrator validates `readonly=true`, `write_requests_made=0`, and `ro_app_data_mutated=false` for required evidence.
- No synthetic evidence is accepted as production evidence.

## CURRENT OPEN BLOCKERS
1. Generate and verify a fresh successful Unified Control Plane evidence set on current `main`.
2. Prove complete backup/export and independently tested restore/integrity.
3. Complete current API/entity verification from authoritative contracts and verified identifiers.
4. Obtain fresh documented warehouse live evidence.
5. Classify the 11 product-code collision groups; no automatic deletion/merge.
6. Complete Gmail OAuth read-only user authorization test.
7. Complete official RO App MCP authorization verification.
8. Complete credential-exposure remediation evidence for Issue #23.
9. Reconcile overlapping governance/remediation PRs against current `main`.
10. Only after all required evidence passes: evaluate production safety gate; production WRITE remains disabled until explicit authorization.

## REQUIRED UPDATE RULE
After every material change:
`OBSERVE -> MEASURE -> FIND -> FIX -> TEST -> VERIFY -> DOCUMENT -> MONITOR`

The newest verified evidence supersedes older contradictory evidence; older records remain history and are not silently rewritten.
