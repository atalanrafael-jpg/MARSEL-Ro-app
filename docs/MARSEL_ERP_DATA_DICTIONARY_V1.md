# MARSEL ROAPP — ERP DATA DICTIONARY V1

Дата: 2026-09-06
Статус: PROPOSED / DESIGN / READ_ONLY

## 1. Назначение

Этот документ определяет канонический словарь данных ERP-контура MARSEL ROAPP. Он является проектной спецификацией, а не доказательством того, что соответствующие поля или сущности уже существуют в RO App.

Правило: `VERIFIED` допускается только после прямой проверки текущего RO App API/данных. До этого состояние — `PROPOSED` или `NOT VERIFIED`.

## 2. Статусы доказательности

| Статус | Значение |
|---|---|
| VERIFIED | подтверждено текущими данными/официальным контрактом |
| DOCUMENTED | есть документированное описание, но live-проверка не выполнена |
| PROPOSED | проектная модель ERP |
| NOT VERIFIED | требуется проверка |
| BLOCKED | проверка невозможна из-за внешнего блокера |

## 3. MDM — мастер-данные

| Entity | Canonical key | Основные атрибуты | Authoritative source | RO App mapping |
|---|---|---|---|---|
| Product | master_product_id | sku, name, category, metal, fineness, weight, stones, price, status | MARSEL Master Catalog | NOT VERIFIED |
| Service | service_id | name, category, duration, price, status | MARSEL ERP | NOT VERIFIED |
| Material | material_id | code, name, type, unit, supplier, purchase_cost | MARSEL ERP | NOT VERIFIED |
| Metal | metal_id | name, fineness, unit, price_basis | MARSEL ERP | NOT VERIFIED |
| Stone | stone_id | type, grade, size, weight, quantity, cost | MARSEL ERP | NOT VERIFIED |
| Customer | customer_id | name, phone, email, consent/status | authoritative CRM source TBD | NOT VERIFIED |
| Supplier | supplier_id | name, contacts, terms, status | ERP procurement | NOT VERIFIED |
| Employee | employee_id | name, role, status | ERP/HR | NOT VERIFIED |
| Warehouse | warehouse_id | name, location, status | RO App only if contract verified | NOT VERIFIED |

## 4. Sales & Orders

| Entity | Canonical key | Основные атрибуты | Status |
|---|---|---|---|
| Sales Order | sales_order_id | customer_id, lines, price, status, dates, channel | PROPOSED |
| Sales Order Line | sales_order_line_id | product/service, quantity, unit_price, discount, tax context | PROPOSED |
| Quote | quote_id | customer, lines, validity, approval status | PROPOSED |
| Return | return_id | order_id, lines, reason, amount, status | PROPOSED |
| External Order | external_order_id | channel, external status, source reference | PROPOSED |

## 5. Inventory & Warehouse

| Entity | Canonical key | Основные атрибуты | Status |
|---|---|---|---|
| Stock Balance | stock_balance_id | warehouse_id, item_id, quantity, unit | PROPOSED |
| Stock Movement | stock_movement_id | item, warehouse, quantity, direction, reason, source document | PROPOSED |
| Reservation | reservation_id | order/work_order, item, quantity, status | PROPOSED |
| Inventory Count | inventory_count_id | warehouse, date, lines, variance, approval | PROPOSED |
| Batch/Serial | lot_serial_id | item, batch/serial, quantity, provenance | PROPOSED |

Warehouse fields/endpoints must not be mapped to RO App until the live contract is authoritative and verified.

## 6. Procurement

| Entity | Canonical key | Основные атрибуты | Status |
|---|---|---|---|
| Purchase Request | purchase_request_id | requester, items, quantities, approval | PROPOSED |
| Purchase Order | purchase_order_id | supplier, lines, prices, dates, status | PROPOSED |
| Receipt | receipt_id | purchase_order_id, received lines, quantities, verification | PROPOSED |
| Supplier Return | supplier_return_id | receipt/order, lines, reason, status | PROPOSED |

## 7. Production

