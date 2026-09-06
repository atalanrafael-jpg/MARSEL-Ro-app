# MARSEL ROAPP — ERP DATA DICTIONARY V1

Дата контрольной точки: 2026-09-06
Статус: DESIGN / READ_ONLY / WRITE=0

## 1. Назначение

Этот документ фиксирует канонический словарь ERP-сущностей MARSEL ROAPP и границы их владения. Он не утверждает наличие сущности в production и не заменяет live evidence.

Правила:
- один canonical ID на мастер-сущность;
- один authoritative source;
- внешние ID хранятся как external references;
- отсутствие подтверждённого API означает `NOT VERIFIED`, а не `NOT EXISTS`;
- production WRITE остаётся запрещённым.

## 2. Статусы доказательности

| Статус | Значение |
|---|---|
| DESIGN | сущность/поле определены архитектурно, live existence не доказана |
| DOCUMENTED | подтверждено официальной документацией/репозиторием |
| LIVE-READ-VERIFIED | подтверждено свежим безопасным GET/read evidence |
| NOT VERIFIED | недостаточно текущего evidence |
| BLOCKED | проверка невозможна до закрытия P0 gate |

## 3. MDM

| Entity | Назначение | Canonical ID | Ключевые поля | Authoritative source | RO App mapping | Evidence |
|---|---|---|---|---|---|---|
| Customer | клиент | `customer_id` | name, contacts, consent/status | MARSEL ERP MDM | customer entity — проверить | NOT VERIFIED |
| Product | изделие/товар | `product_id` | SKU, category, metal, stone, weight, price, cost | MARSEL Master Catalog/MDM | product entity — проверить | NOT VERIFIED |
| Material | материал | `material_id` | type, unit, supplier, cost | ERP MDM | material entity — проверить | NOT VERIFIED |
| Metal | металл | `metal_id` | alloy, fineness, weight/unit cost | ERP MDM | проверить API entity | NOT VERIFIED |
| Stone | камень | `stone_id` | type, grade, dimensions, weight, cost | ERP MDM | проверить API entity | NOT VERIFIED |
| Watch | часы | `watch_id` | brand/model/reference/serial | ERP MDM | проверить API entity | NOT VERIFIED |
| Part | запчасть | `part_id` | SKU, type, cost | ERP MDM | проверить API entity | NOT VERIFIED |
| Service | услуга | `service_id` | type, price, duration | ERP MDM | проверить API entity | NOT VERIFIED |
| Employee | сотрудник | `employee_id` | role, status | ERP HR | проверить API entity | NOT VERIFIED |
| Supplier | поставщик | `supplier_id` | name, contacts, terms | ERP Procurement | проверить API entity | NOT VERIFIED |
| Warehouse | склад | `warehouse_id` | name, branch, status | RO App only after contract verification | warehouse endpoint — NOT VERIFIED | NOT VERIFIED |
| Channel | канал продаж | `channel_id` | type, external account | ERP Integrations | marketplace/e-commerce mapping — проверить | NOT VERIFIED |
| Document | документ | `document_id` | type, number, dates, references | ERP Control | проверить | NOT VERIFIED |

## 4. Sales & Orders

| Entity | Назначение | Canonical ID | Основные связи | Authoritative source | Evidence |
|---|---|---|---|---|---|
| Lead | потенциальный клиент | `lead_id` | customer/contact | ERP CRM | DESIGN |
| Quotation | предложение | `quotation_id` | customer, lines | ERP Sales | DESIGN |
| Order | заказ | `order_id` | customer, lines, channel, fulfillment | ERP Sales; external order IDs retained | RO App order mapping — проверить | NOT VERIFIED |
| OrderLine | строка заказа | `order_line_id` | order, product/service, qty, price | ERP Sales | проверить | NOT VERIFIED |
| Return | возврат | `return_id` | order, lines, reason | ERP Sales | проверить | NOT VERIFIED |
| Fulfillment | исполнение/выдача | `fulfillment_id` | order, warehouse | ERP Inventory/Sales | проверить | NOT VERIFIED |
| Payment | оплата | `payment_id` | order/customer, provider reference | ERP Finance | payment mapping — проверить | NOT VERIFIED |

## 5. Inventory & Warehouse

| Entity | Назначение | Canonical ID | Основные поля | Authoritative source | Evidence |
|---|---|---|---|---|---|
| Stock | текущий остаток | `stock_id` | item, warehouse, qty, reserved | RO App only for confirmed contract | NOT VERIFIED |
| StockMovement | движение | `stock_movement_id` | item, warehouse, qty, direction, timestamp, source document | RO App/ERP according to contract | NOT VERIFIED |
| Reservation | резерв | `reservation_id` | order, item, warehouse, qty, status | ERP Inventory | NOT VERIFIED |
| InventoryCount | инвентаризация | `inventory_count_id` | warehouse, lines, variance | ERP Inventory | NOT VERIFIED |
| LotSerial | партия/серия | `lot_serial_id` | item, lot/serial, qty | ERP Inventory | NOT VERIFIED |

**Warehouse gate:** официальный контракт `GET https://api.roapp.io/warehouse/` должен быть подтверждён свежим authorized READ_ONLY evidence. `/v2/warehouse/` не считать каноническим warehouse-list endpoint без доказательства.

## 6. Procurement

