# MARSEL — MASTER PROJECT PLAN

## 1. Назначение
Единый проект для управления ювелирной студией MARSEL и технологическим контуром ROAPP: операции, каталог, производство, ремонт, часы, склад, продажи, e-commerce, аналитика, автоматизация и контроль качества.

## 2. Системные цели
- Единый источник истины для структуры проекта.
- Разделение ACTIVE и исторических данных.
- READ-ONLY по умолчанию для диагностик.
- Любые production-изменения только после backup/restore, reconciliation, dry-run, idempotency, rollback и post-write verification.
- Полная трассируемость: задача → изменение → тест → CI → evidence.
- Никаких неподтверждённых PASS, API-контрактов, доступов или бизнес-показателей.

## 3. Canonical architecture
- `main` — единственная production-canonical ветка.
- `scripts/` — активные исполняемые контрольные модули.
- `tests/` — автоматические проверки.
- `.github/workflows/` — CI/CD и контроль.
- `docs/` — нормативная документация, инструкции, бизнес-модель и реестры.
- `старые данные/` — исторические версии и архив; не удалять без отдельного решения.
- `.env`, API keys и secrets — никогда не хранить в Git.

## 4. Control gates
1. Repository integrity.
2. Dependency graph.
3. Test discovery and coverage.
4. CI PASS.
5. READ-ONLY API evidence.
6. Data quality.
7. Entity/reference integrity.
8. Product-code collision review.
9. Warehouse contract verification.
10. Backup/restore and reconciliation before any write operation.

## 5. Definition of Done
Задача считается выполненной только если изменение существует в GitHub, имеет проверяемый результат, тесты проходят, артефакты CI сохранены, зависимости не нарушены, документация обновлена и статус подтверждён фактическими данными.

## 6. Business scope
MARSEL: изготовление и продажа ювелирных изделий, ремонт ювелирных изделий, ремонт часов; одна точка, три сотрудника; учёт себестоимости по металлам и камням; планируемый интернет-магазин; несколько способов оплаты.

## 7. Automation priorities
- заказ → клиент → изделие → материалы → себестоимость → склад → производство/ремонт → готовность → продажа → аналитика;
- автоматическая сверка остатков и заказов после подтверждения API-контрактов;
- контроль дублей, orphan/reference errors и кодов изделий;
- ежедневные/плановые read-only audits;
- CI evidence artifacts при любом результате тестов.

## 8. Current policy
Не архивировать файл только по номеру версии. Сначала проверить все imports, workflow references, pytest discovery и runtime dependencies. Архивировать только после доказанного отсутствия активной зависимости.
