# 05_MARSEL_CURRENT_STATE

**Role:** single living project checkpoint. Update this file after every material verified change.

## DATE
2026-08-21

## CURRENT VERSION
Documentation consolidation into five master files.

## CURRENT GITHUB COMMIT
At the beginning of this documentation action, `main` was verified at `4e5e37104389817d6fdad95bfdfa6aac9cb4c0b2`. Four master documents were then committed sequentially before this file. The exact final commit after this write must be re-read from `main` and is the authoritative current commit.

## SYSTEM MODEL
**MARSEL = business contour + ROAPP = technical contour → one unified system → one canonical `main` control plane.**

## RO APP STATUS
🟢 **VERIFIED / PARTIAL**
- Real READ-ONLY API access has been proven in project evidence.
- `GET /v2/orders` returned HTTP 200 in a live smoke test.
- Historical order audit: 4,373 orders; 4,373 unique IDs; 0 duplicate IDs; 0 missing IDs; 0 missing client IDs; 0 missing statuses for that run.
- V20.8 historical detail audit: 6,820 detail requests; 0 detail failures; 0 writes.

🟡 **PARTIAL**
- API inventory documented 124 operations and 45 GET probes in the latest documented control point.
- Full API/entity completeness is not proven.

🔴 **BLOCKED / NOT VERIFIED**
- Warehouse live API contract is NOT VERIFIED.
- Full backup is not proven.
- Restore test is not proven.
- Production WRITE is not authorized by the current safety gate.

## API STATUS
🟢 Live READ-only orders endpoint verified.
🟡 Full contract/schema completeness not verified.
🔴 Do not infer undocumented endpoints or fields.

## DATABASE STATUS
🟡 Read-only audits have been performed against live ROAPP data.
🔴 No claim of full current database inventory is made without a fresh complete audit.

## BACKUP STATUS
🔴 NOT VERIFIED as production-ready.
A successful backup workflow/job is not sufficient unless the backup is complete, restorable and independently tested.

## RESTORE STATUS
🔴 NOT VERIFIED.
No production WRITE may proceed until restore evidence exists.

## DATA QUALITY
🟡 Historical audits show strong order-ID integrity in audited runs.
🟡 11 product-code collision groups were identified and require classification.
🟡 Current completeness across all entity families is not proven.

## WAREHOUSE STATUS
🔴 NOT VERIFIED.
Do not invent warehouse IDs. Existing IDs from historical evidence must remain evidence-only until their source and current validity are rechecked.

## INTEGRATIONS
- GitHub: 🟢 repository access and `main` control confirmed.
- ROAPP API: 🟢 READ-only live access confirmed.
- ROAPP MCP: 🟡 technical integration exists; production authorization/write remains blocked.
- Gmail / Google Workspace: 🟡/🔴 dependent on actual OAuth/live verification; not considered connected without evidence.
- Website / e-commerce / marketplaces / payments / analytics / accounting: 🔵 PROPOSED unless live verification is recorded.

## SECURITY
🟢 READ/WRITE separation is a project invariant.
🟢 Secrets are intended to remain in secret storage, not code/logs.
🔴 Production mutation remains gated.

## OPEN BLOCKERS
1. Complete API/entity verification.
2. Prove complete backup.
3. Prove restore from backup.
4. Resolve/classify 11 product-code collision groups without automatic deletion.
5. Verify warehouse contract.
6. Complete required OAuth/MCP authorization checks.
7. Re-run final read-only audit after blockers are addressed.

## COMPLETED TASKS
- Unified project/control-plane architecture documented.
- GitHub repository `main` established as canonical branch.
- ROAPP API READ-only smoke test proven by historical evidence.
- Orders READ-only audit completed in historical runs.
- Deep detail audit completed without writes.
- Five-file master documentation layer added in this action.

## UNVERIFIED ITEMS
- Full live API completeness.
- Current full database totals across all entities.
- Warehouse contract and official warehouse IDs.
- Complete backup and independently tested restore.
- Production WRITE readiness.
- Live status of external integrations not reverified in this action.

## CHANGELOG / CONTROL HISTORY
- Before consolidation: main = `4e5e37104389817d6fdad95bfdfa6aac9cb4c0b2`.
- Added `01_MARSEL_MASTER.md`.
- Added `02_ROAPP_TECHNICAL_MASTER.md`.
- Added `03_MARSEL_DATA_MASTER.md`.
- Added `04_MARSEL_LEGAL_FINANCE_MASTER.md`.
- Added this current-state checkpoint.

## DECISIONS
- Five master files are the project-context layer for limited Project file capacity.
- Historical/duplicate materials are not allowed to override the canonical current state.
- READ-only remains the default.
- No write, deletion, mass synchronization or invented API contract is allowed without the production gate.

## NEXT SAFE ACTION
**Re-read `main` after this commit, verify the five master files exist, then run the existing read-only CI/self-check. Do not modify ROAPP data.**

## REQUIRED UPDATE RULE
After every material change:
`OBSERVE -> MEASURE -> FIND -> FIX -> TEST -> VERIFY -> DOCUMENT -> MONITOR`

The newest verified evidence always supersedes older contradictory evidence; older records remain history and are not silently rewritten.