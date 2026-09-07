# 05_MARSEL_CURRENT_STATE

**Role:** single living project checkpoint. Update after every material verified change.

## DATE
2026-09-08

## CURRENT VERSION
MARSEL ROAPP unified control plane with production-safety hardening, canonical GitHub governance, automated evidence orchestration, deterministic control-agent state transitions, fail-closed production gating, dependency/lock alignment, security hardening, and isolated optional Apple Core AI conversion path.

## CONTROL CHECKPOINT
- Canonical repository: `atalanrafael-jpg/MARSEL-Ro-app`.
- Canonical branch: `main`.
- Current repository `main` HEAD: `519113faf1f7e3fa1d3fc137a944248826a2aaae`.
- Latest verified application/code HEAD: `c84825442857bb9cc51585093bac68d338fac7d1`.
- Commit `519113faf...` is a documentation-only reconciliation after the verified code HEAD; it does not add production evidence or enable writes.
- Production WRITE remains disabled.
- Live repository metadata previously reported `main` as unprotected and required status checks not configured at branch level; this remains an account/repository administration gate until freshly verified as changed.

## LATEST VERIFIED CHANGES
- `8dacd5a9dbc779041899a4215ef48b565a0f2645` hardened `scripts/marsel_production_gate_v1.py` secret scanning with value-based patterns for credential-shaped API keys, client/private secrets, GitHub tokens, and private-key headers while avoiding harmless configuration-presence flags.
- `c84825442857bb9cc51585093bac68d338fac7d1` added regression tests covering allowed configuration-presence flags and rejection of credential-shaped material without storing a real credential.
- Earlier PR #130 was merged on 2026-09-07 and fixed current-main test collection by registering the dynamically loaded control-agent module in `sys.modules` before `exec_module()`.
- `519113faf1f7e3fa1d3fc137a944248826a2aaae` reconciled this checkpoint documentation with the latest security-hardening state; it is documentation-only.
- No production WRITE was introduced by these changes.

## LATEST VERIFIED CI
- Test workflow run `34129874333` completed successfully on verified application/code HEAD `c84825442857bb9cc51585093bac68d338fac7d1`.
- Scheduled `AI: generate drafts` run `34134525448` also completed successfully on the same verified application/code HEAD.
- No CI result is currently verified for documentation commit `519113faf...`; its combined-status endpoint is empty.
- CI success proves only the tested repository/workflow paths. It does not prove current live RO App API access, backup/restore, OAuth, MCP authorization, or production readiness.

## LATEST LIVE GATE FINDING
- The production control plane remains fail-closed and READ_ONLY.
- The latest documented warehouse evidence gate remains dependent on a repository/environment `ROAPP_API_KEY` being available to the workflow and on fresh live verification.
- Historical warehouse-list evidence is not promoted to current live evidence.
- No fallback, synthetic key, bypass, or production WRITE was introduced.

## WAREHOUSE CONTRACT
- The previous `/v2/warehouse/` probe returned HTTP 404; the documented `/warehouse/` route was the basis for the correction in merged PR #114.
- Code-level correction is present on `main`.
- A repository evidence file records a READ-ONLY warehouse-list contract PASS observed at `2026-09-05T08:41:00Z`; this is historical evidence and does not replace a fresh live gate.
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
- GitHub `main` branch protection and required status checks are not verified as enabled.
- Account-level secret-scanning/push-protection, production environment controls, and Copilot controls are not independently verified through the available connector surface.
- Production WRITE is not authorized.

## CURRENT EXECUTION QUEUE
1. Ensure `ROAPP_API_KEY` is present only in approved GitHub Actions/environment secret storage, then run fresh live warehouse evidence verification.
2. Verify the fresh READ-ONLY warehouse result and evidence artifact on current `main`.
3. Prove complete backup/export and independently tested restore/integrity.
4. Complete current API/entity verification from authoritative contracts and verified identifiers.
5. Complete Gmail OAuth read-only user authorization test.
6. Complete official RO App MCP authorization verification.
7. Complete credential-exposure remediation evidence for Issue #23, including rotation/revocation evidence where required.
8. Enable and verify GitHub `main` protection, secret scanning/push protection, production environment controls, and required status checks through account/repository administration.
9. Reconcile stale/open remediation issues and PRs against current `main`; do not merge stale branches without revalidation.
10. Review the 12 Supabase unused-index INFO findings using actual query workload before any index removal.
11. On a physical Apple Silicon host, run the documented Core AI conversion/runtime verification and attach fresh evidence; do not claim hardware verification from CI alone.
12. Only after all applicable evidence gates pass, evaluate production safety gate. Production WRITE remains disabled until explicit authorization.

## SAFETY
- `MARSEL_WRITE_APPROVED=false` remains mandatory.
- Unified Control Plane live checks are GET-only/read-only.
- Evidence Orchestrator is fail-closed and rejects synthetic evidence.
- Secret scanning is hardened against credential-shaped values while allowing harmless presence flags.
- No production write, credential creation, reviewer fabrication, bypass, or synthetic evidence is authorized.

## REQUIRED UPDATE RULE
After every material change:
`OBSERVE -> MEASURE -> FIND -> FIX -> TEST -> VERIFY -> DOCUMENT -> MONITOR`

The newest verified evidence supersedes older contradictory evidence; older records remain history and are not silently rewritten.
