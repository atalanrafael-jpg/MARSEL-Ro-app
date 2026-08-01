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

## Важно
Этот пакет НЕ содержит реальный API-ключ и не изменяет рабочую базу автоматически.
Сначала выполняются безопасные GET-запросы и проверка ответа. Операции записи должны быть добавлены только после проверки конкретных endpoint'ов и схем API.

## Запуск

1. Скопировать `.env.example` в `.env`.
2. Заполнить `ROAPP_API_KEY`.
3. Установить зависимости:
   `pip install -r requirements.txt`
4. Запустить:
   `uvicorn app.main:app --host 0.0.0.0 --port 8000`

Проверка:
- `GET /health`
- `GET /roapp/orders?page=1`

## Безопасность
Не помещайте API-ключ в GitHub, README, исходный код или скриншоты.
