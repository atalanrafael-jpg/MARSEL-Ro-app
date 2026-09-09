# MARSEL / Ro App — Active Script Registry

Дата контрольной ревизии: 2026-09-09
Ветка контроля: `main`

## 1. ACTIVE / CORE — фактически вызывается Unified Control Plane

| Роль | Файл | Статус |
|---|---|---|
| Structure self-check | `scripts/marsel_canonical_self_check.py` | ACTIVE |
| API inventory entrypoint | `scripts/marsel_api_inventory_v20_32.py` | ACTIVE |
| Data quality | `scripts/marsel_data_quality_v22_readonly.py` | ACTIVE |
| Entity audit | `scripts/marsel_entity_audit_v20_35.py` | ACTIVE |
| Product collision | `scripts/marsel_product_code_collision_audit_v22_3.py` | ACTIVE |
| Warehouse contract | `scripts/marsel_warehouse_contract_v20_48.py` | ACTIVE |

Источник истины для этого ACTIVE-набора: `.github/workflows/marsel-unified-control-plane.yml` на `main`.

## 2. REQUIRED INTERNAL DEPENDENCIES

Эти файлы не являются самостоятельными entrypoints Unified Control Plane, но обязательны для ACTIVE-кода:

- `scripts/marsel_api_inventory_v20_31.py` — импортируется напрямую из `marsel_api_inventory_v20_32.py`; содержит реализацию inventory.
- `scripts/marsel_api_inventory_v20_29.py` — используется как базовый модуль из `marsel_api_inventory_v20_31.py`.

Следовательно, `v20_29` и `v20_31` не являются кандидатами на архивирование до рефакторинга dependency chain.

## 3. BACKUP / EVIDENCE CONTROL DEPENDENCIES

`marsel-backup-evidence-producer.yml` — отдельный supporting control workflow. Он запускается после успешного `MARSEL Unified Control Plane` на `main`, принимает только canonical inventory artifact и выполняет исключительно READ-only export. Его текущие script dependencies:

- `scripts/marsel_full_readonly_backup_v1.py` — полный read-only export по документированным GET endpoint'ам.
- `scripts/marsel_backup_evidence_v1.py` — формирует provenance/evidence из завершённого export и не обращается к RO App.

Оба файла являются dependency-critical для backup/evidence контура и не могут быть архивированы или переименованы без отдельного dependency/test audit.

Важно: наличие workflow и кода не является доказательством актуального backup PASS. Production gate может считать backup доказанным только по текущему успешному запуску с authoritative evidence.

## 4. SUPPORT

- `scripts/marsel_api_v2_canonical_registry_v1.py` — API registry/evidence support.
- `scripts/marsel_api_v2_probe_v1.py` — read-only API probe support.
- `scripts/generate_drafts.py` — draft-generation support; не относится к live Ro App audit.

## 5. LEGACY / REVIEW CANDIDATES

Следующие файлы требуют отдельного dependency audit; их нельзя архивировать только по номеру версии:

- `scripts/marsel_entity_audit_v20_32.py`
- `scripts/marsel_data_contract_v20_26.py`
- `scripts/marsel_coverage_audit_v20_25.py`
- другие исторические варианты, не входящие в ACTIVE entrypoint set и не подтверждённые как internal dependencies.

## 6. Исправленные расхождения

- CORE inventory entrypoint: `v20_32`.
- `v20_31` и `v20_29` ранее были ошибочно отмечены как legacy candidates; фактическая import chain делает их REQUIRED INTERNAL DEPENDENCIES.
- CORE collision: `marsel_product_code_collision_audit_v22_3.py`.
- CORE warehouse: `scripts/marsel_warehouse_contract_v20_48.py`; внутреннее поле `version` — `20.48`.
- `v20_47` не является текущей активной реализацией и не должен указываться как CORE warehouse implementation.
- Старые warehouse-варианты не входят в ACTIVE execution set и сохраняются только как исторический след.

## 7. Правила

1. Workflow является источником истины для фактического ACTIVE execution set.
2. Import/dependency graph является источником истины для REQUIRED INTERNAL DEPENDENCIES.
3. Более новая версия не заменяет старую автоматически; замена фиксируется только после проверки фактической реализации и зависимостей.
4. Архивирование = перенос только после dependency audit и проверки test discovery.
5. История Git/GitHub Actions сохраняется.
6. После любого изменения ACTIVE execution set или dependency chain требуется новый Unified Control Plane run.
7. Production WRITE остаётся отключённым до прохождения всех обязательных gates с прямым evidence.
