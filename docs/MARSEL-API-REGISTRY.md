# MARSEL API / Audit Registry

## Purpose
Единый реестр текущих диагностических и audit-скриптов RO APP. Реестр предотвращает размножение параллельных MASTER-версий.

## Canonical architecture
| Layer | Canonical implementation | Reason |
|---|---|---|
| API inventory | `marsel_api_inventory_v20_31.py` | strict GET-only contract, multi-index discovery, explicit safety gate and SHA-256 evidence workflow |
| Live probe | `marsel_live_probe_v20_27.py` | GET-only probe against a generated inventory with zero-write and HTTP integrity checks |
| Integrity consolidation | `marsel-readonly-integrity-v21.yml` / Integrity workflow | independent consolidation and zero-write safety gate |
| Health registry | `marsel-automation-health-registry.yml` | collects automation state and evidence without changing RO APP |

## Script families
| Script | Role | Status |
|---|---|---|
| `marsel_api_access_diagnostics_v20_21.py` | API access diagnostics | ACTIVE / diagnostic |
| `marsel_api_endpoint_diagnostics_v20_17.py` | endpoint diagnostics | LEGACY |
| `marsel_api_endpoint_diagnostics_v20_18.py` | expanded endpoint diagnostics | LEGACY |
| `marsel_api_inventory_v20_14.py` | initial inventory | LEGACY |
| `marsel_api_inventory_v20_22.py` | inventory generation | LEGACY |
| `marsel_api_inventory_v20_23.py` | inventory used by older Integrity path | LEGACY / retained for compatibility |
| `marsel_api_inventory_v20_28.py` | intermediate inventory | LEGACY / retained for comparison |
| `marsel_api_inventory_v20_29.py` | multi-index inventory + live-probe input | RETAINED: live-probe compatibility |
| `marsel_api_inventory_v20_30.py` | intermediate inventory | LEGACY |
| `marsel_api_inventory_v20_31.py` | strict inventory | CANONICAL |
| `marsel_audit_v20_10.py` | data audit | ACTIVE / VERIFY BY RUN |

## Workflow cleanup
The duplicate `.github/workflows/marsel-api-v20-30-readonly.yml` workflow was removed because it duplicated the V20.31 implementation. Commit: `f23f223016fb5b1385fa1b07844509f9792eb9aa`.

## Safety rules
1. Version number alone does not establish correctness.
2. Canonical status requires workflow usage plus Evidence.
3. Automated production audits remain READ-ONLY.
4. Do not delete scripts still referenced by an active workflow.
5. Future write operations require backup, dry-run, explicit authorization and a separate safety gate.

## Verified evidence
Integrity Consolidation run `31821582025` completed SUCCESS with artifact `marsel-v20-24-integrity-evidence` and SHA-256 `3354d975b8b6bd0e4d093fbcdae5e60009c776cf48209aafef2d6191d01fad1d`.

## Backup controller
Full read-only backup controller `.github/workflows/marsel-full-readonly-backup-v1.yml` is configured for push, manual dispatch, and daily schedule. A successful run with `complete=true`, `failed_endpoints=0`, and zero-write invariants is required before the backup stage can be marked PASS.
