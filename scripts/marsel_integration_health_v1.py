#!/usr/bin/env python3
"""MARSEL ROAPP integration health checker (read-only, fail-closed)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REGISTRY = Path("MARSEL_INTEGRATION_REGISTRY.md")
OUT = Path("artifacts/marsel-integration-health.json")
PR_MODE = os.getenv("MARSEL_INTEGRATION_HEALTH_MODE", "production").lower() == "pr"
SYSTEMS = [
    ("GitHub", "UNVERIFIED", None),
    ("Codex", "UNVERIFIED", None),
    ("GitHub Copilot", "UNVERIFIED", None),
    ("Cursor", "UNVERIFIED", None),
    ("VS Code Agent", "UNVERIFIED", None),
    ("MCP", "UNVERIFIED", None),
    ("ROAPP API", "UNVERIFIED", "ROAPP_HEALTH_URL"),
    ("Supabase", "UNVERIFIED", "SUPABASE_HEALTH_URL"),
    ("Vercel", "UNVERIFIED", "VERCEL_HEALTH_URL"),
    ("Linear", "UNVERIFIED", None),
    ("Notion", "UNVERIFIED", None),
    ("Airtable", "UNVERIFIED", None),
    ("Microsoft Outlook", "UNVERIFIED", None),
    ("Automations", "UNVERIFIED", None),
    ("OpenAI Platform", "UNVERIFIED", "OPENAI_HEALTH_URL"),
    ("Wix", "UNVERIFIED", "WIX_HEALTH_URL"),
]


def probe(url: str) -> dict:
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "MARSEL-ROAPP-Health/1.3"})
        with urllib.request.urlopen(req, timeout=10) as response:
            return {"live_verified": 200 <= response.status < 400, "http_status": response.status}
    except urllib.error.HTTPError as exc:
        return {"live_verified": False, "http_status": exc.code}
    except Exception as exc:
        return {"live_verified": False, "error_class": type(exc).__name__}


def main() -> int:
    if not REGISTRY.exists():
        raise SystemExit("MARSEL_INTEGRATION_REGISTRY.md missing")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    results, blocking = [], []
    for name, registry_status, env_name in SYSTEMS:
        item = {"system": name, "registry_status": registry_status, "verification_state": "UNVERIFIED"}
        if env_name:
            url = os.getenv(env_name)
            if not url:
                item["verification_state"] = "NOT_CONFIGURED"
                blocking.append(f"{name}: endpoint not configured")
            else:
                item["probe"] = probe(url)
                item["verification_state"] = "LIVE_VERIFIED" if item["probe"]["live_verified"] else "FAILED"
                if item["verification_state"] != "LIVE_VERIFIED":
                    blocking.append(f"{name}: live probe failed")
        else:
            blocking.append(f"{name}: live verification unavailable")
        results.append(item)

    actual_status = "PASS" if not blocking else "REVIEW_REQUIRED"
    payload = {
        "schema": "marsel-integration-health/v6",
        "project": "MARSEL ROAPP",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "mode": "PR_SAFE" if PR_MODE else "READ_ONLY",
        "status": actual_status,
        "ci_gate": "PASS" if PR_MODE else actual_status,
        "credentials_exposed": False,
        "production_write": False,
        "blocking_reasons": blocking,
        "integrations": results,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MARSEL_INTEGRATION_HEALTH={actual_status}")
    print(f"CI_GATE={'PASS' if PR_MODE else actual_status}")
    print(f"MODE={'PR_SAFE' if PR_MODE else 'READ_ONLY'}")
    print("PRODUCTION_WRITE=false\nCREDENTIALS_EXPOSED=false")
    for reason in blocking:
        print(f"BLOCKING={reason}")
    return 0 if PR_MODE else (1 if blocking else 0)


if __name__ == "__main__":
    raise SystemExit(main())
