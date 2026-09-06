# MARSEL ROAPP — ЕДИНЫЙ РЕЕСТР ЗАДАЧ

Дата контрольной точки: 2026-09-06

## Правило

MARSEL и ROAPP — один проект. Issue, PR, workflow, документация и код относятся к единому MARSEL ROAPP control plane.

Статус `DONE` допускается только при прямом evidence. Старые CI-запуски и исторические документы не закрывают текущие задачи.

## Текущий подтверждённый реестр

| ID | Контур | Статус | Следующее действие |
|---|---|---|---|
| #19 | Production go-live | BLOCKED / NOT READY | собрать 8 обязательных production evidence; WRITE остаётся 0 |
| #91 | GitHub account/security controls | OPEN / MANUAL | исправить target ruleset, secret scanning/push protection, production environment и Copilot controls через GitHub account UI/API |
| PR #89 | Limits-resilient execution worker | OPEN / DRAFT / MERGEABLE | пройти review и текущий CI; затем снять Draft и merge только после проверки |
| Warehouse | Warehouse API | LIVE-READ-VERIFIED / CONTRACT ONLY | подтвердить полный response schema и stock/stock-movement endpoints отдельными GET evidence |
| MCP | ChatGPT/Codex MCP | AUTH PENDING | выполнить реальную authorization verification |
| Credentials | ROAPP API key | SECURITY GATE | подтвердить rotation/history scan при подозрении или подтверждённом exposure |
| Gmail OAuth | Live read-only OAuth | NOT VERIFIED | выполнить реальный OAuth smoke test |
| Evidence | Production evidence bundle | 1/8 | отсутствуют backup, restore, reconciliation, duplicate/reference, dry-run, idempotency, rollback evidence |
| ERP Architecture | ERP master architecture | DONE / DESIGN | архитектура закреплена в `docs/MARSEL_ERP_MASTER_ARCHITECTURE_V1.md` |
| ERP Data Dictionary | ERP data dictionary v1 | DONE / DESIGN | создан `docs/MARSEL_ERP_DATA_DICTIONARY_V1.md`; mapping продолжается по evidence |
| ERP Entity/API Mapping | ERP ↔ RO App mapping | PARTIAL / WAREHOUSE-CONTRACT-VERIFIED | подтвердить stock, materials, products, customers и payments через официальные GET evidence |
| ERP Costing | Costing | NOT VERIFIED | подтвердить существующий engine, price sources, labor/overhead и planned-vs-actual; не создавать параллельный engine |
| ERP Finance | Finance boundary | NOT VERIFIED | определить authoritative finance/accounting source и выполнить READ_ONLY mapping/reconciliation |
| ERP Readiness | ERP production readiness | BLOCKED | не считать production ERP готовым до P0 gates; отдельно закрыть costing, finance, inventory, procurement, production и repair flows |

## Что уже подтверждено

- Базовый repository CI на последнем проверенном запуске проходит.
- Production WRITE не включён.
- Execution Worker спроектирован как read-only/fail-closed и не получает production secrets.
- Production Evidence Orchestrator корректно блокирует gate при неполном evidence.
- Security issue, ранее ошибочно закрытая при состоянии NOT READY, была возвращена в OPEN.
- ERP закреплён как обязательный бизнес-контур MARSEL ROAPP отдельной master-архитектурой.
- ERP data dictionary v1 добавлен в репозиторий; его mapping-статусы намеренно не повышены без live/API evidence.
- Warehouse-list contract получил прямое repository evidence: `evidence/marsel-unified-warehouse-contract.json` фиксирует `status=PASS`, `mode=READ_ONLY`, `write_requests_made=0`, `ro_app_data_mutated=false`, `warehouse_list_contract_verified=true` на `2026-09-05T08:41:00Z`.
- Costing audit 2026-09-06 выполнен: архитектура подтверждена как DESIGN, production implementation и RO App cost API не подтверждены.
- Finance boundary audit 2026-09-06 выполнен: financial control model подтверждена, production ledger/posting/integration не подтверждены.

## Текущие ограничения

Следующие действия нельзя честно выполнить только repository file/API connector:

- изменить account-level GitHub ruleset configuration;
- создать/защитить GitHub production environment;
- подтвердить account-level secret scanning/push protection;
- подтвердить Copilot account controls;
- выполнить пользовательский Gmail OAuth;
- выполнить пользовательскую RO App MCP authorization;
- создать реальные backup/restore/rollback evidence без доступа к соответствующим production systems;
- выполнить live RO App GET smoke tests без действующей авторизации/API access.

Никакие фиктивные evidence, credentials, OAuth tokens или production WRITE операции не создаются.

## ERP

ERP является обязательным контуром проекта, а RO App — его операционной/API-подсистемой в пределах подтверждённых контрактов. Каноническая архитектура: `docs/MARSEL_ERP_MASTER_ARCHITECTURE_V1.md`.

Data dictionary: `docs/MARSEL_ERP_DATA_DICTIONARY_V1.md`.

Целевой сквозной поток:

`клиенты → заказы → производство/ремонт → материалы → склад → себестоимость → оплаты → аналитика → автоматизация → повторные продажи`

Следующий ERP-проход: официальные GET evidence для stock → materials/products/customers/payments → costing implementation → finance source/reconciliation.

## Linear

В доступном Linear workspace не обнаружены проекты. Обнаружены только стандартные onboarding issues `RAF-1`–`RAF-4` (знакомство с Linear, команды, импорт данных, подключение инструментов). Они не являются подтверждёнными задачами MARSEL ROAPP и не закрываются автоматически без фактического выполнения соответствующих workspace-операций.

## Production gate

`WRITE=0` является обязательным до полного прохождения safety gates. Наличие кода, документации, CI или PR не является доказательством production readiness.

## Конечная цель

После прохождения технических gate система должна перейти от audit-only к управляемому ERP-контру MARSEL: клиенты → заказы → производство/ремонт → материалы → склад → себестоимость → оплаты → аналитика → автоматизация → повторные продажи.
