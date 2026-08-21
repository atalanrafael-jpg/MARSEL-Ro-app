# MARSEL / Ro App — Active Script Registry

Дата контрольной ревизии: 2026-08-21
Ветка: `main`

## 1. ACTIVE / CORE — фактически вызывается Unified Control Plane

| Роль | Файл | Статус |
|---|---|---|
| Structure self-check | `scripts/marsel_canonical_self_check.py` | ACTIVE |
| API inventory | `scripts/marsel_api_inventory_v20_32.py` | ACTIVE |
| Data quality | `scripts/marsel_data_quality_v22_readonly.py` | ACTIVE |
| Entity audit | `scripts/marsel_entity_audit_v20_35.py` | ACTIVE |
| Product collision | `scripts/marsel_product_code_collision_audit_v22_1.py` | ACTIVE |
| Warehouse contract | `scripts/marsel_warehouse_contract_v20_45.py` | ACTIVE |

Источник истины для ACTIVE-набора: `.github/workflows/marsel-unified-control-plane.yml` на `main`.

## 2. SUPPORT

- `scripts/marsel_api_v2_canonical_registry_v1.py` — API registry/evidence support.
- `scripts/marsel_api_v2_probe_v1.py` — read-only API probe support.
- `scripts/generate_drafts.py` — draft-generation support; не относится к live Ro App audit.

## 3. LEGACY / REVIEW CANDIDATES

Следующие файлы обнаружены в репозитории, но не являются самостоятельными active entrypoints Unified Control Plane:

- `scripts/marsel_api_inventory_v20_29.py`
- `scripts/marsel_api_inventory_v20_31.py`
- `scripts/marsel_entity_audit_v20_32.py`
- `scripts/marsel_data_contract_v20_26.py`
- `scripts/marsel_coverage_audit_v20_25.py`
- другие исторические V20.x/V21.x/V22.x варианты.

Их нельзя переносить в `старые данные/` только по номеру версии. Сначала проверяются все references/imports/workflow/test/docs dependencies.

## 4. Исправленные расхождения

- CORE inventory: фактически `v20_32`, не `v20_31`.
- CORE collision: фактически `marsel_product_code_collision_audit_v22_1.py`.
- CORE warehouse: фактически `marsel_warehouse_contract_v20_45.py`; внутреннее поле `version` также `20.45`.
- Версия `20.48` не подтверждена и больше не используется как активная версия.
- Старый путь `scripts/marsel_warehouse_contract_v20_36.py` выведен из ACTIVE и сохранён в `старые данные/` как исторический след.

## 5. Правила

1. Workflow является источником истины для фактического ACTIVE execution set.
2. Более новая версия не заменяет старую автоматически.
3. Архивирование = перенос после dependency audit, а не потеря исторических данных.
4. История Git/GitHub Actions сохраняется.
5. После любого изменения ACTIVE execution set требуется новый Unified Control Plane run.
