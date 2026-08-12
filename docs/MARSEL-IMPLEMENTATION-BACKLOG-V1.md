# MARSEL — Implementation Backlog V1

Date: 2026-08-12
Status: READY / SAFE TO IMPLEMENT OFFLINE

## Objective
Convert the agreed MARSEL scope into implementation-ready units without claiming live Ro App deployment.

## Priority P0 — unblock and verify
1. Restore/verify Ro App API access.
2. Verify `/company`, products, services and orders schemas against live responses.
3. Establish verified backup/export and restore procedure before any write.
4. Run read-only inventory and data-quality audit.

## Priority P1 — reference master data
- Brands
- Categories
- Groups
- Subgroups
- Collections
- Metals/alloys/fineness
- Stones/grades/cuts
- Consumables
- Warehouses
- Employees/roles
- Document types
- Payment methods

Each directory requires stable ID, Russian display name, normalized key, status, sort order, duplicate rule and source-of-truth field.

## Priority P1 — product master
- Canonical MARSEL ID
- SKU/article
- Product type
- Category/group/subgroup/collection
- Brand
- Metal composition and fineness
- Stone composition
- Weight/dimensions/size
- Cost components
- Retail/wholesale price
- Stock state
- Lifecycle
- Photos
- Documents
- 3D/model assets

## Priority P1 — service/operations
### Production
Order/job → materials → stones → operations/labor → waste/loss → responsible employee → stages → final reconciliation.

### Jewelry repair
Customer → received item → diagnosis → agreed work → estimate → materials → operations → technician → status → acceptance/delivery → attachments.

### Watch repair
Customer → watch brand/model/reference/serial where applicable → condition → diagnosis → parts → operations → testing/service checks where applicable → technician → status → acceptance/delivery.

## Priority P1 — cost accounting
Maintain component-level provenance for:
- metal quantity and purity/fineness;
- metal price basis and effective date;
- stone identity, weight/size and quality attributes;
- acquisition/source price;
- processing/setting/labor components;
- calculation version.

No formula becomes production truth until approved and validated against real Ro App capabilities.

## Priority P2 — commerce
- Payment-method mapping
- E-commerce channel mapping
- External product IDs
- SKU mapping
- Price/stock synchronization
- Media mapping
- Sync timestamps
- Conflict policy

## Priority P2 — assets
- Photo ingestion/validation
- 3D/model ingestion/validation
- MIME/type validation
- Size limits
- SHA-256 checksum
- Versioning
- Product-to-asset relationship
- Duplicate asset detection

## Mandatory quality gates
Before write/import:
1. schema verified;
2. backup verified;
3. required fields pass;
4. canonical IDs unique;
5. reference IDs resolve;
6. no critical orphan relations;
7. duplicate report reviewed;
8. dry-run has zero unexplained critical conflicts;
9. write scope explicitly limited;
10. post-write reconciliation planned.

## Current blockers
- Ro App API currently returns HTTP 403 due to subscription/access state observed in the latest audit. Current live data therefore cannot be verified.
- Full production backup/restore is not yet evidenced.

## Safety rule
Until blockers are cleared, implementation may continue in code, schemas, validators, fixtures, tests and documentation. No production DELETE, mass UPDATE or bulk import is authorized by this backlog.
