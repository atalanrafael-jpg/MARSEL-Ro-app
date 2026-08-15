# MARSEL / RO App API — Canonical Registry

## Назначение
Единый реестр API-контуров проекта. Этот документ отражает только текущую архитектуру `main` и не перечисляет удалённые workflow как активные.

## Канонический live-контур

| Layer | Current implementation | Status |
|---|---|---|
| API inventory | `scripts/marsel_api_inventory_v20_31.py` | CANONICAL |
| Data quality | `scripts/marsel_data_quality_v22_readonly.py` | CANONICAL |
| Entity audit | `scripts/marsel_entity_audit_v20_32.py` | CANONICAL |
| Product-code review | `scripts/marsel_product_code_collision_audit_v22_1.py` | CANONICAL / ADVISORY |
| Structural self-check | `scripts/marsel_canonical_self_check.py` | CANONICAL |
| Orchestration | `.github/workflows/marsel-unified-control-plane.yml` | CANONICAL |

## API contract state

`https://api.roapp.io/v2` is the configured base URL. The repository is intentionally READ-ONLY for production audit operations: no POST/PATCH/DELETE operation is executed by the canonical audit workflow.

The canonical registry accepts an endpoint as `CONFIRMED` only when the official RO App documentation explicitly binds the HTTP method to that endpoint. Unknown or insufficiently evidenced routes remain unresolved rather than being guessed.

### Confirmed

| Method | Path | Source | Status |
|---|---|---|---|
| GET | `/orders` | RO App API documentation / Getting Started | CONFIRMED |

### Not yet established

The live inventory has discovered additional documented/API-reference material, but this repository does **not** yet mark every discovered route as contract-confirmed. API completeness therefore remains `NOT_ESTABLISHED` until each route has explicit documentary evidence and, where safe, a matching READ-ONLY verification.

## Pagination and safety

- Pagination is handled by the canonical inventory and entity auditors.
- Parameterized identifiers are never guessed.
- Production audit mode is READ-ONLY.
- `WRITE_REQUESTS_MADE=0` and `RO_APP_DATA_MUTATED=false` are mandatory invariants.
- A review finding is not automatically a hard failure unless the contract establishes that the finding violates a required invariant.

## Historical scripts

Older versioned scripts may remain in the repository as source history or compatibility material. They are **not canonical** and must not be wired into the live Unified Control Plane. New audit functionality must extend the canonical implementations rather than creating another parallel `v20.xx` workflow.

## Current truth

The canonical workflow has successfully executed the API inventory, data-quality, entity and product-code checks on the latest run. The latest run remains `REVIEW_REQUIRED` because API/entity completeness is not yet established. This is an intentional safety state, not a successful production-readiness claim.
