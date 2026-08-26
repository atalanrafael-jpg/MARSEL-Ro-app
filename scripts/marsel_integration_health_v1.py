#!/usr/bin/env python3
"""MARSEL ROAPP integration health checker (read-only, fail-closed)."""
from __future__ import annotations
import json, os, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

REGISTRY = Path("MARSEL_INTEGRATION_REGISTRY.md")
OUT = Path("artifacts/marsel-integration-health.json")
SYSTEMS = [
    ("GitHub", "CONNECTED", None), ("Codex", "CONFIGURED", None),
    ("GitHub Copilot", "CONFIGURED", None), ("Cursor", "CONFIGURED", None),
    ("VS Code Agent", "CONFIGURED", None), ("MCP", "CONFIGURED", None),
    ("ROAPP API", "NOT_VERIFIED", "MARSEL_ROAPP_HEALTH_URL"),
    ("Supabase", "AVAILABLE", "MARSEL_SUPABASE_HEALTH_URL"),
    ("Vercel", "AVAILABLE", "MARSEL_VERCEL_HEALTH_URL"),
    ("Linear", "CONNECTED", None), ("Notion", "CONNECTED", None),
    ("Airtable", "CONNECTED", None), ("Microsoft Outlook", "AVAILABLE", None),
    ("Automations", "AVAILABLE", None),
    ("OpenAI Platform", "NOT_VERIFIED", "MARSEL_OPENAI_HEALTH_URL"),
    ("Wix", "NOT_VERIFIED", "MARSEL_WIX_HEALTH_URL"),
]

def probe(url: str) -> dict:
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "MARSEL-ROAPP-Health/1.1"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return {"live_verified": 200 <= r.status < 400, "http_status": r.status}
    except urllib.error.HTTPError as e:
        return {"live_verified": False, "http_status": e.code}
    except Exception as e:
        return {"live_verified": False, "error_class": type(e).__name__}

def main() -> int:
    if not REGISTRY.exists():
        raise SystemExit("MARSEL_INTEGRATION_REGISTRY.md missing")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results, blocking = [], []
    for name, status, env_name in SYSTEMS:
        item = {"system": name, "registry_status": status, "verification_state": "CONFIGURED" if status == "CONFIGURED" else "UNVERIFIED"}
        if env_name:
            url = os.getenv(env_name)
            if url:
                item["probe"] = probe(url)
                item["verification_state"] = "LIVE_VERIFIED" if item["probe"]["live_verified"] else "FAILED"
                if item["verification_state"] != "LIVE_VERIFIED":
                    blocking.append(f"{name}: live probe failed")
            else:
                item["probe"] = {"status": "NOT_CONFIGURED"}
                item["verification_state"] = "NOT_CONFIGURED"
                blocking.append(f"{name}: endpoint not configured")
        elif status in {"CONNECTED", "AVAILABLE"}:
            blocking.append(f"{name}: live verification unavailable")
        results.append(item)
    overall = "PASS" if not blocking else "REVIEW_REQUIRED"
    payload = {"schema":"marsel-integration-health/v4","project":"MARSEL ROAPP","observed_at":datetime.now(timezone.utc).isoformat(),"mode":"READ_ONLY","status":overall,"credentials_exposed":False,"production_write":False,"blocking_reasons":blocking,"integrations":results}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MARSEL_INTEGRATION_HEALTH={overall}")
    print("MODE=READ_ONLY\nPRODUCTION_WRITE=false\nCREDENTIALS_EXPOSED=false")
    for reason in blocking:
        print(f"BLOCKING={reason}")
    return 1 if blocking else 0

if __name__ == "__main__":
    raise SystemExit(main())
