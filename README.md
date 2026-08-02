# MARSEL RO App ERP — v0.1

Рабочий стартовый пакет интеграционного сервиса для Ювелирной студии MARSEL.

## Что подтверждено по официальной документации RO App
- Base URL Public API: `https://api.roapp.io/v2`
- Авторизация: `Authorization: Bearer <API_KEY>`
- Лимит: до 3 запросов/сек.
- Пагинация: до 50 записей на страницу.
- Пример получения заказов: `GET /orders`.

Источник: официальная документация RO App:
https://roapp.readme.io/reference/getting-started-with-api

## OpenAI Ads conversion tracking

В репозиторий добавлен серверный клиент OpenAI Ads Conversions API: `app/openai_ads.py`.

Он подготовлен для:
- `order_created` как основной ecommerce-конверсионный event;
- передачи `oppref`, когда он доступен;
- единого стабильного `order_id` как server-side `id`, чтобы дедуплицировать событие с browser Pixel через тот же Pixel ID;
- передачи суммы в минимальных денежных единицах (`amount_minor`);
- `validate_only=true` по умолчанию для безопасной первичной проверки;
- batch-отправки до 1000 событий;
- хранения Pixel ID и Conversions API key только в серверных переменных окружения.

OpenAI указывает, что для более устойчивого измерения можно использовать Pixel и Conversions API вместе; при отправке одной и той же конверсии обеими системами нужно использовать одинаковый event ID для дедупликации. `oppref` следует сохранять и передавать в server-side событии, когда он доступен. Источник: OpenAI Help Center — Conversion Measurement:
https://help.openai.com/en/articles/20001409-conversion-measurement

Текущий server-side endpoint: `POST https://bzr.openai.com/v1/events?pid=<PIXEL_ID>`. API key передаётся как `Authorization: Bearer <CONVERSIONS_API_KEY>`. Для первичной проверки используется `validate_only: true`. Источник с описанием API endpoint и формата запроса: OpenAI Ads Conversions API reference, дополнительно сверено с актуальными интеграционными материалами:
https://www.paidaisearch.com/encyclopedia/chatgpt-ads/chapter-09-conversions-api

### Переменные окружения

Скопировать `.env.example` в `.env` и заполнить:

- `OPENAI_ADS_PIXEL_ID`
- `OPENAI_ADS_CONVERSIONS_API_KEY`
- `OPENAI_ADS_VALIDATE_ONLY=true` для первоначальной проверки
- `OPENAI_ADS_SOURCE_URL` для web-событий

**Важно:** Conversions API key должен быть создан именно в Ads Manager → Conversions. Не используйте для CAPI обычный OpenAI Platform API key и не помещайте секрет в GitHub или клиентский JavaScript.

## Важно
Этот пакет не содержит реальные ключи и не изменяет рабочую базу RO App автоматически.
Сначала выполняется безопасная валидация OpenAI Ads событий через `validate_only=true`. Реальная отправка включается только после успешной проверки credentials, Pixel ID, event schema и consent/privacy требований.

## Запуск

1. Скопировать `.env.example` в `.env`.
2. Заполнить `ROAPP_API_KEY` при необходимости работы с RO App.
3. Заполнить OpenAI Ads `Pixel ID` и `Conversions API key`.
4. Установить зависимости:
   `pip install -r requirements.txt`
5. Запустить:
   `uvicorn app.main:app --host 0.0.0.0 --port 8000`

Проверка RO App:
- `GET /health`
- `GET /roapp/orders?page=1`

Тесты:
`pytest -q`

## Безопасность и приватность

Не помещайте API-ключи в GitHub, README, исходный код или скриншоты.

Перед передачей conversion data пользователям необходимо предоставить требуемую информацию о сборе данных и получить необходимые согласия, когда они требуются применимым законодательством. OpenAI также указывает, что данные для расширенного сопоставления должны передаваться только при наличии правового основания и в поддерживаемом формате.
