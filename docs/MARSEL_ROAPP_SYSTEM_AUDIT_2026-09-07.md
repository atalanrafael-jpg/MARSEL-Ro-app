# MARSEL ROAPP — System Audit 2026-09-07

## Executive result

The repository is structurally mature and has a strong READ-ONLY/evidence-first control model, but it is not yet a production ERP/integration platform. The largest remaining gap is not another script: it is closing the boundary between the RO App data source, the MARSEL business model, authenticated integrations, and independently produced evidence.

## Findings

### P0 — Protect the connector API
The FastAPI application exposed `/roapp/orders` and `/roapp/audit/orders` without caller authentication. If the connector is deployed on a reachable network, a third party could use these routes to query business data through the server-side RO App credential.

Status: FIXED on `audit/roapp-hardening-2026-09-07` by adding `MARSEL_INTERNAL_API_KEY` and constant-time header verification. `ROAPP_API_KEY` remains the upstream RO App credential and is never used as the caller credential.

### P1 — Readiness endpoint minimization
`/ready` reported whether the upstream API key was configured. This is not a credential leak, but it unnecessarily disclosed deployment configuration. The endpoint now reports only non-sensitive service state.

Status: FIXED on the audit branch.

### P1 — Evidence gates remain external
Backup/restore, complete live entity coverage, warehouse contract, collision reconciliation, Gmail OAuth, official MCP authorization, credential-rotation proof, and account-level GitHub controls still require direct evidence. CI must validate evidence, not manufacture it.

Status: BLOCKED/EXTERNAL as designed.

### P1 — Integration architecture is incomplete
The repository contains RO App, Gmail, MCP and OpenAI Ads components, but there is not yet a single canonical event/data flow connecting customer → lead → order → production/repair → inventory/cost → payment → attribution → analytics.

Status: ARCHITECTURE GAP.

### P1 — ERP model is proposed, not authoritative
The open ERP data dictionary PRs are useful design work, but they must not become a source of truth for unverified RO App fields. Authoritative fields should be promoted only after live/documented evidence.

Status: REVIEW_REQUIRED.

### P1 — Multiple open PRs are based on older main snapshots
Open PRs #123, #127 and #128 target `main` but were created from earlier base commits. They should be rebased/updated before merge decisions so current canonical controls are not accidentally bypassed.

Status: PROCESS GAP.

### P2 — Production observability
The service has `/health`, but there is no clearly defined production observability contract for request correlation, upstream latency, rate-limit events, error classes, audit run IDs, and evidence artifact IDs.

Status: IMPROVEMENT REQUIRED.

## Target system relationships

```text
                         ┌─────────────────────┐
                         │   Ювелирная студия  │
                         │       MARSEL        │
                         └──────────┬──────────┘
                                    │
                          business events / IDs
                                    │
                    ┌──────────────▼──────────────┐
                    │       MARSEL ROAPP           │
                    │ canonical control plane      │
                    └──────────────┬──────────────┘
                                   │
          ┌────────────────────────┼─────────────────────────┐
          │                        │                         │
     RO App source            Integration bus            Evidence
          │                        │                         │
   orders/products/stock      Gmail / MCP / Ads       immutable artifacts
          │                        │                         │
          └────────────────────────┼─────────────────────────┘
                                   │
                         ERP/analytics model
                                   │
               CRM → sales → repair → production
               → costing → inventory → finance → KPI
```

## Recommended connection rules

1. **RO App remains the operational source** for entities it actually owns until a verified replacement exists.
2. **MARSEL ROAPP is the orchestration/control layer**, not a second uncontrolled database.
3. Every synchronized entity gets a stable cross-system identity map.
4. Every event gets an idempotency key and correlation ID.
5. Read paths and write paths remain separate.
6. Production WRITE remains disabled until all safety evidence passes.
7. Gmail is read-only and used for lead/order communication intelligence only after user authorization.
8. MCP exposes only explicitly authorized tools/scopes; no implicit write access.
9. Ads attribution receives only permitted conversion events and never the RO App secret.
10. Marketplace/e-commerce connectors should synchronize through an adapter layer, never directly into arbitrary RO App endpoints.

## Next implementation order

### Phase 1 — Security and platform boundary
- deploy the connector only behind HTTPS;
- configure a strong `MARSEL_INTERNAL_API_KEY` in the runtime secret store;
- keep `ROAPP_API_KEY` separate and rotate the previously exposed credential tracked by Issue #23;
- add request correlation IDs and structured security events;
- verify MCP OAuth/OIDC independently.

### Phase 2 — Canonical data layer
- close API/entity registry;
- close warehouse/stock contract;
- establish canonical IDs and source-of-truth matrix;
- implement duplicate/reference reconciliation in report-only mode;
- publish data dictionary only for verified fields.

### Phase 3 — Business integrations
- RO App ↔ MARSEL ERP model;
- customer/lead lifecycle;
- repair lifecycle and repeat-sales linkage;
- custom manufacturing workflow;
- inventory/cost by metal and stones;
- payments and order status mapping;
- online store/marketplace adapter;
- Gmail read-only enrichment;
- OpenAI Ads conversion attribution.

### Phase 4 — Recovery and controlled writes
- backup/export evidence;
- independent restore evidence;
- schema reconciliation;
- dry-run;
- idempotency;
- rollback;
- post-write verification;
- only then consider explicit controlled WRITE.

## Definition of done

The system is ready only when every production dependency is backed by current direct evidence, every external integration has a verified contract, every sensitive route is authenticated, every write is gated, and the business lifecycle can be traced end-to-end from lead/customer to order, fulfillment/repair, inventory/cost, payment and KPI.
