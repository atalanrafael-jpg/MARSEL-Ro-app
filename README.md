# MARSEL — RO App integration

Интеграционный проект Ювелирной студии MARSEL для безопасной работы с RO App API.

> **Текущий статус:** API inventory V20.14 подтверждён CI в режиме READ ONLY. Production-данные RO App не изменяются.

## 1. Назначение

Проект объединяет в одном репозитории:

- RO App API client;
- FastAPI-сервис MARSEL;
- read-only аудит заказов;
- официальный inventory API-документации RO App;
- GitHub Actions для автоматических проверок;
- OpenAI Ads Conversions API integration;
- документацию и контроль безопасности.

## 2. Архитектура

```text
app/
├── main.py              # FastAPI entrypoint
├── config.py            # единая конфигурация и secrets из env
├── roapp_client.py      # RO App API client
├── audit.py             # read-only аудит данных заказов
└── openai_ads.py        # OpenAI Ads Conversions API

scripts/
├── marsel_api_inventory_v20_14.py
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

Корневые дубликаты `main.py`, `config.py`, `roapp_client.py` и пустой `__init__.py` удалены. Единственная рабочая Python-точка входа — `app.main:app`.

## 3. RO App API

Параметры API берутся из официальной документации RO App:

- Base URL: `https://api.roapp.io/v2`;
- Bearer authentication через `ROAPP_API_KEY`;
- проверочный endpoint: `GET /orders`.

Источник: официальная документация RO App — `https://roapp.readme.io/reference/getting-started-with-api`.

### V20.14 — подтверждённый результат

Последний успешный официальный inventory:

- `DOCS_INDEX_HTTP=200`;
- `REFERENCE_LINKS=148`;
- `DOCUMENTED_OPERATIONS=148`;
- `DOCUMENTED_GET_OPERATIONS=95`;
- `OPERATIONS_WITH_EXTRACTED_PATHS=146`;
- `GET_OPERATIONS_PROBED=94`;
- `GET_OPERATIONS_NOT_PROBED=1`;
- `OPERATIONS_WITH_UNRESOLVED_PROBE_STATE=53`;
- `WRITE_REQUESTS_MADE=0`;
- `RO App data mutated=False`.

Это означает, что проблема V12/V13 с извлечением только одного endpoint устранена. Два из 148 операций пока не имеют извлечённого пути и требуют отдельного разбора; 53 операции не являются GET-пробами и поэтому намеренно не выполняются.

## 4. Безопасность

Read-only inventory разрешает только `GET`.

Запрещены:

- `POST`;
- `PUT`;
- `PATCH`;
- `DELETE`.

API-ключи не должны находиться в исходниках, README, артефактах или скриншотах. Для CI используется GitHub Actions Secret `ROAPP_API_KEY`.

## 5. Запуск

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Проверки:

```bash
pytest -q
```

Endpoints локального сервиса:

- `GET /health`
- `GET /roapp/orders?page=1`
- `GET /roapp/audit/orders?max_pages=10`

## 6. Docker

```bash
docker compose up --build
```

Docker запускает `app.main:app`; отдельный корневой entrypoint не используется.

## 7. OpenAI Ads

`app/openai_ads.py` предназначен для server-side Conversion Measurement. Секреты должны передаваться только через переменные окружения.

Источник: OpenAI Help Center — Conversion Measurement: `https://help.openai.com/en/articles/20001409-conversion-measurement`.

## 8. CI/CD

GitHub Actions разделены по назначению:

- **test** — базовая проверка проекта;
- **V20.10** — read-only аудит;
- **V20.11** — read-only schema audit;
- **V20.12** — inventory;
- **V20.13** — deep audit;
- **V20.14** — официальный API inventory и проверка документированных GET endpoints.

V20.14 публикует JSON inventory как Actions artifact и не записывает данные в RO App.

## 9. Что сейчас не закрыто

Открытые Issues #4, #8 и #11 относятся к старой проблеме извлечения API-путей. Технически основной дефект уже устранён и V20.14 успешно проходит CI. Они не должны считаться закрытыми автоматически до отдельной проверки оставшихся 2 операций без пути и 53 unresolved probe states.

## 10. Принцип дальнейшей работы

1. Сначала официальная документация.
2. Затем READ ONLY inventory.
3. Затем проверка GET.
4. Только после подтверждения endpoint, payload, прав доступа и резервной копии возможны операции изменения данных.
5. Никаких выдуманных API-путей или неподтверждённых операций.
