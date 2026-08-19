# MARSEL ROAPP

Единая система ювелирной студии MARSEL: бизнес-контур MARSEL и технологический контур ROAPP находятся в одном исходном и операционном проекте.

## Canonical architecture

- MARSEL — бизнес и операционные процессы.
- ROAPP — API, данные, интеграции, автоматизация и контроль.
- GitHub repository: `atalanrafael-jpg/Ro-app`.
- Default branch: `main`.
- Canonical control plane: `.github/workflows/marsel-unified-control-plane.yml`.

## Safety

Все production data mutations запрещены до прохождения полного production gate: backup/restore, reconciliation, READ-ONLY inventory, duplicate/orphan/reference analysis, dry-run, idempotency, rollback и post-write verification.

## Current state

CI и READ-ONLY audit контур продолжают проверку API, качества данных, сущностей, product-code collisions и warehouse contract. Неподтверждённые внешние зависимости не считаются выполненными.

Подробная архитектура и контрольные правила: `MARSEL_ROAPP_UNIFIED_SYSTEM.md`.
