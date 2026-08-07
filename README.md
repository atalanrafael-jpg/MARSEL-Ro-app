# MARSEL — RO App integration

Интеграционный проект Ювелирной студии MARSEL для безопасной работы с RO App API.

> **Текущий статус:** API inventory V20.14 и Master Audit V20.20 работают в режиме READ ONLY. Production-данные RO App не изменяются.

## 1. Назначение

Проект объединяет:

- RO App API client;
- FastAPI-сервис MARSEL;
- read-only аудит заказов;
- официальный inventory API-документации RO App;
- GitHub Actions для автоматических проверок;
- OpenAI Ads Conversions API integration;
- документацию, backup/hash-контроль и безопасность.

## 2. Архитектура

```text
app/
├── main.py
├── config.py
├── roapp_client.py
├── audit.py
└── openai_ads.py

scripts/
├── marsel_api_inventory_v20_14.py
├── marsel_master_audit_v20_20.py
├── marsel_audit_v20_10.py
├── marsel_audit_v20_11.py
├── marsel_deep_audit_v20_13.py
├── marsel_inventory_v20_12.py
└── roapp_reference_fallback.txt

.github/workflows/
├── marsel-api-inventory-v20-14.yml
├── marsel-audit-v20-10.yml
├── marsel-audit-v20-11.yml
├── marsel-deep-audit-v20-13.yml
├── marsel-inventory-v20-12.yml
└── test.yml
```

Единственная рабочая Python-точка входа приложения — `app.main:app`.

## 3. RO App API

Параметры API:

- Base URL: `https://api.roapp.io/v2`;
- Bearer authentication через `ROAPP_API_KEY`;
- подтверждённый read-only endpoint: `GET /orders`.

Источник: официальная документация RO App — `https://roapp.readme.io/reference/getting-started-with-api`.

### V20.14 — официальный API inventory

Последний ранее подтверждённый inventory зафиксировал:

- `DOCS_INDEX_HTTP=200`;
- `REFERENCE_LINKS=148`;
- `DOCUMENTED_OPERATIONS=148`;
- `DOCUMENTED_GET_OPERATIONS=95`;
- `OPERATIONS_WITH_EXTRACTED_PATHS=146`;
- `GET_OPERATIONS_PROBED=94`;
- `GET_OPERATIONS_NOT_PROBED=1`;
- `WRITE_REQUESTS_MADE=0`;
- `RO App data mutated=False`.

В V20.14 дополнительно разделены три разных состояния: GET, которые реально проверены; GET без concrete path; и операции, которые вообще не являются GET. Поэтому `NON_GET_OPERATIONS` больше не смешивается с `GET_OPERATIONS_WITH_UNRESOLVED_PROBE_STATE`.

После следующего CI необходимо использовать новый inventory artifact как источник актуальных чисел, а не переносить старые показатели вручную.

## 4. Master Audit V20.20

Master Audit работает только с `GET /orders` и создаёт локальный snapshot для контроля целостности.

Проверяется:

- количество страниц;
- количество заказов;
- duplicate IDs;
- missing IDs;
- missing status;
- SHA-256 snapshot;
- SHA-256 отчёта.

Raw snapshot намеренно не публикуется в GitHub Actions Artifact, поскольку может содержать клиентские данные. В Artifact сохраняются только `master_audit.json` и `SHA256.json`.

Это **не полный backup базы RO App**. Полный backup возможен только после подтверждения полного API inventory и разрешённых методов чтения для соответствующих сущностей.

## 5. Безопасность

Read-only inventory разрешает только `GET`.

Запрещены:

- `POST`;
- `PUT`;
- `PATCH`;
- `DELETE`.

API-ключи не должны находиться в исходниках, README, артефактах или логах. Для CI используется GitHub Actions Secret `ROAPP_API_KEY`.

До подтверждения endpoint, payload, прав доступа и резервной копии mutation-запросы не выполняются.

## 6. Запуск

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
pytest -q
```

## 7. CI/CD

GitHub Actions разделены по назначению:

- **test** — базовая проверка проекта и read-only аудит;
- **V20.10** — read-only аудит;
- **V20.11** — schema audit;
- **V20.12** — inventory;
- **V20.13** — deep audit;
- **V20.14** — официальный API inventory;
- **V20.20** — Master Audit.

## 8. Что сейчас не закрыто

1. Полный inventory сущностей и их связей нужно повторно подтвердить свежим V20.14 CI после изменения классификации probe-state.
2. Полный backup всей базы пока не подтверждён.
3. Mutation endpoints намеренно не используются.
4. Автоматическое исправление/удаление записей не выполняется до подтверждения API-контракта и backup.

## 9. Принцип дальнейшей работы

1. Официальная документация.
2. READ ONLY API inventory.
3. Проверка подтверждённых GET.
4. Полный read-only audit сущностей и связей.
5. Backup/hash перед любыми изменениями.
6. Формирование предложений `AUDIT → PROPOSE → APPLY`.
7. Mutation только после подтверждения endpoint, payload и прав доступа.
8. После каждой записи — повторный read-only audit и регрессионный тест.

Никаких выдуманных API-путей или неподтверждённых операций.
