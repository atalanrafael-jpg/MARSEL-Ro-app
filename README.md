# MARSEL ROAPP

**MARSEL ROAPP** — единая система для Ювелирной студии MARSEL.

MARSEL и ROAPP в этом проекте **не являются двумя отдельными системами**:

- **MARSEL** — бизнес-контур системы.
- **ROAPP** — API/интеграционный и операционный технологический контур.
- `Ro-app` — текущее техническое имя единого GitHub-репозитория.

Архитектурное решение зафиксировано в [`MARSEL_ROAPP_UNIFIED_SYSTEM.md`](./MARSEL_ROAPP_UNIFIED_SYSTEM.md).

## Единая система

```text
MARSEL ROAPP
├── Business Core
│   ├── Клиенты
│   ├── Заказы
│   ├── Изделия
│   ├── Ремонт ювелирных изделий
│   ├── Ремонт часов
│   ├── Производство
│   ├── Продажи
│   ├── Склад
│   ├── Металлы и камни
│   ├── Услуги
│   └── Финансы
├── ROAPP Integration Core
│   ├── API contracts
│   ├── Data quality
│   ├── Synchronization
│   └── Diagnostics
├── Commerce
├── Web / iOS
├── AI / Automation
└── CI / Security / Observability
```

## Правила

1. Один проект, одна архитектура и единая модель данных.
2. Не создавать параллельные источники истины без документированной причины.
3. Не угадывать API endpoints, поля и идентификаторы.
4. Read-only проверки не должны изменять production data.
5. Production WRITE остаётся заблокированным до прохождения go-live gates.
6. Синхронизация допускается только при наличии проверяемых mapping, idempotency, reconciliation, rollback и post-write verification.
7. Ошибки и дубликаты контролируются централизованно.

## API / CI

Текущая CI-архитектура сохраняет принцип доказательного read-only аудита. Production mutation flows не включаются только на основании предположений о контракте API.

PR #37 (`ci: run MARSEL warehouse contract verification`) относится к **единому проекту MARSEL ROAPP**, а не к отдельному warehouse-проекту.

## Безопасность

- API-ключи хранятся в GitHub Actions Secrets.
- Аудит не должен раскрывать PII.
- Не подтверждённые API paths не используются для live-вызовов.

## Техническое имя

GitHub-репозиторий: `atalanrafael-jpg/Ro-app`.

Каноническое имя продукта/системы: **MARSEL ROAPP**.

Переименование самого GitHub-репозитория не выполнялось этим изменением и не считается выполненным без фактического подтверждения GitHub.
