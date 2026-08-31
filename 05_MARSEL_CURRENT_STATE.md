# 05_MARSEL_CURRENT_STATE

**Role:** single living project checkpoint. Update after every material verified change.

## DATE
2026-08-31

## CURRENT VERSION
MARSEL/ROAPP unified control plane with production-safety hardening, canonical GitHub governance, automated evidence orchestration, and fail-closed production gating.

## CONTROL CHECKPOINT
Current `main` checkpoint: `0df6aae4bc465407e93e94b48846ffb7d6b48aaf`.

The V20.47 warehouse diagnostic naming drift has been corrected and the superseded V20.47 script removed. A fresh Unified Control Plane run on this exact checkpoint remains required before any readiness conclusion.

## SYSTEM MODEL
**MARSEL = business contour + ROAPP = technical contour → one unified system → one canonical `main` control plane.**

## VERIFIED LIVE / REPOSITORY FACTS
- Repository `atalanrafael-jpg/Ro-app` is accessible through the connected GitHub integration.
- The repository is public, active, and `main` is the default branch.
- The Unified Control Plane is configured for push to `main`, pull requests, manual dispatch, and a 6-hour schedule.
- Production Gate is fail-closed and production WRITE remains disabled.
- Historical RO App evidence remains valid only for the runs that produced it.
- The latest verified warehouse diagnostic tested the documented `/v2/warehouse/` forms and received HTTP 404; this does not authorize promotion of any undocumented compatibility route.

## CANONICALIZATION CORRECTION
- Canonical warehouse diagnostic: `scripts/marsel_warehouse_contract_v20_48.py`.
- Superseded `scripts/marsel_warehouse_contract_v20_47.py` has been removed.
- Unified Control Plane references V20.48.
- Warehouse contract remains `NOT_VERIFIED` until authoritative contract/live behavior is resolved.

## RO APP STATUS
🟢 **VERIFIED HISTORICAL LIVE ACCESS**
- `GET /v2/orders` previously returned HTTP 200 in a real read-only smoke test.
- Historical order audit: 4,373 orders; 4,373 unique IDs; 0 duplicate IDs; 0 missing IDs; 0 missing client IDs; 0 missing statuses for that run.
- Historical V20.8 detail audit: 6,820 detail requests; 0 detail failures; 0 writes.

🟡 **PARTIAL**
- Historical API inventory: 124 operations / 45 GET probes.
- Full current API/entity completeness is not yet proven by a fresh complete evidence set.
- Historical product-code review found 11 shared groups; later evidence classified them as legitimate reuse. No automatic deletion/merge is permitted.

🔴 **BLOCKED / NOT VERIFIED**
- Complete production backup is not proven.
- Restore test is not proven.
- Fresh Unified Control Plane result on current `main` is not yet verified.
- Warehouse-list contract is not verified.
- Gmail OAuth user-authorized verification is not complete.
- Official RO App MCP authorization is not complete.
- Credential-exposure remediation tracked by Issue #23 is not closed by direct evidence.
- Production WRITE is not authorized.

## SAFETY
- `MARSEL_WRITE_APPROVED=false` remains mandatory.
- Unified Control Plane live checks are GET-only/read-only.
- Evidence Orchestrator is fail-closed and rejects synthetic evidence.
- Production Gate requires successful upstream control-plane evidence and complete required external evidence.

## CURRENT OPEN BLOCKERS
1. Verify fresh Unified Control Plane result on current canonical `main`.
2. Prove complete backup/export and independently tested restore/integrity.
3. Complete current API/entity verification from authoritative contracts and verified identifiers.
4. Resolve the documented warehouse-list contract discrepancy with authoritative evidence.
5. Keep collision findings review-only; no automatic deletion/merge.
6. Complete Gmail OAuth read-only user authorization test.
7. Complete official RO App MCP authorization verification.
8. Complete credential-exposure remediation evidence for Issue #23.
9. Reconcile governance/remediation PRs against canonical `main`.
10. Only after all required evidence passes: evaluate production safety gate; production WRITE remains disabled until explicit authorization.

## REQUIRED UPDATE RULE
After every material change:
`OBSERVE -> MEASURE -> FIND -> FIX -> TEST -> VERIFY -> DOCUMENT -> MONITOR`

The newest verified evidence supersedes older contradictory evidence; older records remain history and are not silently rewritten.
