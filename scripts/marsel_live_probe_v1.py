#!/usr/bin/env python3
"""MARSEL ROAPP safe live probes; GET only, no credentials persisted."""
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

def probe(url):
    start = time.monotonic()
    try:
        req = Request(url, method="GET", headers={"User-Agent": "MARSEL-ROAPP-Health/1.0"})
        with urlopen(req, timeout=10) as r:
            return {"verified": 200 <= r.status < 400, "http_status": r.status,
                    "latency_ms": round((time.monotonic() - start) * 1000, 1)}
    except Exception as exc:
        return {"verified": False, "error_class": type(exc).__name__,
                "latency_ms": round((time.monotonic() - start) * 1000, 1)}

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results = []
    for system, env_name in TARGETS.items():
        url = os.getenv(env_name)
        if not url:
            results.append({"system": system, "status": "NOT_CONFIGURED", "verified": False})
            continue
        result = probe(url)
        result.update({"system": system, "status": "LIVE_VERIFIED" if result["verified"] else "FAILED"})
        results.append(result)

    OUT.write_text(json.dumps({
        "schema": "marsel-live-probes/v1",
        "project": "MARSEL ROAPP",
        "mode": "READ_ONLY",
        "credentials_exposed": False,
        "production_write": False,
        "results": results,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    missing = [r["system"] for r in results if r["status"] == "NOT_CONFIGURED"]
    failed = [r["system"] for r in results if r["status"] == "FAILED"]
    verified = [r["system"] for r in results if r["status"] == "LIVE_VERIFIED"]

    print("MARSEL_LIVE_PROBES=PASS" if not missing and not failed else "MARSEL_LIVE_PROBES=BLOCKED")
    print("LIVE_VERIFIED=" + ",".join(verified) if verified else "LIVE_VERIFIED=NONE")
    if missing:
        print("NOT_CONFIGURED=" + ",".join(missing))
    if failed:
        print("FAILED=" + ",".join(failed))

    # PR-safe workflows can explicitly opt into non-blocking diagnostics.
    pr_safe = os.getenv("MARSEL_PR_SAFE", "false").lower() == "true"
    return 0 if pr_safe else (1 if missing or failed else 0)

if __name__ == "__main__":
    raise SystemExit(main())
