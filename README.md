# MARSEL — RO App integration

Интеграционный проект Ювелирной студии MARSEL для безопасной работы с RO App API.

> **Текущий режим:** READ ONLY. Production-данные RO App не изменяются.

## 1. Назначение

Проект объединяет:

- RO App API client;
- FastAPI-сервис MARSEL;
- read-only аудит заказов и каталога;
- API inventory и диагностику официальной документации RO App;
- GitHub Actions для автоматических проверок;
- документацию, backup/hash-контроль и безопасность.

## 2. Архитектура

Основные компоненты:

```text
app/
├── main.py
├── config.py
├── roapp_client.py
├── audit.py
└── openai_ads.py

scripts/
├── marsel_data_quality_v22_readonly.py
├── marsel_product_code_collision_audit_v22_1.py
├── marsel_api_inventory_v20_14.py
├── marsel_master_audit_v20_20.py
└── ...

.github/workflows/
├── marsel-data-quality-v22-readonly.yml
├── marsel-api-inventory-v20-22.yml
├── marsel-api-inventory-v20-23.yml
└── ...
```

## 3. RO App API

Параметры API, подтверждённые проектной документацией:

- Base URL: `https://api.roapp.io/v2`;
- Bearer authentication через `ROAPP_API_KEY`;
- подтверждённый пример: `GET /orders`;
- rate limit: 3 requests/second;
- пагинация: `page`, до 50 записей за запрос.

Источник: официальная документация RO App — `https://roapp.readme.io/reference/getting-started-with-api`.

### Важное ограничение

Наличие ссылки на API-документацию не означает, что каждая операция из документации доступна текущему ключу или безопасна для production. Исполняются только операции, которые подтверждены документированным методом/path и разрешены текущей политикой проекта.

## 4. V22.1 — comprehensive data-quality audit

Актуальный read-only аудит `scripts/marsel_data_quality_v22_readonly.py` проверяет три основные коллекции:

- `/catalog/products`;
- `/catalog/services`;
- `/orders`.

Для каждой коллекции контролируются:

- полная пагинация;
- количество прочитанных строк;
- соответствие API count фактически прочитанным строкам;
- отсутствие записей без ID;
- duplicate IDs;
- duplicate product/service code;
- duplicate SKU;
- duplicate order number;
- отсутствующие title/number там, где они ожидаются.

Аудит использует только `GET`. Запросы `POST`, `PUT`, `PATCH`, `DELETE` блокированы политикой проекта.

Последний зафиксированный коммит V22.1 исправляет проверку завершения пагинации и добавляет контроль `count == rows_read`. Это изменение опубликовано в `0272b0bdc14e14ba6b8ac67cd6755171b6a917bb`.

## 5. Product code collision audit V22.1

Отдельный read-only аудит анализирует коллизии кодов товаров. Коллизия кода сама по себе не классифицируется как доказанная порча данных: это finding, требующий проверки бизнес-правила уникальности.

Источник реализации: `scripts/marsel_product_code_collision_audit_v22_1.py`.

## 6. Master Audit и backup

Master Audit создаёт локальный snapshot для контроля целостности и SHA-256 отчётов.

Raw snapshot с клиентскими данными не публикуется в GitHub Actions Artifact.

**Полный backup всей базы RO App пока не подтверждён.** Наличие read-only аудита не является доказательством наличия полного резервного копирования всех сущностей.

Перед любыми изменениями production необходимы:

1. подтверждённый полный перечень доступных сущностей;
2. подтверждённые GET-методы для резервного чтения;
3. проверенный экспорт/snapshot;
4. контроль целостности;
5. план восстановления;
6. только после этого — отдельная процедура `AUDIT → PROPOSE → APPLY`.

## 7. Безопасность

API-ключи не должны находиться в исходниках, README, артефактах или логах. Для CI используется GitHub Actions Secret `ROAPP_API_KEY`.

Автоматическое удаление или изменение записей запрещено до подтверждения endpoint, payload, прав доступа, идемпотентности и возможности отката.

Дубликаты сначала выявляются и попадают в отчёт. Автоматическое удаление не выполняется.

## 8. CI/CD

Workflow разделены по назначению:

- базовые тесты;
- API inventory;
- endpoint diagnostics;
- read-only data-quality audit;
- product code collision audit;
- schema/deep audits.

Актуальные результаты должны считаться источником фактического состояния. Старые показатели из предыдущих версий inventory нельзя переносить вручную в новые отчёты.

## 9. Что сейчас закрыто и что нет

### Закрыто в коде

- READ ONLY политика;
- защита от write-запросов в аудитах;
- аудит products/services/orders;
- проверка пагинации;
- проверка count против фактически прочитанных строк;
- проверки дубликатов и пропущенных идентификаторов;
- hash-контроль отчётов.

### Не подтверждено

1. Полный backup всей рабочей базы RO App.
2. Полный inventory всех сущностей и связей на текущем состоянии API.
3. Безопасная процедура массового исправления production-записей.
4. Возможность автоматического удаления/слияния дублей без потери связанных данных.
5. Реальное изменение production-данных через API.

## 10. Принцип дальнейшей работы

```text
OFFICIAL DOCS
      ↓
READ-ONLY INVENTORY
      ↓
LIVE GET PROBES
      ↓
DATA-QUALITY AUDIT
      ↓
BACKUP / HASH / RESTORE CHECK
      ↓
AUDIT FINDINGS
      ↓
PROPOSED CHANGES
      ↓
CONTROLLED APPLY
      ↓
POST-CHANGE READ-ONLY AUDIT
      ↓
REGRESSION TEST
```

Никаких выдуманных API-путей, неподтверждённых операций или заявлений о выполненном изменении без фактического подтверждения результата.