| Entity | Canonical ID | Основные связи | Evidence |
|---|---|---|---|
| PurchaseRequest | `purchase_request_id` | requester, supplier/material | DESIGN |
| PurchaseOrder | `purchase_order_id` | supplier, lines | DESIGN |
| PurchaseOrderLine | `purchase_order_line_id` | PO, material, qty, cost | DESIGN |
| Receipt | `receipt_id` | PO, warehouse, lines | DESIGN |
| SupplierReturn | `supplier_return_id` | receipt/PO, lines | DESIGN |

## 7. Production

| Entity | Canonical ID | Основные связи | Evidence |
|---|---|---|---|
| BOM | `bom_id` | product, materials, quantities | DESIGN |
| ProductionJob | `production_job_id` | order/product/BOM | DESIGN |
| WorkOrder | `work_order_id` | production job, operation, employee | DESIGN |
| MaterialConsumption | `material_consumption_id` | work order, material, qty | DESIGN |
| WIP | `wip_id` | production job, stage | DESIGN |
| QualityCheck | `quality_check_id` | production/repair, result | DESIGN |
| FinishedGood | `finished_good_id` | product, production job, stock | DESIGN |
| Scrap | `scrap_id` | production job, material, reason | DESIGN |

## 8. Repair / Service

| Entity | Canonical ID | Основные связи | Evidence |
|---|---|---|---|
| Repair | `repair_id` | customer, item/watch, intake | DESIGN |
| RepairDiagnosis | `repair_diagnosis_id` | repair, findings | DESIGN |
| RepairEstimate | `repair_estimate_id` | repair, services/materials | DESIGN |
| RepairApproval | `repair_approval_id` | repair, customer decision | DESIGN |
| RepairWorkOrder | `repair_work_order_id` | repair, employee, operations | DESIGN |
| RepairMaterial | `repair_material_id` | repair, material, qty, cost | DESIGN |
| RepairDelivery | `repair_delivery_id` | repair, customer, payment | DESIGN |
| WarrantyCase | `warranty_case_id` | repair/order, reason, resolution | DESIGN |

## 9. Costing

| Entity | Canonical ID | Назначение | Evidence |
|---|---|---|---|
| CostModel | `cost_model_id` | версия правил расчёта | DESIGN |
| MaterialCost | `material_cost_id` | стоимость металла/камней/материалов | DESIGN; existing implementation must be checked before creating another |
| LaborCost | `labor_cost_id` | трудозатраты | DESIGN |
| OverheadCost | `overhead_cost_id` | накладные расходы | DESIGN |
| ProductCost | `product_cost_id` | плановая/фактическая себестоимость изделия | DESIGN |
| CostAllocation | `cost_allocation_id` | распределение затрат | DESIGN |

**MARSEL requirement:** costing must separately support metal and stones, plus labor and overhead. No second parallel costing implementation is to be introduced until the repository and existing systems are audited.

## 10. Finance

| Entity | Canonical ID | Назначение | Evidence |
|---|---|---|---|
| Payment | `payment_id` | входящая/исходящая оплата | NOT VERIFIED |
| Expense | `expense_id` | расход | DESIGN |
| Revenue | `revenue_id` | выручка | DESIGN |
| AccountsReceivable | `ar_id` | дебиторка | DESIGN |
| AccountsPayable | `ap_id` | кредиторка | DESIGN |
| FinancialEntry | `financial_entry_id` | финансовая проводка | DESIGN |
| Reconciliation | `reconciliation_id` | сверка payment/order/finance | DESIGN |

Finance authoritative source is not assigned to RO App by default. It requires a separate validated integration and accounting/tax requirements review.

## 11. Entity ownership matrix

| Domain | Canonical owner | RO App role |
|---|---|---|
| Product catalog | MARSEL Master Catalog/MDM | operational data where contract verified |
| Customer | ERP MDM/CRM | operational representation where verified |
| Orders | ERP Sales | operational order subsystem where verified |
| Warehouse/stock | ERP Inventory with RO App operational source where contract verified | candidate source, currently NOT VERIFIED |
| Procurement | ERP Procurement | integration target |
| Production | ERP Production | integration target |
| Repair | ERP Repair | integration target |
| Costing | ERP Costing | validated reuse of existing model required |
| Finance | ERP Finance / selected accounting source | external integration candidate |
| Audit/evidence | MARSEL Control Plane | GitHub repository/evidence |

## 12. API mapping policy

For every mapping record:

`ERP entity → RO App endpoint → HTTP method → auth requirement → response schema → ID mapping → pagination → error model → live evidence → status`

Do not mark an endpoint `PASS` from a guessed path, historical screenshot, synthetic response, or stale run. Live READ evidence is required for production claims.

## 13. P0 verification queue

1. Warehouse contract and live GET.
2. Product/customer/order entity availability and schema.
3. Stock/stock movement availability and schema.
4. Existing costing implementation audit.
5. Payment/finance integration boundary.
6. Backup/restore and reconciliation evidence.
7. Credential remediation and authorization checks.

## 14. Gate

`DATA_DICTIONARY=DESIGN_COMPLETE`
`ENTITY_API_MAPPING=NOT_VERIFIED`
`ERP_READINESS=BLOCKED`
`PRODUCTION_WRITE=0`

This document is a design/control artifact, not proof of production ERP readiness.
