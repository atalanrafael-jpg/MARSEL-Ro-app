# MARSEL ROAPP

**Единая система Ювелирной студии MARSEL.** MARSEL и ROAPP — два внутренних контура одной системы, не отдельные проекты.

## Canonical source

- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Canonical branch: `main`
- Canonical structure: `01_MASTER/` → `02_MARSEL/` → `03_ROAPP/` → `04_DEVELOPMENT/` → `05_CONTROL/` → `06_ARCHIVE/`
- Canonical system definition: `01_MASTER/MARSEL_ROAPP_CANONICAL.md`
- Master registry: `01_MASTER/MARSEL_ROAPP_MASTER_REGISTRY.md`
- Current state: `01_MASTER/MARSEL_ROAPP_CURRENT_STATE.md`
- Canonical control plane: `.github/workflows/marsel-unified-control-plane.yml`

## Operating model

`OBSERVE → MEASURE → FIND → FIX → TEST → VERIFY → DOCUMENT → MONITOR`

For ROAPP live work:

`INVENTORY → DATA QUALITY → ENTITY AUDIT → COLLISION REVIEW → WAREHOUSE CONTRACT → SAFETY GATE → EVIDENCE`

All ROAPP live auditing is **READ-ONLY**. Parameterized identifiers are never guessed. Missing, incomplete, or conflicting evidence produces `REVIEW_REQUIRED`, not `PASS`.

## Production safety

**Production WRITE is disabled.** A controlled write is considered only after direct evidence exists for backup/export, restore integrity, schema reconciliation, complete READ-ONLY inventory, duplicate/reference analysis, dry-run, idempotency, rollback, controlled write and post-write verification.

A successful CI run, the existence of write methods, or documentation alone is not proof of production synchronization or WRITE readiness.

## Control plane

The canonical active workflow registry is `05_CONTROL/ACTIVE-WORKFLOW-REGISTRY.md`.
The canonical active script registry is `05_CONTROL/ACTIVE-SCRIPT-REGISTRY.md`.

Versioned implementation files that remain because of verified dependency chains are not separate systems and are not independent entrypoints. They are candidates for later consolidation after dependency and test verification.

## Evidence rule

Evidence precedence:

1. Current `main` repository state.
2. Current CI/workflow evidence tied to current `main`.
3. Direct live API evidence with timestamps/artifacts.
4. Current official ROAPP documentation.
5. Historical material in `06_ARCHIVE/`.

`DONE` / `PASS` requires current direct evidence. `PLANNED`, `CODED`, `NOT_TESTED`, `ASSUMED`, `OLD_PASS`, and `UNVERIFIED` are not `PASS`.

## Current status

This branch is the **canonical cleanup candidate**. It removes duplicate master documents, removes the obsolete `старые данные` tree, establishes the single canonical structure, and removes obsolete versioned workflow entrypoints without weakening safety gates.
