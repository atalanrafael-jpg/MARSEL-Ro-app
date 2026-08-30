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
        req = Request(url, method="GET", headers={"User-Agent": "MARSEL-ROAPP-Health/1.1"})
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

    missing = [r["system"] for r in results if r["status"] == "NOT_CONFIGURED"]
    failed = [r["system"] for r in results if r["status"] == "FAILED"]
    verified = [r["system"] for r in results if r["status"] == "LIVE_VERIFIED"]
    review_required = bool(missing or failed)

    OUT.write_text(json.dumps({
        "schema": "marsel-live-probes/v1",
        "project": "MARSEL ROAPP",
        "mode": "READ_ONLY",
        "status": "REVIEW_REQUIRED" if review_required else "PASS",
        "credentials_exposed": False,
        "production_write": False,
        "results": results,
        "review_reasons": [
            *(f"{system}: endpoint not configured" for system in missing),
            *(f"{system}: live probe failed" for system in failed),
        ],
        "note": "Auxiliary health evidence is non-blocking; Production Gate remains fail-closed and authoritative.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("MARSEL_LIVE_PROBES=REVIEW_REQUIRED" if review_required else "MARSEL_LIVE_PROBES=PASS")
    print("LIVE_VERIFIED=" + ",".join(verified) if verified else "LIVE_VERIFIED=NONE")
    if missing:
        print("NOT_CONFIGURED=" + ",".join(missing))
    if failed:
        print("FAILED=" + ",".join(failed))

    # This workflow produces diagnostic evidence only. It never decides production readiness.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
