# MARSEL ROAPP

**Единая система Ювелирной студии MARSEL.** MARSEL — бизнес-контур; ROAPP — технологический контур той же системы.

## Canonical source

- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Branch: `main`
- Canonical control plane: `.github/workflows/marsel-unified-control-plane.yml`
- Canonical system document: [`MARSEL_ROAPP_UNIFIED_SYSTEM.md`](MARSEL_ROAPP_UNIFIED_SYSTEM.md)
- Master project control: [`docs/PROJECT_MASTER_CONTROL.md`](docs/PROJECT_MASTER_CONTROL.md)
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

## Canonical technical components

- `scripts/marsel_api_inventory_v20_32.py`
- `scripts/marsel_data_quality_v22_readonly.py`
- `scripts/marsel_entity_audit_v20_35.py`
- `scripts/marsel_product_code_collision_audit_v22_3.py`
- `scripts/marsel_warehouse_contract_v20_48.py`
- `scripts/marsel_api_v2_probe_v1.py`
- `scripts/marsel_api_v2_canonical_registry_v1.py`
- `scripts/marsel_canonical_self_check.py`

Internal dependencies on older numbered implementations remain until separately refactored and verified; version numbers alone are not grounds for deletion.

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

## Documentation

Use [`MARSEL_ROAPP_UNIFIED_SYSTEM.md`](MARSEL_ROAPP_UNIFIED_SYSTEM.md) for the canonical architecture and safety model, and [`docs/PROJECT_MASTER_CONTROL.md`](docs/PROJECT_MASTER_CONTROL.md) for the canonical master project control procedures.
