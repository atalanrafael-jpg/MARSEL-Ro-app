# MARSEL ROAPP — ERP STOCK / MATERIALS EVIDENCE GATE

Date: 2026-09-06
Status: READ-ONLY / EVIDENCE GATE
Production WRITE: 0

## Purpose

Close the next ERP control pass without inventing RO App endpoints or promoting repository-only paths to live API contracts.

## Verified repository surface

The repository contains a READ-ONLY inventory implementation that targets:

- `/orders`
- `/catalog/services`
- `/catalog/products`
- `/catalog/bundles`
- `/inquiries`
- `/bookings`
- `/estimates`
- `/invoices`

The implementation explicitly permits GET only and forbids POST/PUT/PATCH/DELETE. Its output is an audit artifact and is not committed as production data.

## Stock / StockMovement

Status: NOT VERIFIED.

No independently verified RO App production collection contract for stock balances or stock movements was found in the repository evidence inspected during this pass.

Warehouse-list contract remains separately promoted only to LIVE-READ-VERIFIED for the recorded audit run. That evidence does not prove stock balances, movements, or the complete warehouse schema.

## Materials / Metals / Stones

Status: NOT VERIFIED.

ERP data-model definitions exist for material, metal and stone costing, but repository model/spec presence is not evidence of a corresponding RO App production endpoint or live schema.

No new connector or endpoint implementation is introduced by this gate.

## Required next evidence

1. Official RO App documentation for stock and stock-movement collections.
2. Authorized GET smoke test for each documented collection.
3. Capture exact response schema, IDs, pagination and timestamps.
4. Reconcile warehouse → stock → movement references.
5. Identify material/metal/stone entities and their authoritative source.
6. Perform READ-ONLY duplicate, missing-ID and reference-integrity checks.
7. Update ERP entity/API mapping only from captured evidence.

## Safety gate

No POST, PUT, PATCH or DELETE operation is allowed.

No stock, material, metal or stone record is created, changed, merged or deleted.

No cost or financial value is invented.

## Result

`STOCK = NOT VERIFIED`
`STOCK_MOVEMENT = NOT VERIFIED`
`MATERIALS = NOT VERIFIED`
`METALS = NOT VERIFIED`
`STONES = NOT VERIFIED`
`ERP_READINESS = BLOCKED`
`PRODUCTION_WRITE = 0`
