# MARSEL ROAPP — MASTER PROJECT CONTROL

## Purpose
Единая контрольная точка проекта: техническое состояние RO App integration, качество данных, безопасность, бизнес-автоматизация и коммерческий контур MARSEL.

## Canonical state — 2026-09-13
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Canonical branch: `main-MARSEL-ROAPP`
- Canonical HEAD before this documentation reconciliation: `238d1c7121d902ae3bdacf59b33525b585c79090`.
- The canonical HEAD commit is verified and contains the security hardening boundary; its message states that Production WRITE remains disabled.
- Current integration mode: READ-ONLY.
- Production WRITE: DISABLED.
- Canonical live audit workflow: `.github/workflows/marsel-unified-control-plane.yml`.
- Canonical warehouse implementation: `scripts/marsel_warehouse_contract_v20_48.py`.
- Historical implementations and snapshots do not override current evidence.

## Canonical-branch correction
The repository's live GitHub metadata identifies `main-MARSEL-ROAPP` as the default/canonical branch. Earlier project documents referred to `main`; those references were stale and are not current source-of-truth. They must not be used for routing current work.

## Latest verified CI
- Previously recorded successful CI runs remain historical evidence unless freshly tied to the current canonical HEAD.
- No CI result is promoted to current PASS solely because an older checkpoint passed.
- CI success proves only the tested repository/build path for that run; it does not prove production readiness, current live API access, backup/restore, OAuth, MCP, or WRITE readiness.

## Evidence precedence
1. Current `main-MARSEL-ROAPP` repository state.
2. Current GitHub workflow/run evidence tied to current `main-MARSEL-ROAPP`.
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
- [ ] Production writes explicitly enabled only after all gates pass and explicit authorization exists

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
8. GitHub account/repository security controls require account-level administration; branch-protection state was not independently readable through the current connector and is therefore NOT VERIFIED.
9. ReadMe ↔ GitHub bi-directional sync requires external ReadMe configuration in a dedicated docs repository.
10. Production WRITE remains disabled until every applicable safety gate passes and explicit authorization exists.
11. Repository branch consolidation is not complete: 157 branches were discovered in the current branch inventory. Historical/candidate branches must be classified by commit ancestry and divergence before any deletion. No branch is deleted automatically.

## Branch governance
- Canonical branch: `main-MARSEL-ROAPP`.
- `main` is not the current branch name and must not be treated as canonical.
- The branch inventory contains historical audit, backup, feature, fix, automation, integration, security, test and version branches.
- Duplicate branch names/labels or similar purpose do not prove duplicate content.
- Branch deletion is blocked until each branch is classified for ancestry/divergence, unique commits, required PR/issue references, and recoverability.

## Safety rule
Never claim backup, restore, reconciliation, security rotation, OAuth, MCP authorization or WRITE readiness without direct evidence. Never guess an API endpoint or identifier. Never execute a production mutation merely to make a test green. Never expose or commit `ROAPP_API_KEY`.

## Continuation rule
Every execution starts from this file and the current `main-MARSEL-ROAPP` checkpoint, verifies current CI/live evidence, fixes the next highest-priority safe defect, records the result, and repeats until all required gates are PASS or an external blocker is documented.
