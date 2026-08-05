# MARSEL RO App ERP — v20.3

Рабочий интеграционный пакет для Ювелирной студии MARSEL.

## Статус v20.3

Версия зафиксирована в `VERSION`. Релиз проходит автоматическую проверку GitHub Actions.

Критерий технического подтверждения: успешный CI run для commit релиза, включая существующие тесты и безопасные RO App read-only проверки. До такого результата v20.3 не считается полностью подтверждённой.

## RO App API

По проектной документации:
- Base URL Public API: `https://api.roapp.io/v2`
- Авторизация: `Authorization: Bearer <API_KEY>`
- Лимит: до 3 запросов/сек.
- Пагинация: до 50 записей за запрос.
- Проверочный endpoint: `GET /orders`.

Источник: официальная документация RO App:
https://roapp.readme.io/reference/getting-started-with-api

## Read-only контроль

GitHub Actions содержит:
- `RO App API read-only smoke test`;
- `MARSEL read-only orders audit`;
- `MARSEL read-only order schema audit v2`.

Эти проверки выполняют только GET-запросы и не должны создавать, изменять или удалять данные RO App.

## OpenAI Ads conversion tracking

В репозитории присутствует серверный клиент OpenAI Ads Conversions API: `app/openai_ads.py`.

Он подготовлен для:
- `order_created` как ecommerce-конверсионного event;
- передачи `oppref`, когда он доступен;
- стабильного `order_id` для дедупликации browser Pixel и server-side события;
- `amount_minor`;
- `validate_only=true` для безопасной первичной проверки;
- batch-отправки;
- хранения Pixel ID и Conversions API key только в серверных переменных окружения.

Источник: OpenAI Help Center — Conversion Measurement:
https://help.openai.com/en/articles/20001409-conversion-measurement

## Переменные окружения

Скопировать `.env.example` в `.env` и заполнить необходимые переменные.

Для RO App в GitHub Actions используется секрет:

`ROAPP_API_KEY`

**Не помещайте API-ключи в GitHub-код, README, исходники или скриншоты.**

## Локальный запуск

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Проверки:
- `GET /health`
- `GET /roapp/orders?page=1`
- `pytest -q`

## Безопасность

v20.3 не включает массовую запись в RO App. Любые будущие операции изменения данных должны проходить отдельную проверку endpoint, payload, прав доступа, идемпотентности и резервной копии.

Подробные критерии релиза: `CHANGELOG_v20.3.md`.
