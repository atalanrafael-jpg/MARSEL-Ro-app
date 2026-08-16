# MARSEL / ROAPP — MASTER PROJECT CONTROL

## Purpose
Единая контрольная точка проекта: техническое состояние RO App integration, качество данных, безопасность, бизнес-автоматизация и коммерческий контур MARSEL.

## Canonical repository
- Repository: `atalanrafael-jpg/Ro-app`
- Branch: `main`
- Production writes: DISABLED until all write-safety gates pass.
- Current integration mode: READ-ONLY.

## 100% completion gates

### Engineering
- [ ] Unit tests GREEN
- [ ] All required CI workflows GREEN
- [ ] No known import/runtime failures
- [ ] Canonical structure check PASS
- [ ] Dependency/security review PASS

### RO App API
- [ ] Official API registry complete for required MARSEL entities
- [ ] Every method/path has official evidence
- [ ] No guessed endpoints
- [ ] Live GET verification complete where safe
- [ ] Parameterized identifiers never guessed

### Data
- [ ] Orders inventory complete
- [ ] Clients inventory complete
- [ ] Products inventory complete
- [ ] Services inventory complete
- [ ] Warehouses/directories inventory complete
- [ ] Duplicate/anomaly review complete
- [ ] Reconciliation complete

### Recovery
- [ ] Full backup created
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

### MARSEL Revenue Engine
- [ ] Customer lifecycle defined
- [ ] Repair-to-repeat-sales flow defined
- [ ] Custom manufacturing sales flow defined
- [ ] Daily action queue defined
- [ ] KPI model connected to factual business data
- [ ] 30-day content system prepared
- [ ] Lead attribution and conversion tracking prepared

## Status rule
A gate is `PASS` only when evidence exists. `PLANNED`, `CODED`, `NOT_TESTED`, or `ASSUMED` are not PASS.

## Current known blocker policy
If CI, API evidence, backup/restore, reconciliation, security, or write-safety is not proven, project status remains `NOT_READY`.
