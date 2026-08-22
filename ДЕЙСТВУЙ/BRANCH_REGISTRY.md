# Реестр веток и контроль источников

## Каноническая рабочая ветка

`act/marsel-unified-system-2026-08-22`

## Главная ветка

`main` остаётся базовой веткой репозитория. Она не используется как рабочая ветка для дальнейшей консолидации до завершения нового CI.

## Обнаруженные исторические ветки

В репозитории обнаружены многочисленные ветки, в том числе:

- `fix/issue-42-warehouse-contract`
- `fix/unified-issues-19-25-27-30-31-35-42`
- `fix/pr40-sync-2026-08-22`
- `backup/pr40-before-sync-2026-08-22`
- `backup/pr40-conflict-fix-2026-08-22`
- `ops/run-warehouse-contract-2026-08-18`
- `ops/warehouse-contract-verification-2026-08-18`
- `audit/raw-read-integrity`
- `audit/v21-readonly-integrity`
- `audit-v6-readonly`
- `audit-v6-readonly-final`
- `audit-v6-readonly-final2`
- `audit-v6-readonly-final3`
- `audit-v6-readonly-final4`
- `feat/roapp-readonly-audit`
- `feat/marsel-roapp-api-hardening-v23`
- `codex/marsel-api-v2-readonly-preflight`
- `chore/marsel-system-consolidation-2026-08-21`
- `chore/marsel-unified-structure-2026-08-21`

Полный список был получен из GitHub branch inventory 2026-08-22.

## Политика

Исторические ветки не являются рабочим источником данных. Не следует автоматически сливать их содержимое в новую систему. Перед переносом каждого артефакта требуется проверить:

1. происхождение;
2. дату и commit;
3. соответствие текущему API-контракту;
4. наличие дубликатов;
5. наличие подтверждающего CI;
6. отсутствие конфликта с текущей канонической реализацией.

Удаление исторических веток не выполняется на этом этапе, поскольку это необратимое изменение истории и не требуется для канонизации рабочего дерева.
