# MARSEL — MASTER IMPLEMENTATION STATUS

Date: 2026-08-12
Status: ACTIVE / VERIFIED AGAINST REPOSITORY

## Rule
"Implemented" means different things. Every item is tracked separately as CODE, CONFIG, API, PRODUCTION and VERIFIED. Repository presence does not mean live Ro App deployment.

## Status legend
- CONFIRMED: directly evidenced in repository or execution artifact.
- PARTIAL: architecture/code exists, but live deployment or end-to-end verification is missing.
- BLOCKED: cannot be verified because required external access is unavailable.
- NOT CONFIRMED: no sufficient evidence found.

## MASTER MATRIX

| Area | CODE | CONFIG | API | PRODUCTION | VERIFIED | Current status |
|---|---|---|---|---|---|---|
| API/read-only audit | YES | YES | YES | NO WRITE | YES | CONFIRMED |
| Safety gates | YES | YES | N/A | YES | YES | CONFIRMED |
| Naming system | YES | YES | N/A | NO | YES | CONFIRMED |
| Master catalog model | YES | YES | NOT MAPPED | NO | STRUCTURE | PARTIAL |
| Brands | PARTIAL | PARTIAL | NOT VERIFIED | NO | NO | NOT CONFIRMED |
| Groups/subgroups | PARTIAL | PARTIAL | NOT VERIFIED | NO | NO | NOT CONFIRMED |
| Documents | YES MODEL | PARTIAL | NOT VERIFIED | NO | NO | PARTIAL |
| Warehouses | PARTIAL | PARTIAL | NOT VERIFIED | NO | NO | NOT CONFIRMED |
| Products | YES MODEL | PARTIAL | READ AUDIT EXISTS | NO | READ BLOCKED | PARTIAL/BLOCKED |
| Product photos | YES MODEL | YES MODEL | NOT VERIFIED | NO | NO | PARTIAL |
| 3D/model assets | ASSET MODEL | PARTIAL | NOT VERIFIED | NO | NO | PARTIAL |
| Metals | YES MODEL | PARTIAL | NOT VERIFIED | NO | NO | PARTIAL |
| Stones | YES MODEL | PARTIAL | NOT VERIFIED | NO | NO | PARTIAL |
| Metal cost accounting | MODEL ONLY | NO | NOT VERIFIED | NO | NO | NOT CONFIRMED |
| Stone cost accounting | MODEL ONLY | NO | NOT VERIFIED | NO | NO | NOT CONFIRMED |
| Production | PARTIAL | PARTIAL | NOT VERIFIED | NO | NO | NOT CONFIRMED |
| Jewelry repair | PARTIAL | PARTIAL | NOT VERIFIED | NO | NO | NOT CONFIRMED |
| Watch repair | PARTIAL | PARTIAL | NOT VERIFIED | NO | NO | NOT CONFIRMED |
| Sales/orders | YES | YES | GET /orders audited | NO WRITE | READ BLOCKED | PARTIAL/BLOCKED |
| Payments | PARTIAL | PARTIAL | NOT VERIFIED | NO | NO | NOT CONFIRMED |
| E-commerce/Wix channel | MODEL | MODEL | NOT VERIFIED | NO | NO | PARTIAL |
| Backup | CODE/PLAN | YES | NOT VERIFIED | NO | NO | BLOCKED/NOT CONFIRMED |
| Real synchronization | CODE/PLAN | YES | API access required | NO | NO | BLOCKED |
| Production writes | SAFETY BLOCK | SAFETY BLOCK | NOT VERIFIED | DISABLED | N/A | BLOCKED BY DESIGN |

## Confirmed catalog architecture
The catalog model defines a canonical `marsel_id`, SKU/article, product type, category/collection, metal and stone relations, stock, price/cost, lifecycle, assets and documents. Photos/documents are linked assets rather than duplicate products. 3D/model assets are represented by the `model` asset type. This is a design model, not proof of live Ro App configuration.

## Mandatory remaining implementation sequence
1. Verify current Ro App API access.
2. Map live schemas before any import.
3. Build/verify reference directories: brands, categories, groups, subgroups, materials, stones, warehouses, employees, documents.
4. Complete canonical product catalog mapping.
5. Complete photo + 3D asset mapping.
6. Define source-of-truth and formulas for metal/stone cost accounting.
7. Map production, jewelry repair and watch repair workflows.
8. Map payments and e-commerce channels.
9. Obtain/verify backup and restore procedure.
10. Run dry-run with zero unexplained critical conflicts.
11. Only then enable controlled writes.
12. Run post-write audit and reconciliation.

## Safety
No production DELETE, mass UPDATE or bulk import is authorized by this status file. The repository must not claim live implementation until the corresponding API operation and post-write verification are evidenced.
