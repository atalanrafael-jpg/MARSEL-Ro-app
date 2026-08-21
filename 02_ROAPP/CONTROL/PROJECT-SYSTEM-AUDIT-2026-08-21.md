# MARSEL / Ro App — Глубокая системная ревизия

Дата: 2026-08-21
Ветка: `main`

## Цель

Проверять проект как единую систему, а не как набор отдельных файлов и веток. Каждое изменение должно проходить через последовательность: обнаружение → классификация → dependency check → исправление → CI → повторная проверка → фиксация контрольной точки.

## Этапы полной ревизии

### Этап 1 — Repository topology

Проверяются:
- branches;
- active workflows;
- scripts;
- app/runtime;
- tests;
- docs/contracts;
- configuration;
- archive zone.

### Этап 2 — Execution truth

Источником истины для того, что реально запускается, является текущий `.github/workflows/marsel-unified-control-plane.yml` на `main`, а не старые документы или номера версий файлов.

На контрольную дату workflow фактически вызывает:
- `marsel_canonical_self_check.py`
- `marsel_api_inventory_v20_32.py`
- `marsel_data_quality_v22_readonly.py`
- `marsel_entity_audit_v20_35.py`
- `marsel_product_code_collision_audit_v22_1.py`
- `marsel_warehouse_contract_v20_36.py`

### Этап 3 — Documentation consistency

Обнаружено расхождение между старой canonical-структурой и фактическим workflow:
- документ ссылался на inventory `v20_31`, а workflow запускает `v20_32`;
- документ не отражал warehouse audit;
- script registry содержал ошибочное имя collision script;
- warehouse ранее был ошибочно описан как `20.48`.

Исправлено:
- canonical structure commit `2c2bcb161ee812f496dcd2db14e0a1efc704728a`;
- active script registry commit `a8f8bb9bedc7cb4cc7b4cf27ac4869640b70b4a1`.

### Этап 4 — Version integrity

Номер в имени файла и внутреннее поле `version` проверяются отдельно.

Для warehouse сейчас подтверждено:
- filename: `marsel_warehouse_contract_v20_36.py`;
- internal version: `20.45`.

`20.48` НЕ считается подтверждённой версией.

### Этап 5 — Dependency-safe archival

Архивация допускается только после проверки:
- workflow references;
- Python imports/subprocess calls;
- test references;
- documentation references;
- runtime references.

До завершения этого этапа старые скрипты не удаляются и не переносятся массово.

### Этап 6 — Security and safety

Обязательные invariants:
- live Ro App audit = READ ONLY;
- WRITE_REQUESTS_MADE = 0;
- RO_APP_DATA_MUTATED = false;
- no guessed IDs;
- secrets only from GitHub Secrets;
- incomplete evidence cannot become PASS.

`generate-drafts.yml` рассматривается отдельно, поскольку содержит `issues: write` и не является READ-ONLY live-audit.

### Этап 7 — CI proof

После каждого изменения active execution set требуется новый Unified Control Plane run на текущем `main`.

Старый успешный run не считается доказательством текущего состояния.

## Контрольная точка

Система сейчас находится в состоянии:

`REVIEW_REQUIRED`

Причины, которые нельзя скрывать:
1. Warehouse contract ещё требует фактического live подтверждения documented GET contract.
2. Warehouse filename/internal version не нормализованы и намеренно не объявляются как `20.48`.
3. Legacy dependency audit ещё не завершён, поэтому старые файлы не архивируются автоматически.

## Правило дальнейшей работы

Не возвращаться к уже проверенным этапам без появления новой фактической информации. Каждая новая ревизия начинается с последней подтверждённой контрольной точки и проверяет только изменившиеся или ещё не подтверждённые области.
