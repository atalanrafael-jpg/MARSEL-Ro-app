# MARSEL API / Audit Registry

## Purpose
Единый реестр текущих диагностических и audit-скриптов RO APP. Документ предотвращает размножение параллельных MASTER-версий и фиксирует, какой слой проверки за что отвечает.

## Current script families detected in `scripts/`
| Script | Role | Status |
|---|---|---|
| `marsel_api_access_diagnostics_v20_21.py` | API access diagnostics | ACTIVE / VERIFY BY RUN |
| `marsel_api_endpoint_diagnostics_v20_17.py` | endpoint diagnostics | LEGACY / COMPARE |
| `marsel_api_endpoint_diagnostics_v20_18.py` | expanded endpoint diagnostics | LEGACY / COMPARE |
| `marsel_api_inventory_v20_14.py` | initial API inventory | LEGACY |
| `marsel_api_inventory_v20_22.py` | API inventory generation | LEGACY / COMPARE |
| `marsel_api_inventory_v20_23.py` | read-only inventory used by Integrity | ACTIVE |
| `marsel_api_inventory_v20_28.py` | later inventory revision | VERIFY |
| `marsel_api_inventory_v20_29.py` | later inventory revision | VERIFY |
| `marsel_api_inventory_v20_30.py` | later inventory revision | VERIFY |
| `marsel_api_inventory_v20_31.py` | later inventory revision | VERIFY |
| `marsel_audit_v20_10.py` | data audit | VERIFY |

## Rules
1. A higher version number is not automatically the canonical implementation.
2. Canonical status requires a successful scheduled run and Evidence.
3. Do not delete older scripts until behavior has been compared and the active workflow no longer depends on them.
4. Production data remains READ-ONLY for automated audits.
5. Any future write workflow requires backup, dry-run, explicit authorization and a separate safety gate.

## Current verified automation
- Integrity Consolidation run `31821582025`: SUCCESS.
- Evidence artifact: `marsel-v20-24-integrity-evidence`.
- Artifact SHA-256: `3354d975b8b6bd0e4d093fbcdae5e60009c776cf48209aafef2d6191d01fad1d`.

## Next maintenance task
Compare the `v20_23`, `v20_28`, `v20_29`, `v20_30`, and `v20_31` inventory implementations and designate one canonical implementation based on actual workflow usage and test evidence. Until then, keep all candidates read-only and do not delete them.
