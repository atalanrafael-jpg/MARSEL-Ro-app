# MARSEL — Reference Directories & Operational Model V1

Date: 2026-08-12
Status: DESIGN / IMPLEMENTATION READY — NOT LIVE IN RO APP

## Purpose
Define the canonical Russian-language reference data required for MARSEL before any production import or synchronization.

## 1. Brand directory
Fields: `brand_id`, `name`, `normalized_name`, `description`, `status`, `sort_order`, `created_at`, `updated_at`.
Rules: unique normalized name; no silent duplicates; inactive brands remain historical references.

## 2. Product taxonomy
Hierarchy: `category → group → subgroup → collection → product`.
Every level has stable ID, Russian display name, normalized key, status and sort order.

Suggested jewelry categories: Rings, Earrings, Pendants, Necklaces, Bracelets, Chains, Brooches, Sets, Wedding/Engagement, Custom/Other.
Suggested service categories: Jewelry repair, Watch repair, Manufacturing, Cleaning/Polishing, Resizing, Stone setting, Other.
These are proposed seed values, not claimed as existing Ro App values.

## 3. Material directory
Separate references for metals, alloys/finishes, stones and consumables. Metal records include fineness, unit, supplier/source reference and pricing history. Stone records include type, variety, shape/cut, size/weight, quality attributes and pricing source where applicable.

## 4. Warehouse directory
Fields: `warehouse_id`, `name`, `code`, `type`, `address`, `status`, `responsible_employee_id`.
Warehouse types: main stock, production, repair, finished goods, quarantine/quality, transit. These are proposed taxonomy values and require confirmation against live Ro App capabilities.

## 5. Document directory
Document types: order document, work order, receipt/acceptance, invoice, act, certificate, stone document, metal document, supplier document, customer attachment, internal production document.
Every document must have owner entity, document type, number/date where applicable, file reference, checksum where available and access classification.

## 6. Product master
Canonical identity: `marsel_id` + SKU/article. A product may have many photos, documents and 3D/model assets. Assets must not create duplicate products.

Minimum product fields: name, SKU, category/group/subgroup, brand, collection, product type, metal, stones, weight, dimensions/size, cost, price, stock state, lifecycle, photos, documents, model assets.

## 7. 3D assets
Supported logical asset type: `model`. Recommended metadata: format, filename, checksum, version, source, upload timestamp, product link, preview image and status. Supported formats must be verified against the eventual Ro App/file-storage implementation before upload.

## 8. Cost accounting
Cost must be traceable, not a single unexplained number.

Metal cost components: net metal weight × applicable fineness/purity factor × selected price basis + defined processing components.
Stone cost components: stone identity + weight/size + quality attributes + acquisition price/source + defined setting/processing components.
Final product cost must retain component-level provenance and calculation version. Exact formulas and price source are configuration decisions and must be approved before production use.

## 9. Production
Production job should link customer/order, product, material consumption, stones, labor/operations, waste/loss, responsible employee, stages, status, timestamps and final reconciliation.

## 10. Jewelry repair
Repair order should capture received item, customer, diagnosis, agreed work, estimated/final price, consumed materials/stones, operations, technician, status, acceptance/delivery evidence and attachments.

## 11. Watch repair
Same control model as jewelry repair, with watch-specific fields for brand/model/reference, serial number when applicable, condition, tests, parts, water-resistance/service checks where applicable and customer acceptance. These fields require validation against the actual Ro App service/order schema.

## 12. Payments
Payment directory must separate method from transaction. Proposed methods: cash, bank card, bank transfer, online payment, other. Actual availability must be verified against Ro App before configuration.

## 13. E-commerce
Use a channel mapping layer so e-commerce identifiers do not replace MARSEL canonical IDs. Required mapping: channel, external product ID, SKU, publication status, price, stock state, media, category mapping and synchronization timestamp.

## 14. Data-quality gates
Before import/write:
- unique canonical IDs;
- unique normalized reference names;
- no orphan relations;
- valid material/stone references;
- valid warehouse references;
- asset checksums where available;
- required-field validation;
- duplicate detection;
- dry-run with zero unexplained critical conflicts.

## 15. Safety boundary
This specification does not authorize production writes. Live schema, supported API methods, backup/restore and subscription/API access must be verified first. Proposed seed values are not evidence of current Ro App configuration.
