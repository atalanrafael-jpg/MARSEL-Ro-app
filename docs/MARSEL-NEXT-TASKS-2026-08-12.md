# MARSEL — параллельный контур работ

Дата: 2026-08-12

## Цель

Продолжать развитие проекта, пока live API RO App недоступен из-за `403 subscription expired`, не выдавая непроверенные данные за фактическое состояние production.

## Разрешённые работы без live API

1. Поддерживать READ-ONLY API-клиент и запрет mutation-методов.
2. Улучшать диагностику `401/403/404/405/429/5xx`.
3. Проверять код статически и добавлять offline regression tests.
4. Поддерживать API verification ledger без неподтверждённых response fields.
5. Подготавливать схемы аудита products/services/orders.
6. Подготавливать безопасный CHANGESET-контур без APPLY.
7. Проверять секреты: ключи не должны попадать в исходники, README и артефакты.
8. Готовить документацию и чек-листы внедрения.

## Заблокированные работы

Пока live API возвращает `403 subscription expired`, нельзя подтвердить:

- полный production backup;
- актуальные количества и состав сущностей;
- текущие дубли и ошибки данных;
- реальные права конкретного API key;
- production mutations;
- post-change audit.

## Gate после восстановления подписки

`API ACCESS → FULL READ INVENTORY → BACKUP/HASH → DATA QUALITY → FINDINGS → DRY-RUN CHANGESET → отдельное разрешение APPLY → POST-AUDIT`.

## Правило

Никаких автоматических удалений, слияний, массовых исправлений или изменения production до прохождения всех gates.
