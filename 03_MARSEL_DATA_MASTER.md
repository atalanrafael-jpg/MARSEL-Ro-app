# 03_MARSEL_DATA_MASTER

**Purpose:** canonical data layer: registry, dictionary, quality, warehouse and cost accounting.

## 1. Master registry
Every entity must have:
`entity_type / source / live_id / external_id / code / name / status / created_at / updated_at / relation_keys / evidence / verified_at`

Never invent IDs, codes, relations or statuses.

Target entity families:
- company / branch / employee / role
- customer / contact / segment
- order / order item / repair / production task
- product / service / category / brand
- metal / stone / component / spare part / consumable
- warehouse / location / stock / movement
- payment / income / expense / cost
- document / communication / warranty

## 2. Data dictionary rules
For each field record:
`name / type / required / nullable / enum / relation / source / validation / example / status`

Field status:
- VERIFIED LIVE
- VERIFIED DOCUMENTATION
- PROJECT CONFIGURATION
- BUSINESS REQUIREMENT
- PROPOSED
- UNVERIFIED

A project template is never treated as a live ROAPP schema without evidence.

## 3. Data quality
Checks:
- IDs present and unique
- duplicate codes/names assessed
- required fields
- valid relations
- orphan records
- invalid statuses
- invalid types/formats
- inconsistent quantities/prices
- pagination completeness
- reconciliation against source totals

Error taxonomy:
FACTUAL / DUPLICATE / MISSING DATA / INVALID RELATION / CLASSIFICATION / CONFIGURATION / API / SECURITY / INTEGRATION / PERFORMANCE / LEGAL-TAX / UNVERIFIED.

## 4. Current verified audit evidence
Historical READ-ONLY evidence in project records includes:
- 4,373 orders audited with 4,373 unique IDs and zero duplicate IDs in that run;
- zero missing order IDs, client IDs and statuses in that run;
- 6,820 successful detail requests with zero detail failures in V20.8;
- later Unified Control Plane audit documented 1,721 products, 728 services and 4,397 orders with `ACCESS_FAILURE=0`, `HARD_ISSUE=0`, `WRITE=0` for that specific run.

These are dated audit snapshots, not an assertion of today's live totals unless a new live run confirms them.

## 5. Collision policy
The project has documented **11 product-code collision groups** in a prior audit.
- Do not auto-delete.
- Compare IDs, codes, names, relations, history and usage.
- Classify each group.
- Propose merge/rename/archive only after evidence and backup.

## 6. Warehouse model
`Warehouse -> Zone/Cell (if supported) -> Product -> Stock -> Movement -> Order -> Write-off/Transfer/Sale`

Warehouse API contract: **NOT VERIFIED** at the current control point. Do not create official warehouse IDs from names or guesses.

## 7. Cost accounting
`COST = METAL + STONES + COMPONENTS + LABOR + OTHER DIRECT COSTS`

Track separately when source data exists:
- fineness
- mass
- metal unit cost/value
- stone type and characteristics
- stone cost
- labor
- direct additional costs

No factual cost is calculated from missing source values.

## 8. Reconciliation
For imports/synchronization:
`SOURCE -> MAPPING -> TRANSFORMATION -> VALIDATION -> DESTINATION -> RECONCILIATION -> VERIFY`

Every material data movement needs counts before/after, error list and reconciliation evidence.