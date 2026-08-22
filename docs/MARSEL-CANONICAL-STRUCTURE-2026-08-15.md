# MARSEL / ROAPP — ЕДИНАЯ КАНОНИЧЕСКАЯ СТРУКТУРА

Дата ревизии: 2026-08-22  
Ветка: `main`

## 1. Единая система

`MARSEL` и `ROAPP` — один продукт и один исходный контур: `atalanrafael-jpg/Ro-app`.

- MARSEL — бизнес-контур.
- ROAPP — технологический контур: API, данные, интеграции, автоматизация, MCP и CI/CD.
- `main` — каноническая ветка.
- Параллельные бизнес- и технические проекты не считаются отдельными источниками истины.

## 2. Единственная точка live-аудита RO App
Дата контрольной ревизии: 2026-08-21
Ветка: `main`

## 1. Единственная точка live-аудита Ro App

`.github/workflows/marsel-unified-control-plane.yml`

Порядок выполнения:

1. Canonical structure self-check
2. RO App secret presence check
3. API inventory — READ ONLY
4. Data quality — READ ONLY
5. Entity audit — READ ONLY
6. Product-code collision review — READ ONLY / advisory
6. Product-code collision review — READ ONLY
7. Warehouse contract audit — READ ONLY
8. Unified safety/quality gate
9. Unified evidence artifact
10. Artifact upload

Другие workflow не должны выполнять самостоятельный live-аудит RO App.

## 3. Канонические runtime-компоненты

- `scripts/marsel_canonical_self_check.py` — structural self-check.
- `scripts/marsel_api_inventory_v20_32.py` — API inventory.
- `scripts/marsel_data_quality_v22_readonly.py` — data quality.
- `scripts/marsel_entity_audit_v20_35.py` — entity audit.
- `scripts/marsel_product_code_collision_audit_v22_1.py` — advisory collision review.
- `scripts/marsel_warehouse_contract_v20_36.py` — warehouse contract audit.
- `scripts/marsel_api_v2_probe_v1.py` — canonical read-only probe.
- `scripts/marsel_api_v2_canonical_registry_v1.py` — API evidence/registry support.

Старые versioned auditors сохраняются только как исторический материал и не подключаются к live Control Plane.

## 2. Фактически используемые runtime-компоненты Unified Control Plane

Имена ниже сверены с текущим `.github/workflows/marsel-unified-control-plane.yml` на `main`.

- `scripts/marsel_canonical_self_check.py`
- `scripts/marsel_api_inventory_v20_32.py`
- `scripts/marsel_data_quality_v22_readonly.py`
- `scripts/marsel_entity_audit_v20_35.py`
- `scripts/marsel_product_code_collision_audit_v22_1.py`
- `scripts/marsel_warehouse_contract_v20_36.py`

Поддержка/API registry:

- `scripts/marsel_api_v2_probe_v1.py`
- `scripts/marsel_api_v2_canonical_registry_v1.py`

Support runtime:

- `scripts/generate_drafts.py`

## 3. Важное правило версий

Имя файла и внутренняя версия скрипта являются разными атрибутами. Нельзя объявлять скрипт версией `20.48`, если фактический файл на `main` содержит другую внутреннюю версию. На контрольную дату warehouse-файл называется `marsel_warehouse_contract_v20_36.py`, а его внутренний отчёт содержит `version: 20.45`. Это зафиксировано как технический debt до отдельного version-normalization commit.

## 4. Единая прикладная структура

```text
Ro-app/
├── app/                 # application runtime
├── ai_service/          # AI service layer
├── config/              # configuration and fixtures
├── data/                # reference/catalog data
├── docs/                # canonical documentation and contracts
├── scripts/             # canonical + justified specialized checks
├── docs/                # документация и контракты
├── scripts/             # runtime/audit scripts
├── tests/               # tests
├── javascript/          # GPT integration
├── typescript/          # GPT integration
├── python/              # Python integration
├── 02_ROAPP/CONTROL/    # control registries
├── .github/workflows/   # CI + Unified Control Plane
├── .agents/             # agent skills/contracts
├── старые данные/       # historical material; not active
└── requirements.txt     # Python dependencies
```

## 5. CI-разделение

- `marsel-unified-control-plane.yml` — единственный RO App live-audit workflow.
- `test.yml` — unit/compile/dependency validation; live RO App audit сюда не входит.
- `language-quality.yml` — языковые проверки.
- `generate-drafts.yml` — draft generation; не является READ-ONLY control plane.
- `mcp-production.yml` — MCP-specific readiness checks.

## 6. Обязательные safety invariants
├── 02_ROAPP/CONTROL/    # контрольные реестры
├── старые данные/       # архивные файлы; не источник active configuration
├── .github/workflows/   # CI/CD
└── requirements.txt
```

## 5. CI/CD разделение

### CORE

- `marsel-unified-control-plane.yml` — единственный live Ro App audit.
- `test.yml` — unit/integration test workflow; live Ro App audit не должен находиться внутри него.
- `mcp-production.yml` — MCP production-readiness.

### SUPPORT

- `language-quality.yml` — language checks.
- `generate-drafts.yml` — scheduled draft generation; это не READ-ONLY control plane и workflow имеет `issues: write`.

## 6. Safety invariants

Канонический live-контур обязан подтверждать:

- `WRITE_REQUESTS_MADE=0`;
- `RO_APP_DATA_MUTATED=false`;
- `identifiers_guessed=false`;
- отсутствие POST/PUT/PATCH/DELETE в live-аудите;
- неполные или неподтверждённые live-данные = `REVIEW_REQUIRED`, никогда не `PASS`;
- старый успешный запуск не заменяет новый запуск на текущем `main`;
- секреты не хранятся в репозитории.

## 7. Правила архива

`старые данные/` предназначена только для исторических файлов, устаревших snapshots и заменённых реализаций.

Архивные материалы не являются источником текущего состояния и не должны подключаться в production workflow без отдельной миграции и повторной проверки.

Удаление исторических данных не производится, если их назначение нельзя подтвердить. В таком случае они остаются в архиве.

## 8. Критерий системной готовности

Проект не объявляется полностью готовым только на основании наличия кода или успешного CI.

Для production WRITE обязательны прямые evidence по:

`backup/export → restore integrity → schema reconciliation → full READ-ONLY inventory → duplicate/orphan/reference analysis → dry-run → idempotency → rollback → controlled write → post-write verification`.

До прохождения этих gate'ов production WRITE остаётся отключённым.
- отсутствие guessed identifiers;
- отсутствие POST/PUT/PATCH/DELETE в live-аудите;
- неполные или неподтверждённые live-данные = `REVIEW_REQUIRED`, никогда не `PASS`;
- старый успешный run не заменяет новый run на текущем `main`;
- секреты не хранятся в репозитории.

## 7. Legacy / archive policy

Старые GitHub Actions runs и Git history не удаляются.

Файлы репозитория переводятся в `старые данные/` только после доказательства отсутствия зависимостей в:

- active workflows;
- tests;
- runtime/imports;
- documentation/contracts;
- scripts invoked by other scripts.

Сам факт более старого номера версии не является достаточным основанием для архивации.

## 8. Критерий завершения

Проект считается VERIFIED только после успешного Unified Control Plane на текущем `main`, полного evidence artifact и прохождения всех safety/data/entity/collision/warehouse gates.

До этого итоговый статус: `REVIEW_REQUIRED`.
