# MARSEL — MASTER IMPLEMENTATION STATUS

Date: 2026-08-13
Status: ACTIVE / OFFLINE IMPLEMENTATION CONTINUING

## Verified facts

- Production RO App writes remain disabled by design.
- The latest available comprehensive audit evidence shows RO App API access blocked with HTTP 403 and an expired-subscription message; live products/services/orders therefore remain unverified.
- Production backup/restore remains unverified.
- Offline implementation is permitted: schemas, validators, fixtures, tests and documentation.

## Completed in this phase

### Master directories V1
Added:
- `config/marsel_master_directories_v1.json`
- `scripts/marsel_master_directories_v1_validate.py`
- `.github/workflows/marsel-master-directories-v1.yml`

The offline dataset contains stable IDs and Russian display names for:
- warehouses;
- warehouse zones;
- metals/fineness reference;
- product types;
- payment methods;
- publication channels.

The dataset is explicitly marked `OFFLINE_MASTER_DATA_ONLY` and `production_import_allowed=false`.

### Quality gate
The validator checks:
- JSON validity;
- schema/status safety flags;
- required record fields;
- non-empty stable IDs;
- duplicate IDs inside and across directories;
- non-empty Russian display names.

The GitHub Actions workflow is configured to validate changes to the dataset, validator and workflow.

## Current implementation matrix

| Area | Offline code/config | Live API | Production | Status |
|---|---|---|---|---|
| API/read-only audit | YES | BLOCKED | NO WRITE | CONFIRMED |
| Safety gates | YES | N/A | DISABLED WRITES | CONFIRMED |
| Master catalog model | YES | NOT MAPPED | NO | PARTIAL |
| Master directories | YES | NOT VERIFIED | NO IMPORT | PARTIAL / READY FOR MAPPING |
| Metals reference | YES | NOT VERIFIED | NO | PARTIAL |
| Warehouses/zones | YES | NOT VERIFIED | NO | PARTIAL |
| Payments | YES | NOT VERIFIED | NO | PARTIAL |
| Products | YES | READ BLOCKED | NO | BLOCKED |
| Orders | YES | READ BLOCKED | NO WRITE | BLOCKED |
| Repairs | MODEL/PARTIAL | NOT VERIFIED | NO | PARTIAL |
| Production | MODEL/PARTIAL | NOT VERIFIED | NO | PARTIAL |
| Cost accounting | MODEL | NOT VERIFIED | NO | NOT CONFIRMED |
| Photos/3D | MODEL | NOT VERIFIED | NO | PARTIAL |
| Backup/restore | PLAN/CODE | NOT VERIFIED | NO | BLOCKED |
| Synchronization | PLAN/CODE | BLOCKED | NO | BLOCKED |

## Next execution sequence

1. Complete offline reference-directory schemas for brands, categories, groups, subgroups, stones, employees and document types.
2. Add canonical product fixture schema and duplicate/reference integrity validator.
3. Add repair/production workflow fixtures and transition validator.
4. Add metal/stone costing calculation contract without inventing prices or production formulas.
5. Add asset/3D governance validator.
6. Harden the API access diagnostic to distinguish authentication, subscription, permissions and endpoint failures.
7. When RO App access is restored: verify live schemas, backup/restore, then dry-run only.
8. Production writes remain prohibited until all mandatory gates pass.

## Final-point criteria

The project is not considered production-ready until all of the following are evidenced:

- live API access verified;
- live schemas mapped;
- verified backup and restore;
- read-only audit passes;
- canonical IDs and references pass;
- duplicate report reviewed;
- dry-run has zero unexplained critical conflicts;
- controlled write scope explicitly defined;
- post-write reconciliation passes.
