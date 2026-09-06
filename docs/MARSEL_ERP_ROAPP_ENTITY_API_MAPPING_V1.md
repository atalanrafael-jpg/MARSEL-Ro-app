# MARSEL ROAPP — ERP ↔ RO APP ENTITY/API MAPPING V1

Дата контрольной точки: 2026-09-06
Статус: READ_ONLY / WRITE=0

## 1. Правило доказательности

Mapping разделяет архитектурное соответствие и фактически подтверждённый API.

`DOCUMENTED` означает, что факт зафиксирован в проектной документации.
`LIVE-READ-VERIFIED` требует свежего авторизованного GET evidence.
`NOT VERIFIED` означает, что endpoint/schema нельзя честно утверждать.

Нельзя повышать статус на основании guessed endpoint, historical screenshot или synthetic response.

## 2. Подтверждённый API-контур

| Поле | Значение | Статус |
|---|---|---|
| Base URL | `https://api.roapp.io/v2` | VERIFIED |
| Auth | Bearer token / `ROAPP_API_KEY` | VERIFIED |
| Verified read endpoint | `GET /orders` | VERIFIED |
| Page size | up to 50 | VERIFIED |
| Pagination | `page` | VERIFIED |
| Rate limit | 3 req/s | VERIFIED |
| Write methods | POST/PUT/PATCH/DELETE blocked | VERIFIED / policy |

Источник этих contract facts: `docs/MARSEL-ROAPP-API-VERIFICATION-LEDGER-V23.md` и `app/roapp_contract.py`.

## 3. Entity mapping

| ERP entity | RO App mapping | Method | Schema | Status | Safe next action |
|---|---|---|---|---|---|
| Customer | related order client data | GET via `/orders` response | nested client object observed in project audit; exact canonical schema not independently promoted | NOT VERIFIED as standalone entity | fresh GET + schema capture |
| Product | order line/product reference | GET via `/orders` if present | exact fields not promoted | NOT VERIFIED | fresh GET + field mapping |
| Order | `/orders` | GET | endpoint verified; complete response schema not promoted here | LIVE-READ-VERIFIED endpoint / schema partial | capture current schema |
| OrderLine | nested order data | GET via `/orders` | exact schema not promoted | NOT VERIFIED | fresh GET |
| Payment | no verified mapping | — | — | NOT VERIFIED | identify official endpoint from docs, then GET probe |
| Warehouse | `/warehouse/` | GET | warehouse-list contract verified by repository evidence; response schema not independently promoted | LIVE-READ-VERIFIED contract / schema partial | capture current response schema when authorized GET access is available |
| Stock | no verified mapping | — | — | NOT VERIFIED | official docs + GET |
| StockMovement | no verified mapping | — | — | NOT VERIFIED | official docs + GET |
| Reservation | no verified mapping | — | — | NOT VERIFIED | official docs + GET |
| Material | no verified mapping | — | — | NOT VERIFIED | official docs + GET |
| Metal | no verified mapping | — | — | NOT VERIFIED | official docs + GET |
| Stone | no verified mapping | — | — | NOT VERIFIED | official docs + GET |
| Supplier | no verified mapping | — | — | NOT VERIFIED | official docs + GET |
| Procurement documents | no verified mapping | — | — | NOT VERIFIED | official docs + GET |
| BOM | no verified mapping | — | — | NOT VERIFIED | ERP-side design; RO App mapping unknown |
| ProductionJob | no verified mapping | — | — | NOT VERIFIED | ERP-side design; RO App mapping unknown |
| Repair | no verified mapping | — | — | NOT VERIFIED | ERP-side design; RO App mapping unknown |
| CostModel | no verified mapping | — | — | NOT VERIFIED | audit existing costing implementation first |
| ProductCost | no verified mapping | — | — | NOT VERIFIED | audit existing costing implementation first |
| FinancialEntry | no verified mapping | — | — | NOT VERIFIED | define finance authoritative source |

## 4. Evidence update — warehouse

Repository evidence `evidence/marsel-unified-warehouse-contract.json` records a successful warehouse contract audit at `2026-09-05T08:41:00Z` in `READ_ONLY` mode, with `write_requests_made: 0`, `ro_app_data_mutated: false`, and `warehouse_list_contract_verified: true`.

This is sufficient to promote the **warehouse-list contract** to `LIVE-READ-VERIFIED` for the recorded audit run. It is **not** sufficient to promote the full warehouse response schema, stock balances, stock movements, or other inventory entities.

Evidence source: `evidence/marsel-unified-warehouse-contract.json`.

## 5. Authoritative-source decision

| Domain | Current controlled decision |
|---|---|
| Product/catalog publication | MARSEL Master Catalog / configured catalog source; marketplace is not a second master |
| Operational orders | RO App is the operational source only within verified contracts |
| Customer master | ERP MDM target; RO App representation must be mapped before sync |
| Inventory | ERP Inventory target; RO App can be operational source only after warehouse/stock contracts are verified |
| Costing | ERP Costing target; reuse existing implementation if one is already authoritative; do not create parallel logic |
| Finance | separate authoritative source must be selected and validated |
| Audit/evidence | MARSEL control plane / GitHub |

## 6. `/orders` promotion record

The repository explicitly identifies `GET /orders` as a verified read endpoint. Existing project records also describe a historical successful live test and a historical audit of 4,373 orders. Those historical counts are evidence of that run, not a current production count. Current production readiness still requires fresh evidence.

## 7. Required live mapping sequence

For each candidate entity:

1. confirm endpoint in official documentation;
2. perform authorized GET only;
3. capture HTTP status and response shape;
4. map source IDs to canonical ERP IDs;
5. record nullable/required fields;
6. record pagination and rate limits;
7. run duplicate/reference checks;
8. assign evidence timestamp/hash;
9. update this mapping only with verified facts.

## 8. Current gate

`ERP_DATA_DICTIONARY = DONE / DESIGN`
`ENTITY_API_MAPPING = PARTIAL / WAREHOUSE-CONTRACT-VERIFIED`
`WAREHOUSE = LIVE-READ-VERIFIED (contract only)`
`STOCK = NOT VERIFIED`
`COSTING = NOT VERIFIED`
`FINANCE = NOT VERIFIED`
`ERP_READINESS = BLOCKED`
`PRODUCTION_WRITE = 0`

No production synchronization or write operation is enabled by this document.
