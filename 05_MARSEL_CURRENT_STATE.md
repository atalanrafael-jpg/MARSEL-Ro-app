# 05_MARSEL_CURRENT_STATE

**Role:** single living project checkpoint. Update after every material verified change.

## DATE
2026-09-07

## CURRENT VERSION
MARSEL ROAPP unified control plane with production-safety hardening, canonical GitHub governance, automated evidence orchestration, deterministic control-agent state transitions, fail-closed production gating, dependency/lock alignment, security hardening, and an isolated optional Apple Core AI conversion path.

## CONTROL CHECKPOINT
- Canonical repository: `atalanrafael-jpg/MARSEL-Ro-app`.
- Canonical branch: `main`.
- Current canonical `main` HEAD: `5779c4d7d78b6bdb139b9d1fff3792b8149eac37`.
- This checkpoint commit reconciles the state document with the preceding task-registry reconciliation commit `c015e2bc2cf31909ddbb103119cf4fcf2e40d2a6`.
- Production WRITE remains disabled.
- Live repository metadata reports `main` as **unprotected**; required status checks are not configured at branch level. This is an account/repository administration blocker, not a code failure.

## LATEST VERIFIED CHANGE
- PR #130 (`test(control-agent): fix dynamic import registration on current main`) was merged on 2026-09-07. It fixes current-main test collection by registering the dynamically loaded control-agent module in `sys.modules` before `exec_module()`.
- Commit `c015e2bc2cf31909ddbb103119cf4fcf2e40d2a6` reconciled the MARSEL task registry after PR #130.
- Commit `5779c4d7d78b6bdb139b9d1fff3792b8149eac37` reconciled this current-state checkpoint with that lineage.
- The dependency alignment from PR #125 and the security hardening from PR #129 are present in the current commit lineage.
- No production WRITE was introduced by these changes.

## LATEST VERIFIED CI
- Test workflow run `34087800404` completed successfully on current `main` HEAD `5779c4d7d78b6bdb139b9d1fff3792b8149eac37`.
- The run's test job completed successfully; the verified test/evidence artifact was `marsel-test-evidence-34087800404` with SHA-256 `ae96d55fd3e98778e09546c96d1db5c8b5326c2db216af099ecd4c524d04eae5`.
- This CI result proves the repository test/build path for that run; it does not prove current live RO App API access, backup/restore, OAuth, MCP authorization, or production readiness.

## LATEST LIVE GATE FINDING
- The latest documented warehouse evidence gate failed during the RO App secret preflight because `ROAPP_API_KEY` was unavailable to the workflow.
- Because the credential preflight failed, the documented warehouse diagnostic, read-only invariant verification, and evidence upload did not run.
- The dependent Production Gate run was skipped; this is not production-readiness evidence and must not be counted as PASS.
- No fallback, synthetic key, bypass, or production WRITE was introduced.

## WAREHOUSE CONTRACT
- The authoritative RO App documentation distinguishes the general v2 API root from the documented warehouse endpoint.
- The previous `/v2/warehouse/` probe returned HTTP 404; the documented `/warehouse/` route was the basis for the correction in merged PR #114.
- Code-level correction is present on `main`.
- A repository evidence file records a READ-ONLY warehouse-list contract PASS observed at `2026-09-05T08:41:00Z`; this is historical evidence and does not replace the blocked fresh live gate.
- Fresh current live evidence is still required before the warehouse evidence gate can be marked CURRENT/VERIFIED.

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
- Apple Core AI Torch integration is configured and merged, but hardware/runtime verification remains outstanding.

🔴 **BLOCKED / NOT VERIFIED**
- Complete production backup is not proven.
- Independently tested restore/integrity is not proven.
- Fresh current-main unified evidence bundle is not established as production-gate evidence.
- Gmail OAuth user-authorized verification is not complete.
- Official RO App MCP authorization is not complete.
- Credential-exposure remediation tracked by Issue #23 is not closed by direct evidence.
- GitHub `main` branch protection is currently OFF; required status checks are not configured.
- Account-level secret-scanning/push-protection, production environment controls, and Copilot controls are not independently verified through the available connector surface.
- Apple Core AI hardware/runtime gate is not verified.
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
9. Reconcile stale/open remediation issues and PRs against current `main`; do not merge stale branches without revalidation. In particular, open draft PRs #127, #128, and #123 are based on older `main` snapshots and require rebase/revalidation before consideration.
10. Review the 12 Supabase unused-index INFO findings using actual query workload before any index removal.
11. On a physical Apple Silicon host, run the documented Core AI conversion/runtime verification and attach fresh evidence; do not claim hardware verification from CI alone.
12. Only after all applicable evidence gates pass, evaluate production safety gate. Production WRITE remains disabled until explicit authorization.

## SAFETY
- `MARSEL_WRITE_APPROVED=false` remains mandatory.
- Unified Control Plane live checks are GET-only/read-only.
- Evidence Orchestrator is fail-closed and rejects synthetic evidence.
- No production write, credential creation, reviewer fabrication, bypass, or synthetic evidence is authorized.

## REQUIRED UPDATE RULE
After every material change:
`OBSERVE -> MEASURE -> FIND -> FIX -> TEST -> VERIFY -> DOCUMENT -> MONITOR`

The newest verified evidence supersedes older contradictory evidence; older records remain history and are not silently rewritten.
