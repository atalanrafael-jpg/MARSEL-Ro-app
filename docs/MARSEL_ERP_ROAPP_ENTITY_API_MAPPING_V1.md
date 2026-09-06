# MARSEL ROAPP — ERP ↔ RO APP ENTITY/API MAPPING V1

Дата контрольной точки: 2026-09-06
Статус: DESIGN / READ_ONLY / WRITE=0

## 1. Назначение

Первичная матрица сопоставления ERP-сущностей с RO App API. Документ использует только текущие repository evidence и не превращает архитектурные сущности в подтверждённые live API endpoints.

## 2. Evidence rule

`CONFIRMED` означает, что текущий canonical repository registry содержит прямую официальную документационную привязку метода и пути.

`MAPPING_REQUIRED` означает, что ERP-сущность существует в модели, но текущего достаточного endpoint/schema evidence нет.

`NOT_VERIFIED` означает, что контракт требует отдельной live/documentation проверки.

Параметризованные identifiers и недокументированные routes не угадываются.

## 3. Current mapping

| ERP entity | RO App entity/API | Method/path | Evidence status | ERP role | Notes |
|---|---|---|---|---|---|
| Product | Products | — | MAPPING_REQUIRED | operational projection only after contract | Current registry does not establish a confirmed non-parameterized collection route |
| Service | Services | — | MAPPING_REQUIRED | operational projection only after contract | Current registry records historical inventory count, not a current endpoint contract |
| Customer | People / contacts | GET `/contacts/people` | CONFIRMED | operational reference where semantics match | Official route is recorded in canonical API registry; field/schema reconciliation still required |
| SalesOrder | Orders | GET `/orders` | CONFIRMED | operational source where confirmed | Endpoint is officially recorded; current schema mapping remains pending |
| SalesOrderLine | Order lines | — | MAPPING_REQUIRED | child projection | Requires current documented response schema |
| Warehouse | Warehouse | — | NOT_VERIFIED | operational source only after contract | Existing warehouse contract remains unresolved; documented `/v2/warehouse/` forms previously returned 404 |
| StockMovement | Inventory/warehouse movements | — | NOT_VERIFIED | operational source only after contract | No confirmed current collection contract in registry |
| Reservation | Stock/order reservation | — | NOT_VERIFIED | integration target | Requires authoritative contract |
| Supplier | Supplier/procurement entity | — | MAPPING_REQUIRED | ERP target owner | No confirmed current RO App route in registry |
| PurchaseOrder | Procurement | — | MAPPING_REQUIRED | ERP target owner | No confirmed current RO App route in registry |
| BOM | Production BOM | — | PROPOSED | ERP target owner | Not established as RO App source |
| ProductionOrder | Production | — | PROPOSED | ERP target owner | Not established as RO App source |
| RepairOrder | Repair/service | — | MAPPING_REQUIRED | ERP/service target owner | Current architecture requires mapping; no confirmed API route in registry |
| CostVersion | Costing | — | PROPOSED | ERP costing owner | No evidence that RO App currently owns versioned costing |
| CostComponent | Costing components | — | PROPOSED | ERP costing owner | Must remain componentized and traceable |
| Price | Product price | — | MAPPING_REQUIRED | MARSEL/ERP commercial layer | Requires current product/price schema evidence |
| Payment | Payment | — | NOT_VERIFIED | financial reference | Live methods are not currently verified |
| FinancialEntry | Finance | — | PROPOSED | external finance owner unless explicitly assigned | Must not be assigned to RO App by assumption |
| Media/3D Asset | Catalog/media | — | PROPOSED | Master Catalog owner | RO App ownership not established |

## 4. Confirmed API evidence currently available

The canonical API registry currently records only these independently confirmed official collection routes:

- `GET /orders`
- `GET /contacts/people`

The registry explicitly states that complete MARSEL entity coverage is not established and that unresolved routes must remain unresolved rather than inferred.

## 5. ERP implementation rule

Until entity/API mapping is directly verified:

1. ERP may use the canonical data model as DESIGN.
2. RO App may be treated as operational source only for confirmed entities/contracts.
3. No production WRITE is enabled.
4. No stock, product, customer, order, price or financial mutation is performed.
5. No endpoint is created from naming convention alone.
6. Schema mapping must include source field, target field, cardinality, identifier mapping, nullability, update semantics and evidence reference.

## 6. Next READ_ONLY mapping pass

Priority order:

1. Orders — response schema and line/customer/payment references.
2. People — customer identity fields and stable identifier semantics.
3. Products — authoritative current collection contract.
4. Services — authoritative current collection contract.
5. Warehouse/stock — authoritative current contract and movement semantics.
6. Prices/costing — verify whether RO App exposes source data or ERP remains owner.
7. Repairs/production/procurement — determine whether these are RO App domains or ERP-owned domains.

## 7. Production gate

This document is evidence mapping only. It authorizes no write operation. Production WRITE remains `0` until backup/restore, reconciliation, dry-run, idempotency, rollback and post-write verification gates are independently evidenced.
