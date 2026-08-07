#!/usr/bin/env python3
"""MARSEL V20.16 — read-only API/data-quality gate.

Uses the official V20.14 inventory JSON when available, probes documented concrete
GET endpoints, fully paginates /orders, and writes a machine-readable report.
No POST/PUT/PATCH/DELETE requests are made.
"""
import hashlib
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "30"))
PAGE_SIZE = int(os.environ.get("MARSEL_PAGE_SIZE", "100"))
INVENTORY = Path(os.environ.get("MARSEL_API_INVENTORY_INPUT", "marsel-api-inventory-v20-14.json"))
OUT = Path(os.environ.get("MARSEL_DATA_QUALITY_OUTPUT", "marsel-data-quality-v20-16.json"))

if not KEY:
    print("ROAPP_API_KEY is required", file=sys.stderr)
    raise SystemExit(1)

headers = {
    "Authorization": f"Bearer {KEY}",
    "Accept": "application/json",
    "User-Agent": "MARSEL-Audit-V20.16",
}


def extract_rows(payload, resource):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in (resource, "data", "items", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return None


def read_orders(client):
    rows = []
    pages = []
    page = 1
    complete = False
    while True:
        started = time.time()
        response = client.get(
            f"{BASE}/orders",
            params={"page": page, "pageSize": PAGE_SIZE},
            headers=headers,
        )
        elapsed = round(time.time() - started, 3)
        response.raise_for_status()
        payload = response.json()
        batch = extract_rows(payload, "orders")
        page_info = {
            "page": page,
            "http": response.status_code,
            "elapsed_s": elapsed,
            "batch_size": len(batch) if isinstance(batch, list) else None,
        }
        pages.append(page_info)
        if not isinstance(batch, list):
            break
        rows.extend(x for x in batch if isinstance(x, dict))
        if len(batch) < PAGE_SIZE:
            complete = True
            break
        page += 1
        time.sleep(0.25)
        if page > 10000:
            raise RuntimeError("pagination safety limit exceeded")
    return rows, pages, complete


def concrete_get_paths():
    if not INVENTORY.exists():
        return []
    report = json.loads(INVENTORY.read_text(encoding="utf-8"))
    paths = []
    for op in report.get("operations", []):
        if "GET" not in op.get("methods", []):
            continue
        for path in op.get("paths", []):
            if not any(token in path for token in ("{", "}", ":")) and path.startswith("/"):
                paths.append(path)
    return sorted(set(paths))


def probe_gets(client, paths):
    results = []
    for path in paths:
        started = time.time()
        try:
            response = client.get(BASE + path, headers=headers)
            elapsed = round(time.time() - started, 3)
            item = {"path": path, "http": response.status_code, "elapsed_s": elapsed}
            if response.status_code == 200:
                try:
                    payload = response.json()
                    item["json_type"] = type(payload).__name__
                    item["row_count"] = len(extract_rows(payload, path.strip("/").split("/")[-1])) if extract_rows(payload, path.strip("/").split("/")[-1]) is not None else None
                except ValueError:
                    item["json_type"] = "invalid_json"
            results.append(item)
        except Exception as exc:
            results.append({"path": path, "http": None, "error": f"{type(exc).__name__}: {exc}"})
    return results


def duplicate_groups(values):
    counts = Counter(v for v in values if v not in (None, ""))
    return {str(k): v for k, v in counts.items() if v > 1}


with httpx.Client(timeout=TIMEOUT) as client:
    orders, pages, orders_complete = read_orders(client)
    get_probes = probe_gets(client, concrete_get_paths())

ids = [row.get("id") for row in orders]
numbers = [row.get("number") for row in orders]
missing_id = sum(v is None for v in ids)
missing_number = sum(v in (None, "") for v in numbers)
dup_ids = duplicate_groups(ids)
dup_numbers = duplicate_groups(numbers)

report = {
    "version": "20.16",
    "readonly": True,
    "write_requests_made": 0,
    "ro_app_data_mutated": False,
    "api_base": BASE,
    "orders": {
        "total": len(orders),
        "pages": pages,
        "pagination_complete": orders_complete,
        "missing_id": missing_id,
        "missing_number": missing_number,
        "duplicate_id_groups": dup_ids,
        "duplicate_number_groups": dup_numbers,
        "duplicate_id_group_count": len(dup_ids),
        "duplicate_number_group_count": len(dup_numbers),
    },
    "documented_concrete_get_probes": get_probes,
}
report["summary"] = {
    "orders_total": len(orders),
    "orders_pages": len(pages),
    "orders_pagination_complete": orders_complete,
    "duplicate_order_id_groups": len(dup_ids),
    "duplicate_order_number_groups": len(dup_numbers),
    "concrete_get_paths_probed": len(get_probes),
    "concrete_get_http_200": sum(x.get("http") == 200 for x in get_probes),
    "concrete_get_http_non_200": sum(x.get("http") not in (200, None) for x in get_probes),
    "concrete_get_errors": sum(x.get("http") is None for x in get_probes),
    "write_requests_made": 0,
    "ro_app_data_mutated": False,
}
report["report_sha256"] = hashlib.sha256(
    json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print("=== MARSEL V20.16 / DATA QUALITY / READ ONLY ===")
for key, value in report["summary"].items():
    print(f"{key.upper()}={value}")
print(f"REPORT={OUT}")
print(f"REPORT_SHA256={report['report_sha256']}")
print("RESULT=PASS" if orders_complete and not dup_ids and not dup_numbers else "RESULT=REVIEW_REQUIRED")
print("WRITE_REQUESTS=0")
print("RO_APP_DATA_MUTATED=False")
