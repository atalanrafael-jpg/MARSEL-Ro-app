# MARSEL ROAPP — ERP MASTER ARCHITECTURE V1

Дата контрольной точки: 2026-09-06
Статус: DESIGN / READ_ONLY / WRITE=0

## 1. Назначение

ERP — обязательный бизнес-контур MARSEL ROAPP. Он не удаляется и не заменяется RO App. RO App остаётся операционным/API-подсистемным контуром там, где его источник и контракт подтверждены.

Цель ERP-контура:

`клиент → заказ → продажа/ремонт → производство → материалы → склад → себестоимость → оплата → аналитика → автоматизация`

ERP должен объединять процессы через общие мастер-данные и аудируемые связи, а не создавать независимые копии одних и тех же сущностей.

## 2. Канонические принципы

1. Один MARSEL ROAPP control plane.
2. Один canonical ID для каждой мастер-сущности, где он определён.
3. Для каждой сущности назначается один authoritative source; остальные системы хранят ссылки/представления.
4. RO App не объявляется источником истины там, где контракт/API ещё не подтверждены.
5. Производственные WRITE остаются запрещены до прохождения safety gates.
6. Любая синхронизация должна быть идемпотентной, обратимой и аудируемой.
7. Исторические документы не считаются текущим evidence без свежей проверки.

## 3. ERP-модули

| Код | Модуль | Назначение | Приоритет |
|---|---|---|---|
| ERP-MDM | Master Data | товары, услуги, материалы, металлы, камни, клиенты, поставщики, сотрудники, склады | P0 |
| ERP-SALES | Sales & Orders | предложения, заказы, цены, отгрузка, возвраты | P0 |
| ERP-INVENTORY | Inventory & Warehouse | остатки, движения, резервы, партии/серии, инвентаризации | P0 |
| ERP-PROC | Procurement | поставщики, заявки, закупки, приёмка, возвраты | P1 |
| ERP-PROD | Production | BOM, техоперации, производственные задания, WIP, выпуск, брак | P1 |
| ERP-REPAIR | Repair / Service | приёмка, диагностика, оценка, ремонт, материалы, выдача, гарантия | P1 |
| ERP-COST | Costing | металл, камни, труд, накладные, плановая/фактическая себестоимость | P0 |
| ERP-FIN | Finance | доходы, расходы, оплаты, AR/AP, финансовые проводки и отчётность | P0 |
| ERP-CRM | CRM | клиенты, история контактов, повторные продажи, сервисная история | P1 |
| ERP-HR | HR | сотрудники, роли, ресурсы, организационная структура | P2 |
| ERP-ANALYTICS | BI / KPI | маржа, продажи, склад, производство, ремонт, финансовые KPI | P1 |
| ERP-CONTROL | Audit / Security | RBAC, approvals, audit trail, data quality, evidence, gates | P0 |
| ERP-AI | AI / Automation | контролируемые очереди, аномалии, рекомендации и автоматизация | P2 |

## 4. MARSEL-специфические данные

Минимальный мастер-слой должен поддерживать:

- Master Product ID;
- SKU/артикул;
- категорию и вид изделия;
- металл и пробу;
- камни и характеристики камней;
- весовые параметры;
- BOM/состав изделия;
- фото и 3D-файл как связанные catalog assets;
- закупочную стоимость материалов;
- трудозатраты;
- себестоимость;
- розничную цену;
- ремонт как отдельный service workflow;
- складскую трассировку материалов и готовых изделий.

## 5. Границы ответственности систем

| Домен | Правило |
|---|---|
| Master Product ID | Канонический идентификатор MARSEL |
| RO App | Источник фактических ERP-данных только для подтверждённых сущностей и API-контрактов |
| Marketplace | Источник внешнего Order ID и внешнего статуса соответствующего канала |
| Master Catalog | Канонический каталоговый слой согласно действующей архитектуре проекта |
| ERP Finance | Будущий управляемый финансовый контур после отдельной проверки требований и интеграций |
| GitHub / Control Plane | Источник кода, конфигурации, документации и технического evidence |

Эта матрица не разрешает автоматическую перезапись данных между системами. Для каждой интеграции требуется отдельный контракт.

## 6. Ключевые сквозные процессы

### 6.1 Lead-to-Cash

`CRM → quotation → sales order → reservation/stock → fulfillment → payment → financial record → KPI`

### 6.2 Procure-to-Stock

`purchase request → supplier → purchase order → receipt → quality/verification → stock → payable`

### 6.3 Make-to-Stock / Make-to-Order

`demand → BOM → material reservation → work order → material consumption → WIP → QC → finished good → stock → cost`

### 6.4 Repair-to-Cash

`repair intake → diagnosis → estimate → customer approval → work order → materials/labor → QC → delivery → payment → service history`

## 7. Интеграции

Первый слой интеграций:

- RO App API/MCP — только после подтверждения авторизации и endpoint contract;
- marketplace/e-commerce — внешние заказы и статусы;
- payment providers — оплаты и reconciliation;
- accounting/tax systems — если выбран внешний финансовый источник истины;
- catalog/media storage — фото и 3D assets;
- GitHub Actions — audit, CI, evidence и control plane.

Каждая интеграция должна иметь:

`contract → auth → read test → mapping → idempotency → dry-run → reconciliation → rollback → production gate`

## 8. Безопасность

До production WRITE обязательна последовательность:

`READ → ANALYZE → BACKUP → RESTORE CHECK → RECONCILIATION → DRY-RUN → IDEMPOTENCY → ROLLBACK → SAFETY GATE → CONTROLLED WRITE → POST-WRITE VERIFY`

Нельзя создавать synthetic evidence, угадывать endpoint/ID или выполнять массовое изменение данных только на основании документации.

## 9. Текущий статус

ERP-контур архитектурно закреплён в MARSEL ROAPP, но production ERP readiness не считается достигнутой.

Подтверждено в текущем репозитории:

- RO APP / ERP зарегистрирован как единый домен;
- RO APP определён как ERP/API operational subsystem;
- production WRITE остаётся `0`;
- имеются отдельные P0 blockers: backup/restore, API/entity completeness, warehouse contract, production evidence и credential remediation;
- полное внедрение ERP-конфигурации и автоматический расчёт себестоимости в рабочем аккаунте исторически не были подтверждены.

## 10. Следующий контрольный проход

1. Создать ERP data dictionary для MDM, sales, inventory, procurement, production, repair, costing и finance.
2. Сопоставить существующие RO App API entities с ERP entities.
3. Зафиксировать authoritative source для каждой сущности.
4. Проверить существующие модели себестоимости и не создавать вторую параллельную реализацию.
5. Добавить ERP readiness checks в production evidence bundle.
6. После закрытия P0 — выполнить только READ_ONLY интеграционные smoke tests.
7. WRITE остаётся запрещённым до отдельного PASS production gate.
