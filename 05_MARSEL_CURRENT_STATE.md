# 05_MARSEL_CURRENT_STATE

**Role:** single living project checkpoint. Update after every material verified change.

## DATE
2026-09-04

## CURRENT VERSION
MARSEL ROAPP unified control plane with production-safety hardening, canonical GitHub governance, automated evidence orchestration, and fail-closed production gating.

## CONTROL CHECKPOINT
- Canonical repository: `atalanrafael-jpg/MARSEL-Ro-app`.
- Canonical branch: `main`.
- Current canonical `main` HEAD observed before this remediation: `745a522c3b95fe14216963d126d66080df07c816`.
- Production WRITE remains disabled.

## VERIFIED REPOSITORY FACTS
- PR #113 Control Agent head `294a7b9281726759dc6e817ae97f706071b26103` passed the current PR-triggered CI suite and was moved from Draft to Ready for review.
- PR #113 is open, mergeable and not merged; human review remains required.
- PR #114 was created from current `main` to correct the warehouse-list contract implementation. It is open and not merged; live CI verification remains required.
- Historical RO App evidence remains valid only for the runs that produced it.

## WAREHOUSE CONTRACT CORRECTION
- The current RO App API reference uses `https://api.roapp.io/v2` as the general v2 base, while the documented Get Warehouses method uses `GET https://api.roapp.io/warehouse/`.
- The warehouse endpoint accepts `type` (default `product`) and optional `branch_id`.
- The previous `/v2/warehouse/` probes returned HTTP 404; the undocumented compatibility route `/warehouse/` returned live data.
- PR #114 changes the canonical diagnostic to use the documented `/warehouse/` endpoint from the API root and adds regression tests.
- No undocumented route is promoted to PASS merely because it responds successfully.
- The warehouse gate remains NOT VERIFIED until a fresh authorized READ-ONLY Actions run produces and validates the evidence artifact.

## RO APP STATUS
🟢 **VERIFIED HISTORICAL LIVE ACCESS**
- `GET /v2/orders` previously returned HTTP 200 in a real READ-ONLY smoke test.
- Historical order audit: 4,373 orders; 4,373 unique IDs; 0 duplicate IDs; 0 missing IDs; 0 missing client IDs; 0 missing statuses for that run.
- Historical V20.8 detail audit: 6,820 detail requests; 0 detail failures; 0 writes.

🟡 **PARTIAL**
- Historical API inventory and entity coverage remain historical evidence, not proof of current completeness.
- Product-code collision findings remain review-only; no automatic deletion/merge is permitted.

🔴 **BLOCKED / NOT VERIFIED**
- Complete production backup is not proven.
- Restore test is not proven.
- Fresh current-main Unified Control Plane result is not established by this checkpoint.
- Warehouse-list contract requires fresh live evidence after PR #114.
- Gmail OAuth user-authorized verification is not complete.
- Official RO App MCP authorization is not complete.
- Credential-exposure remediation tracked by Issue #23 is not closed by direct evidence.
- Main branch protection/account-level GitHub controls require account authorization outside the current repository connector surface.
- Production WRITE is not authorized.

## CURRENT EXECUTION QUEUE
1. Validate PR #114 with fresh CI and, when authorized, inspect its real warehouse evidence artifact.
2. Close the warehouse contract issues only after direct evidence proves the documented endpoint and response schema.
3. Verify complete backup/export and independently tested restore/integrity.
4. Complete current API/entity verification from authoritative contracts and verified identifiers.
5. Complete Gmail OAuth read-only user authorization test.
6. Complete official RO App MCP authorization verification.
7. Complete credential-exposure remediation evidence for Issue #23.
8. Verify GitHub `main` protection and required status checks through account-level settings.
9. Reconcile stale/open remediation PRs against current `main`; do not merge stale branches without revalidation.
10. Only after all applicable evidence gates pass, evaluate production safety gate. Production WRITE remains disabled until explicit authorization.

## SAFETY
- `MARSEL_WRITE_APPROVED=false` remains mandatory.
- Unified Control Plane live checks are GET-only/read-only.
- Evidence Orchestrator is fail-closed and rejects synthetic evidence.
- No production write, credential creation, reviewer fabrication, bypass, or synthetic evidence is authorized.

## REQUIRED UPDATE RULE
After every material change:
`OBSERVE -> MEASURE -> FIND -> FIX -> TEST -> VERIFY -> DOCUMENT -> MONITOR`

The newest verified evidence supersedes older contradictory evidence; older records remain history and are not silently rewritten.
