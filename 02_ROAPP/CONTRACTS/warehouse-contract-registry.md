# RO App Warehouse Contract Registry

**Status:** REVIEW_REQUIRED
**Mode:** READ-ONLY
**Last verified:** 2026-08-21

## Canonical contract status

| Contract | Status | Evidence / rule |
|---|---|---|
| Warehouse list | `DOCUMENTED_LIVE_UNVERIFIED` | Official RO App v2.0.1 documentation explicitly defines `GET https://api.roapp.io/v2/warehouse/`, with optional `branch_id` and `type` (`product` default, `asset`). The current MARSEL live audit received HTTP 404, so the documented contract is not yet live-verified. |
| Warehouse stock | `DOCUMENTED_LIVE_UNVERIFIED` | Official documentation defines `GET https://api.roapp.io/warehouse/goods/{warehouse_id}`. Live verification must succeed for the confirmed warehouse IDs. |
| Warehouse by ID / goods | `LIVE_VERIFIED` | CI has previously confirmed live GET responses for 11 warehouse IDs; the evidence must be regenerated against the currently documented contract. |
| Undocumented compatibility endpoints | `DIAGNOSTIC_ONLY` | May be probed for investigation but can never produce `PASS` or replace the documented contract. |
| Warehouse WRITE | `DISABLED` | No write requests are permitted by the audit gate. |

## Official documentation

- Warehouse list: https://roappua.readme.io/reference/get-warehouses
- Warehouse stock: https://roappua.readme.io/reference/get-stock

The official v2.0.1 warehouse-list page identifies `GET https://api.roapp.io/v2/warehouse/` as the operation for retrieving the company's warehouse list and documents `branch_id` plus `type` (`product` / `asset`).

## Gate rule

`PASS` requires:

1. the documented warehouse-list operation to return HTTP 200 with valid JSON containing warehouse identifiers;
2. the documented warehouse-stock operation to return successful READ-ONLY responses for the discovered warehouse IDs;
3. repeatable CI evidence for both operations; and
4. `write_requests_made=0` and `ro_app_data_mutated=false`.

A guessed or undocumented endpoint must never be promoted to the canonical contract.

## Current blocker

The warehouse-list contract is **documented**, but it is **not currently live-verified** for MARSEL because the audit received HTTP 404 from the documented endpoint. Therefore the warehouse gate remains `REVIEW_REQUIRED` / `NOT_VERIFIED`.

This is materially different from saying that the endpoint is undocumented: the endpoint is documented by RO App, but the current live result does not match the documented contract.

## Required evidence to close the blocker

1. Successful read-only request to the documented warehouse-list operation.
2. Valid response containing warehouse identifiers.
3. Successful read-only stock requests using the documented stock operation.
4. Repeatable CI verification with the evidence artifacts.

Until all conditions are satisfied, do not change the gate to `PASS` and do not enable production WRITE.
