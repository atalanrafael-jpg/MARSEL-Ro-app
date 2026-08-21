# MARSEL / Ro App — Active Script Registry

Дата проверки: 2026-08-21

## Назначение

Этот реестр отделяет подтверждённо используемые скрипты от исторических версий и кандидатов на архивирование. Реестр не является разрешением на удаление файлов.

## ACTIVE / CORE

### Unified Control Plane
Используются активным контрольным контуром:
- `marsel_canonical_self_check.py`
- `marsel_api_inventory_v20_29.py`
- `marsel_data_quality_v22_readonly.py`
- `marsel_entity_audit_v20_35.py`
- `marsel_product_collision_v20_36.py`
- `marsel_warehouse_contract_v20_36.py`

### API registry and probe support
- `marsel_api_v2_canonical_registry_v1.py`
- `marsel_api_v2_probe_v1.py`

### Support
- `generate_drafts.py`

## REVIEW / LEGACY CANDIDATES

Файлы с более ранними версиями, не включённые в текущий Unified Control Plane, нельзя удалять автоматически. До переноса в `старые данные/` требуется подтвердить отсутствие ссылок из workflows, тестов, документации и runtime-кода.

Примеры обнаруженных исторических линий:
- `marsel_api_inventory_v20_31.py`
- `marsel_api_inventory_v20_32.py`
- `marsel_entity_audit_v20_32.py`
- более ранние V20.x contract/coverage/catalog scripts

## Правила

1. Активный workflow должен ссылаться только на файлы из ACTIVE или на явно документированную поддержку.
2. Более новая версия файла не считается автоматически заменой старой без проверки интерфейса и зависимостей.
3. Архивирование выполняется перемещением после проверки, а не удалением.
4. История Git и GitHub Actions остаётся сохранённой независимо от расположения файлов.
5. Любое изменение ACTIVE-набора требует повторной проверки CI.
