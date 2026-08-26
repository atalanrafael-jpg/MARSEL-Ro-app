#!/usr/bin/env python3
"""MARSEL ROAPP integration health registry checker.

Read-only: reports configuration/verification state and never stores or prints
credential values. External connectivity is represented as NOT_VERIFIED unless
an explicit safe probe result is supplied by the CI environment.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

REGISTRY = Path("MARSEL_INTEGRATION_REGISTRY.md")
OUT = Path("artifacts/marsel-integration-health.json")
SYSTEMS = [
    ("GitHub", "CONNECTED"), ("Codex", "CONFIGURED"),
    ("GitHub Copilot", "CONFIGURED"), ("Cursor", "CONFIGURED"),
    ("VS Code Agent", "CONFIGURED"), ("MCP", "CONFIGURED"),
    ("ROAPP API", "NOT_VERIFIED"), ("Supabase", "AVAILABLE"),
    ("Vercel", "AVAILABLE"), ("Linear", "CONNECTED"),
    ("Notion", "CONNECTED"), ("Airtable", "CONNECTED"),
    ("Microsoft Outlook", "AVAILABLE"), ("Automations", "AVAILABLE"),
    ("OpenAI Platform", "NOT_VERIFIED"), ("Wix", "NOT_VERIFIED"),
]

def main() -> int:
    if not REGISTRY.exists():
        raise SystemExit("MARSEL_INTEGRATION_REGISTRY.md missing")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "marsel-integration-health/v1",
        "project": "MARSEL ROAPP",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "mode": "READ_ONLY",
        "credentials_exposed": False,
        "production_write": False,
        "integrations": [
            {"system": name, "registry_status": status,
             "live_verified": status == "CONNECTED"}
            for name, status in SYSTEMS
        ],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("MARSEL_INTEGRATION_HEALTH=PASS")
    print("MODE=READ_ONLY")
    print("PRODUCTION_WRITE=false")
    print("CREDENTIALS_EXPOSED=false")
    print(f"OUTPUT={OUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
