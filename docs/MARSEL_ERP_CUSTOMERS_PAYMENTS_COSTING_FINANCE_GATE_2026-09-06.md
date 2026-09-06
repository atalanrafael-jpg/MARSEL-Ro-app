# MARSEL ROAPP — ERP CUSTOMERS / PAYMENTS / COSTING / FINANCE GATE

Date: 2026-09-06
Mode: READ-ONLY repository audit
Production WRITE: 0

## 1. Customers

Status: NOT VERIFIED as a standalone RO App production API contract.

Repository evidence confirms that customer/client data is referenced by the order/entity audit layer, while the canonical live collection evidence currently remains limited to `/orders`. No independently verified standalone customer collection route was established in this pass.

Decision: customer master remains an ERP/MDM target; order-linked client fields must not be promoted into a standalone customer API contract without live evidence.

## 2. Payments

Status: NOT VERIFIED.

Repository search found payment directory/design references, but no independently verified production payment transaction endpoint or payment ledger implementation. Existing finance documentation explicitly requires actual availability to be verified against RO App before configuration.

Decision: do not model a production payment ledger as if it were already available in RO App. Do not activate payment integrations or writes.

## 3. Costing

Status: IMPLEMENTATION NOT VERIFIED.

The ERP data model and costing audit define the required dimensions: metal, stones, labor and overhead, with planned/actual cost and provenance/versioning. Repository evidence does not prove a live costing engine, live price sources, labor-rate engine, overhead allocation or RO App cost endpoint.

Decision: no parallel costing engine is introduced. Existing implementation, if any, must be located and verified before extension.

## 4. Finance

Status: NOT VERIFIED.

No production chart of accounts, journal/financial-entry ledger, payment transaction ledger, reconciliation engine, revenue-recognition implementation, cost-to-finance posting or RO App finance endpoint was verified in the repository.

Decision: RO App is not promoted as the authoritative accounting source. A finance/accounting source must be identified and then mapped READ_ONLY.

## 5. Gate result

`CUSTOMERS = NOT VERIFIED`
`PAYMENTS = NOT VERIFIED`
`COSTING_IMPLEMENTATION = NOT VERIFIED`
`FINANCE_IMPLEMENTATION = NOT VERIFIED`
`ERP_READINESS = BLOCKED`
`PRODUCTION_WRITE = 0`

## 6. Required external evidence

To advance these gates, obtain only authorized READ evidence:

1. Official RO App documentation for customer/payment/cost/finance endpoints, if available.
2. Authorized GET smoke tests with exact endpoint, HTTP status and response schema.
3. Customer/order identity reconciliation.
4. Payment/order/revenue reconciliation.
5. Cost component reconciliation: metal, stones, labor, overhead.
6. Identify the actual accounting/finance system used by MARSEL and verify its source-of-truth role.
7. Preserve timestamps, hashes and evidence artifacts.

No credentials, tokens or financial records are requested or transmitted through this audit.
