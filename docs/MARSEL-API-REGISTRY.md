# MARSEL / RO App API — Canonical Registry

## Назначение
Единый реестр API-контуров проекта. Отражает только текущую архитектуру `main`; исторические версии не считаются активными.

## Канонический live-контур

| Layer | Current implementation | Status |
|---|---|---|
| API inventory | `scripts/marsel_api_inventory_v20_32.py` | CANONICAL |
| Data quality | `scripts/marsel_data_quality_v22_readonly.py` | CANONICAL |
| Entity audit | `scripts/marsel_entity_audit_v20_35.py` | CANONICAL |
| Product-code review | `scripts/marsel_product_code_collision_audit_v22_1.py` | CANONICAL / ADVISORY |
| Structural self-check | `scripts/marsel_canonical_self_check.py` | CANONICAL |
| Orchestration | `.github/workflows/marsel-unified-control-plane.yml` | CANONICAL |

## API contract state

Base URL: `https://api.roapp.io/v2`.

Official source: https://help.roapp.io/en/articles/3393227-api-general-information

RO App documents the public API as a REST API with Bearer authentication and a limit of up to 3 requests/second. The official documentation also states that the previous API version remains supported until September 1, 2026, which is relevant to the current audit date.

The canonical production audit remains READ-ONLY. No POST/PATCH/DELETE operation is executed by the canonical audit workflow.

An endpoint is `CONFIRMED` only when official RO App documentation explicitly binds the HTTP method to that endpoint. Unknown or insufficiently evidenced routes remain unresolved; endpoints are never guessed.

### Independently confirmed official routes

| Method | Path | Official evidence | Status |
|---|---|---|---|
| GET | `/orders` | RO App API documentation | CONFIRMED |
| GET | `/contacts/people` | RO App API Reference: Get People | CONFIRMED |

Official source for `/contacts/people`: https://roappua.readme.io/reference/get-people

### Not yet established

The live inventory currently confirms 24 operations from the available documentation set, but required MARSEL entity completeness is not yet established. Seven entity classes are currently blocked by the repository's evidence gate because a non-parameterized, contract-confirmed collection route has not been established in the canonical inventory. This is a documentation/evidence blocker, not permission to guess an endpoint.

## Data findings

The latest live READ-ONLY run audited:

- Products: 1,721
- Services: 728
- Orders: 4,397
- API access failures: 0
- Hard data-quality issues: 0
- Duplicate product-code groups: 11 (review required)
- Production writes: 0
- RO App data mutated: false

Duplicate product codes are not automatically rewritten. Resolution requires identifying the intended canonical product and a verified write contract; until then the collision report remains advisory and production-safe.

## Pagination and safety

- Pagination is handled by the canonical inventory and entity auditors.
- Parameterized identifiers are never guessed.
- Production audit mode is READ-ONLY.
- `WRITE_REQUESTS_MADE=0` and `RO_APP_DATA_MUTATED=false` are mandatory invariants.
- A review finding is not silently converted to PASS.

## Historical scripts

Older versioned scripts may remain as source history or compatibility material. They are not canonical and must not be wired into the live Unified Control Plane. New audit functionality must extend the canonical implementations rather than creating another parallel workflow.

## Current truth

The latest unified run is `REVIEW_REQUIRED`, not production-ready. API inventory, data quality, entity audit and product collision checks all execute successfully, but the final gate correctly stops because entity completeness is not established and 11 duplicate product-code groups require review.
