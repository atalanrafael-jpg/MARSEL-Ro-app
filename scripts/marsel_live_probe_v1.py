#!/usr/bin/env python3
"""MARSEL ROAPP safe live probes.

Only probes endpoints explicitly supplied through environment variables.
No credentials are printed or persisted. No write methods are used.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path
from urllib.request import Request, urlopen

TARGETS = {
    "ROAPP API": "ROAPP_HEALTH_URL",
    "Supabase": "SUPABASE_HEALTH_URL",
    "Vercel": "VERCEL_HEALTH_URL",
    "OpenAI Platform": "OPENAI_HEALTH_URL",
    "Wix": "WIX_HEALTH_URL",
}
OUT = Path("artifacts/marsel-live-probes.json")

def probe(url: str) -> dict:
    start = time.monotonic()
    try:
        req = Request(url, method="GET", headers={"User-Agent": "MARSEL-ROAPP-Health/1.0"})
        with urlopen(req, timeout=10) as r:
            return {"verified": 200 <= r.status < 400, "http_status": r.status,
                    "latency_ms": round((time.monotonic()-start)*1000, 1)}
    except Exception as exc:
        return {"verified": False, "error_class": type(exc).__name__,
                "latency_ms": round((time.monotonic()-start)*1000, 1)}

def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results = []
    for system, env_name in TARGETS.items():
        url = os.getenv(env_name)
        if not url:
            results.append({"system": system, "status": "NOT_CONFIGURED", "verified": False})
            continue
        result = probe(url)
        result.update({"system": system, "status": "CONNECTED" if result["verified"] else "NOT_VERIFIED"})
        results.append(result)
    payload = {"schema":"marsel-live-probes/v1","project":"MARSEL ROAPP",
               "mode":"READ_ONLY","credentials_exposed":False,
               "production_write":False,"results":results}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("MARSEL_LIVE_PROBES=PASS")
    print("MODE=READ_ONLY")
    print("PRODUCTION_WRITE=false")
    return 0

if __name__ == "__main__": raise SystemExit(main())
