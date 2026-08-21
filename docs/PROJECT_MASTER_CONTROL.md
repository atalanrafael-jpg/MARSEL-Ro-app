# MARSEL / ROAPP — MASTER PROJECT CONTROL

## Purpose
Единая контрольная точка проекта: техническое состояние RO App integration, качество данных, безопасность, бизнес-автоматизация и коммерческий контур MARSEL.

## Canonical state
- Repository: `atalanrafael-jpg/Ro-app`
- Branch: `main`
- Current HEAD: `f4e213ec6eaf3f4d58bccf037015a6d7e38694a3` (`chore: remove duplicate warehouse audit workflow from canonical control plane`).
- Current integration mode: READ-ONLY.
- Production WRITE: DISABLED.
- Canonical warehouse implementation: `scripts/marsel_warehouse_contract_v20_36.py`.
- Warehouse audit is controlled by the Unified Control Plane; the previously separate warehouse workflow has been removed to avoid duplicate control paths.

## Evidence precedence
1. Current `main` repository state.
2. Current GitHub workflow/run evidence tied to the current `main` HEAD.
3. Direct live API evidence with timestamps/artifacts.
4. Current official RO App documentation.
5. Older project documents are historical only and must not override current evidence.

## Verified external facts
- RO App documents Public API v2 and states that API requests are performed on behalf of the employee whose API key is used; access to a warehouse/location depends on that employee's permissions.
- RO App states that if an endpoint is not available in the latest API documentation, the previous API version may be used until September 1, 2026.
- RO App's current API documentation must be treated as the source for refreshing the API registry; the registry is not a permanent substitute for current official documentation.
- RO App documents stock/product-price synchronization with websites, but website sales do not automatically write off RO App inventory or automatically create a sale in RO App. This must be accounted for in MARSEL ecommerce synchronization design.
- Warehouse/stock operations require verified warehouse identifiers; identifiers must never be guessed.

## 100% completion gates

### Engineering
- [ ] Unit tests GREEN on current `main` HEAD
- [ ] All required CI workflows GREEN on current `main` HEAD
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

### MARSEL Revenue Engine
- [ ] Customer lifecycle defined
- [ ] Repair-to-repeat-sales flow defined
- [ ] Custom manufacturing sales flow defined
- [ ] Daily action queue defined
- [ ] KPI model connected to factual business data
- [ ] 30-day content system prepared
- [ ] Lead attribution and conversion tracking prepared

## Current blockers
1. Current CI/live results for the current `main` HEAD must be directly verified; older successful runs do not prove current state.
2. Warehouse/stock contract requires direct evidence and safe verification with real permitted identifiers; identifiers must never be guessed.
3. Duplicate/anomaly and reconciliation gates remain open until current evidence is attached.
4. Backup/restore evidence is not yet proven by this control record.
5. Production WRITE remains prohibited until all required gates are evidenced.

## Status rule
A gate is `PASS` only when current evidence exists. `PLANNED`, `CODED`, `NOT_TESTED`, `ASSUMED`, `OLD_PASS`, or `UNVERIFIED` are not PASS.

## Safety rule
Never claim backup, restore, reconciliation, security, rotation, or WRITE readiness without direct evidence. Never guess an API endpoint or identifier. Never execute a production mutation merely to make a test green.

## Continuation rule
Every future execution starts from this file and the current `main` HEAD, verifies current CI/live evidence, closes the next open gate, records the result, and repeats until either all gates are PASS or a technically unresolvable external blocker is documented.
