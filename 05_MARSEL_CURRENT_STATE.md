# 05_MARSEL_CURRENT_STATE

**Role:** single living project checkpoint. Update after every material verified change.

## DATE
2026-08-29

## CURRENT VERSION
MARSEL/ROAPP unified control plane with production-safety hardening, canonical GitHub governance, and warehouse-contract diagnostic separation.

## CONTROL CHECKPOINT
Current `main` checkpoint: `740402b6904e19ac889763b928f99a3452926a65` — `fix: separate warehouse list contract from stock detail diagnostic`.

## SYSTEM MODEL
**MARSEL = business contour + ROAPP = technical contour → one unified system → one canonical `main` control plane.**

## APPLICATION
- FastAPI connector service is present under `app/`.
- Health endpoint: `GET /health`.
- Configuration readiness endpoint: `GET /ready`.
- ROAPP order read endpoint: `GET /roapp/orders`.
- ROAPP read-only audit endpoint: `GET /roapp/audit/orders`.
- MCP HTTP mode is explicitly configuration-gated and JWT-protected when enabled.
- Production container runs as a non-root user and has an HTTP healthcheck.

## CI / DELIVERY
- Canonical unit-test and audit workflows exist on `main`.
- Production mutation remains fail-closed.
- Repository-level secret guard is present with read-only repository permissions.
- Unified Control Plane runs on push to `main`, pull requests, manual dispatch, and schedule; live RO App checks are skipped on pull requests to avoid secret exposure.
- The latest warehouse-contract code change is committed, but a new CI result for commit `740402b` is **NOT VERIFIED** because the commit-specific workflow lookup returned no run.

## RO APP STATUS
🟢 **VERIFIED / PARTIAL**
- Real READ-ONLY API access has been proven in project evidence.
- `GET /v2/orders` returned HTTP 200 in a live smoke test.
- Historical order audit: 4,373 orders; 4,373 unique IDs; 0 duplicate IDs; 0 missing IDs; 0 missing client IDs; 0 missing statuses for that run.
- V20.8 historical detail audit: 6,820 detail requests; 0 detail failures; 0 writes.
- Historical API inventory documented 124 operations and 45 GET probes.

🟡 **PARTIAL**
- Full API/entity completeness is not proven by the historical inventory alone.
- Warehouse list-contract logic has been corrected to evaluate the documented list contract independently from stock-detail diagnostics.

🔴 **BLOCKED / NOT VERIFIED**
- Full backup is not proven.
- Restore test is not proven.
- Production WRITE is not authorized by the current safety gate.
- Credential exposure remediation in Issue #23 is not closed until direct rotation/history/log/artifact evidence is verified.
- Fresh warehouse live evidence for the latest code is not yet verified.

## API STATUS
🟢 Live READ-only orders endpoint verified historically.
🟡 Full contract/schema completeness not verified.
🔴 Do not infer undocumented endpoints, fields, or identifiers.

## DATABASE STATUS
🟡 Read-only audits have been performed against live ROAPP data.
🔴 No claim of a fresh complete current database inventory is made without new complete audit evidence.

## BACKUP / RESTORE
🔴 Complete production backup and independently tested restore remain unverified.

## DATA QUALITY
🟡 Historical audits show strong order-ID integrity in audited runs.
🟡 11 product-code collision groups were identified; they require classification as legitimate reuse vs real collision/unresolved finding before any mutation.
🟡 Current completeness across all entity families is not proven.

## WAREHOUSE
🟡 The latest code separates the documented warehouse list contract from stock-detail diagnostics. A warehouse PASS now requires discovered warehouse IDs plus a successful documented `/v2/warehouse/` list contract; stock detail is reported separately. This code change is committed in `740402b`.
⚪ Fresh CI/live evidence for `740402b` is not yet verified.

## INTEGRATIONS
- GitHub: 🟢 repository access and `main` control confirmed.
- ROAPP API: 🟢 READ-only live access confirmed historically.
- ROAPP MCP: 🟡 technical integration exists; production authorization/write remains blocked.
- Gmail / Google Workspace: 🟡/🔴 not considered connected without live user-authorized OAuth verification.
- Website / e-commerce / marketplaces / payments / analytics / accounting: 🔵 proposed unless live verification is recorded.

## SECURITY
🟢 READ/WRITE separation is a project invariant.
🟢 Repository-level secret guard is present on `main`.
🟢 Secrets are intended to remain in secure secret storage, not code/logs.
🟢 Production container runs as non-root.
🔴 Historical credential exposure remediation remains open until direct rotation and exposure-cleanup evidence is verified (Issue #23).
🔴 Production mutation remains gated.

## GITHUB GOVERNANCE
🟢 `main` is the canonical branch.
🟡 Governance/remediation PRs and branches must be compared with current `main` before merge or cleanup. No branch deletion is authorized from age/name alone.

## OPEN BLOCKERS
1. Complete API/entity verification.
2. Obtain fresh live warehouse evidence for Issue #42.
3. Prove complete backup.
4. Prove restore from backup.
5. Resolve/classify 11 product-code collision groups without automatic deletion.
6. Complete required Gmail OAuth user-authorized verification.
7. Verify official RO App MCP authorization separately.
8. Close credential-exposure remediation only after direct rotation and repository/history/log/artifact verification (Issue #23).
9. Re-run final read-only audit after blockers are addressed.
10. Reconcile overlapping open PRs before merging governance/remediation changes.

## REQUIRED UPDATE RULE
After every material change:
`OBSERVE -> MEASURE -> FIND -> FIX -> TEST -> VERIFY -> DOCUMENT -> MONITOR`

The newest verified evidence supersedes older contradictory evidence; older records remain history and are not silently rewritten.