| Entity | Canonical key | Основные атрибуты | Status |
|---|---|---|---|
| BOM | bom_id | product, components, quantities, version | PROPOSED |
| Work Order | work_order_id | product, quantity, operations, assignee, status | PROPOSED |
| Material Consumption | consumption_id | work_order_id, material, quantity, cost | PROPOSED |
| WIP | wip_id | work_order_id, operation, status, accumulated cost | PROPOSED |
| Finished Good | finished_good_id | work_order_id, product, quantity, QC, cost | PROPOSED |
| Scrap | scrap_id | work_order_id, material, quantity, reason, cost | PROPOSED |

## 8. Repair / Service

| Entity | Canonical key | Основные атрибуты | Status |
|---|---|---|---|
| Repair Intake | repair_id | customer, item description, condition, received_at | PROPOSED |
| Diagnosis | diagnosis_id | repair_id, findings, estimate, risks | PROPOSED |
| Repair Work Order | repair_work_order_id | repair_id, technician, operations, status | PROPOSED |
| Repair Material Usage | repair_material_usage_id | repair_work_order_id, material, quantity, cost | PROPOSED |
| Repair QC | repair_qc_id | repair_work_order_id, checks, result | PROPOSED |
| Delivery | delivery_id | repair/order, recipient, date, status | PROPOSED |
| Warranty Case | warranty_case_id | source order/repair, issue, decision, status | PROPOSED |

## 9. Costing

Фактическая себестоимость не рассчитывается без подтверждённых исходных данных.

| Cost component | Key | Source data | Status |
|---|---|---|---|
| Metal cost | metal_cost_id | metal quantity × verified cost basis | PROPOSED |
| Stone cost | stone_cost_id | stone quantity/weight × verified cost | PROPOSED |
| Labor cost | labor_cost_id | verified labor rate × actual/approved labor | PROPOSED |
| Components cost | component_cost_id | verified purchase cost | PROPOSED |
| Other direct cost | direct_cost_id | verified direct expense | PROPOSED |
| Total cost | cost_record_id | sum of verified components | PROPOSED |

Costing must preserve planned vs actual values and the source/evidence for each component.

## 10. Finance

| Entity | Canonical key | Основные атрибуты | Status |
|---|---|---|---|
| Payment | payment_id | document, amount, method, date, status | PROPOSED |
| Revenue Record | revenue_id | source order, amount, date, channel | PROPOSED |
| Expense Record | expense_id | category, amount, date, source | PROPOSED |
| AR | ar_id | customer, source document, balance, status | PROPOSED |
| AP | ap_id | supplier, source document, balance, status | PROPOSED |
| Financial Entry | financial_entry_id | debit/credit model, amount, source, timestamp | PROPOSED |

Tax/accounting implementation requires separate legal and accounting validation; this dictionary does not itself establish tax treatment.

## 11. CRM / Analytics / Control

| Entity | Canonical key | Purpose | Status |
|---|---|---|---|
| Customer Interaction | interaction_id | contact history and channel | PROPOSED |
| Lead | lead_id | source, stage, owner, conversion | PROPOSED |
| KPI Snapshot | kpi_snapshot_id | factual KPI values and period | PROPOSED |
| Audit Event | audit_event_id | actor, action, object, timestamp, result | PROPOSED |
| Evidence Record | evidence_id | source, hash/reference, status, timestamp | PROPOSED |
| Approval | approval_id | request, actor, decision, timestamp | PROPOSED |

## 12. Ownership rules

1. Every master entity has one authoritative source.
2. External IDs are stored as references, not replacements for the MARSEL canonical ID.
3. Cross-system mappings must be explicit and versioned.
4. No automatic merge/delete is permitted from collision findings.
5. No field is considered mapped to RO App without current contract/live evidence.
6. Historical project documents do not override current live evidence.

## 13. Required next verification

1. Read current RO App API inventory and entity audit.
2. Build `ERP entity → RO App entity → endpoint → method → field` mapping only from verified evidence.
3. Mark unavailable fields explicitly as `NOT VERIFIED`.
4. Validate costing against existing implementation before creating any parallel calculation.
5. Add the resulting mapping to the production evidence gate.

## 14. Safety

This document does not authorize production WRITE, synchronization, deletion, merge, or migration. Any future mutation requires the project safety sequence:

`READ → ANALYZE → BACKUP → RESTORE CHECK → DRY-RUN → WRITE → VERIFY`
