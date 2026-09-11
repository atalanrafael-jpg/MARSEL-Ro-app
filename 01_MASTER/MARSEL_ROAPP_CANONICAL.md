# MARSEL ROAPP — CANONICAL SYSTEM

**Status:** CANONICAL
**System:** MARSEL ROAPP
**Repository:** `atalanrafael-jpg/MARSEL-Ro-app`
**Canonical branch:** `main`

## 1. Identity
MARSEL ROAPP is one unified business and technical system. MARSEL and ROAPP are internal contours of the same system, not separate projects.

## 2. Canonical structure
```text
01_MASTER/        system control, registry, state, decisions, tasks, changes
02_MARSEL/        business, brand, services, catalog, commerce
03_ROAPP/         API, data, products, materials, inventory, orders, customers
04_DEVELOPMENT/   code, GitHub, CI/CD, tests, automation, AI/MCP
05_CONTROL/       quality, backup/restore, security, production gates, verification
06_ARCHIVE/       historical and superseded material only
```

## 3. Authority
Only this canonical structure and the registries referenced from `01_MASTER` define the current system. Files with historical dates, version suffixes, old project names, or obsolete architecture are not authoritative.

## 4. Safety boundaries
- ROAPP integration: READ-ONLY.
- Production WRITE: disabled.
- Secrets: never committed, printed, rotated, or copied into repository files.
- Evidence: never fabricated or downgraded to make a gate pass.
- `main` is the only production/canonical branch.

## 5. Consolidation rule
A capability has one implementation, one owner, one registry entry, and one active workflow. Historical implementations are archived or removed; they are not kept as parallel active alternatives.

## 6. Change control
Changes to the canonical system must be made through reviewed GitHub changes and must pass the repository protection rules. This cleanup does not bypass required reviews or production gates.
