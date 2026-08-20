# MARSEL / Ro App — Единая каноническая структура

Дата ревизии: 2026-08-20
Канонический репозиторий: `atalanrafael-jpg/Ro-app`
Каноническая ветка: `main`

## 1. Единая система

MARSEL и ROAPP — один проект и один исходный контур.

- MARSEL — бизнес-контур: бренд, клиенты, заказы, изделия, ремонт, производство, склад, материалы, финансы, продажи и маркетинг.
- ROAPP — технологический контур той же системы: API, данные, интеграции, автоматизация, MCP и CI/CD.
- `atalanrafael-jpg/Ro-app` — единый источник истины.
- Запрещены независимые MARSEL/ROAPP runtime-контуры и дублирующие live-аудиты.

## 2. Единственная точка live-аудита RO App

`.github/workflows/marsel-unified-control-plane.yml`

Порядок:

1. API inventory — READ ONLY
2. Data quality — READ ONLY
3. Entity audit — READ ONLY
4. Product-code collision review — READ ONLY
5. Warehouse contract audit — READ ONLY
6. Unified safety/quality gate
7. Unified evidence artifact

Специализированные live-аудиты не должны запускаться отдельным workflow, если их проверка уже входит в Unified Control Plane.

## 3. Канонические runtime-компоненты

- `scripts/marsel_api_inventory_v20_32.py` — текущая точка входа inventory; использует `v20_31` как общий слой.
- `scripts/marsel_api_inventory_v20_31.py` — внутренний слой inventory.
- `scripts/marsel_api_inventory_v20_29.py` — базовый общий движок inventory.
- `scripts/marsel_data_quality_v22_readonly.py` — data quality.
- `scripts/marsel_entity_audit_v20_35.py` — entity audit.
- `scripts/marsel_product_code_collision_audit_v22_1.py` — collision review.
- `scripts/marsel_warehouse_contract_v20_36.py` — warehouse contract audit; запускается внутри Unified Control Plane.
- `scripts/marsel_api_v2_probe_v1.py` — канонический read-only probe.
- `scripts/marsel_api_v2_canonical_registry_v1.py` — evidence/registry support.

Версионные внутренние слои сохраняются только как зависимости канонического entrypoint либо как исторически необходимые компоненты. Новый отдельный live-аудит для той же области не добавляется.

## 4. Единая прикладная структура

```text
Ro-app/
├── app/                 # единый прикладной runtime
├── ai_service/          # AI service layer
├── config/              # конфигурация и fixtures
├── data/                # reference/catalog data
├── docs/                # единая документация и контракты
├── scripts/             # канонические и специализированные проверки
├── tests/               # unit/integration tests
├── javascript/          # GPT integration
├── typescript/          # GPT integration
├── python/              # Python integration
├── plugins/             # упакованный MARSEL ROAPP plugin
├── .agents/             # Codex/agent skill surface
├── .github/workflows/   # CI + единый MARSEL live-audit
└── requirements.txt     # Python dependencies
```

## 5. CI-разделение

- `marsel-unified-control-plane.yml` — единственный live Ro App audit и единый evidence gate.
- `test.yml` — только unit tests, compile и dependency checks.
- `mcp-production.yml` — application/MCP tests и dependency vulnerability audit; live RO App data audit не выполняет.
- `language-quality.yml` — языковые проверки.
- `generate-drafts.yml` — генерация drafts.

## 6. Обязательные safety invariants

Канонический контур обязан подтверждать:

- `WRITE_REQUESTS_MADE=0`;
- `RO_APP_DATA_MUTATED=false`;
- отсутствие угаданных идентификаторов;
- отсутствие POST/PUT/PATCH/DELETE в live-аудите;
- неполные live-данные = `REVIEW_REQUIRED`, никогда не `PASS`;
- старый успешный запуск не заменяет новый запуск на текущем commit.

## 7. Plugin и agent surfaces

`plugins/marsel-roapp/` и `.agents/skills/roapp-mcp/` относятся к одному MARSEL ROAPP проекту, но обслуживают разные поверхности интеграции. Их нельзя считать двумя проектами. Изменения MCP-поверхности должны оставаться read-only и синхронизироваться по единой политике безопасности.

## 8. Критерий завершения

Проект считается проверенным только после успешного запуска Unified Control Plane на актуальном `main` с единым evidence artifact и прохождением всех safety/data/entity/collision/warehouse gates.

До этого статус проекта — `REVIEW_REQUIRED`.
