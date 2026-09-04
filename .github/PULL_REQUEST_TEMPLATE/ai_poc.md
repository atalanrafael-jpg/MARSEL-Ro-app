---
name: AI PoC: add FastAPI AI service, scheduled draft generator and workflows
about: Adds PoC for LLM integration — FastAPI service, scheduled draft generator and GitHub Actions.
---

### Summary
This PR adds a PoC integration of LLM-driven features for Ro-app:

- `ai_service/ai_service.py` — FastAPI service with endpoints:
  - `POST /moderate` — moderation (Anthropic/OpenAI)
  - `POST /generate-post` — generate post variants (OpenAI)
  - `GET /health` — health check
- `scripts/generate_drafts.py` — script generating draft Issues with AI variants
- `.github/workflows/generate-drafts.yml` — scheduled workflow (daily cron)
- `requirements.txt`, `.env.example`, `README.md` (AI PoC docs)

Purpose: quickly validate content moderation and automated draft generation. Next steps: embeddings indexing (Pinecone/Qdrant), recommendation endpoint, monitoring.

### Checklist
- [ ] Add repository secrets (Settings → Secrets):
  - `OPENAI_API_KEY`
  - `GH_PAT` (or ensure `GITHUB_TOKEN` has repo perms)
  - OPTIONAL: `ANTHROPIC_API_KEY`, `PINECONE_API_KEY`, `PINECONE_ENV`
- [ ] Test local service (see README)
- [ ] Run Actions workflow manually (Actions → "AI: generate drafts (scheduled)" → Run workflow)
- [ ] Review created draft Issues for tone/quality

### How to test locally
1. Checkout branch `ai/poc`
2. Copy `.env.example` → `.env` and fill keys
3. `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
4. `uvicorn ai_service.ai_service:app --reload --port 8000`
5. `curl -X POST "http://localhost:8000/generate-post" -H "Content-Type: application/json" -d '{"topic":"community growth","tone":"friendly","length":"short","count":3}'`

### Notes
- Default model in PoC: `gpt-4o-mini` (changeable via `OPENAI_MODEL` env)
- The PoC redacts simple PII patterns before sending to LLMs; further redaction rules are recommended.
- Keep secrets out of code; use GitHub Secrets for Actions.

