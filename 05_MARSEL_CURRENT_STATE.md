# 05_MARSEL_CURRENT_STATE

**Role:** single living project checkpoint. Update after every material verified change.

## DATE
2026-08-24

## CURRENT VERSION
MARSEL/ROAPP unified control plane with production-safety hardening, credential-pattern guard, and canonical GitHub governance work in progress.

## CONTROL CHECKPOINT
Current verified `main` HEAD observed in the repository: `3b7f626cc3aeaeaa0b11b1a6d437f96f293d935f`.
Latest material changes include credential-handling/incident-response hardening and a read-only secret-guard workflow. The secret-guard commit itself has not been treated as CI-PASS because no status result is currently exposed by the connected GitHub status endpoint.

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
- Unit-test and audit workflows exist on the canonical `main` control plane.
- Production mutation remains fail-closed.
- A repository-level `MARSEL Secret Guard` workflow is now present and scans tracked text files for high-risk credential patterns with `contents: read` permissions only.
- Fresh CI PASS for the newest secret-guard commit is **NOT VERIFIED** because the connected GitHub status endpoint currently returned no status entries.

## RO APP STATUS
🟢 **VERIFIED / PARTIAL**
- Real READ-ONLY API access has been proven in project evidence.
- `GET /v2/orders` returned HTTP 200 in a live smoke test.
- Historical order audit: 4,373 orders; 4,373 unique IDs; 0 duplicate IDs; 0 missing IDs; 0 missing client IDs; 0 missing statuses for that run.
- V20.8 historical detail audit: 6,820 detail requests; 0 detail failures; 0 writes.
- Historical API inventory documented 124 operations and 45 GET probes.

🟡 **PARTIAL**
- Full API/entity completeness is not proven by the historical inventory alone.
- Fresh live warehouse evidence remains a separate acceptance gate (#42).

🔴 **BLOCKED / NOT VERIFIED**
- Full backup is not proven.
- Restore test is not proven.
- Production WRITE is not authorized by the current safety gate.
- Credential exposure remediation in Issue #23 is not closed; rotation/history/log/artifact evidence must be directly verified.

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
🟡 PR #65 (`chore/marsel-github-governance-v1`) is open/draft and proposes canonical repository governance, branch lifecycle rules, and automated governance checks. It has not been merged.
🟡 Multiple older/open remediation PRs remain and must be compared with current `main` before merge or cleanup. No branch deletion is authorized from age/name alone.

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

## COMPLETED SOFTWARE TASKS
- Unified project/control-plane architecture documented.
- GitHub repository `main` established as canonical branch.
- ROAPP API READ-only smoke test proven by historical evidence.
- Orders READ-only audit completed in historical runs.
- Deep detail audit completed without writes.
- Master documentation layer added.
- Legal/tax master updated with official-source checkpoints.
- Production MCP workflow hardened.
- Release-readiness fail-closed controller added.
- Production container hardened: non-root runtime + healthcheck.
- CI production-container build and `/health` smoke validation added.
- Credential-handling/incident-response controls added.
- Repository-level read-only secret-pattern guard added.

## UNVERIFIED ITEMS
- Fresh CI PASS for the newest secret-guard workflow.
- Full live API completeness.
- Current full database totals across all entities.
- Fresh warehouse contract evidence.
- Complete backup and independently tested restore.
- Production WRITE readiness.
- Live Gmail OAuth authorization.
- Live MCP authorization.
- Final reconciliation of overlapping PRs/branches.
- MARSEL-specific legal/tax applicability where business-form facts are required.

## REQUIRED UPDATE RULE
After every material change:
`OBSERVE -> MEASURE -> FIND -> FIX -> TEST -> VERIFY -> DOCUMENT -> MONITOR`

The newest verified evidence supersedes older contradictory evidence; older records remain history and are not silently rewritten.
