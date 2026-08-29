#!/usr/bin/env python3
"""MARSEL V22.3 — product-code ambiguity audit, READ ONLY.

Repeated product codes are review findings only when stable identity fields
prove an exact identity collision. API/access failures are recorded as
incomplete evidence instead of aborting before the evidence file is written.
No write request is made.
"""
import hashlib
import json
import os
import sys
import time
from collections import defaultdict

import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
OUT = os.environ.get("MARSEL_COLLISION_OUTPUT", "marsel-product-code-collisions-v22-3-readonly.json")
PAGE_SIZE = int(os.environ.get("MARSEL_PAGE_SIZE", "100"))
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "30"))
INTERVAL = max(float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34")), 0.34)
PATH = "/catalog/products"

if not KEY:
    print("ROAPP_API_KEY is required", file=sys.stderr)
    raise SystemExit(2)
if PAGE_SIZE <= 0:
    print("MARSEL_PAGE_SIZE must be positive", file=sys.stderr)
    raise SystemExit(2)

client = httpx.Client(
    headers={"Authorization": f"Bearer {KEY}", "Accept": "application/json", "User-Agent": "MARSEL-V22.3-READONLY"},
    timeout=TIMEOUT,
)
last = 0.0
rows = []
page = 1
api_error = None
pagination_complete = False

try:
    while True:
        wait = INTERVAL - (time.monotonic() - last)
        if wait > 0:
            time.sleep(wait)
        last = time.monotonic()
        response = client.get(f"{BASE}{PATH}", params={"page": page, "limit": PAGE_SIZE})
        if response.status_code != 200:
            api_error = {
                "http": response.status_code,
                "body": response.text[:1000],
                "page": page,
            }
            break
        payload = response.json()
        if isinstance(payload, list):
            batch, paging = payload, {}
        elif isinstance(payload, dict):
            batch = payload.get("data") or payload.get("items") or payload.get("products") or []
            paging = payload.get("paging") or {}
        else:
            api_error = {"error": "Unexpected /catalog/products response shape", "page": page}
            break
        if not isinstance(batch, list):
            api_error = {"error": "Unexpected /catalog/products data shape", "page": page}
            break
        rows.extend(item for item in batch if isinstance(item, dict))
        total_pages = paging.get("total_pages") or paging.get("totalPages")
        if total_pages is not None:
            if page >= int(total_pages):
                pagination_complete = True
                break
        elif len(batch) < PAGE_SIZE:
            pagination_complete = True
            break
        page += 1
finally:
    client.close()

IDENTITY_KEYS = (
    "name", "title", "sku", "category_id", "is_serial", "uom",
    "brand", "brand_id", "manufacturer", "manufacturer_id", "model",
    "model_id", "product_type", "product_type_id", "barcode", "ean", "gtin",
    "reference", "reference_id",
)

def norm(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return value
    return " ".join(str(value).strip().casefold().split())

def identity(item):
    return tuple((key, norm(item.get(key))) for key in IDENTITY_KEYS)

def display_record(item):
    result = {"id": item.get("id"), "code": item.get("code")}
    for key in IDENTITY_KEYS:
        if key in item:
            result[key] = item.get(key)
    return result

by_code = defaultdict(list)
for item in rows:
    code = item.get("code")
    if code is not None and str(code).strip():
        by_code[str(code).strip()].append(item)

shared_groups = {}
legitimate_reuse_groups = {}
real_collision_groups = {}
unresolved_groups = {}
for code, items in sorted(by_code.items()):
    if len(items) <= 1:
        continue
    records = [display_record(item) for item in items]
    shared_groups[code] = records
    identities = {identity(item) for item in items}
    if len(identities) > 1:
        legitimate_reuse_groups[code] = records
        continue
    present_identity = set().union(*(item.keys() for item in items)).intersection(IDENTITY_KEYS)
    if not present_identity:
        unresolved_groups[code] = records
    else:
        real_collision_groups[code] = records

report = {
    "version": "22.3",
    "mode": "READ_ONLY",
    "api_base": BASE,
    "endpoint": PATH,
    "pagination": "page + limit",
    "products_rows": len(rows),
    "pagination_complete": pagination_complete,
    "access_error": api_error,
    "status": "PASS" if api_error is None and not (real_collision_groups or unresolved_groups) else "REVIEW_REQUIRED",
    "shared_code_group_count": len(shared_groups),
    "legitimate_reuse_group_count": len(legitimate_reuse_groups),
    "real_collision_group_count": len(real_collision_groups),
    "unresolved_group_count": len(unresolved_groups),
    "shared_code_groups": shared_groups,
    "legitimate_reuse_groups": legitimate_reuse_groups,
    "real_collision_groups": real_collision_groups,
    "unresolved_groups": unresolved_groups,
    "gate_relevant_issue_count": len(real_collision_groups) + len(unresolved_groups),
    "write_requests_made": 0,
    "ro_app_data_mutated": False,
    "interpretation": "Repeated codes are informational unless stable identity fields prove exact identity duplication. Missing identity data or API access failure is unresolved, never proof of collision.",
}
raw = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
report["report_sha256"] = hashlib.sha256(raw).hexdigest()
with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(report, handle, ensure_ascii=False, indent=2)

print("=== MARSEL V22.3 / PRODUCT CODE AMBIGUITY AUDIT / READ ONLY ===")
print(f"ENDPOINT={PATH}")
print(f"PRODUCTS_ROWS={len(rows)}")
print(f"PAGINATION_COMPLETE={pagination_complete}")
if api_error:
    print(f"API_ACCESS_ERROR_HTTP={api_error.get('http', '')}")
print(f"SHARED_CODE_GROUP_COUNT={len(shared_groups)}")
print(f"LEGITIMATE_REUSE_GROUP_COUNT={len(legitimate_reuse_groups)}")
print(f"REAL_COLLISION_GROUP_COUNT={len(real_collision_groups)}")
print(f"UNRESOLVED_GROUP_COUNT={len(unresolved_groups)}")
print("WRITE_REQUESTS_MADE=0")
print("RO_APP_DATA_MUTATED=False")
print(f"REPORT={OUT}")
print(f"REPORT_SHA256={report['report_sha256']}")
print(f"RESULT={report['status']}")
