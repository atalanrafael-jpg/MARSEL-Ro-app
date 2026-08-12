from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import re
import logging
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

app = FastAPI(title="Ro-app AI PoC")
logging.basicConfig(level=logging.INFO)


class GenerateRequest(BaseModel):
    topic: str
    tone: Optional[str] = "informal"
    length: Optional[str] = "short"
    count: Optional[int] = 3


class ModerateRequest(BaseModel):
    text: str


def redact_pii(text: str) -> str:
    # Simple redaction for emails and phone numbers; extend as needed
    text = re.sub(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", "[REDACTED_EMAIL]", text)
    text = re.sub(r"(\+?\d[\d\-\s]{7,}\d)", "[REDACTED_PHONE]", text)
    return text


def call_openai_completion(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 400):
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.8,
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.exception("OpenAI call failed")
        raise


def call_anthropic_moderation(text: str):
    # Basic wrapper for Anthropic moderation (optional)
    if not ANTHROPIC_API_KEY:
        return {"ok": True, "reason": "anthropic not configured"}
    try:
        from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = f"{HUMAN_PROMPT}Is the following user content violating policy or harmful? Return a short JSON: {{'flagged': bool, 'reason': str}}\\n\\nContent:\\n{text}\\n{AI_PROMPT}"
        resp = client.completions.create(model="claude-instant-v1", prompt=prompt, max_tokens_to_sample=150)
        return {"ok": True, "raw": resp}
    except Exception:
        logging.exception("Anthropic moderation failed")
        return {"ok": False, "error": "anthropic call failed"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/moderate")
def moderate(req: ModerateRequest):
    text = req.text or ""
    redacted = redact_pii(text)
    # Prefer Anthropic if configured, otherwise rely on OpenAI moderation (if configured)
    if ANTHROPIC_API_KEY:
        result = call_anthropic_moderation(redacted)
        return {"provider": "anthropic", "result": result}
    if OPENAI_API_KEY:
        try:
            import openai

            openai.api_key = OPENAI_API_KEY
            resp = openai.Moderation.create(input=redacted)
            return {"provider": "openai", "result": resp}
        except Exception:
            logging.exception("OpenAI moderation failed")
            raise HTTPException(status_code=500, detail="Moderation failed")
    raise HTTPException(status_code=400, detail="No moderation provider configured")


@app.post("/generate-post")
def generate_post(req: GenerateRequest):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic required")
    prompt = f"Generate {req.count} short social media post variations about the topic: \"{topic}\". Tone: {req.tone}. Length: {req.length}. Provide results as numbered items without extra commentary."
    redacted_prompt = redact_pii(prompt)
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not configured")
    content = call_openai_completion(redacted_prompt, model=DEFAULT_MODEL)
    # Try to split into variants
    variants = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        # Accept numbered lines or plain lines
        m = re.match(r"^\d+[\).\-\s]+(.+)$", line)
        variants.append(m.group(1).strip() if m else line)
    # Fallback: if content is short, return as single variant
    if not variants:
        variants = [content]
    return {"topic": topic, "variants": variants[: req.count]}
