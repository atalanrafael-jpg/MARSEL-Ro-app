# MARSEL ROAPP — MASTER PROJECT CONTROL

## Purpose
Единая контрольная точка проекта: техническое состояние RO App integration, качество данных, безопасность, бизнес-автоматизация и коммерческий контур MARSEL.

## Canonical state — 2026-09-04
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Branch: `main`
- Current observed `main` HEAD: `745a522c3b95fe14216963d126d66080df07c816` (`docs: refresh canonical MARSEL current state checkpoint`).
- Current integration mode: READ-ONLY.
- Production WRITE: DISABLED.
- Canonical live audit workflow: `.github/workflows/marsel-unified-control-plane.yml`.
- Canonical warehouse implementation: `scripts/marsel_warehouse_contract_v20_48.py`.
- Historical implementations and snapshots belong in `старые данные/` and do not override current evidence.

## Fresh runtime evidence
- Run `33868944393` for `MARSEL Live Integration Probes` on current `main` HEAD `745a522c...` completed `success` on 2026-09-04.
- This fresh successful run does not by itself prove backup/restore, full entity completeness, OAuth, MCP authorization, or production readiness.
- PR #113 remains open; its current head has previously verified green PR-triggered CI, but merge is not automatic and live OpenAI authorization is not claimed without direct evidence.

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
1. Backup/export and independent restore/integrity evidence remain unproven.
2. Complete current API/entity verification remains open.
3. Warehouse-list contract discrepancy remains unresolved: documented `/v2/warehouse/` forms previously returned HTTP 404; undocumented compatibility behavior is not accepted as official PASS.
4. Collision/reference findings require controlled reconciliation; no automatic deletion.
5. Gmail OAuth requires actual user-authorized live verification.
6. Official RO App MCP authorization requires separate live verification.
7. Historical credential-exposure remediation requires direct evidence (Issue #23).
8. GitHub account/ruleset/security settings require account-level action where connector access is read-only. Direct ruleset inspection shows active ruleset `21230907` currently targets malformed pattern `refs/heads/Include by pattern main` rather than `refs/heads/main`.
9. ReadMe ↔ GitHub bi-directional sync (Issue #106) requires external ReadMe setup in a dedicated empty docs repository; production application repository must not be connected directly without explicit approval.

## Open issue consolidation
- Issue #42 was closed as a duplicate of the broader current warehouse blocker tracked by Issue #87. No technical evidence was discarded.
- Remaining open work is tracked by the current GitHub issue set, with #19, #23, #25, #27, #30, #66, #77, #83, #85, #87, #88, #91, #92, #94 and #106 requiring review/verification as applicable.

## Status rule
A gate is `PASS` only when current direct evidence exists. `PLANNED`, `CODED`, `NOT_TESTED`, `ASSUMED`, `OLD_PASS`, or `UNVERIFIED` are not PASS.

## Safety rule
Never claim backup, restore, reconciliation, security rotation, OAuth, MCP authorization or WRITE readiness without direct evidence. Never guess an API endpoint or identifier. Never execute a production mutation merely to make a test green.

## Continuation rule
Every execution starts from this file and the current `main` HEAD, verifies current CI/live evidence, closes the next highest-priority open gate, records the result, and repeats until all required gates are PASS or an external blocker is documented.
