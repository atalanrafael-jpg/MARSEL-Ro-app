# MARSEL ROAPP — MASTER PROJECT CONTROL

## Purpose
Единая контрольная точка проекта: техническое состояние RO App integration, качество данных, безопасность, бизнес-автоматизация и коммерческий контур MARSEL.

## Canonical state — 2026-09-08
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Branch: `main`
- Current repository `main` HEAD: `a4ec23ed4ebe6616f111b9fa36507478b1379585`.
- Latest verified application/code checkpoint: `c84825442857bb9cc51585093bac68d338fac7d1`.
- Subsequent commits are documentation-only reconciliations unless explicitly stated otherwise.
- Current integration mode: READ-ONLY.
- Production WRITE: DISABLED.
- Canonical live audit workflow: `.github/workflows/marsel-unified-control-plane.yml`.
- Canonical warehouse implementation: `scripts/marsel_warehouse_contract_v20_48.py`.
- Historical implementations and snapshots do not override current evidence.

## Latest verified CI
- Test workflow run `34129874333` completed successfully on verified application/code checkpoint `c84825442857bb9cc51585093bac68d338fac7d1`.
- Scheduled `AI: generate drafts` run `34134525448` also completed successfully on that checkpoint.
- No CI result is currently verified for the documentation-only reconciliation commits.
- This proves the tested repository build/test path for those runs only; it does not prove production readiness, current live API access, backup/restore, OAuth, MCP, or WRITE readiness.

## Evidence precedence
1. Current `main` repository state.
2. Current GitHub workflow/run evidence tied to current `main`.
3. Direct live API evidence with timestamps/artifacts.
4. Current official RO App documentation.
5. Older project documents are historical only.

## Completion gates

### Engineering
- [ ] Unit tests GREEN on current verified application checkpoint
- [ ] Required production/quality workflows GREEN on current verified application checkpoint
- [ ] No known import/runtime failures
- [ ] Canonical structure check PASS
- [ ] Dependency/security review PASS

### RO App API
- [ ] Official API registry complete for required MARSEL entities
- [ ] Every method/path has official evidence
- [x] No guessed endpoints
- [ ] Safe current live GET verification complete
- [ ] Parameterized identifiers never guessed
- [ ] Warehouse/stock contract closed with direct authoritative evidence

### Data
- [ ] Current orders inventory complete
- [ ] Current clients inventory complete
- [ ] Current products inventory complete
- [ ] Current services inventory complete
- [ ] Current warehouses/directories inventory complete
- [ ] Duplicate/anomaly/reference review complete
- [ ] Reconciliation complete

### Recovery
- [ ] Full permitted backup/export created
- [ ] Backup manifest/checksums verified
- [ ] Restore tested safely
- [x] Recovery procedure documented

### Writes
- [ ] Write contracts officially verified
- [ ] Validation complete
- [ ] Dry-run complete
- [ ] Idempotency/duplicate protection complete
- [ ] Rollback procedure tested
- [ ] Post-write verification tested
- [ ] Production writes explicitly enabled only after all gates pass

### MARSEL operations
- [ ] Customer lifecycle defined
- [ ] Repair-to-repeat-sales flow defined
- [ ] Custom manufacturing sales flow defined
- [ ] Daily action queue defined
- [ ] KPI model connected to factual business data
- [ ] Lead attribution and conversion tracking prepared

## Current blockers
1. Backup/export and independent restore/integrity evidence are not proven.
2. Complete current API/entity verification is not proven.
3. Warehouse live contract requires fresh authoritative GET evidence; historical/undocumented compatibility behavior is not promoted to PASS.
4. Duplicate/reference reconciliation requires controlled current evidence; no automatic deletion.
5. Gmail OAuth requires actual user-authorized live verification.
6. Official RO App MCP authorization requires separate live verification.
7. Credential-exposure remediation tracked by Issue #23 requires direct rotation/exposure evidence.
8. GitHub account/repository security controls require account-level administration; current `main` protection/status checks are not independently verified as enabled.
9. ReadMe ↔ GitHub bi-directional sync requires external ReadMe configuration in a dedicated docs repository.
10. Production WRITE remains disabled until every applicable safety gate passes and explicit authorization exists.

## Issue consolidation — 2026-09-08
Open issues currently include #19, #23, #27, #30, #77, #83, #85, #91 and #106. Their bodies have been reconciled where current evidence permits. No issue is marked completed merely because code or documentation exists.

- #19: production gate — BLOCKED / NOT READY.
- #23: credential exposure — SECURITY REMEDIATION REQUIRED.
- #27: Gmail OAuth — IMPLEMENTATION / USER AUTHORIZATION REQUIRED.
- #30: API/entity coverage — REVIEW_REQUIRED.
- #77: published RO App example token — security review/rotation responsibility remains external to this repository.
- #83: evidence discovery — REVIEW_REQUIRED.
- #85: security bridge — BLOCKED until gates 1–8 are directly evidenced.
- #91: GitHub account-level controls — MANUAL/EXTERNAL.
- #106: ReadMe GitHub sync — EXTERNAL CONFIGURATION REQUIRED.

## Status rule
A gate is `PASS` only when current direct evidence exists. `PLANNED`, `CODED`, `NOT_TESTED`, `ASSUMED`, `OLD_PASS`, or `UNVERIFIED` are not PASS.

## Safety rule
Never claim backup, restore, reconciliation, security rotation, OAuth, MCP authorization or WRITE readiness without direct evidence. Never guess an API endpoint or identifier. Never execute a production mutation merely to make a test green. Never expose or commit `ROAPP_API_KEY`.

## Continuation rule
Every execution starts from this file and the current `main` checkpoint, verifies current CI/live evidence, fixes the next highest-priority safe defect, records the result, and repeats until all required gates are PASS or an external blocker is documented.
