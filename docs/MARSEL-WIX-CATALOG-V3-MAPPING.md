# MARSEL ↔ Wix Catalog V3 Mapping Baseline

Status: DISCOVERED / NO PRODUCT MUTATIONS

## Verified Wix site
- Site: Ювелирная студия Mar
- Wix Stores catalog: V3
- Site status: Draft
- Currency: RUB
- Locale: ru-RU / Europe/Moscow
- Velo: disabled

## Wix V3 facts verified from official Wix documentation
- Products V3 supports products, variants, pricing, SKU, inventory, media, categories and metadata.
- Product media supports up to 15 media items per product in `itemsInfo.items`; the first item is the read-only `main` media.
- Media can reference an existing Wix Media Manager file ID or an external URL.

## Canonical MARSEL mapping
- `marsel_id` -> canonical internal identity; do not replace with a display name.
- `sku` -> Wix product/variant SKU where applicable.
- `title` -> Wix product name.
- `description` -> Wix product description, only after approved source facts are present.
- `price` -> Wix price only under explicit source-of-truth policy.
- `stock_status` -> Wix inventory state only under explicit synchronization policy.
- `asset` -> Wix product media items; preserve deterministic ordering.
- `category_id` -> Wix category mapping after live category schema discovery.
- `collection_id` -> MARSEL collection metadata; do not conflate with Wix category.

## Important constraints
- Wix V3 and V1 endpoints must not be mixed. The MARSEL site is verified as V3.
- No products, prices, inventory or media have been created/changed by this mapping document.
- Before bulk import: retrieve live Ro App schemas, retrieve live Wix catalog data, produce field-level reconciliation, backup permitted Ro App data, dry-run, then controlled test mutation.
- AI-generated descriptions are drafts; operational and commercial facts remain authoritative from source systems.
