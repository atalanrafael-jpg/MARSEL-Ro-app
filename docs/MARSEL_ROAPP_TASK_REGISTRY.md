# MARSEL ROAPP — ЕДИНЫЙ РЕЕСТР ЗАДАЧ

Дата контрольной точки: 2026-08-19

## Правило

MARSEL и ROAPP — один проект. Issue, PR, workflow, документация и код относятся к единому MARSEL ROAPP control plane.

Статусы не меняются на `DONE` без прямого evidence.

## Реестр

| ID | Контур | Статус | Следующее действие |
|---|---|---|---|
| #19 | Production go-live | BLOCKED | backup → restore → reconciliation → dry-run → idempotency → rollback → post-write verification |
| #25 | Automation Health | REVIEW_REQUIRED | закрыть API completeness и evidence |
| #27 | Gmail OAuth | REVIEW_REQUIRED | persistent encrypted token store + live read-only OAuth test |
| #30 | API/entity coverage | REVIEW_REQUIRED | подтвердить оставшиеся entities без угадывания ID |
| #31 | Control Protocol | CONSOLIDATED | правила перенесены в canonical control plane |
| #35 | Product-code collisions | REVIEW_REQUIRED | классифицировать 11 групп; не удалять автоматически |
| Warehouse | Warehouse API | NOT_VERIFIED | получить официальный контракт или зафиксировать отсутствие публичного endpoint |
| MCP | ChatGPT/Codex MCP | BUILD VERIFIED / AUTH PENDING | пройти реальную authorization verification |
| Ads CAPI | OpenAI Ads | CODE CONSOLIDATED | main содержит hardened implementation; реальное подключение требует Ads Manager credentials и order boundary |

## Закрытые дубли PR

- PR #32 — закрыт как устаревшая/дублирующая реализация Ads CAPI.
- PR #36 — закрыт после переноса актуальной реализации в `main`.
- PR #37 — закрыт как superseded: canonical unified workflow уже находится в `main`.

PR #28 Gmail остаётся открытым draft до production hardening и live verification.

## Production gate

`WRITE=0` является обязательным до полного прохождения всех safety gates. Наличие кода, документации или успешного CI не является доказательством production readiness.

## Конечная цель

После прохождения технических gate система должна перейти от audit-only к управляемому ERP-контру MARSEL: клиенты → заказы → производство/ремонт → материалы → склад → себестоимость → оплаты → аналитика → автоматизация → повторные продажи.
