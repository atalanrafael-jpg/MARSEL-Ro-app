# MARSEL ROAPP — ERP DATA DICTIONARY V1

Дата контрольной точки: 2026-09-06
Статус: DESIGN / READ_ONLY / WRITE=0

## Назначение

Канонический словарь ERP-сущностей для MARSEL ROAPP. Документ фиксирует минимальную модель данных и не утверждает, что все поля уже существуют в RO App.

## Правила

- `marsel_id` — канонический ID MARSEL там, где он определён.
- Внешние IDs никогда не заменяют canonical ID.
- `source_system` и `source_record_id` обязательны для интеграционных представлений.
- Ссылки между сущностями должны быть разрешимыми; orphan-связи являются data-quality error.
- Поля, не подтверждённые live API, имеют статус `PROPOSED`.

## 1. Master Data

| Entity | Ключевые поля | Связи | Статус |
|---|---|---|---|
| Product | marsel_id, sku, name, category_id, lifecycle, status | materials, stones, assets, prices | CANONICAL DESIGN |
| Category | category_id, parent_id, name, normalized_key, status | products | DESIGN |
| Material | material_id, type, name, unit, supplier_ref, price_basis | products, BOM, stock | DESIGN |
| Metal | metal_id, alloy, fineness, unit, price_basis | material, BOM, costing | DESIGN |
| Stone | stone_id, type, variety, cut, size, weight, quality | product, BOM, costing | DESIGN |
| Customer | customer_id, name/contact references, status | orders, repairs, CRM | DESIGN |
| Supplier | supplier_id, name, status, contacts | procurement, receipts, AP | DESIGN |
| Employee | employee_id, name, role, status | production, repair, warehouse | DESIGN |
| Warehouse | warehouse_id, code, type, status | stock movements, reservations | DESIGN; live contract NOT VERIFIED |
| Asset | asset_id, owner_type, owner_id, type, checksum, version | product/document | DESIGN |

## 2. Commercial / Operations

| Entity | Ключевые поля | Связи | Статус |
|---|---|---|---|
| SalesOrder | order_id, external_id, customer_id, status, totals, timestamps | customer, lines, payment | RO App evidence exists for orders; current schema mapping pending |
| SalesOrderLine | line_id, order_id, product_id, qty, price | order, product | MAPPING REQUIRED |
| PurchaseOrder | po_id, supplier_id, status, totals | supplier, lines, receipt | PROPOSED |
| PurchaseOrderLine | line_id, po_id, material_id, qty, price | PO, material | PROPOSED |
| StockMovement | movement_id, warehouse_id, item_id, qty, direction, reason, timestamp | product/material, warehouse | PROPOSED; live contract required |
| Reservation | reservation_id, item_id, warehouse_id, qty, order_ref | order, stock | PROPOSED |
| BOM | bom_id, product_id, version, status | BOM lines, production | PROPOSED |
| BOMLine | bom_line_id, bom_id, material_id/product_id, qty, loss_factor | BOM, material | PROPOSED |
| ProductionOrder | production_id, product_id, bom_id, status, responsible_employee_id | BOM, materials, stock, QC | PROPOSED |
| RepairOrder | repair_id, customer_id, received_item, diagnosis, status, price | customer, materials, labor, documents | DESIGN |
| RepairOperation | operation_id, repair_id, operation_type, employee_id, duration, cost | repair, employee | DESIGN |

## 3. Costing / Finance

| Entity | Ключевые поля | Связи | Статус |
|---|---|---|---|
| CostVersion | cost_version_id, product_id, version, effective_at, method | components, product | DESIGN |
| CostComponent | component_id, cost_version_id, type, source_ref, quantity, unit_cost, amount | material/labor/overhead | DESIGN |
| Price | price_id, product_id, price_type, amount, currency, effective_at | product | DESIGN |
| Payment | payment_id, order_id, method, amount, currency, status, timestamp | order, customer | PROPOSED; live methods not verified |
| FinancialEntry | entry_id, source_type, source_id, account, debit, credit, currency, timestamp | order/payment/procurement | PROPOSED |
| SupplierPayable | payable_id, supplier_id, source_document, amount, status | supplier, PO/receipt | PROPOSED |
| CustomerReceivable | receivable_id, customer_id, source_document, amount, status | customer, order | PROPOSED |

## 4. Costing rules

Product cost must be componentized. Minimum components:

1. metal: quantity/weight × approved price basis × fineness/purity factor;
2. stones: stone reference + quantity/weight/quality + acquisition price/source;
3. labor: approved operation/time/rate basis;
4. overhead: explicitly defined allocation basis;
5. losses/waste: separately traceable;
6. calculation version and source evidence.

A final cost value without component provenance is insufficient for production costing.

## 5. Integration envelope

Every synchronized record should expose, where applicable:

- `source_system`
- `source_record_id`
- `marsel_id`
- `external_id`
- `mapping_version`
- `source_updated_at`
- `last_synced_at`
- `sync_status`
- `checksum` or deterministic fingerprint when applicable

## 6. Evidence status

`CONFIRMED` = directly verified current evidence.
`HISTORICAL` = evidence from a prior run; not current proof.
`PROPOSED` = architecture only.
`MAPPING REQUIRED` = entity exists conceptually but live API mapping is incomplete.
`NOT VERIFIED` = required live contract/evidence is missing.

## 7. Safety

This dictionary authorizes no production mutation. Before implementation: authoritative API documentation → live READ_ONLY contract → mapping → reconciliation → dry-run → idempotency → rollback evidence → safety gate.
