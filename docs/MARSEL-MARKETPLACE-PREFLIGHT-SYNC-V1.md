# MARSEL — Marketplace Preflight + Stock/Order Sync V1

Status: DESIGN / READ-ONLY UNTIL LIVE API VERIFICATION

## 1. Objective
Provide a controlled layer between the MARSEL Master Catalog and external marketplaces. No marketplace becomes the canonical source of product identity, price or inventory.

## 2. Mandatory API verification gate
Before any production synchronization, verify against the actual Ro App API:
- authentication and permission scope;
- company/branch identity;
- product/catalog endpoints;
- inventory/stock endpoints;
- warehouse/location endpoints;
- order endpoints;
- order-line identifiers;
- customer references where exposed;
- pagination;
- rate limits;
- error/status semantics;
- idempotency or a safe equivalent;
- update/write semantics;
- timestamps and incremental-change support;
- backup/export capability.

Unknown endpoint names, fields or enum values must never be guessed.

## 3. Preflight checks
A product may be published only when all required checks pass:
- canonical `master_product_id` exists;
- SKU is present and normalized;
- category/group mapping is valid;
- required product attributes are complete;
- price is valid;
- inventory source is known;
- available quantity is reconciled;
- required photos exist;
- 3D exists when required by the selected experience;
- required documents exist;
- marketplace-specific fields pass validation;
- no duplicate external listing is detected;
- product is not blocked, archived or otherwise ineligible.

Preflight returns `PASS`, `BLOCKED` or `REVIEW` with machine-readable reason codes.

## 4. Stock synchronization model
Canonical flow:
`Ro App verified stock → MARSEL normalized availability → channel-specific quantity → marketplace`

For each stock update record:
- master product ID;
- SKU;
- warehouse/location;
- source quantity;
- reserved quantity when supported;
- available quantity;
- channel quantity;
- synchronization timestamp;
- source version/timestamp when supported;
- result/error.

Never overwrite stock from a stale marketplace response.

## 5. Unique-item protection
For unique jewelry, watches or other one-off inventory, the synchronization layer must prevent concurrent sales across channels. Reservation must precede final sale where the channel/API supports it. If reservation is not supported, the integration must use a documented consistency strategy and flag conflicts instead of pretending inventory is exact.

## 6. Order synchronization
Canonical flow:
`Marketplace order → external order ID → idempotency check → master product resolution → stock validation → MARSEL order/import layer → reconciliation`

Each imported order must preserve:
- marketplace/channel;
- external order ID;
- external line ID;
- master product ID/SKU;
- quantity;
- price and currency;
- order status;
- timestamps;
- delivery/fulfilment references where available;
- raw-source reference or audit reference where permitted.

The same external order/line must not create duplicate internal sales.

## 7. Returns/cancellations
Cancellation and return events must reference the original external order and product. Returned stock must not automatically become available until the configured inspection/state rule is satisfied.

## 8. Conflict handling
A conflict must become an explicit exception, not an automatic destructive overwrite.

Examples:
- stock mismatch;
- unknown SKU;
- duplicate external listing;
- stale update;
- order for unavailable unique item;
- price mismatch;
- unsupported status;
- API permission failure.

## 9. Retry/idempotency
Transient failures may retry with bounded backoff. Every write-capable operation must have an idempotency strategy before production activation. Repeated execution must not create duplicate products, orders, reservations or stock movements.

## 10. Audit log
Store, where supported:
- operation ID;
- channel;
- entity ID;
- request class;
- result;
- timestamp;
- retry count;
- error code;
- reconciliation result.

Do not store secrets or unnecessary personal data in logs.

## 11. Reconciliation jobs
Scheduled reconciliation should compare:
- product/listing mappings;
- stock quantities;
- reservations;
- imported orders;
- cancellations;
- returns;
- synchronization timestamps.

Results: `MATCH`, `MISMATCH`, `UNKNOWN`, `BLOCKED`.

## 12. Rollout sequence
1. Read-only API inventory.
2. Schema verification.
3. Master Catalog mapping.
4. Marketplace mapping validation.
5. Preflight dry-run.
6. Stock read-only comparison.
7. Order read-only comparison.
8. Controlled write pilot on approved test scope.
9. Reconciliation.
10. Gradual production expansion.

## 13. Hard safety rules
- No guessed Ro App endpoints or fields.
- No live write before authentication/permissions and schema are verified.
- No bulk import without backup/export verification.
- No destructive overwrite on conflicts.
- No marketplace becomes source of truth for canonical product identity.
- No production activation while critical reconciliation checks fail.

## 14. Current state
This document defines the implementation contract. It does not claim that the listed Ro App API capabilities exist. The previously referenced Ro App documentation URL could not be independently retrieved by the current web check, so the actual endpoint/field mapping remains **UNVERIFIED** until the live API documentation or authenticated schema is available.
