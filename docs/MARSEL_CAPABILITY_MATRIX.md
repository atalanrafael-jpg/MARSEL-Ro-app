# MARSEL ROAPP — Capability Matrix

**Purpose:** one canonical inventory of capabilities, evidence state, blockers, and acceptance criteria. This is a control document, not proof that a capability is live.

## Status model

- **VERIFIED** — current direct evidence exists.
- **PARTIAL** — some evidence exists, but the acceptance gate is not complete.
- **BLOCKED** — a required gate prevents safe promotion.
- **NOT VERIFIED** — no sufficient current evidence.
- **PROPOSED** — designed capability, not established as live.

## Current matrix

| Domain | Capability | Status | Current evidence / gate |
|---|---|---:|---|
| Project control | Canonical MARSEL ROAPP identity / single control plane | VERIFIED | Current main governance and fail-closed controls are present. |
| RO App API | Authenticated read-only API access | VERIFIED | Current repository contains read-only API controls; historical direct `/v2/orders` evidence exists. Freshness must still be checked for release gates. |
| RO App API | API inventory | VERIFIED | Inventory/control-plane implementation exists; completeness remains a separate acceptance criterion. |
| RO App API | Full entity coverage | PARTIAL | Issue #30 requires fresh verification for warehouse/stock plus products, services, customers and payments. |
| Data quality | Orders/products/services audit | PARTIAL | Existing audit evidence exists; current live freshness must be established before production promotion. |
| Data quality | Duplicate/orphan/reference analysis | PARTIAL | Duplicate/reference controls exist; current acceptance evidence remains required. |
| Warehouse | Official live warehouse/stock contract | NOT VERIFIED | Issue #30 explicitly requires fresh authorized GET verification. |
| Backup | Complete permitted backup/export | NOT VERIFIED | Production gate requires direct backup evidence. |
| Recovery | Independent restore + integrity test | NOT VERIFIED | Production gate requires direct restore evidence. |
| Safety | Production WRITE fail-closed | VERIFIED | Current production gate keeps `MARSEL_WRITE_APPROVED=false`; no production WRITE is authorized by this matrix. |
| Safety | Mutation dry-run | NOT VERIFIED | Required by production gate before any production mutation. |
| Safety | Idempotency evidence | NOT VERIFIED | Required by production gate. |
| Safety | Rollback evidence | NOT VERIFIED | Required by production gate. |
| Security | Credential exposure remediation | BLOCKED | Issue #23 requires rotation/exposure verification evidence. |
| Security | Secret scanning / push protection | PARTIAL | Required by issue #91; account/repository setting verification remains separate. |
| GitHub | Protected `main` / required checks | BLOCKED | Issue #91 and #106 identify account/repository administration work still required. |
| MCP | Local/read-only MCP implementation | VERIFIED | Current main contains MCP setup and read-only boundary controls. |
| MCP | Official RO App MCP authorization | NOT VERIFIED | Project gate requires direct authorization evidence. |
| Gmail | Secure OAuth read-only integration | NOT VERIFIED | Issue #27 requires explicit user authorization and successful live read-only test. |
| Observability | Correlation/telemetry contract | PROPOSED | Issue #134 is open; implementation/verification not accepted as complete. |
| Master data | Canonical entity/integration contract | PROPOSED | Issue #133 is open; fields must remain backed by live/documented evidence. |
| External commerce | Website/marketplace/payment/social adapters | PROPOSED | Issue #135 is open; start with read-only discovery and sandbox verification. |
| Business ERP | CRM / orders / repair / production / finance / analytics | PARTIAL | Architecture and project models exist; live RO App implementation and acceptance must be verified per module. |
| Costing | Metal / stones / labor / direct-cost profitability | PROPOSED | Business requirement exists; live automatic calculation is not accepted without source data and implementation evidence. |
| Automation | Trigger → Validate → Action → Log → Verify → Alert | PROPOSED | Target architecture; individual automations require separate evidence. |
| AI | Controlled AI analysis/recommendations | PROPOSED | Target capability; no claim of autonomous production action. |
| Growth | E-commerce / social commerce / marketplaces | PROPOSED | Target business capability; issue #135 requires adapter contracts and sandbox verification. |

## Production gate

Production WRITE remains disabled until the required evidence set is independently verified. Required evidence includes backup, restore/integrity, reconciliation, read-only audit, duplicate/reference analysis, dry-run, idempotency, rollback, security controls, and post-write verification.

## Important distinction

A repository file, CI success, architecture document, or historical audit is **not** itself proof of current live production capability. Current acceptance requires fresh direct evidence appropriate to the capability.

## Next execution order

1. Discover and verify existing evidence artifacts from repository/Actions.
2. Freshly verify blocked API/entity coverage.
3. Establish complete backup/export evidence.
4. Perform independent restore/integrity verification.
5. Resolve security exposure and account-level GitHub gates.
6. Verify MCP/Gmail only where explicitly required.
7. Run final read-only audit.
8. Re-evaluate production gate.

**Safety invariant:** no production WRITE, deletion, mass mutation, credential bypass, or synthetic evidence creation is authorized by this document.
