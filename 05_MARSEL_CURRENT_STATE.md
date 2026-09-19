# 05_MARSEL_CURRENT_STATE

**Role:** single living project checkpoint. Update after every material verified change.

## DATE
2026-09-20

## CURRENT VERSION
MARSEL ROAPP unified control plane with production-safety hardening, canonical GitHub governance, automated evidence orchestration, deterministic control-agent state transitions, fail-closed production gating, dependency/lock alignment, security hardening, Chrome 153 compatibility hardening, and isolated optional Apple Core AI conversion path.

## CONTROL CHECKPOINT
- Canonical repository: `atalanrafael-jpg/MARSEL-Ro-app`.
- Canonical branch: `main`.
- Current application/code checkpoint: `77e96c1dec0590ac2b2f14502da5f570a8f70419`.
- Repository default branch: `main`.
- Owner MVP vertical slice is present in `web/index.html` and served at `/app`; Supabase Auth/RLS integration is present.
- Production WRITE remains disabled.
- Current integration mode: READ-ONLY.
- Compatibility branches are not independent development lines.
- The authoritative current control checkpoint is `docs/PROJECT_MASTER_CONTROL.md`; this file is the living project-state mirror and must not retain older checkpoints after a material main update.

## CHROME 153 COMPATIBILITY
- Official Chrome 153 Stable release date: 2026-09-08.
- Chrome 153 removes non-standard navigation targets using `_current`.
- Chrome 153 lists Protected Audience, Related Website Sets, Shared Storage, `document.requestStorageAccessFor`, and Attribution Reporting for deprecation/removal.
- Chrome 153 moves several non-XSLT XML parsing paths (`DOMParser`, `XMLHttpRequest.responseXML`, standalone SVG, external SVG) to a memory-safe Rust implementation while preserving web-standard behavior; these APIs are therefore not treated as regressions by the guard.
- Repository source search found no current `DOMParser`, `responseXML`, `requestStorageAccessFor`, or Protected Audience implementation that requires a code migration.
- A fail-closed CI guard was added at `scripts/marsel_chrome_153_compatibility_guard.py` to reject `_current` navigation targets and the listed deprecated API identifiers in source/configuration files.
- CI workflow added at `.github/workflows/marsel-chrome-153-compatibility.yml`.
- The guard itself has not yet been accepted as VERIFIED until its GitHub Actions run completes successfully on this branch.
- Chrome 153 also begins the two-week Stable release cadence; future browser compatibility checks should follow Beta-to-Stable cadence rather than waiting for four-week milestones.

## LATEST VERIFIED CHANGES
- Backup/restore safety gate advanced to VERIFIED on current `main`: Backup Evidence Producer run `35469023100` succeeded and Restore Verification run `35469309884` succeeded against the generated artifact; restore was isolated and produced 10,410 restored records with zero production writes/mutations.
- `8dacd5a9dbc779041899a4215ef48b565a0f2645` hardened `scripts/marsel_production_gate_v1.py` secret scanning with value-based patterns for credential-shaped API keys, client/private secrets, GitHub tokens, and private-key headers while avoiding harmless configuration-presence flags.
- `c84825442857bb9cc51585093bac68d338fac7d1` added regression tests covering allowed configuration-presence flags and rejection of credential-shaped material without storing a real credential.
- Earlier PR #130 was merged on 2026-09-07 and fixed current-main test collection by registering the dynamically loaded control-agent module in `sys.modules` before `exec_module()`.
- `519113faf1f7e3fa1d3fc137a944248826a2aaae` reconciled this checkpoint documentation with the latest security-hardening state; it is documentation-only.
- No production WRITE was introduced by these changes.

## LATEST VERIFIED CI
- Repository control records the latest verified Unified Control Plane and Execution Worker runs on application/code checkpoint `3eae5f89317e0cc4e928f7c7331958baaa789bf8`.
- Current `main` advanced afterward through the Railway PORT fix and control/documentation updates to `b29c80a9ec337111459ac22535ba67a529f251bb`, followed by the current control-checkpoint refresh commit `77e96c1dec0590ac2b2f14502da5f570a8f70419`.
- Railway production deployment `c96d55ad-5966-48a4-9506-90ba20cd793c` is successful for current `main` commit `b29c80a9ec337111459ac22535ba67a529f251bb`.
- Owner UI `/app` end-to-end browser verification remains NOT VERIFIED.
- A successful historical CI run does not prove current live RO App API access, OAuth, MCP authorization, or production readiness.

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
- Complete READ-ONLY backup/export evidence is VERIFIED on prior current-main checkpoint `2e00d5132278cfb7d37566dfca7ba07c99203fab` via Backup Evidence Producer run `35469023100`.
- Independently tested isolated restore/integrity is now VERIFIED via Restore Verification run `35469309884`: `RESTORE_EVIDENCE=PASS`, `RESTORED_RECORDS=10410`, `PRODUCTION_WRITE_ATTEMPTED=False`, `RO_APP_DATA_MUTATED=False`.
- Fresh current-main unified evidence bundle is not established as production-gate evidence.
- Gmail OAuth user-authorized verification is not complete.
- Official RO App MCP authorization is not complete.
- Credential-exposure remediation tracked by Issue #23 is not closed by direct evidence.
- GitHub `main` branch protection and required status checks are not verified as enabled.
- Account-level secret-scanning/push-protection, production environment controls, and Copilot controls are not independently verified through the available connector surface.
- Production WRITE is not authorized.

## CURRENT EXECUTION QUEUE
1. Directly verify the deployed Owner UI `/app` end-to-end.
2. Obtain fresh authorized RO App GET evidence for applicable API/entity coverage.
3. Obtain fresh authoritative warehouse/stock contract evidence.
4. Complete current duplicate/reference reconciliation.
5. Complete credential-exposure remediation evidence for Issue #23.
6. Complete official RO App MCP authorization verification.
7. Complete Gmail OAuth read-only authorization if integration remains in scope.
8. Complete current Wix ↔ RO App reconciliation, mutation dry-run, idempotency and rollback evidence.
9. Verify GitHub account-level security/branch administration under Issue #91.
10. Keep production WRITE disabled until every applicable safety gate passes and explicit authorization exists.

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
