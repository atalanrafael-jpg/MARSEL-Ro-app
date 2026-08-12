# MARSEL — Repair Data Contract V1

Status: DESIGN / NOT LIVE IN RO APP

## Purpose
Define a single auditable data contract for jewelry, watch and eyewear repair without losing type-specific information.

## Core entities
- `customer`
- `repair_order`
- `item`
- `diagnosis`
- `operation`
- `material_consumption`
- `asset`
- `document`
- `approval`
- `quality_check`
- `delivery`
- `warranty_case`

## Required relationships
`customer 1:N repair_order`
`repair_order 1:1 item` (or an explicit multi-item model if live system requires it)
`repair_order 1:N diagnosis`
`repair_order 1:N operation`
`operation 1:N material_consumption`
`repair_order 1:N asset`
`repair_order 1:N document`
`repair_order 1:N approval`
`repair_order 1:N quality_check`
`repair_order 0:1 delivery`
`repair_order 0:N warranty_case`

## Immutable evidence
The following must not be silently overwritten after acceptance: intake condition, intake photos, customer approvals, material consumption records, final price after delivery and delivery evidence. Corrections require an auditable correction event where supported.

## Financial fields
Keep separate values for estimate, approved price, final price, material cost, labor/operation cost, other approved costs and calculated margin. Currency and tax treatment must come from verified MARSEL/Ro App configuration.

## Inventory fields
Each consumption record should contain material/part ID, quantity, unit, source warehouse, cost basis, operation link, repair order link and timestamp where supported.

## Status controls
Recommended states:
`received`, `diagnostics`, `awaiting_customer_approval`, `approved`, `in_repair`, `quality_check`, `rework`, `ready`, `delivered`, `cancelled`.

A status transition must be explicit and auditable. No direct `received → delivered` transition should be permitted in the application workflow without a documented exception path.

## Approval controls
If an operation changes scope or increases the agreed price, the order must enter `awaiting_customer_approval`. The approval record should capture proposed change, price delta, timestamp, approver/customer reference and approval evidence where supported.

## Quality controls
Quality check records result, checker, timestamp, findings and rework requirement. Failed QC creates `rework`; it must not silently mark the order ready.

## Type-specific fields
### Jewelry
Metal/alloy/fineness, weight, stones, setting, dimensions/size, existing damage.

### Watches
Brand, model/reference, serial where applicable, condition, parts, movement/service operations and applicable test results.

### Eyewear
Brand, model/reference, frame material/color, lens type, defects, frame/temple/hinge/nose-pad/lens operations and adjustment result.

## Asset rules
Assets must carry a canonical parent ID, asset type (`photo`, `model`, `document` where applicable), filename/reference, version and checksum when supported. Intake and final evidence must remain distinguishable.

## Reconciliation rules
A repair order cannot be considered complete if any of the following remain unresolved:
- missing required customer/item identity;
- unapproved price change;
- unresolved material consumption;
- failed quality check;
- missing required delivery evidence;
- orphaned assets/documents.

## API safety
This contract does not authorize live writes. Before mapping to Ro App: verify live endpoints, supported fields/statuses, backup/restore, authentication/subscription state, then run read-only schema discovery and dry-run validation.
