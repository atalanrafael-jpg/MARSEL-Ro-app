#!/usr/bin/env python3
"""Fail-closed, read-only MARSEL RO App backup exporter."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "backup"
MAX_ITEMS = int(os.getenv("MARSEL_BACKUP_MAX_ITEMS", "10000"))
ALLOWED_HOSTS = {"api.remonline.app"}


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
        if not isinstance(url, str):
            fail(f"endpoint_url_invalid:{name}")
        parsed = urlparse(url)
        if (
            parsed.scheme != "https"
            or parsed.hostname not in ALLOWED_HOSTS
            or parsed.port not in (None, 443)
            or parsed.username
            or parsed.password
            or parsed.fragment
        ):
            fail(f"endpoint_url_not_allowlisted:{name}")
    return plan


def fetch(url: str, token: str) -> bytes:
    req = Request(
        url,
        method="GET",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        with urlopen(req, timeout=30) as response:
            if response.getcode() != 200:
                fail(f"unexpected_http_status:{response.getcode()}")
            return response.read()
    except HTTPError as exc:
        fail(f"http_error:{exc.code}")
    except URLError as exc:
        fail(f"network_error:{exc.reason}")


def publish_atomically(staging: Path, final_out: Path) -> None:
    final_out.parent.mkdir(parents=True, exist_ok=True)
    previous = final_out.with_name(f".{final_out.name}.previous")
    if previous.exists():
        shutil.rmtree(previous)
    if final_out.exists():
        final_out.replace(previous)
    try:
        staging.replace(final_out)
    except Exception:
        if previous.exists() and not final_out.exists():
            previous.replace(final_out)
        raise
    if previous.exists():
        shutil.rmtree(previous)


def main() -> int:
    token = os.getenv("ROAPP_API_TOKEN", "")
    if not token:
        fail("ROAPP_API_TOKEN_missing")
    plan = load_plan()
    final_out = Path(os.getenv("MARSEL_BACKUP_OUTPUT", str(DEFAULT_OUTPUT))).resolve()

    with tempfile.TemporaryDirectory(prefix="marsel-backup-", dir=final_out.parent) as tmp:
        staging = Path(tmp) / "snapshot"
        staging.mkdir()
        manifest = {
            "schema": "marsel-backup-manifest/v1",
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "readonly": True,
            "write_requests_made": 0,
            "entities": [],
        }
        for item in plan:
            body = fetch(item["url"], token)
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError as exc:
                fail(f"response_not_json:{item['name']}:{exc}")
            if isinstance(parsed, list) and len(parsed) > MAX_ITEMS:
                fail(f"entity_limit_exceeded:{item['name']}")
            filename = f"{item['name']}.json"
            canonical = json.dumps(
                parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            (staging / filename).write_bytes(canonical)
            manifest["entities"].append(
                {
                    "name": item["name"],
                    "source": item["url"],
                    "file": filename,
                    "sha256": hashlib.sha256(canonical).hexdigest(),
                    "bytes": len(canonical),
                }
            )
        (staging / "manifest.json").write_bytes(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        )
        publish_atomically(staging, final_out)

    print(f"BACKUP_EXPORT=PASS entities={len(manifest['entities'])} output={final_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
