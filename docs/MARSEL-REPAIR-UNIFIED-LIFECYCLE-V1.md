# MARSEL — Unified Repair Lifecycle V1

Status: DESIGN / NOT LIVE IN RO APP

## Scope
Unified operational control for jewelry, watch and eyewear repairs while preserving type-specific fields.

## 1. Identity chain
`customer_id → repair_order_id → item_id → diagnosis_id → operation_id → material_consumption_id → asset_id → document_id`

Every child record must point to the correct parent. No orphan production records.

## 2. Intake
Required before work starts:
- customer identity;
- item type and description;
- visible condition and existing damage;
- completeness/accessories;
- intake date/time;
- receiving employee;
- intake photos where required;
- customer acceptance of recorded condition.

## 3. Diagnosis
Record:
- complaint;
- observed defects;
- diagnosis;
- recommended repair;
- estimated work;
- estimated materials/parts;
- preliminary price;
- technician/diagnostician.

## 4. Approval gate
Additional work must not silently increase the price.

Lifecycle includes `awaiting_customer_approval` whenever diagnosis reveals additional work or cost.

## 5. Work execution
Each operation records:
- operation ID;
- responsible employee;
- start/end timestamps;
- consumed materials/parts;
- quantity and unit;
- cost basis;
- notes;
- related photos/documents where required.

## 6. Cost structure
Keep separate:
- estimated price;
- final customer price;
- material/part cost;
- labor/operation cost;
- other approved cost components;
- margin.

Do not overwrite component provenance with a single total.

## 7. Quality control
`in_repair → quality_check → ready`

Quality check must be a distinct step. Failed QC returns the order to an explicit rework state.

## 8. Delivery
Before delivery:
- final condition recorded;
- final price recorded;
- all consumed parts reconciled;
- required attachments present;
- customer acceptance/delivery evidence recorded;
- responsible delivery employee recorded.

## 9. Warranty / repeat visit
A repeat repair can reference the original repair order. Store warranty eligibility, warranty period, reason for repeat visit and whether work is covered.

## 10. Inventory
Parts/material consumption must support:
`stock → reservation/consumption → repair order → reconciliation`.

Unused issued parts must support return/correction where the live system permits it.

## 11. Type-specific modules
### Jewelry
Metal, fineness, stones, weight, setting, polishing, soldering, resizing and other jewelry-specific attributes.

### Watches
Brand/model/reference, serial where applicable, condition, parts, movement/service operations and applicable tests.

### Eyewear
Brand/model, frame material/color, lens type, frame/temple/hinge/nose-pad/lens defects, adjustment and replacement operations.

## 12. Evidence policy
Assets should distinguish at minimum:
- intake photo;
- defect photo;
- work-in-progress photo;
- final photo;
- customer document;
- repair document.

Assets must use canonical parent IDs and, where supported, checksum/version metadata.

## 13. Analytics
The model must support reporting by repair type, technician, operation, materials/parts, revenue, cost, margin, turnaround time, overdue orders, repeat/warranty repairs and rework.

## 14. Safety
This specification authorizes no live Ro App write. Before implementation: verify live schema/API, backup/restore, field support, status mapping and dry-run. Proposed lifecycle values must not be assumed to exist in Ro App.
