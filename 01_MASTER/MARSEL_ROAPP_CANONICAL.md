# MARSEL ROAPP — CANONICAL SYSTEM

**Status:** CANONICAL
**System:** MARSEL ROAPP
**Repository:** `atalanrafael-jpg/MARSEL-Ro-app`
**Current canonical branch:** `main`

## Identity
MARSEL ROAPP is one unified business and technical system. MARSEL and ROAPP are internal contours of the same system, not separate projects.

## Canonical structure
```text
01_MASTER/        system control, registry, state, decisions, tasks, changes
02_MARSEL/        business, brand, services, catalog, commerce
03_ROAPP/         API, data, products, materials, inventory, orders, customers
04_DEVELOPMENT/   code, GitHub, CI/CD, tests, automation, AI/MCP
05_CONTROL/       quality, backup/restore, security, production gates, verification
06_ARCHIVE/       historical and superseded material only
```

## Authority
Only this canonical structure and the registries referenced from `01_MASTER` define the current system. Historical material is not authoritative.

## Safety boundaries
- ROAPP integration: READ-ONLY.
- Production WRITE: disabled.
- Secrets: never committed, printed, rotated, or copied into repository files.
- Evidence: never fabricated or downgraded to make a gate pass.
- `main` is the technical canonical branch and current execution source.
- `Main`, `main-MARSEL-ROAPP` and `main-MARSEL-ROAPP-PROTECTION` are non-canonical compatibility/snapshot branches, aligned to the current `main` commit on 2026-09-18.
- GitHub repository default branch is `main`.

## Consolidation rule
A capability has one implementation, one owner, one registry entry, and one active workflow. Historical implementations are archived or removed only after dependency and recovery checks.

Feature, audit, backup, temporary and historical branches remain non-canonical until their unique changes are independently reviewed and safely incorporated into `main`. They must not be treated as separate MARSEL ROAPP systems.

Branch deletion is an administrative operation and must not be simulated by documentation or by moving a branch ref.
