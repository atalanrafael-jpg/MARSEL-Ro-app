#!/usr/bin/env python3
"""MARSEL V22.1 — product-code collision audit, READ ONLY.

Products are exposed by the RO App catalog API at /catalog/products.
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
OUT = os.environ.get("MARSEL_COLLISION_OUTPUT", "marsel-product-code-collisions-v22-1-readonly.json")
PAGE_SIZE = int(os.environ.get("MARSEL_PAGE_SIZE", "100"))
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "30"))
INTERVAL = float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34"))
PATH = "/catalog/products"

if not KEY:
    print("ROAPP_API_KEY is required", file=sys.stderr)
    raise SystemExit(2)
if PAGE_SIZE <= 0:
    print("MARSEL_PAGE_SIZE must be positive", file=sys.stderr)
    raise SystemExit(2)

client = httpx.Client(
    headers={
        "Authorization": f"Bearer {KEY}",
        "Accept": "application/json",
        "User-Agent": "MARSEL-V22.1-READONLY",
    },
    timeout=TIMEOUT,
)
last = 0.0
rows = []
page = 1

while True:
    wait = INTERVAL - (time.monotonic() - last)
    if wait > 0:
        time.sleep(wait)
    last = time.monotonic()

    response = client.get(f"{BASE}{PATH}", params={"page": page, "limit": PAGE_SIZE})
    response.raise_for_status()
    payload = response.json()

    if isinstance(payload, list):
        batch, paging = payload, {}
    elif isinstance(payload, dict):
        batch = payload.get("data") or payload.get("items") or payload.get("products") or []
        paging = payload.get("paging") or {}
    else:
        raise RuntimeError("Unexpected /catalog/products response shape")

    if not isinstance(batch, list):
        raise RuntimeError("Unexpected /catalog/products data shape")

    rows.extend(item for item in batch if isinstance(item, dict))

    total_pages = paging.get("total_pages") or paging.get("totalPages")
    if total_pages is not None:
        if page >= int(total_pages):
            break
    elif len(batch) < PAGE_SIZE:
        break
    page += 1

by_code = defaultdict(list)
for item in rows:
    code = item.get("code")
    if code is not None and str(code).strip() != "":
        by_code[str(code)].append(item)

collisions = {}
for code, items in sorted(by_code.items()):
    if len(items) > 1:
        collisions[code] = [
            {
                "id": item.get("id"),
                "name": item.get("name") or item.get("title"),
                "sku": item.get("sku"),
                "category_id": item.get("category_id"),
                "is_serial": item.get("is_serial"),
                "uom": item.get("uom"),
            }
            for item in items
        ]

report = {
    "version": "22.1",
    "mode": "READ_ONLY",
    "api_base": BASE,
    "endpoint": PATH,
    "pagination": "page + limit",
    "products_rows": len(rows),
    "pagination_complete": True,
    "duplicate_code_group_count": len(collisions),
    "duplicate_code_groups": collisions,
    "write_requests_made": 0,
    "ro_app_data_mutated": False,
    "interpretation": "REVIEW_REQUIRED: identical product codes are candidates for review; this report does not assume that code uniqueness is required by RO App.",
}
report["report_sha256"] = hashlib.sha256(
    json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()

with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(report, handle, ensure_ascii=False, indent=2)

print("=== MARSEL V22.1 / PRODUCT CODE COLLISION AUDIT / READ ONLY ===")
print(f"ENDPOINT={PATH}")
print(f"PRODUCTS_ROWS={len(rows)}")
print(f"DUPLICATE_CODE_GROUP_COUNT={len(collisions)}")
print("WRITE_REQUESTS_MADE=0")
print("RO_APP_DATA_MUTATED=False")
print(f"REPORT={OUT}")
print(f"REPORT_SHA256={report['report_sha256']}")
print("RESULT=REVIEW_REQUIRED; NO RO APP DATA CREATED, UPDATED OR DELETED")
