#!/usr/bin/env python3
"""RO APP V2 read-only probe driven by the latest evidence-first inventory.

The probe never invents endpoints. If the inventory report is absent, it is
built from the official RO App documentation by the canonical V20.31
inventory script. Only documented GET operations are probed; parameterized
routes are never called without a concrete verified identifier.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from urllib.parse import urlsplit

import httpx

BASE = os.getenv("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.getenv("ROAPP_API_KEY")
INVENTORY = os.getenv("MARSEL_API_INVENTORY_OUTPUT", "marsel-canonical-api-inventory.json")

if not KEY:
    raise SystemExit("FAIL: ROAPP_API_KEY is not configured")


def build_inventory() -> None:
    """Create the current evidence report when the canonical workflow has not."""
    if os.path.exists(INVENTORY):
        return
    env = os.environ.copy()
    env["MARSEL_API_INVENTORY_OUTPUT"] = INVENTORY
    env.setdefault("ROAPP_API_BASE", BASE)
    env.setdefault("MARSEL_MAX_DOCS", "200")
    env.setdefault("MARSEL_INVENTORY_BUDGET_SECONDS", "300")
    env.setdefault("ROAPP_TIMEOUT", "8")
    env.setdefault("ROAPP_MAX_RETRIES", "0")
    env.setdefault("ROAPP_MIN_REQUEST_INTERVAL", "0.34")
    result = subprocess.run(
        [sys.executable, "scripts/marsel_api_inventory_v20_31.py"],
        env=env,
        check=False,
    )
    if result.returncode != 0 or not os.path.exists(INVENTORY):
        raise SystemExit("FAIL: canonical API inventory could not be generated")


def find_operations(value: object) -> list[dict]:
    """Find operation records without assuming one undocumented JSON schema."""
    found: list[dict] = []
    if isinstance(value, dict):
        if isinstance(value.get("method"), str) and isinstance(value.get("path"), str):
            found.append(value)
        for child in value.values():
            found.extend(find_operations(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(find_operations(child))
    return found


def has_placeholder(path: str) -> bool:
    return bool(re.search(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>", path))


def absolute_url(path: str) -> str:
    """Join API paths without ever producing /v2/v2/... URLs."""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    origin = f"{urlsplit(BASE).scheme}://{urlsplit(BASE).netloc}"
    if path.startswith("/v2/") or path == "/v2":
        return origin + path
    if path.startswith("/1.1/") or path == "/1.1":
        return origin + path
    return BASE + "/" + path.lstrip("/")


build_inventory()
with open(INVENTORY, encoding="utf-8") as fh:
    report = json.load(fh)

operations = find_operations(report)
confirmed_gets = []
seen: set[str] = set()
for op in operations:
    if op.get("method", "").upper() != "GET":
        continue
    evidence = str(op.get("evidence", ""))
    status = str(op.get("status", "CONFIRMED"))
    if evidence not in {"DOCUMENTATION_CONFIRMED", "OPENAPI_CONFIRMED", "URL_CONFIRMED"}:
        continue
    if status not in {"", "CONFIRMED", "DOCUMENTATION_CONFIRMED"}:
        continue
    path = op["path"]
    if has_placeholder(path) or path in seen:
        continue
    seen.add(path)
    confirmed_gets.append({"name": op.get("name", path), "path": path, "evidence": evidence})

if not confirmed_gets:
    raise SystemExit("FAIL: no documented GET operations available for canonical probe")

results = []
headers = {
    "Authorization": f"Bearer {KEY}",
    "Accept": "application/json",
    "User-Agent": "MARSEL-Canonical-V2-Probe-READONLY",
}
with httpx.Client(timeout=30, follow_redirects=True) as client:
    for entry in confirmed_gets:
        response = client.get(absolute_url(entry["path"]), headers=headers)
        results.append({
            "name": entry["name"],
            "path": entry["path"],
            "evidence": entry["evidence"],
            "status_code": response.status_code,
            "ok": response.is_success,
        })

failed = [x for x in results if not x["ok"]]
summary = {
    "inventory_file": INVENTORY,
    "registry_count": len(confirmed_gets),
    "success": len(results) - len(failed),
    "failed": len(failed),
    "write_requests_made": 0,
    "ro_app_data_mutated": False,
    "result": "PASS" if results and not failed else "REVIEW_REQUIRED",
}
print(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2))
sys.exit(0 if summary["result"] == "PASS" else 2)
