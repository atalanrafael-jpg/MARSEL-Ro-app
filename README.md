# Ro-app — AI PoC (branch: ai/poc)

## Цель PoC
- Быстрая модерация и генерация драфтов публикаций с помощью LLM.
- Создание ежедневных draft issues с вариантами постов.

## Как запустить локально
1) Склонировать и перейти в ветку ai/poc
2) Создать виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3) Скопировать .env.example в .env и заполнить ключи
4) Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
5) Запустить сервис (опционально):
   ```bash
   uvicorn ai_service.ai_service:app --reload --port 8000
   ```
6) Тестировать endpoint:
   ```bash
   curl -X POST "http://localhost:8000/generate-post" -H "Content-Type: application/json" -d '{"topic":"community growth","tone":"friendly","length":"short","count":3}'
   ```

## GitHub Actions
- Workflow `.github/workflows/generate-drafts.yml` запускается по расписанию и создаёт draft Issue с вариантами публикаций.
- Перед запуском добавьте секреты в Settings → Secrets:
  - OPENAI_API_KEY
  - GH_PAT (или GITHUB_TOKEN with repo permissions)
  - OPTIONAL: ANTHROPIC_API_KEY

## Security & Cost notes
- PoC использует inexpensive model by default (gpt-4o-mini). Adjust model selection in .env or Actions.
- Redact PII before sending to LLMs. Do not put secrets in code.

## TODO / next steps
- Add embeddings indexing (Pinecone/Qdrant) and recommendation endpoint
- Add moderation webhook for on‑post submissions
- Add Sentry for error tracking
