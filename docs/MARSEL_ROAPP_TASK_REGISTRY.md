# MARSEL ROAPP — ЕДИНЫЙ РЕЕСТР ЗАДАЧ

Дата контрольной точки: 2026-08-31

## Правило

MARSEL и ROAPP — один проект. Issue, PR, workflow, документация и код относятся к единому MARSEL ROAPP control plane.

Статус `DONE` допускается только при прямом evidence. Старые CI-запуски и исторические документы не закрывают текущие задачи.

## Текущий подтверждённый реестр

| ID | Контур | Статус | Следующее действие |
|---|---|---|---|
| #19 | Production go-live | BLOCKED / NOT READY | собрать 8 обязательных production evidence; WRITE остаётся 0 |
| #91 | GitHub account/security controls | OPEN / MANUAL | исправить target ruleset, secret scanning/push protection, production environment и Copilot controls через GitHub account UI/API |
| PR #89 | Limits-resilient execution worker | OPEN / DRAFT / MERGEABLE | пройти review и текущий CI; затем снять Draft и merge только после проверки |
| Warehouse | Warehouse API | NOT VERIFIED | получить прямое доказательство официального GET-контракта |
| MCP | ChatGPT/Codex MCP | AUTH PENDING | выполнить реальную authorization verification |
| Credentials | ROAPP API key | SECURITY GATE | подтвердить rotation/history scan при подозрении или подтверждённом exposure |
| Gmail OAuth | Live read-only OAuth | NOT VERIFIED | выполнить реальный OAuth smoke test |
| Evidence | Production evidence bundle | 1/8 | отсутствуют backup, restore, reconciliation, duplicate/reference, dry-run, idempotency, rollback evidence |

## Что уже подтверждено

- Базовый repository CI на последнем проверенном запуске проходит.
- Production WRITE не включён.
- Execution Worker спроектирован как read-only/fail-closed и не получает production secrets.
- Production Evidence Orchestrator корректно блокирует gate при неполном evidence.
- Security issue, ранее ошибочно закрытая при состоянии NOT READY, была возвращена в OPEN.

## Текущие ограничения

Следующие действия нельзя честно выполнить только repository file/API connector:

- изменить account-level GitHub ruleset configuration;
- создать/защитить GitHub production environment;
- подтвердить account-level secret scanning/push protection;
- подтвердить Copilot account controls;
- выполнить пользовательский Gmail OAuth;
- выполнить пользовательскую RO App MCP authorization;
- создать реальные backup/restore/rollback доказательства без доступа к соответствующим production systems.

Никакие фиктивные evidence, credentials, OAuth tokens или production WRITE операции не создаются.

## Linear

В доступном Linear workspace не обнаружены проекты. Обнаружены только стандартные onboarding issues `RAF-1`–`RAF-4` (знакомство с Linear, команды, импорт данных, подключение инструментов). Они не являются подтверждёнными задачами MARSEL ROAPP и не закрываются автоматически без фактического выполнения соответствующих workspace-операций.

## Production gate

`WRITE=0` является обязательным до полного прохождения safety gates. Наличие кода, документации, CI или PR не является доказательством production readiness.

## Конечная цель

После прохождения технических gate система должна перейти от audit-only к управляемому ERP-контру MARSEL: клиенты → заказы → производство/ремонт → материалы → склад → себестоимость → оплаты → аналитика → автоматизация → повторные продажи.
