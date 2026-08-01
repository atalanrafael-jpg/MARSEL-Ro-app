# API-интеграция RO App

## Подтверждено официальной документацией

Base URL:
`https://api.roapp.io/v2`

Authentication:
`Authorization: Bearer YOUR_API_KEY`

Подтвержденный пример:
`GET /orders`

Rate limit:
3 requests/second.

Pagination:
параметр `page`, до 50 записей за запрос.

Источник:
https://roapp.readme.io/reference/getting-started-with-api

## Запись данных

В этой версии операции POST/PATCH/DELETE намеренно НЕ включены.
Перед изменением рабочей базы необходимо проверить конкретный endpoint, обязательные поля, формат payload и правила идемпотентности в официальной документации.
