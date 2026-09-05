# 05_MARSEL_CURRENT_STATE

**Role:** single living project checkpoint. Update after every material verified change.

## DATE
2026-09-05

## CURRENT VERSION
MARSEL ROAPP unified control plane with production-safety hardening, canonical GitHub governance, automated evidence orchestration, deterministic control-agent state transitions, and fail-closed production gating.

## CONTROL CHECKPOINT
- Canonical repository: `atalanrafael-jpg/MARSEL-Ro-app`.
- Canonical branch: `main`.
- Current canonical `main` HEAD verified: this checkpoint commit's parent is `f8558e5beefbe6cf2c37b064ed5805aac33c7300`; the live branch subsequently advanced to this documentation reconciliation commit.
- Production WRITE remains disabled.
- Live GitHub branch metadata reports `main` as **unprotected**; required status checks are not configured at branch level. This is an account/repository administration blocker, not a code failure.

## LATEST LIVE GATE FINDING
- The latest warehouse evidence job reached the secret preflight and failed at `Verify RO App secret` because `ROAPP_API_KEY` was not available to the workflow.
- Because the credential preflight failed, the documented warehouse diagnostic, read-only invariant verification, and evidence upload did not run.
- The dependent Production Gate run was `skipped`; this is not production-readiness evidence and must not be counted as PASS.
- No fallback, synthetic key, bypass, or production WRITE was introduced.

## VERIFIED REPOSITORY FACTS
- PR #114 (`fix: restore verified RO App warehouse contract`) was merged into `main` on 2026-09-05. It aligns the canonical warehouse diagnostic with the documented `GET /warehouse/` endpoint and adds regression coverage.
- PR #113 (Control Agent v3) is closed and not merged; its changes must not be treated as part of canonical `main`.
- PR #112 (optional Apple Core AI Torch integration) remains open and is explicitly NOT HARDWARE-VERIFIED; it is isolated and does not change production requirements or introduce live RO App writes.
- The latest commit sequence on `main` adds a deterministic control-agent state model, strict sequential stage transitions, write-gate tests, dependency/lock alignment, and final audit reconciliation.
- CodeQL is currently executing on the current main lineage.

## WAREHOUSE CONTRACT
- The authoritative RO App documentation distinguishes the general v2 API root from the documented warehouse endpoint.
- The previous `/v2/warehouse/` probe returned HTTP 404; the documented `/warehouse/` route was the basis for the correction in merged PR #114.
- Code-level correction is present on `main`.
- Fresh live evidence is still required before the warehouse evidence gate can be marked VERIFIED.

## RO APP STATUS
🟢 **VERIFIED HISTORICAL LIVE ACCESS**
- `GET /v2/orders` previously returned HTTP 200 in a real READ-ONLY smoke test.
- Historical order audit: 4,373 orders; 4,373 unique IDs; 0 duplicate IDs; 0 missing IDs; 0 missing client IDs; 0 missing statuses for that run.
- Historical V20.8 detail audit: 6,820 detail requests; 0 detail failures; 0 writes.

🟡 **PARTIAL**
- Historical API inventory/entity coverage remains historical evidence, not proof of current completeness.
- Product-code collision findings remain review-only; no automatic deletion/merge is permitted.
- Supabase security advisor previously reported no security lints.
- Supabase performance advisor previously reported 12 unused-index INFO findings; these are optimization candidates, not automatically removable objects.

🔴 **BLOCKED / NOT VERIFIED**
- Complete production backup is not proven.
- Independently tested restore/integrity is not proven.
- Fresh current-main evidence bundle is not established as production-gate evidence.
- Gmail OAuth user-authorized verification is not complete.
- Official RO App MCP authorization is not complete.
- Credential-exposure remediation tracked by Issue #23 is not closed by direct evidence.
- GitHub `main` branch protection is currently OFF; required status checks are not configured.
- Account-level secret-scanning/push-protection, production environment controls, and Copilot controls are not independently verified through the available connector surface.
- Production WRITE is not authorized.

## CURRENT EXECUTION QUEUE
1. Provide `ROAPP_API_KEY` to the GitHub Actions repository/environment secret store, then rerun the warehouse live evidence workflow.
2. Verify the fresh READ-ONLY warehouse result and evidence artifact on current `main`.
3. Prove complete backup/export and independently tested restore/integrity.
4. Complete current API/entity verification from authoritative contracts and verified identifiers.
5. Complete Gmail OAuth read-only user authorization test.
6. Complete official RO App MCP authorization verification.
7. Complete credential-exposure remediation evidence for Issue #23.
8. Enable and verify GitHub `main` protection, secret scanning/push protection, production environment controls, and required status checks through account/repository administration.
9. Reconcile stale/open remediation PRs against current `main`; do not merge stale branches without revalidation.
10. Review the 12 Supabase unused-index INFO findings using actual query workload before any index removal.
11. Only after all applicable evidence gates pass, evaluate production safety gate. Production WRITE remains disabled until explicit authorization.

## SAFETY
- `MARSEL_WRITE_APPROVED=false` remains mandatory.
- Unified Control Plane live checks are GET-only/read-only.
- Evidence Orchestrator is fail-closed and rejects synthetic evidence.
- No production write, credential creation, reviewer fabrication, bypass, or synthetic evidence is authorized.

## REQUIRED UPDATE RULE
After every material change:
`OBSERVE -> MEASURE -> FIND -> FIX -> TEST -> VERIFY -> DOCUMENT -> MONITOR`

The newest verified evidence supersedes older contradictory evidence; older records remain history and are not silently rewritten.
