# RO App Warehouse Contract Registry

**Status:** REVIEW_REQUIRED
**Mode:** READ-ONLY
**Last verified:** 2026-08-21

## Canonical contract status

| Contract | Status | Evidence / rule |
|---|---|---|
| Warehouse list | `UNVERIFIED` | No confirmed official list endpoint in the current checked RO App documentation; current `/v2/warehouse/` probe returns HTTP 404. |
| Warehouse by ID / goods | `LIVE_VERIFIED` | CI has confirmed 11 live GET responses for warehouse goods. |
| Undocumented compatibility endpoints | `DIAGNOSTIC_ONLY` | May be probed for investigation but can never produce `PASS`. |
| Warehouse WRITE | `DISABLED` | No write requests are permitted by the audit gate. |

## Gate rule

`PASS` requires a documented, currently verified warehouse-list contract plus successful documented warehouse GET verification. A guessed or undocumented endpoint must never be promoted to the canonical contract.

## Current blocker

The project has 11 live-confirmed warehouse GET results, but the documented warehouse-list contract is not currently verified. Therefore the warehouse gate remains `REVIEW_REQUIRED` / `NOT_VERIFIED` until the official RO App contract is confirmed.

## Required evidence to close the blocker

1. Official RO App documentation or API schema identifying the warehouse-list operation.
2. Successful read-only request against that documented operation.
3. Response schema containing warehouse identifiers.
4. Repeatable CI verification using the documented operation.

Until all four conditions are satisfied, do not change the gate to `PASS` and do not enable production WRITE.
