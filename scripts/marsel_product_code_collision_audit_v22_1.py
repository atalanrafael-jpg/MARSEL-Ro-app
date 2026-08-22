#!/usr/bin/env python3
"""MARSEL V22.2 — product-code ambiguity audit, READ ONLY.

A shared product code is not treated as a data defect unless the records are
identical on the available product identity fields. RO App does not document
code uniqueness as a global invariant, so the audit reports shared codes for
review without making the unified quality gate fail on legitimate variants.
No write request is made.
"""
import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict

import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
OUT = os.environ.get("MARSEL_COLLISION_OUTPUT", "marsel-product-code-collisions-v22-2-readonly.json")
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
        "User-Agent": "MARSEL-V22.2-READONLY",
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
    if code is not None and str(code).strip():
        by_code[str(code).strip()].append(item)

shared_groups = {}
exact_duplicate_groups = {}
for code, items in sorted(by_code.items()):
    if len(items) <= 1:
        continue
    records = [
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
    shared_groups[code] = records
    identities = {
        (
            str(item.get("name") or item.get("title") or "").strip().casefold(),
            item.get("category_id"),
            str(item.get("sku") or "").strip().casefold(),
            item.get("is_serial"),
            str(item.get("uom") or "").strip().casefold(),
        )
        for item in items
    }
    if len(identities) == 1:
        exact_duplicate_groups[code] = records

report = {
    "version": "22.2",
    "mode": "READ_ONLY",
    "api_base": BASE,
    "endpoint": PATH,
    "pagination": "page + limit",
    "products_rows": len(rows),
    "pagination_complete": True,
    "shared_code_group_count": len(shared_groups),
    "exact_duplicate_identity_group_count": len(exact_duplicate_groups),
    "shared_code_groups": shared_groups,
    "exact_duplicate_identity_groups": exact_duplicate_groups,
    "gate_relevant_issue_count": len(exact_duplicate_groups),
    "write_requests_made": 0,
    "ro_app_data_mutated": False,
    "interpretation": "Shared codes are informational review items because RO App documentation does not establish global code uniqueness. Only exact duplicate identity groups are gate-relevant.",
}
raw = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
report["report_sha256"] = hashlib.sha256(raw).hexdigest()
with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(report, handle, ensure_ascii=False, indent=2)

print("=== MARSEL V22.2 / PRODUCT CODE AMBIGUITY AUDIT / READ ONLY ===")
print(f"ENDPOINT={PATH}")
print(f"PRODUCTS_ROWS={len(rows)}")
print(f"SHARED_CODE_GROUP_COUNT={len(shared_groups)}")
print(f"EXACT_DUPLICATE_IDENTITY_GROUP_COUNT={len(exact_duplicate_groups)}")
print("WRITE_REQUESTS_MADE=0")
print("RO_APP_DATA_MUTATED=False")
print(f"REPORT={OUT}")
print(f"REPORT_SHA256={report['report_sha256']}")
print("RESULT=PASS" if not exact_duplicate_groups else "RESULT=REVIEW_REQUIRED")
