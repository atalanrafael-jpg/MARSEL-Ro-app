# MARSEL / RO App — Master Status

Дата: 2026-08-13

## Подтверждено

- Репозиторий: `atalanrafael-jpg/Ro-app`.
- Основная ветка: `main`.
- GitHub Actions получает `ROAPP_API_KEY` из Actions Secret; секрет не хранится в исходном коде.
- Read-only аудит использует только `GET`.
- Последний проверенный comprehensive audit: run `31567679013`, job `94022798298`.
- `WRITE_REQUESTS_MADE=0`.
- `RO_APP_DATA_MUTATED=False`.
- Artifact создан: `marsel-v22-comprehensive-data-quality-readonly`, artifact ID `9130070599`.

## Текущий блокер

Последний реальный запрос к RO App API вернул HTTP 403 для `products`, `services` и `orders`.

Причина, возвращённая API:
`Your subscription has expired. Please renew your license to continue.`

Поэтому текущий DATA QUALITY gate заблокирован именно доступом RO App.

## Не считать выполненным до повторного успешного API-аудита

- актуальный полный аудит products/services/orders;
- актуальная проверка клиентов, складов и связанных справочников;
- backup рабочей базы через фактически доступные API-объекты;
- dry-run исправлений на актуальных данных;
- любые операции записи в RO App;
- массовая синхронизация;
- Webhooks;
- Wix/каталог;
- финальный post-deployment audit.

## Правило безопасности

До восстановления доступа RO App запрещены массовые изменения рабочей базы. После восстановления сначала выполняется READ-ONLY повторная проверка, затем backup и dry-run; запись допускается только после отдельной верификации конкретного endpoint и payload.
