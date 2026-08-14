# MARSEL BUSINESS — Canonical Project Registry

Status: canonical structure

## Rule
One goal = one master domain. Same-name projects are aliases of the canonical domain. Shared data uses one master entity definition.

## Canonical domains
1. CORE DATA — products, categories, materials, metals, stones, services, customers, suppliers, employees, warehouses.
2. OPERATIONS — orders, production, repairs, procurement, stock, BOM.
3. FINANCE — cost, pricing, revenue, profit.
4. CATALOG & E-COMMERCE — catalog, website, prices, online orders.
5. MARKETING & GROWTH — traffic, leads, conversion, analytics.
6. RO APP / ERP — API, data quality, backup, integrity, endpoint registry, post-audit.
7. AUTOMATION & INFRASTRUCTURE — GitHub, Actions, webhooks, scheduled checks, monitoring.
8. QA & CONTROL — duplicates, validation, evidence, risks, decisions.

## Consolidation policy
- Preserve source records until independently verified as migrated.
- Do not delete or overwrite source data during consolidation.
- Deduplicate by canonical entity ID where available; otherwise require deterministic matching evidence.
- Every migration must be auditable and reversible.
- ChatGPT Project/UI objects cannot be physically merged by this repository automation; this registry is the canonical data/operational structure.

## RO APP placement
RO APP is an ERP/API operational subsystem under MARSEL BUSINESS, not a separate business goal.

## Completion gate
Consolidation is considered complete only when migration inventory, duplicate resolution, integrity checks, and post-audit all pass.