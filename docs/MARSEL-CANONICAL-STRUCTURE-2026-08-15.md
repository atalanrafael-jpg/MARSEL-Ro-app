# MARSEL / Ro App — Единая каноническая структура

Дата ревизии: 2026-08-15
Ветка: `main`

## 1. Единственная точка автоматического live-аудита

`.github/workflows/marsel-unified-control-plane.yml`

Порядок:

1. API inventory — READ ONLY
2. Data quality — READ ONLY
3. Entity audit — READ ONLY
4. Product-code collision review — READ ONLY
5. Unified safety/quality gate
6. Unified evidence artifact

Другие workflow не должны выполнять самостоятельный live-аудит Ro App.

## 2. Канонические runtime-компоненты

- `scripts/marsel_api_inventory_v20_31.py` — текущая точка входа inventory; использует `v20_29` как общий движок.
- `scripts/marsel_api_inventory_v20_29.py` — внутренний общий движок inventory; напрямую workflow не запускается.
- `scripts/marsel_data_quality_v22_readonly.py` — data quality.
- `scripts/marsel_entity_audit_v20_32.py` — entity audit.
- `scripts/marsel_product_code_collision_audit_v22_1.py` — collision review.
- `scripts/marsel_api_v2_probe_v1.py` — канонический read-only probe.
- `scripts/marsel_api_v2_canonical_registry_v1.py` — evidence/registry support.

Специализированные проверки каталогов, reference-data, backup и контрактов сохраняются только там, где они не дублируют live-аудит Unified Control Plane.

## 3. Единая прикладная структура

```text
Ro-app/
├── app/                 # прикладной runtime
├── ai_service/          # AI service layer
├── config/              # конфигурация и fixture
├── data/                # reference/catalog data
├── docs/                # единая документация и контракты
├── scripts/             # канонические и специализированные проверки
├── tests/               # unit/integration tests
├── javascript/          # GPT integration
├── typescript/          # GPT integration
├── python/              # Python integration
├── .github/workflows/   # CI + единый MARSEL live-audit
└── requirements.txt     # Python dependencies
```

## 4. CI-разделение

- `marsel-unified-control-plane.yml` — единственный live Ro App audit.
- `test.yml` — только unit tests; live API-аудит сюда не входит.
- `language-quality.yml` — языковые проверки.
- `generate-drafts.yml` — генерация drafts.

## 5. Обязательные safety invariants

Канонический контур обязан подтверждать:

- `WRITE_REQUESTS_MADE=0`;
- `RO_APP_DATA_MUTATED=false`;
- отсутствие угаданных идентификаторов;
- отсутствие POST/PUT/PATCH/DELETE в live-аудите;
- неполные live-данные = `REVIEW_REQUIRED`, никогда не `PASS`;
- старый успешный запуск не заменяет новый запуск на текущем `main`.

## 6. Что удалено при консолидации

Удалены подтверждённо устаревшие дублирующие audit/inventory/quality/test-компоненты. Generic `test.yml` больше не содержит собственного Ro App live-аудита.

## 7. Критерий завершения

Проект считается проверенным только после успешного запуска канонического Unified Control Plane на текущем `main` с созданием единого evidence artifact и прохождением всех safety/data/entity/collision gates.

До этого статус проекта — `REVIEW_REQUIRED`.
