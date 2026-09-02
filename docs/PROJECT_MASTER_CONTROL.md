# MARSEL / ROAPP — MASTER PROJECT CONTROL

## Purpose
Единая контрольная точка проекта: техническое состояние RO App integration, качество данных, безопасность, бизнес-автоматизация и коммерческий контур MARSEL.

## Canonical state — 2026-09-02
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Branch: `main`
- Current HEAD must always be treated as the primary source of truth.
- Current integration mode: READ-ONLY.
- Production WRITE: DISABLED.
- Canonical live audit workflow: `.github/workflows/marsel-unified-control-plane.yml`.
- Canonical warehouse implementation: `scripts/marsel_warehouse_contract_v20_47.py`.
- Historical implementations and snapshots belong in `старые данные/` and do not override current evidence.

## Evidence precedence
1. Current `main` repository state.
2. Current GitHub workflow/run evidence tied to current `main`.
3. Direct live API evidence with timestamps/artifacts.
4. Current official RO App documentation.
5. Older project documents are historical only.

## 100% completion gates

### Engineering
- [ ] Unit tests GREEN on current `main` HEAD
- [ ] Required CI workflows GREEN on current `main` HEAD
- [ ] No known import/runtime failures
- [ ] Canonical structure check PASS
- [ ] Dependency/security review PASS

### RO App API
- [ ] Official API registry complete for required MARSEL entities
- [ ] Every method/path has official evidence
- [ ] No guessed endpoints
- [ ] Safe live GET verification complete
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
- [ ] Recovery procedure documented

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
1. Fresh CI/live evidence for current `main` must be verified.
2. Warehouse/stock contract requires direct authoritative evidence.
3. Complete API/entity coverage remains open.
4. Backup/export and independent restore/integrity evidence remain unproven.
5. Collision/reference findings require controlled reconciliation; no automatic deletion.
6. Gmail OAuth and official RO App MCP authorization require separate live verification.
7. Historical credential-exposure remediation requires direct evidence.
8. GitHub account/ruleset/security settings require account-level verification where repository file/API access is insufficient.

## Status rule
A gate is `PASS` only when current direct evidence exists. `PLANNED`, `CODED`, `NOT_TESTED`, `ASSUMED`, `OLD_PASS`, or `UNVERIFIED` are not PASS.

## Safety rule
Never claim backup, restore, reconciliation, security rotation, OAuth, MCP authorization or WRITE readiness without direct evidence. Never guess an API endpoint or identifier. Never execute a production mutation merely to make a test green.

## Continuation rule
Every execution starts from this file and the current `main` HEAD, verifies current CI/live evidence, closes the next highest-priority open gate, records the result, and repeats until all required gates are PASS or an external blocker is documented.
