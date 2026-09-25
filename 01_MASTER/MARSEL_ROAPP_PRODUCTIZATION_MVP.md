# MARSEL ROAPP — PRODUCTIZATION / MVP CONTRACT

Date: 2026-09-18
Canonical system: MARSEL ROAPP
Repository: atalanrafael-jpg/MARSEL-Ro-app
Technical canonical branch: main

## Purpose
Prioritize delivery of a usable owner product over adding further strategic frameworks. The repository is not considered "made" merely because control-plane, audit, MCP and documentation layers exist.

## Already real
- Canonical repository/branch and safety controls are established.
- Read-only RO App connector exists.
- Runtime exposes health/readiness plus RO App orders and bounded order audit.
- MCP exposes read-only order inspection/audit.
- Active Supabase project contains an RLS-enabled repair-oriented schema.
- Production WRITE is disabled.

## Current product gap
The owner UI vertical slice is now implemented in the repository and served by the FastAPI runtime at `/app`. It uses Supabase Auth and RLS for application data, with RO App remaining READ-ONLY. The remaining Gate A work is live deployment and direct end-to-end verification; Supabase application tables currently have zero rows.

## MVP vertical slice
AUTH → OWNER DASHBOARD → CLIENT → REPAIR → ITEM → STATUS → ATTACHMENT → AUDIT → DEPLOY → VERIFY

### Owner Dashboard
Active repairs/orders, overdue, due soon, status distribution, unresolved exceptions, last integration/audit state, with VERIFIED / REVIEW_REQUIRED / BLOCKED states.

### Clients
Search, client card, phone/email, linked repairs/orders.

### Repairs / Orders
Create local MARSEL repair record; client; item type (jewelry/watch/glasses/other); description; metal; stone details; serial number; condition; due date; status lifecycle; status history.

### Evidence
Safe attachment references, creator and timestamp.

### Integrations
RO App connection/audit state and evidence. Never claim CONNECTED without current direct evidence. RO App remains READ-ONLY in MVP.

## Source of truth
- MARSEL workflow: application database.
- RO App operational data: RO App until current reconciliation contract is verified.
- Channel/e-commerce data: separate source until verified.
- AI: recommendation/automation layer, never authoritative for operational or financial facts.

## Gates
A — Usable: owner completes the workflow without GitHub/Python/ChatGPT.
B — Data-safe: auth/RLS/audit/attachments/roles verified.
C — RO App read integration: fresh live evidence and reconciliation, no writes.
D — Staging mutation: schema, backup, dry-run, idempotency and rollback evidence.
E — Production: explicit authorization plus all security gates.

## Execution rule
Do not add another strategic subsystem before Gate A passes unless it directly unblocks Gate A. The next unit is a vertical slice, not another framework.