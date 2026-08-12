# MARSEL Master Catalog V1

Status: DESIGN / NOT LIVE IN RO APP

## 1. Purpose
MARSEL Master Catalog is the canonical product registry for jewelry, watches, eyewear and accessories. One canonical product record may be published to multiple sales channels without creating independent product identities.

## 2. Source of truth
`master_product_id` is the canonical MARSEL identity. Marketplace listings, website listings, catalog pages, online try-on records, photos and 3D assets reference the master record rather than becoming separate product masters.

## 3. Product identity
Required/controlled fields:
- `master_product_id`
- SKU
- product name
- brand ID
- product type
- category ID
- group ID
- status
- country/market where applicable

Do not fabricate SKU, brand, stock, price, material, stone or document values.

## 4. Jewelry attributes
- metal/material;
- alloy/fineness;
- metal weight;
- stone type;
- stone count;
- stone characteristics where verified;
- dimensions;
- ring size where applicable;
- product weight;
- hallmark/marking information where applicable;
- certificates/documents where applicable.

## 5. Watch attributes
- brand;
- model/reference;
- serial number where applicable and lawfully handled;
- movement/type;
- case material;
- strap/bracelet;
- dimensions;
- water-resistance information where verified;
- documents.

## 6. Eyewear attributes
- brand;
- model/reference;
- frame material;
- frame color;
- lens type;
- lens characteristics where verified;
- dimensions;
- included accessories;
- documents.

## 7. Commercial data
Keep separate:
- base price;
- channel price;
- discount;
- currency;
- tax treatment;
- cost basis;
- calculated margin;
- availability;
- reservation quantity;
- sale status.

Price and stock are time-sensitive operational values and must not be duplicated as uncontrolled static values in channel records.

## 8. Inventory
Inventory is maintained by location/warehouse and linked to the master product. Recommended state flow:
`available → reserved → sold`.

Corrections and transfers must remain auditable. A unique physical product must not be sold twice because of channel synchronization lag.

## 9. Media / 3D
Assets are separate records with:
- asset ID;
- master product ID;
- asset type;
- version;
- filename/reference;
- checksum where supported;
- status;
- publication channels.

Supported asset types include photo, 3D model and document. Online try-on uses a reference to the master product and appropriate media asset; it does not create a new product.

## 10. Marketplace readiness
A product receives a marketplace readiness result before publication:
- identity complete;
- required category mapped;
- required attributes complete;
- valid price;
- valid inventory source;
- required media present;
- required documents present;
- channel-specific rules passed.

Failed checks block publication rather than silently publishing incomplete data.

## 11. Channel layer
Each marketplace listing stores only channel-specific mapping/state, for example:
- channel ID;
- external listing ID;
- publication state;
- channel category mapping;
- channel-specific title/description where needed;
- last synchronization timestamp;
- synchronization result/error.

The marketplace listing is not a second master product.

## 12. Orders
Marketplace orders must resolve to `master_product_id` and the actual inventory location/stock movement. Order import must be idempotent so the same external order cannot create duplicate sales.

## 13. Returns
Returns must reference the original order and master product. Returned inventory requires explicit inspection/state before becoming available again.

## 14. Analytics
Support reporting by product, category, brand, channel and period:
- units sold;
- gross revenue;
- discounts;
- commissions/fees;
- logistics;
- advertising;
- returns;
- product cost;
- contribution/margin where reliable inputs exist.

## 15. Data quality controls
Block or flag:
- duplicate master IDs;
- duplicate normalized SKUs;
- missing required fields;
- orphan media;
- orphan marketplace listings;
- negative/contradictory inventory;
- unapproved price changes;
- stale channel synchronization;
- duplicate imported orders.

## 16. Lifecycle
`draft → ready_for_publication → published → temporarily_unavailable → discontinued → archived`

Actual Ro App statuses must be mapped to verified live IDs; these are MARSEL canonical values only.

## 17. Governance
Only the Master Catalog may define canonical product identity. Channel adapters may transform data for a destination but must not silently change the canonical source.

## 18. Safety
This specification does not authorize production writes. Before implementation, verify Ro App schema/API, inventory semantics, backup/restore, marketplace requirements, authentication and idempotency. Then run read-only discovery and dry-run validation before controlled rollout.
