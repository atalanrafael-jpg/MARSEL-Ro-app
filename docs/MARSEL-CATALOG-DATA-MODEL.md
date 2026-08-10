# MARSEL — Catalog Data Model v1

Status: STRUCTURE FIRST / NO PRODUCT IMPORTS

## Design principles
- One canonical `marsel_id` per product/project.
- Stable IDs, never names, are used for relationships and synchronization.
- Product facts are authoritative from operational records; AI may enrich text but must not invent financial, stock, metal, stone, certification or compliance facts.
- Photos and documents are assets linked to a product, never duplicate product records.
- Category, collection, material and stone are separate dimensions.
- Channel publication is metadata on the canonical product, not a copied product.

## Product entity
Required:
- marsel_id
- sku / article
- title
- product_type
- category_id
- collection_id (nullable)
- status
- metal_ids
- stone_ids
- weight_g (nullable)
- dimensions (nullable)
- stock_status
- price (nullable)
- cost (nullable)
- made_to_order
- description
- created_at
- updated_at

## Metal entity
- metal_id
- metal_type
- fineness
- color
- weight_g
- cost_basis
- source
- effective_at

## Stone entity
- stone_id
- stone_type
- origin (nullable)
- quantity
- carat_weight (nullable)
- shape (nullable)
- cut (nullable)
- color (nullable)
- clarity (nullable)
- certificate_id (nullable)
- cost (nullable)

AI must never infer commercially material stone attributes from an image as authoritative facts.

## Asset entity
- asset_id
- marsel_id
- asset_type: main/front/back/side/detail/model/certificate/technical/before/after
- original_uri
- web_uri (nullable)
- thumbnail_uri (nullable)
- sort_order
- source
- author (nullable)
- publication_status
- created_at

## Document entity
- document_id
- marsel_id
- document_type
- uri
- issuer (nullable)
- issue_date (nullable)
- expiry_date (nullable)
- verification_status

## Category and collection
Category describes what the item is (ring, earrings, pendant, chain, bracelet, necklace, brooch, watch, repair, custom work).
Collection describes the commercial/design grouping (e.g. Wedding, Diamonds, Gold, Custom, Repair, Watch).

## Lifecycle
Product: Idea -> Project -> Production -> Ready -> In stock -> Reserved -> Sold.
Repair lifecycle is separate and must not be forced into product lifecycle.

## Channels
- wix
- internal_catalog
- customer_selection
- social
- print

Publication state is tracked per channel against the canonical product.

## Synchronization rules
- Use stable external IDs for Wix/Ro App mapping.
- Never create a second product solely for another channel.
- Deletes are disabled by default.
- Financial, stock and accounting fields require explicit source-of-truth rules.
- Every mutation must be idempotent, auditable and verified.

## Photo structure
Each product may have: 01_main, 02_front, 03_back, 04_side, 05_detail, 06_on_model, 07_certificate. Additional technical/before/after assets are supported where relevant.

## Import gate
No bulk photo/product import is approved until the live Ro App/Wix schemas are mapped, backup/restore is verified, and a dry-run produces zero unexplained critical conflicts.
