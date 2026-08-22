# 05_MARSEL_CURRENT_STATE

**Role:** single living project checkpoint. Update after every material verified change.

## DATE
2026-08-22

## CURRENT VERSION
MARSEL/ROAPP unified control plane with production-container hardening and CI container smoke validation.

## CONTROL CHECKPOINT
Current `main` checkpoint after production-container hardening and CI validation changes: `9ed602a3846350ac1232c0b336b8c1d8c2e37277`.

## SYSTEM MODEL
**MARSEL = business contour + ROAPP = technical contour → one unified system → one canonical `main` control plane.**

## APPLICATION
- FastAPI connector service is present under `app/`.
- Health endpoint: `GET /health`.
- Configuration readiness endpoint: `GET /ready`.
- ROAPP order read endpoint: `GET /roapp/orders`.
- ROAPP read-only audit endpoint: `GET /roapp/audit/orders`.
- MCP HTTP mode is explicitly configuration-gated and JWT-protected when enabled.
- Production container now runs as a non-root user and has an HTTP healthcheck.

## CI / DELIVERY
- Unit-test workflow runs on push, pull request and manual dispatch.
- CI now builds the production Docker image and starts it to verify `/health` before release evidence is accepted.
- Production mutation remains fail-closed.

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
- Fresh live warehouse API evidence is not recorded in this checkpoint.
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

## BACKUP / RESTORE
🔴 Complete production backup and independently tested restore remain unverified.

## DATA QUALITY
🟡 Historical audits show strong order-ID integrity in audited runs.
🟡 11 product-code collision groups were identified and require classification.
🟡 Current completeness across all entity families is not proven.

## INTEGRATIONS
- GitHub: 🟢 repository access and `main` control confirmed.
- ROAPP API: 🟢 READ-only live access confirmed.
- ROAPP MCP: 🟡 technical integration exists; production authorization/write remains blocked.
- Gmail / Google Workspace: 🟡/🔴 not considered connected without live OAuth verification.
- Website / e-commerce / marketplaces / payments / analytics / accounting: 🔵 proposed unless live verification is recorded.

## SECURITY
🟢 READ/WRITE separation is a project invariant.
🟢 Secrets are intended to remain in secure secret storage, not code/logs.
🟢 Production container runs as non-root.
🔴 Production mutation remains gated.

## OPEN BLOCKERS
1. Complete API/entity verification.
2. Prove complete backup.
3. Prove restore from backup.
4. Resolve/classify 11 product-code collision groups without automatic deletion.
5. Preserve fresh live warehouse evidence.
6. Complete required OAuth/MCP authorization checks.
7. Re-run final read-only audit after blockers are addressed.

## COMPLETED SOFTWARE TASKS
- Unified project/control-plane architecture documented.
- GitHub repository `main` established as canonical branch.
- ROAPP API READ-only smoke test proven by historical evidence.
- Orders READ-only audit completed in historical runs.
- Deep detail audit completed without writes.
- Five-file master documentation layer added.
- Legal/tax master updated with official-source checkpoints.
- Production MCP workflow hardened.
- Release-readiness fail-closed controller added.
- Production container hardened: non-root runtime + healthcheck.
- CI production-container build and `/health` smoke validation added.

## UNVERIFIED ITEMS
- Full live API completeness.
- Current full database totals across all entities.
- Fresh warehouse contract evidence.
- Complete backup and independently tested restore.
- Production WRITE readiness.
- Live status of external integrations not reverified in this action.
- MARSEL-specific legal/tax applicability where business-form facts are required.

## REQUIRED UPDATE RULE
After every material change:
`OBSERVE -> MEASURE -> FIND -> FIX -> TEST -> VERIFY -> DOCUMENT -> MONITOR`

The newest verified evidence supersedes older contradictory evidence; older records remain history and are not silently rewritten.
