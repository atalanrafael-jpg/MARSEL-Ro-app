# MARSEL ROAPP — MASTER PROJECT CONTROL

## Purpose
Единая контрольная точка проекта: техническое состояние RO App integration, качество данных, безопасность, бизнес-автоматизация и коммерческий контур MARSEL.

## Canonical state — 2026-09-09
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Branch: `main`
- Current repository `main` HEAD: `238d1c7121d902ae3bdacf59b33525b585c79090`.
- Current main includes security hardening commit `238d1c7`, including a separate `MARSEL_INTERNAL_API_KEY` boundary credential and authentication on connector RO App order/audit endpoints.
- Current integration mode: READ-ONLY.
- Production WRITE: DISABLED.
- Canonical live audit workflow: `.github/workflows/marsel-unified-control-plane.yml`.
- Canonical warehouse implementation: `scripts/marsel_warehouse_contract_v20_48.py`.
- Historical implementations and snapshots do not override current evidence.

## Latest verified CI
- No workflow run is currently returned by the connected GitHub workflow-run/status queries for HEAD `238d1c7121d902ae3bdacf59b33525b585c79090`.
- Therefore current-main CI is **NOT VERIFIED** in this control document.
- Earlier successful CI runs do not prove current-main CI, production readiness, current live API access, backup/restore, OAuth, MCP, or WRITE readiness.

## Evidence precedence
1. Current `main` repository state.
2. Current GitHub workflow/run evidence tied to current `main`.
3. Direct live API evidence with timestamps/artifacts.
4. Current official RO App documentation.
5. Older project documents are historical only.

## Completion gates

### Engineering
- [ ] Unit tests GREEN on current main HEAD
- [ ] Required production/quality workflows GREEN on current main HEAD
- [ ] No known import/runtime failures
- [ ] Canonical structure check PASS on current main HEAD
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
1. Current-main CI status is not yet directly verified for HEAD `238d1c7`.
2. Backup/export and independent restore/integrity evidence are not proven.
3. Complete current API/entity verification is not proven.
4. Warehouse live contract requires fresh authoritative GET evidence; historical/undocumented compatibility behavior is not promoted to PASS.
5. Duplicate/reference reconciliation requires controlled current evidence; no automatic deletion.
6. Gmail OAuth requires actual user-authorized live verification.
7. Official RO App MCP authorization requires separate live verification.
8. Credential-exposure remediation tracked by Issue #23 requires direct rotation/exposure evidence.
9. GitHub account/repository security controls are not independently readable through the current connector; the repository has rejected direct writes to `main` and reports seven required status checks, so protection is active in practice, but the exact rule configuration is not fully verified here.
10. ReadMe ↔ GitHub bi-directional sync requires external ReadMe configuration in a dedicated docs repository.
11. Production WRITE remains disabled until every applicable safety gate passes and explicit authorization exists.

## Open issue control
Open issues currently include #19, #23, #27, #30, #77, #83, #85, #91, #106, #133, #134 and #135. No issue is marked completed merely because code or documentation exists.

- #19: production gate — BLOCKED / NOT READY.
- #23: credential exposure — SECURITY REMEDIATION REQUIRED.
- #27: Gmail OAuth — IMPLEMENTATION / USER AUTHORIZATION REQUIRED.
- #30: API/entity coverage — REVIEW_REQUIRED.
- #77: published RO App example token — security review/rotation responsibility remains external to this repository.
- #83: evidence discovery — REVIEW_REQUIRED.
- #85: security bridge — BLOCKED until gates 1–8 are directly evidenced.
- #91: GitHub account-level controls — MANUAL/EXTERNAL.
- #106: ReadMe GitHub sync — EXTERNAL CONFIGURATION REQUIRED.
- #133: canonical Master Data / Integration Contract — OPEN / P1.
- #134: observability and correlation contract — OPEN / P1.
- #135: integration adapters — OPEN / P2.

## Status rule
A gate is `PASS` only when current direct evidence exists. `PLANNED`, `CODED`, `NOT_TESTED`, `ASSUMED`, `OLD_PASS`, or `UNVERIFIED` are not PASS.

## Safety rule
Never claim backup, restore, reconciliation, security rotation, OAuth, MCP authorization or WRITE readiness without direct evidence. Never guess an API endpoint or identifier. Never execute a production mutation merely to make a test green. Never expose or commit `ROAPP_API_KEY`.

## Continuation rule
Every execution starts from this file and the current `main` checkpoint, verifies current CI/live evidence, fixes the next highest-priority safe defect, records the result, and repeats until all required gates are PASS or an external blocker is documented.
