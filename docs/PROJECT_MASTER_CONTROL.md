# MARSEL / ROAPP — MASTER PROJECT CONTROL

## Purpose
Единая контрольная точка проекта: техническое состояние RO App integration, качество данных, безопасность, бизнес-автоматизация и коммерческий контур MARSEL.

## Canonical state
- Repository: `atalanrafael-jpg/Ro-app`
- Canonical work branch: `act/marsel-unified-system-2026-08-22`
- Baseline: current `main` at the moment this branch was created.
- Integration mode: READ-ONLY.
- Production WRITE: DISABLED.
- The canonical work branch is the only active implementation line until a new control point is explicitly approved.

## Evidence precedence
1. Current HEAD of the canonical work branch.
2. Current GitHub workflow/run evidence tied to that HEAD.
3. Direct live API evidence with timestamps/artifacts.
4. Current official RO App documentation.
5. Older project documents, branches, commits and CI runs are historical only and cannot override current evidence.

## 100% completion gates

### Engineering
- [ ] Unit tests GREEN on current canonical HEAD
- [ ] Required CI workflows GREEN on current canonical HEAD
- [ ] No known import/runtime failures
- [ ] Canonical structure check PASS
- [ ] Dependency/security review PASS

### RO App API
- [ ] Official API registry complete for required MARSEL entities
- [ ] Every method/path has official evidence
- [ ] No guessed endpoints
- [ ] Live GET verification complete where safe
- [ ] Parameterized identifiers never guessed
- [ ] Warehouse/stock contract closed with direct evidence

### Data
- [ ] Orders inventory complete
- [ ] Clients inventory complete
- [ ] Products inventory complete
- [ ] Services inventory complete
- [ ] Warehouses/directories inventory complete
- [ ] Duplicate/anomaly review complete
- [ ] Reconciliation complete

### MARSEL service domains
- [ ] JEWELRY model verified
- [ ] WATCH model verified
- [ ] EYEWEAR repair model verified
- [ ] Shared Customer → Order → Object → Diagnosis → Estimate → Work → Parts/Materials → QC → Delivery → Payment → Warranty flow verified
- [ ] Domain-specific fields are isolated and not mixed

### Recovery
- [ ] Full permitted backup created
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

## Current blockers
1. Current CI/live results for the current canonical HEAD must be directly verified; older successful runs do not prove current state.
2. Warehouse/stock contract requires direct evidence and safe verification with real permitted identifiers; identifiers must never be guessed.
3. Duplicate/anomaly and reconciliation gates remain open until current evidence is attached.
4. Backup/restore evidence is not yet proven by this control record.
5. Production WRITE remains prohibited until all required gates are evidenced.

## Status rule
A gate is `PASS` only when current evidence exists. `PLANNED`, `CODED`, `NOT_TESTED`, `ASSUMED`, `OLD_PASS`, or `UNVERIFIED` are not PASS.

## Safety rule
Never claim backup, restore, reconciliation, security, rotation, or WRITE readiness without direct evidence. Never guess an API endpoint or identifier. Never execute a production mutation merely to make a test green.

## Continuation rule
Every future execution starts from this file and the current canonical HEAD, verifies current CI/live evidence, closes the next open gate, records the result, and repeats until either all gates are PASS or a technically unresolvable external blocker is documented.

## CI CONTROL CHECKPOINT

This commit is an intentional no-functional-change checkpoint used to force a fresh CI evaluation of the canonical branch. It does not alter RO App data, API behavior, production write permissions, or business logic.
