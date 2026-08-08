#!/usr/bin/env python3
"""MARSEL V20.27 — Live GET-only API probe.

Consumes the V20.23 inventory and probes only concrete GET endpoints already
identified by documentation/OpenAPI. Parameterized paths are never guessed.
No POST/PUT/PATCH/DELETE is ever issued.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

VERSION = "20.27"
INVENTORY = Path(os.environ.get("MARSEL_API_INVENTORY_INPUT", "marsel-api-inventory-v20-23.json"))
OUT = Path(os.environ.get("MARSEL_LIVE_PROBE_OUTPUT", "marsel-live-probe-v20-27.json"))
BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "30"))
MIN_INTERVAL = float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34"))
PARAM_RE = re.compile(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>")
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
_last = 0.0


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def wait_rate_limit() -> None:
    global _last
    delay = MIN_INTERVAL - (time.monotonic() - _last)
    if delay > 0:
        time.sleep(delay)


def probe(url: str):
    global _last
    wait_rate_limit()
    req = Request(url, headers={"Authorization": f"Bearer {KEY}", "Accept": "application/json", "User-Agent": f"MARSEL-Audit-V{VERSION}"}, method="GET")
    started = time.time()
    try:
        _last = time.monotonic()
        with urlopen(req, timeout=TIMEOUT) as r:
            body = r.read().decode("utf-8", errors="replace")
            return {"http": r.status, "elapsed_s": round(time.time() - started, 3), "content_type": r.headers.get("Content-Type", ""), "body": body[:2_000_000]}
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:10000]
        return {"http": e.code, "elapsed_s": round(time.time() - started, 3), "content_type": e.headers.get("Content-Type", "") if e.headers else "", "body": body, "error": "HTTPError"}
    except Exception as e:
        return {"http": None, "elapsed_s": round(time.time() - started, 3), "content_type": "", "body": "", "error": f"{type(e).__name__}: {e}"}


def shape(value, depth=0):
    if depth >= 3:
        return "..."
    if isinstance(value, dict):
        return {k: shape(value[k], depth + 1) for k in sorted(value)[:100]}
    if isinstance(value, list):
        return {"type": "array", "items": shape(value[0], depth + 1) if value else "empty"}
    if value is None:
        return "null"
    return type(value).__name__


def main() -> int:
    if not KEY:
        print("ROAPP_API_KEY is required", file=sys.stderr)
        return 2
    if not INVENTORY.exists():
        print(f"inventory not found: {INVENTORY}", file=sys.stderr)
        return 1
    try:
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"invalid inventory JSON: {exc}", file=sys.stderr)
        return 1

    ops = inventory.get("operations", [])
    errors = []
    probes = []
    seen = set()
    for op in ops:
        method = str(op.get("method", "")).upper()
        path = str(op.get("path", ""))
        if method in WRITE_METHODS:
            errors.append(f"write-capable method present in inventory: {method} {path}")
            continue
        if method != "GET":
            continue
        if not path or PARAM_RE.search(path):
            probes.append({"method": "GET", "path": path, "status": "NOT_PROBED", "reason": "parameterized_or_empty_path"})
            continue
        if path in seen:
            continue
        seen.add(path)
        result = probe(BASE + path)
        item = {"method": "GET", "path": path, "url": BASE + path, "http": result.get("http"), "elapsed_s": result.get("elapsed_s"), "content_type": result.get("content_type"), "error": result.get("error")}
        body = result.get("body", "")
        if result.get("http") in {200, 201, 202, 204}:
            if body.strip():
                try:
                    parsed = json.loads(body)
                    item["json_valid"] = True
                    item["json_type"] = type(parsed).__name__
                    item["shape"] = shape(parsed)
                    if isinstance(parsed, dict):
                        item["top_level_keys"] = sorted(parsed.keys())[:100]
                    elif isinstance(parsed, list):
                        item["array_length"] = len(parsed)
                except json.JSONDecodeError:
                    item["json_valid"] = False
                    item["error"] = "successful HTTP response is not valid JSON"
            else:
                item["json_valid"] = result.get("http") == 204
        else:
            item["json_valid"] = None
            item["error_body_sample"] = body[:500] if body else None
        probes.append(item)

    successful = [p for p in probes if p.get("http") in {200, 201, 202, 204}]
    valid_json = [p for p in successful if p.get("json_valid") is True]
    not_probed = [p for p in probes if p.get("status") == "NOT_PROBED"]
    status = "PASS" if not errors and len(probes) > 0 else "FAIL"
    report = {
        "version": VERSION,
        "status": status,
        "readonly": True,
        "method_policy": {"allowed": ["GET"], "blocked": sorted(WRITE_METHODS)},
        "inventory_sha256": digest(INVENTORY),
        "metrics": {
            "inventory_operations": len(ops),
            "get_paths_probed": len(successful) + sum(1 for p in probes if p.get("http") is not None and p.get("status") != "NOT_PROBED"),
            "successful_responses": len(successful),
            "valid_json_responses": len(valid_json),
            "parameterized_not_probed": len(not_probed),
            "http_error_responses": sum(1 for p in probes if isinstance(p.get("http"), int) and p["http"] >= 400),
        },
        "probes": probes,
        "contract_state": {
            "live_response_schema": "CHECKED_FOR_PROBED_CONCRETE_GETS",
            "field_types": "OBSERVED_FOR_PROBED_JSON",
            "pagination_behavior": "OBSERVED_ONLY_WHEN_RETURNED",
            "http_error_shapes": "OBSERVED_ONLY_WHEN_RETURNED",
            "parameterized_identifiers_guessed": False,
            "completeness_claim": "NOT_ESTABLISHED",
        },
        "safety": {"write_requests_made": 0, "ro_app_data_mutated": False},
        "errors": errors,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report["report_sha256"] = digest(OUT)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"V{VERSION}_LIVE_PROBE={status}")
    print(f"SUCCESSFUL_RESPONSES={len(successful)}")
    print(f"VALID_JSON_RESPONSES={len(valid_json)}")
    print(f"PARAMETERIZED_NOT_PROBED={len(not_probed)}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    print(f"REPORT_SHA256={report['report_sha256']}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

# V20.27 trigger revision: intentionally no-op; preserves GET-only behavior.
