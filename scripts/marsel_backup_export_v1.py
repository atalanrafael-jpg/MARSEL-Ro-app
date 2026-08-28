#!/usr/bin/env python3
"""Read-only MARSEL backup exporter.

Exports explicitly configured RO App API collections without mutating RO App.
The script accepts only GET requests and writes a local snapshot manifest with
SHA-256 hashes. It deliberately does not create backup evidence by itself:
evidence may be emitted only by the CI wrapper after successful validation.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "backup"
MAX_ITEMS = int(os.getenv("MARSEL_BACKUP_MAX_ITEMS", "10000"))


def fail(message: str) -> None:
    raise SystemExit(f"BACKUP_EXPORT_FAIL: {message}")


def load_plan() -> list[dict]:
    raw = os.getenv("MARSEL_BACKUP_ENDPOINTS_JSON", "")
    if not raw:
        fail("MARSEL_BACKUP_ENDPOINTS_JSON_missing")
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"endpoint_plan_invalid_json:{exc}")
    if not isinstance(plan, list) or not plan:
        fail("endpoint_plan_must_be_nonempty_list")
    seen = set()
    for item in plan:
        if not isinstance(item, dict):
            fail("endpoint_plan_item_not_object")
        name, url = item.get("name"), item.get("url")
        if not isinstance(name, str) or not name or not name.replace("_", "").isalnum():
            fail("endpoint_name_invalid")
        if name in seen:
            fail(f"duplicate_endpoint_name:{name}")
        seen.add(name)
        if not isinstance(url, str) or not url.startswith("https://"):
            fail(f"endpoint_url_invalid:{name}")
    return plan


def fetch(url: str, token: str) -> bytes:
    req = Request(url, method="GET", headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    try:
        with urlopen(req, timeout=30) as response:
            if response.getcode() != 200:
                fail(f"unexpected_http_status:{response.getcode()}")
            return response.read()
    except HTTPError as exc:
        fail(f"http_error:{exc.code}")
    except URLError as exc:
        fail(f"network_error:{exc.reason}")


def main() -> int:
    token = os.getenv("ROAPP_API_TOKEN", "")
    if not token:
        fail("ROAPP_API_TOKEN_missing")
    plan = load_plan()
    out = Path(os.getenv("MARSEL_BACKUP_OUTPUT", str(DEFAULT_OUTPUT)))
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"schema": "marsel-backup-manifest/v1", "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "readonly": True, "write_requests_made": 0, "entities": []}
    for item in plan:
        body = fetch(item["url"], token)
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            fail(f"response_not_json:{item['name']}:{exc}")
        if isinstance(parsed, list) and len(parsed) > MAX_ITEMS:
            fail(f"entity_limit_exceeded:{item['name']}")
        filename = f"{item['name']}.json"
        target = out / filename
        canonical = json.dumps(parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        target.write_bytes(canonical)
        manifest["entities"].append({"name": item["name"], "source": item["url"], "file": filename, "sha256": hashlib.sha256(canonical).hexdigest(), "bytes": len(canonical)})
    manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    (out / "manifest.json").write_bytes(manifest_bytes)
    print(f"BACKUP_EXPORT=PASS entities={len(manifest['entities'])} output={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
