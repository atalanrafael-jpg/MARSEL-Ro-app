# MARSEL ROAPP

**Единая система Ювелирной студии MARSEL.** MARSEL — бизнес-контур; ROAPP — технологический контур той же системы.

## Canonical source

- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Branch: `main`
- Canonical index: [`docs/MARSEL-CANONICAL-INDEX.md`](docs/MARSEL-CANONICAL-INDEX.md)
- Permanent project core: [`MARSEL_ROAPP_MASTER_CORE.md`](MARSEL_ROAPP_MASTER_CORE.md)
- Current project control: [`docs/PROJECT_MASTER_CONTROL.md`](docs/PROJECT_MASTER_CONTROL.md)
- Canonical architecture: [`MARSEL_ROAPP_UNIFIED_SYSTEM.md`](MARSEL_ROAPP_UNIFIED_SYSTEM.md)
- Canonical live audit: `.github/workflows/marsel-unified-control-plane.yml`
- Historical material: `старые данные/`

## Operating model

`OBSERVE → MEASURE → FIND → FIX → TEST → VERIFY → DOCUMENT → MONITOR`

For RO App live work:

`INVENTORY → DATA QUALITY → ENTITY AUDIT → COLLISION REVIEW → WAREHOUSE CONTRACT → SAFETY GATE → EVIDENCE`

All RO App live auditing is **READ-ONLY**. Parameterized identifiers are never guessed. Missing, incomplete, or conflicting evidence produces `REVIEW_REQUIRED`, not `PASS`.

## Production safety

**Production WRITE is disabled.** A controlled write is considered only after direct evidence exists for:

`backup/export → restore integrity → schema reconciliation → full READ-ONLY inventory → duplicate/orphan/reference analysis → dry-run → idempotency → rollback → controlled write → post-write verification`

A successful CI run, the existence of write methods, or documentation alone is not proof of production synchronization or WRITE readiness.

## Canonical control components

The exact owner for each control responsibility is defined by [`docs/MARSEL-CANONICAL-INDEX.md`](docs/MARSEL-CANONICAL-INDEX.md). Do not create a parallel registry, workflow or implementation without first checking that index.

The active script set is governed by `02_ROAPP/CONTROL/ACTIVE-SCRIPT-REGISTRY.md`. Internal versioned dependencies remain until dependency analysis and fresh verification justify refactoring or archival.

## Current external gates

The following must not be reported as completed without fresh direct evidence:

- backup/export and independent restore/integrity test;
- complete API/entity coverage;
- authoritative warehouse/stock contract;
- collision/reference reconciliation;
- user-authorized Gmail OAuth read-only verification;
- official RO App MCP authorization;
- credential-exposure remediation evidence;
- GitHub account/ruleset/security controls requiring account-level verification.

## Evidence rule

Evidence precedence:

1. Current `main` repository state.
2. Current CI/workflow evidence tied to current `main`.
3. Direct live API evidence with timestamps/artifacts.
4. Current official RO App documentation.
5. Older project documents as historical context only.

`DONE` / `PASS` requires current direct evidence. `PLANNED`, `CODED`, `NOT_TESTED`, `ASSUMED`, `OLD_PASS`, and `UNVERIFIED` are not `PASS`.

## Start here

1. Read `docs/MARSEL-CANONICAL-INDEX.md`.
2. Read `docs/PROJECT_MASTER_CONTROL.md` for the current checkpoint.
3. Check current CI/evidence before continuing work.
4. Fix the highest-priority safe blocker.
5. Update the canonical control artifact and evidence.
6. Do not create a second source of truth.
