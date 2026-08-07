#!/usr/bin/env python3
"""MARSEL V20.19 strict read-only entity inventory.

Consumes the V20.14 API inventory and probes only concrete GET collection
paths. No write methods are issued and response bodies are not persisted.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from hashlib import sha256

import httpx

BASE = os.getenv("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.getenv("ROAPP_API_KEY", "")
TIMEOUT = float(os.getenv("ROAPP_TIMEOUT", "30"))
INPUT = os.getenv("MARSEL_API_INVENTORY_INPUT", "marsel-api-inventory-v20-14.json")
OUTPUT = os.getenv("MARSEL_ENTITY_INVENTORY_OUTPUT", "marsel-entity-inventory-v20-19.json")

SAFE_METHODS = {"GET"}
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
PLACEHOLDER_RE = re.compile(r"\{[^}]+\}|:[A-Za-z_][\w-]*|<[A-Za-z_][\w-]*>")


def die(msg: str) -> None:
    print(f"ERROR={msg}", file=sys.stderr)
    raise SystemExit(1)


def load_inventory() -> dict:
    with open(INPUT, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        die("inventory_not_object")
    return data


def extract_paths(data: dict) -> list[str]:
    """Extract concrete paths from both legacy and V20.14 nested schemas."""
    candidates: list[object] = []
    for key in ("paths", "operations", "documented_operations", "endpoints"):
        value = data.get(key)
        if isinstance(value, list):
            candidates.extend(value)

    out: list[str] = []

    def add(value: object) -> None:
        if isinstance(value, str):
            p = value.strip()
        elif isinstance(value, dict):
            p = value.get("path") or value.get("url") or value.get("endpoint")
        else:
            return
        if not isinstance(p, str) or not p.startswith("/"):
            return
        if PLACEHOLDER_RE.search(p):
            return
        if p not in out:
            out.append(p)

    for item in candidates:
        if isinstance(item, dict):
            # Current inventory stores extracted paths as a list on each operation.
            nested = item.get("paths")
            if isinstance(nested, list):
                for path in nested:
                    add(path)
            else:
                add(item)
        else:
            add(item)

    return out


def classify(status: int | None, error: str | None) -> str:
    if error:
        if "timeout" in error.lower():
            return "TIMEOUT"
        return "NETWORK_ERROR"
    if status == 200:
        return "OK"
    if status in (401, 403):
        return "AUTH_REQUIRED"
    if status == 404:
        return "NOT_FOUND"
    if status == 405:
        return "METHOD_NOT_ALLOWED"
    if status == 429:
        return "RATE_LIMIT"
    if status is not None and 500 <= status <= 599:
        return "SERVER_ERROR"
    return "HTTP_ERROR"


def main() -> None:
    if not KEY:
        die("ROAPP_API_KEY_missing")
    inv = load_inventory()
    paths = extract_paths(inv)
    if not paths:
        die("no_collection_paths_in_inventory")

    headers = {"Authorization": f"Bearer {KEY}", "Accept": "application/json"}
    results = []
    write_requests = 0
    mutated = False

    with httpx.Client(base_url=BASE, headers=headers, timeout=TIMEOUT, follow_redirects=True) as client:
        for path in paths:
            started = time.monotonic()
            status = None
            content_type = None
            error = None
            try:
                response = client.get(path)
                status = response.status_code
                content_type = response.headers.get("content-type", "")
            except httpx.TimeoutException as exc:
                error = f"timeout:{type(exc).__name__}"
            except httpx.HTTPError as exc:
                error = f"network:{type(exc).__name__}"
            elapsed_ms = round((time.monotonic() - started) * 1000, 1)
            results.append({
                "path": path,
                "method": "GET",
                "http": status,
                "classification": classify(status, error),
                "content_type": content_type,
                "latency_ms": elapsed_ms,
                "error": error,
            })

    classifications = {}
    for row in results:
        classifications[row["classification"]] = classifications.get(row["classification"], 0) + 1

    report = {
        "version": "20.19",
        "mode": "READ_ONLY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "api_base": BASE,
        "source_inventory": INPUT,
        "source_inventory_sha256": sha256(open(INPUT, "rb").read()).hexdigest(),
        "collection_paths_considered": len(paths),
        "results": results,
        "classifications": classifications,
        "write_requests": write_requests,
        "ro_app_data_mutated": mutated,
        "safe_methods_used": sorted(SAFE_METHODS),
        "write_methods_used": sorted(WRITE_METHODS & set()),
    }
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")

    digest = sha256(open(OUTPUT, "rb").read()).hexdigest()
    print("=== MARSEL V20.19 / ENTITY INVENTORY / READ ONLY ===")
    print(f"COLLECTION_PATHS_CONSIDERED={len(paths)}")
    print(f"CLASSIFICATIONS={json.dumps(classifications, sort_keys=True)}")
    print(f"WRITE_REQUESTS={write_requests}")
    print(f"RO_APP_DATA_MUTATED={mutated}")
    print(f"REPORT={OUTPUT}")
    print(f"REPORT_SHA256={digest}")
    print("RESULT=OK" if not mutated and write_requests == 0 else "RESULT=REVIEW_REQUIRED")


if __name__ == "__main__":
    main()
