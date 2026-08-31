# 05_MARSEL_CURRENT_STATE

**Role:** single living project checkpoint. Update after every material verified change.

## DATE
2026-08-31

## CURRENT VERSION
MARSEL/ROAPP unified control plane with production-safety hardening, canonical GitHub governance, automated evidence orchestration, and fail-closed production gating.

## CONTROL CHECKPOINT
Current `main` checkpoint: `214851f9f601b4661796a611f9c2a0bfdb65d82c` — superseded warehouse V20.47 script removed after canonicalizing the warehouse diagnostic to V20.48.

## SYSTEM MODEL
**MARSEL = business contour + ROAPP = technical contour → one unified system → one canonical `main` control plane.**

## VERIFIED LIVE / REPOSITORY FACTS
- Repository `atalanrafael-jpg/Ro-app` is accessible with admin/maintain/push permissions through the connected GitHub integration.
- The repository is public, active, and `main` is the default branch.
- The Unified Control Plane is configured for push to `main`, pull requests, manual dispatch, and a 6-hour schedule.
- Production Gate is fail-closed and production WRITE remains disabled.
- Generic CI, CodeQL, Codex validation, Secret Guard, Integration Health and MCP production-readiness workflows have successful runs on the latest tested revision.
- Historical RO App live evidence remains valid only for the runs that produced it: 4,373-order audit; V20.8 detail audit with 6,820 successful detail requests; and prior API inventory/data-quality evidence.

## CANONICALIZATION CORRECTION
- The warehouse audit previously had a naming drift: the file `marsel_warehouse_contract_v20_47.py` had been internally changed to version 20.48 while the Unified Control Plane still referenced the old filename.
- This was corrected: the canonical Unified Control Plane now references `scripts/marsel_warehouse_contract_v20_48.py`; the superseded V20.47 script was removed.
- V20.48 is fail-closed: the authoritative documented warehouse-list contract remains `/v2/warehouse/`; undocumented compatibility routes are not promoted to PASS.
- Fresh V20.48 diagnostic evidence tested `/v2/warehouse/?type=product` and `/v2/warehouse/?type=product&page=1`; both returned HTTP 404 in that run. Therefore warehouse-list contract remains `NOT_VERIFIED` until authoritative contract/live behavior is resolved.

## RO APP STATUS
🟢 **VERIFIED HISTORICAL LIVE ACCESS**
- `GET /v2/orders` previously returned HTTP 200 in a real read-only smoke test.
- Historical order audit: 4,373 orders; 4,373 unique IDs; 0 duplicate IDs; 0 missing IDs; 0 missing client IDs; 0 missing statuses for that run.
- Historical V20.8 detail audit: 6,820 detail requests; 0 detail failures; 0 writes.

🟡 **PARTIAL**
- Historical API inventory: 124 operations / 45 GET probes.
- Full current API/entity completeness is not yet proven by a fresh complete evidence set.
- Historical product-code review found 11 shared groups; the later audit classified them as legitimate reuse, with no real collisions and no unresolved groups. No automatic deletion/merge is allowed.

🔴 **BLOCKED / NOT VERIFIED**
- Complete production backup is not proven.
- Restore test is not proven.
- Fresh Unified Control Plane run on the latest canonical revision is not yet verified as PASS.
- Warehouse-list contract is not verified.
- Gmail OAuth user-authorized verification is not complete.
- Official RO App MCP authorization is not complete.
- Credential-exposure remediation tracked by Issue #23 is not closed by direct evidence.
- Production WRITE is not authorized.

## SAFETY
- Production mutation remains explicitly disabled: `MARSEL_WRITE_APPROVED=false`.
- Unified Control Plane live checks are GET-only/read-only.
- Evidence Orchestrator is fail-closed and rejects synthetic evidence.
- Production Gate requires successful upstream control-plane evidence and complete required external evidence.

## CURRENT OPEN BLOCKERS
1. Obtain PASS/FAIL result of the fresh Unified Control Plane run triggered by the latest canonicalization commits.
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
