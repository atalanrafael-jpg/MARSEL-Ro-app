# MARSEL — MASTER Operating System V1

Status: DESIGN / NOT LIVE IN RO APP

## 1. Business core
MARSEL is organized into four operating contours:
- SALES: jewelry, watches, eyewear, accessories, catalog, online store, online try-on.
- PRODUCTION: custom manufacturing, metals, stones, costing, production stages, quality control.
- SERVICE: jewelry repair, watch repair, eyewear repair, diagnostics, parts, warranty, before/after evidence.
- MANAGEMENT: inventory, money, employees, customers, documents, analytics and exceptions.

## 2. Canonical identity chain
`customer → order → item/product → service/sale → operations → materials → money → documents/assets → history → analytics`

Every operational record must have a stable canonical ID and explicit parent relationship. No orphan records in production.

## 3. Unified product passport
A product/item record should consolidate:
- MARSEL ID;
- SKU/reference;
- brand/category/group/subgroup;
- material/metal/fineness;
- stones;
- weight/dimensions/size where applicable;
- cost and price history;
- stock/location;
- photos;
- 3D assets and versions;
- catalog/store links;
- try-on links;
- repair/service history;
- warranty;
- documents.

One physical/commercial item must not become multiple independent truths merely because it appears in inventory, catalog or online store.

## 4. Immutable/auditable history
Critical accepted events must be append-only or correction-audited where the live system supports it: intake condition, approvals, material consumption, delivered final price, delivery evidence, status changes and important product changes.

## 5. Error prevention
The application should block, rather than merely warn about, critical invalid operations. Examples:
- no delivery before QC and required reconciliation;
- no price increase without customer approval;
- no completion with unresolved material consumption;
- no inventory write without an operation basis;
- no duplicate customer/product creation when canonical duplicate rules detect a match;
- no deletion of critical evidence without an auditable policy.

## 6. Exception Center
Create one management queue with severity and actionable resolution for:
- overdue repairs/orders;
- awaiting approvals;
- failed QC;
- duplicate customers/products/SKUs;
- missing cost;
- abnormal/negative stock;
- missing photos or 3D assets where required;
- orphan documents/assets;
- API/synchronization errors;
- unresolved reconciliation differences.

Every exception should have: object ID, severity, reason, detected_at, owner, resolution state and resolution evidence where supported.

## 7. Profitability
Maintain separate:
- revenue;
- material/part cost;
- labor/operation cost;
- other approved cost;
- gross profit;
- margin.

Report by business contour, product/category, repair type, operation, employee and period where data supports it.

## 8. Employee performance
Operational analytics may include workload, turnaround time, rework, warranty cases, revenue/cost/margin contribution and overdue work. Metrics must be based on verified records and clearly defined formulas.

## 9. Online try-on
`catalog → product → media/3D → preview → save/delete → product card → inquiry/order`.
Preview must reference the canonical product ID. It must not silently create payment, reservation or inventory write. User photos are temporary assets unless explicitly retained under a defined policy.

## 10. 3D asset governance
For each supported product:
- photo asset;
- 3D model asset;
- preview asset when generated;
- version;
- canonical product ID;
- checksum where supported.

The current asset must be unambiguous. Replacing a model creates a traceable version rather than silently overwriting the historical reference.

## 11. Dashboard
Management dashboard should surface:
- today's/month's sales;
- gross profit and margin;
- average ticket;
- service workload and overdue orders;
- stock value and shortages;
- customer activity and repeat purchases;
- best/low-performing products;
- products missing required media;
- Exception Center counts.

## 12. Automated MASTER audit
The audit must return PASS/FAIL for at least:
- customer duplicates;
- product duplicates;
- SKU duplicates;
- reference-data integrity;
- orphan documents/assets;
- stock anomalies;
- costing anomalies;
- open/overdue repairs;
- status-transition violations;
- API/schema diagnostics.

## 13. Backup and change gate
Before mass production changes:
`backup → backup verification → read-only audit → dry-run → controlled change → post-change reconciliation`.

A failed critical gate blocks production write.

## 14. Environment separation
Maintain explicit DEV / TEST / PRODUCTION separation where the available infrastructure supports it. New API mappings, imports and automation must be validated before production.

## 15. Priority roadmap
### P0 — Data safety
API access verification, backup/restore, read-only audit, duplicate detection, data integrity.

### P1 — Operations
Customer, product/item, orders, repair, production, inventory, costing.

### P2 — Sales growth
Catalog, photo/3D, online try-on, online store, CRM/repeat sales.

### P3 — Management
Dashboard, automated reports, Exception Center, KPI and notifications.

## 16. Phone policy
MARSEL canonical phone category is `mobile` / `Мобильный` only. Multiple numbers are allowed where needed, but all use the same category. Duplicate detection uses normalized numbers.

## 17. Safety / implementation boundary
This document is the master design specification. It does not assert that every field, status or API operation exists in Ro App. Live schema, endpoint support, authentication, backup/restore and field mapping must be verified before production implementation.
