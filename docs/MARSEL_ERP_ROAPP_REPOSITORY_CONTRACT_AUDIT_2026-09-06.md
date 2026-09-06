# MARSEL ROAPP — ERP ↔ RO App Repository Contract Audit

Дата контрольной точки: 2026-09-06  
Режим: READ_ONLY  
Production WRITE: `0`

## 1. Цель

Проверить репозиторий `atalanrafael-jpg/MARSEL-Ro-app` на наличие уже реализованных RO App контрактов для ERP-сущностей и не создавать параллельные реализации.

## 2. Фактически найдено в `main`

| Домен | Repository implementation | Evidence status | ERP mapping status |
|---|---|---|---|
| Orders | `app/roapp_client.py` → `GET /orders`; canonical data-quality/entity audit | LIVE-READ-VERIFIED endpoint; historical live evidence | PARTIAL / LIVE-READ-VERIFIED |
| Products | `scripts/marsel_data_quality_v22_readonly.py` → `/catalog/products`; entity audit reuses this path | CODE/DOCUMENTED; current live status requires fresh authorized run | NOT VERIFIED as current standalone contract |
| Services | `scripts/marsel_data_quality_v22_readonly.py` → `/catalog/services`; entity audit reuses this path | CODE/DOCUMENTED; current live status requires fresh authorized run | NOT VERIFIED as current standalone contract |
| Warehouse | `scripts/marsel_warehouse_contract_v20_48.py` → documented `/warehouse/` probe | LIVE-READ-VERIFIED contract from recorded evidence; schema partial | LIVE-READ-VERIFIED contract only |
| Customers | entity audit models `clients`, but no independently confirmed standalone collection route | NOT VERIFIED | NOT VERIFIED |
| Payments | repository documentation/model references only; no confirmed production endpoint implementation found | NOT VERIFIED | NOT VERIFIED |
| Stock / StockMovement | no verified production collection implementation found | NOT VERIFIED | NOT VERIFIED |
| Materials / Metals / Stones | ERP model/spec references exist, but no verified RO App collection contract found | NOT VERIFIED | NOT VERIFIED |

## 3. Important implementation findings

### RO App client

`app/roapp_client.py` intentionally exposes only read operations and implements `get_orders()` / paginated `get_orders_pages()`. No POST/PUT/PATCH/DELETE method is implemented.

### Canonical API contract

`app/roapp_contract.py` currently contains only one verified read endpoint: `/orders`. Write methods remain blocked.

### Data-quality audit

`scripts/marsel_data_quality_v22_readonly.py` contains collection paths for `products`, `services`, and `orders`, and performs only GET requests with pagination and duplicate/missing-ID checks. Presence of these paths in code is repository implementation evidence, not fresh production evidence.

### Entity audit

`scripts/marsel_entity_audit_v20_32.py` explicitly reuses `orders`, `products`, and `services` as safe-live collection paths based on the canonical read-only data-quality audit. The script itself explicitly states that live verification is not equivalent to official API contract confirmation and does not guess parameterized entities.

### Warehouse

`scripts/marsel_warehouse_contract_v20_48.py` implements a read-only probe of the documented `/warehouse/` contract. Existing repository evidence records a successful warehouse-list contract audit with zero writes and no data mutation. This does not establish stock balances or stock-movement contracts.

## 4. ERP consequence

The repository already contains reusable read-only infrastructure for Orders, Products, Services and Warehouse. No parallel ERP connector for these domains should be created before the existing implementations are reconciled with current official RO App documentation and fresh authorized GET evidence.

For Customers, Payments, Stock, StockMovement, Materials, Metals and Stones, the correct state remains `NOT VERIFIED`; endpoint names must not be inferred from entity names.

## 5. Safety decision

- Production writes: `0`.
- No production synchronization enabled.
- No duplicate auto-merge/delete performed.
- No credentials or API keys modified.
- No endpoint promoted solely because a code path exists.
- No parallel costing or finance engine created.

## 6. Next evidence gate

1. Fresh authorized GET evidence for existing product/service/order routes.
2. Fresh official documentation confirmation for each route before contract promotion.
3. Official route discovery for Customers, Payments, Stock and StockMovement.
4. Response-schema capture and canonical-ID mapping.
5. Only after read evidence: costing implementation audit and finance-source reconciliation.

## 7. Current ERP gate

`ERP_DATA_DICTIONARY = DONE / DESIGN`  
`REPOSITORY_CONTRACT_AUDIT = DONE`  
`ENTITY_API_MAPPING = PARTIAL / WAREHOUSE-CONTRACT-VERIFIED`  
`STOCK = NOT VERIFIED`  
`COSTING = NOT VERIFIED`  
`FINANCE = NOT VERIFIED`  
`ERP_READINESS = BLOCKED`  
`PRODUCTION_WRITE = 0`
