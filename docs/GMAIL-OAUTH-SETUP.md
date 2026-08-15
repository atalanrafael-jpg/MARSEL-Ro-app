# Gmail OAuth — `atalanrafael@gmail.com`

## Назначение

Ro-app получает только read-only доступ к Gmail через официальный Gmail API. Gmail API поддерживает авторизованный доступ к почтовому ящику; OAuth scopes определяют уровень доступа. urlGmail API documentationhttps://developers.google.com/workspace/gmail/api/guides

## 1. Google Cloud

1. Создайте/выберите проект в Google Cloud.
2. Включите Gmail API.
3. Создайте OAuth Client ID типа **Web application**.
4. Добавьте redirect URI:
   `https://YOUR-DOMAIN/gmail/callback`
5. Используйте минимальный scope:
   `https://www.googleapis.com/auth/gmail.readonly`

Google описывает server-side OAuth flow с authorization code, access token и refresh token в официальной документации. urlOAuth 2.0 для web-server приложенийhttps://developers.google.com/identity/protocols/oauth2/web-server

## 2. Переменные окружения

```text
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
```

Не добавляйте эти значения в Git. GitHub рекомендует хранить чувствительные credentials в Secrets и не hardcode-ить их в исходном коде. urlGitHub — secure credentialshttps://docs.github.com/en/rest/authentication/keeping-your-api-credentials-secure

## 3. Запуск

После настройки переменных окружения откройте:

`https://YOUR-DOMAIN/gmail/connect`

После подтверждения Google выполнит callback на `/gmail/callback`.

Приложение дополнительно проверяет, что авторизованный аккаунт — именно `atalanrafael@gmail.com`.

## 4. Проверка

- `GET /gmail/status` — состояние подключения.
- `GET /gmail/messages?max_results=10` — read-only smoke test; возвращаются только IDs сообщений.
- `POST /gmail/disconnect` — удаляет credentials из памяти текущего процесса.

## 5. Production hardening — обязательно до боевого использования

Текущая реализация намеренно хранит OAuth credentials только в памяти процесса. Это безопаснее, чем коммитить токены, но не обеспечивает сохранение авторизации после перезапуска и не подходит для нескольких worker/instance.

Перед production необходимо заменить in-memory storage на зашифрованное серверное хранилище refresh token, ограничить доступ к нему и добавить аудит/ротацию. GitHub Secrets предназначены для хранения credentials, но refresh token Gmail должен храниться в подходящем защищённом runtime secret/token store, а не в Git. urlGitHub Actions secretshttps://docs.github.com/en/actions/reference/security/secure-use
