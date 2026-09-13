# MARSEL ROAPP — ERP ENTITY OWNERSHIP MATRIX V1

Дата: 2026-09-06
Статус: DESIGN / READ_ONLY / WRITE=0

## Цель

Определить, какая система владеет сущностью, а какие системы только ссылаются на неё. Матрица предотвращает параллельные master-записи и неконтролируемую перезапись данных.

## Ownership

| Entity | Canonical owner | RO App role | Marketplace/e-commerce | Control/evidence |
|---|---|---|---|---|
| MARSEL identity | MARSEL master | reference | reference | GitHub docs |
| Master Product ID | MARSEL master | operational reference where supported | channel mapping | GitHub evidence |
| Product catalog | Master Catalog / MARSEL | operational projection where confirmed | publication projection | catalog evidence |
| Category taxonomy | MARSEL reference layer | mapping target | channel mapping | data-quality checks |
| Metal / stone reference | MARSEL reference layer | operational reference where supported | usually not owner | source/pricing evidence |
| Customer | ERP/CRM target owner | operational record where confirmed | channel-specific customer reference | audit trail |
| Supplier | ERP procurement target owner | reference if supported | not owner | procurement evidence |
| Employee | MARSEL/ERP HR target owner | reference | not owner | access/audit controls |
| Warehouse | RO App operational owner until ERP contract exists | operational source | stock projection | live GET required |
| Stock balance | RO App operational source where confirmed | source | synchronized projection | reconciliation |
| Stock movement | RO App operational source where confirmed | source | projection | immutable movement evidence |
| Sales order | Source depends on channel; preserve external ID | operational source where confirmed | external channel source | reconciliation |
| Purchase order | ERP procurement target owner | integration if supported | not owner | PO evidence |
| BOM | ERP/production target owner | reference if supported | not owner | versioned BOM |
| Production order | ERP production target owner | operational integration if supported | not owner | work-order evidence |
| Repair order | ERP/service target owner | operational integration if supported | not owner | acceptance/delivery evidence |
| Cost version | ERP costing target owner | calculation source only if confirmed | price projection | component provenance |
| Price | MARSEL/ERP commercial layer | operational price where confirmed | channel-specific price may differ | effective dates |
| Payment | Financial/payment system target owner | status/reference if confirmed | channel payment source | reconciliation |
| Financial entry | Finance/accounting source | reference only | reference | accounting evidence |
| Media/3D asset | Master Catalog/media layer | linked reference | channel derivative | checksum/version |

## Ownership rules

1. No system may overwrite another system's canonical entity without an explicit contract.
2. External order IDs remain external identifiers and are mapped to canonical MARSEL IDs.
3. RO App becomes authoritative for a domain only after its current endpoint and data semantics are directly verified.
4. Financial ownership is not assigned to RO App by assumption; it requires explicit accounting design and integration evidence.
5. Costing is versioned and component-based; no hidden single-value replacement is permitted.
6. Synchronization is one-way or explicitly bi-directional per contract, never inferred.

## Current unresolved ownership gates

- Warehouse contract: NOT VERIFIED.
- Current API/entity completeness: NOT VERIFIED.
- Finance source of truth: DESIGN / REQUIREMENTS.
- Customer/CRM source of truth: DESIGN / MAPPING REQUIRED.
- Production and repair operational contracts: MAPPING REQUIRED.
- Costing implementation in working account: NOT VERIFIED.

## Safety

The matrix is architectural evidence only. It does not authorize writes, imports, deletions, stock corrections, price changes or financial postings.
