# Gmail OAuth — `atalanrafael@gmail.com`

## Назначение

Ro-app получает только read-only доступ к Gmail через официальный Gmail API. Gmail API поддерживает авторизованный доступ к почтовому ящику; OAuth scopes определяют уровень доступа. urlGmail API documentationhttps://developers.google.com/workspace/gmail/api/guides

## 1. Google Cloud

1. Создайте/выберите проект в Google Cloud.
2. Включите Gmail API.
3. Создайте OAuth Client ID типа **Web application**.
4. Добавьте redirect URI: `https://YOUR-DOMAIN/gmail/callback`.
5. Используйте минимальный scope: `https://www.googleapis.com/auth/gmail.readonly`.

Google описывает server-side OAuth flow с authorization code, access token и refresh token в официальной документации. urlOAuth 2.0 для web-server приложенийhttps://developers.google.com/identity/protocols/oauth2/web-server

## 2. Runtime secrets

```text
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_TOKEN_ENCRYPTION_KEY=<Fernet key>
GMAIL_TOKEN_STORE_PATH=/var/lib/marsel/gmail_oauth.db
```

`GMAIL_TOKEN_ENCRYPTION_KEY` должен генерироваться и храниться в защищённом runtime secret manager. Не добавляйте его, OAuth client secret или Gmail tokens в Git, logs, issues, PRs или artifacts. GitHub рекомендует не hardcode-ить credentials в исходном коде. urlGitHub — secure credentialshttps://docs.github.com/en/rest/authentication/keeping-your-api-credentials-secure

## 3. Storage и state

Production storage использует SQLite с отдельным подключением на операцию, transaction locking и `busy_timeout`, что позволяет нескольким worker-процессам на одном хосте использовать общий store. OAuth `state` хранится как SHA-256 hash, имеет TTL 10 минут и удаляется при первом успешном callback, поэтому state является одноразовым.

Gmail credentials сохраняются в SQLite только в зашифрованном виде через Fernet. Ключ шифрования хранится отдельно от базы данных.

Для нескольких хостов/контейнеров production следует заменить SQLite на общий managed token/state store с эквивалентными transactional guarantees; не использовать локальный filesystem как общий store между хостами.

## 4. Запуск

После настройки переменных окружения откройте:

`https://YOUR-DOMAIN/gmail/connect`

После подтверждения Google выполнит callback на `/gmail/callback`.

Приложение дополнительно проверяет, что авторизованный аккаунт — именно `atalanrafael@gmail.com`.

## 5. Проверка

- `GET /gmail/status` — состояние подключения.
- `GET /gmail/messages?max_results=10` — read-only smoke test; возвращаются только IDs сообщений.
- `POST /gmail/disconnect` — удаляет сохранённые credentials из token store.

## 6. Production gate

Перед production необходимо дополнительно выполнить live OAuth authorization, read-only Gmail API smoke test, secret/history scan и проверку deployment storage. CI unit tests не заменяют live OAuth verification.

Production WRITE в RO App не связан с Gmail OAuth и должен оставаться отключённым до прохождения отдельного RO App safety gate.