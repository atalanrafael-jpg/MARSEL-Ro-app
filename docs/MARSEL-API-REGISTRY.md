# MARSEL / RO App API — Canonical Registry

## Назначение
Единый реестр API-контуров проекта MARSEL ROAPP. Отражает только текущую архитектуру `main`; исторические версии сохраняются как история и не считаются активными.

## Каноническая архитектура

- MARSEL = бизнес-контур.
- ROAPP = технический контур.
- MARSEL ROAPP = одна объединённая система.
- Канонический repository: `atalanrafael-jpg/MARSEL-Ro-app`.
- Каноническая ветка: `main`.
- Канонический live audit control plane: `.github/workflows/marsel-unified-control-plane.yml`.
- Production audit mode: READ-ONLY.

## Канонический live-контур

| Layer | Current implementation | Status |
|---|---|---|
| API inventory | `scripts/marsel_api_inventory_v20_32.py` | CANONICAL |
| Data quality | `scripts/marsel_data_quality_v22_readonly.py` | CANONICAL |
| Entity audit | `scripts/marsel_entity_audit_v20_35.py` | CANONICAL |
| Product-code review | `scripts/marsel_product_code_collision_audit_v22_3.py` | CANONICAL / ADVISORY |
| Warehouse contract | `scripts/marsel_warehouse_contract_v20_48.py` | CANONICAL |
| API v2 probe | `scripts/marsel_api_v2_probe_v1.py` | CANONICAL |
| API v2 registry | `scripts/marsel_api_v2_canonical_registry_v1.py` | CANONICAL |
| Structural self-check | `scripts/marsel_canonical_self_check.py` | CANONICAL |
| Orchestration | `.github/workflows/marsel-unified-control-plane.yml` | CANONICAL |

Internal dependencies on `v20_31` and `v20_29` remain historical/active dependencies until separately refactored and verified; version numbers alone are not grounds for deletion.

## API contract state

Base URL recorded by the repository: `https://api.roapp.io/v2`.

Official documentation references recorded by the repository:
- `https://help.roapp.io/en/articles/3393227-api-general-information`
- `https://roappua.readme.io/reference/get-people`

The repository records the RO App public API as REST with Bearer authentication and a documented limit of up to 3 requests/second. These claims are retained as repository evidence, but their current official status must be revalidated before being used as a production contract.

**Important date correction:** the previous registry stated that an older API version remained supported until September 1, 2026. The current audit date is September 3, 2026, so that statement is now stale. It must not be treated as evidence of current compatibility. Current version support remains `REVIEW_REQUIRED` until verified against the live official RO App documentation.

The canonical production audit remains READ-ONLY. No POST/PATCH/DELETE operation is executed by the canonical audit workflow.

An endpoint is `CONFIRMED` only when official RO App documentation explicitly binds the HTTP method to that endpoint. Unknown, parameter-dependent, or insufficiently evidenced routes remain unresolved; endpoints are never guessed.

### Independently confirmed official routes recorded in the repository

| Method | Path | Official evidence | Status |
|---|---|---|---|
| GET | `/orders` | RO App API documentation | CONFIRMED |
| GET | `/contacts/people` | RO App API Reference: Get People | CONFIRMED |

The repository currently does not establish complete MARSEL entity coverage from official documentation. Seven entity classes remain blocked by the evidence gate because a non-parameterized, contract-confirmed collection route has not been established in the canonical inventory.

This is an evidence/documentation blocker, not permission to infer or guess routes.

## Latest repository evidence

The registry records the following latest READ-ONLY audit results:

- Products: 1,721
- Services: 728
- Orders: 4,397
- API access failures: 0
- Hard data-quality issues: 0
- Duplicate product-code groups: 11 — review required
- Production writes: 0
- `RO_APP_DATA_MUTATED=false`

These figures are historical evidence from the recorded audit state and must not be presented as current live values without a fresh run.

## Data and safety rules

- Pagination is handled by the canonical inventory and entity auditors.
- Parameterized identifiers are never guessed.
- Production audit mode is READ-ONLY.
- `WRITE_REQUESTS_MADE=0` and `RO_APP_DATA_MUTATED=false` are mandatory invariants for the canonical audit.
- A review finding is never silently converted to `PASS`.
- Duplicate product codes are not automatically rewritten.
- A verified write contract, intended canonical record, dry-run, idempotency and rollback evidence are required before any controlled production write can be considered.

## Historical scripts

Older versioned scripts may remain as source history or compatibility material. They are not canonical and must not be wired into the live Unified Control Plane. New audit functionality must extend the canonical implementations rather than create parallel live audit paths.

## Current truth

The project state is `REVIEW_REQUIRED`, not production-ready. The canonical architecture is consolidated under MARSEL ROAPP, while API/entity completeness and the recorded 11 duplicate product-code groups remain unresolved gates. Fresh evidence is required before changing these statuses.
