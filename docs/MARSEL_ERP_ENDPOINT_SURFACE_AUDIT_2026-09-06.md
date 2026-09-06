# MARSEL ROAPP — ERP Endpoint Surface Audit

Дата: 2026-09-06  
Режим: READ_ONLY / WRITE=0

## Цель

Проверить, какие RO App endpoint paths уже присутствуют в repository implementation и не ошибочно ли они принимаются за подтверждённые ERP API contracts.

## Repository evidence

Скрипт `scripts/marsel_inventory_v20_12.py` содержит READ-only targets:

- `/orders`
- `/catalog/services`
- `/catalog/products`
- `/catalog/bundles`
- `/inquiries`
- `/bookings`
- `/estimates`
- `/invoices`

Скрипт явно запрещает POST/PUT/PATCH/DELETE и фиксирует `write_requests_made=0` / `ro_app_data_mutated=false` в своём отчёте.

## Контрольная классификация

| Entity / path | Repository presence | API contract status | ERP promotion |
|---|---|---|---|
| Orders `/orders` | IMPLEMENTED | VERIFIED | LIVE-READ-VERIFIED within verified endpoint scope |
| Products `/catalog/products` | IMPLEMENTED | repository/read-audit evidence only | NOT VERIFIED as full contract |
| Services `/catalog/services` | IMPLEMENTED | repository/read-audit evidence only | NOT VERIFIED as full contract |
| Bundles `/catalog/bundles` | IMPLEMENTED as inventory target | no current contract promotion | NOT VERIFIED |
| Inquiries `/inquiries` | IMPLEMENTED as inventory target | no current contract promotion | NOT VERIFIED |
| Bookings `/bookings` | IMPLEMENTED as inventory target | no current contract promotion | NOT VERIFIED |
| Estimates `/estimates` | IMPLEMENTED as inventory target | no current contract promotion | NOT VERIFIED |
| Invoices `/invoices` | IMPLEMENTED as inventory target | no current contract promotion | NOT VERIFIED |
| Warehouse | separate repository contract evidence | warehouse-list contract only | LIVE-READ-VERIFIED / CONTRACT ONLY |
| Stock | no verified mapping | no verified GET evidence | NOT VERIFIED |
| StockMovement | no verified mapping | no verified GET evidence | NOT VERIFIED |
| Materials / Metals / Stones | no verified mapping | no verified GET evidence | NOT VERIFIED |
| Customers | no verified standalone mapping | no verified GET evidence | NOT VERIFIED |
| Payments | no verified mapping | no verified GET evidence | NOT VERIFIED |

## Important control finding

Наличие endpoint path в audit/inventory script не является доказательством официального API contract. Эти paths нельзя автоматически добавлять в canonical API registry или ERP entity mapping со статусом `LIVE-READ-VERIFIED`.

## Safety

- Production WRITE = 0.
- Новые endpoint contracts не активированы.
- Никаких POST/PUT/PATCH/DELETE операций не добавлено.
- Никакие production данные не изменяются.
- Не создаётся параллельный ERP connector.

## Decision

Существующую READ-only inventory infrastructure сохраняем как audit capability, но canonical ERP/API mapping повышается только после отдельного evidence: official documentation → authorized GET → captured response/status/shape → pagination/rate limit → IDs/reference checks → timestamp/hash.

## Next P0

1. Fresh authorized GET evidence for stock/stock movements.
2. Determine whether materials/metals/stones exist as official RO App entities.
3. Verify standalone customer/payment contracts or explicitly document that they are unavailable.
4. Reconcile products/services inventory evidence with canonical API registry.
5. Continue costing implementation audit and finance source/reconciliation.

## Gate

`ERP_ENDPOINT_SURFACE_AUDIT = DONE / READ_ONLY`

`ERP_ENTITY_API_MAPPING = PARTIAL`

`ERP_INVENTORY = BLOCKED / STOCK NOT VERIFIED`

`ERP_COSTING = NOT VERIFIED`

`ERP_FINANCE = NOT VERIFIED`

`ERP_READINESS = BLOCKED`

`PRODUCTION_WRITE = 0`
