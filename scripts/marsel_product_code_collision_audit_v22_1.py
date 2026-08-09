#!/usr/bin/env python3
"""MARSEL V22.1 — product-code collision audit, READ ONLY.

Purpose: inspect the 11 product code collision groups found by V22 and
produce a review report with product IDs, names, SKUs, categories and
serial flags. No write request is made.
"""
import hashlib, json, os, sys, time
from collections import defaultdict
import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
OUT = os.environ.get("MARSEL_COLLISION_OUTPUT", "marsel-product-code-collisions-v22-1-readonly.json")
PAGE_SIZE = int(os.environ.get("MARSEL_PAGE_SIZE", "50"))
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "30"))
INTERVAL = float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34"))

if not KEY:
    print("ROAPP_API_KEY is required", file=sys.stderr); raise SystemExit(2)

client = httpx.Client(headers={"Authorization": f"Bearer {KEY}", "Accept": "application/json", "User-Agent": "MARSEL-V22.1-READONLY"}, timeout=TIMEOUT)
last = 0.0
rows = []
page = 1
while True:
    wait = INTERVAL - (time.monotonic() - last)
    if wait > 0: time.sleep(wait)
    last = time.monotonic()
    r = client.get(f"{BASE}/products", params={"page": page, "pageSize": PAGE_SIZE})
    r.raise_for_status()
    payload = r.json()
    batch = payload.get("data", []) if isinstance(payload, dict) else payload
    paging = payload.get("paging", {}) if isinstance(payload, dict) else {}
    if not isinstance(batch, list):
        raise RuntimeError("Unexpected /products response shape")
    rows.extend(x for x in batch if isinstance(x, dict))
    total_pages = paging.get("total_pages") or paging.get("totalPages")
    if total_pages is not None:
        if page >= int(total_pages): break
    elif len(batch) < PAGE_SIZE:
        break
    page += 1

by_code = defaultdict(list)
for x in rows:
    code = x.get("code")
    if code is not None and str(code).strip() != "": by_code[str(code)].append(x)

collisions = {}
for code, items in sorted(by_code.items()):
    if len(items) > 1:
        collisions[code] = [{
            "id": x.get("id"),
            "name": x.get("name") or x.get("title"),
            "sku": x.get("sku"),
            "category_id": x.get("category_id"),
            "is_serial": x.get("is_serial"),
            "uom": x.get("uom"),
        } for x in items]

report = {
    "version": "22.1",
    "mode": "READ_ONLY",
    "api_base": BASE,
    "products_rows": len(rows),
    "pagination_complete": True,
    "duplicate_code_group_count": len(collisions),
    "duplicate_code_groups": collisions,
    "write_requests_made": 0,
    "ro_app_data_mutated": False,
    "interpretation": "REVIEW_REQUIRED: identical product codes are candidates for review; this report does not assume that code uniqueness is required by RO App.",
}
report["report_sha256"] = hashlib.sha256(json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
with open(OUT, "w", encoding="utf-8") as f: json.dump(report, f, ensure_ascii=False, indent=2)
print("=== MARSEL V22.1 / PRODUCT CODE COLLISION AUDIT / READ ONLY ===")
print(f"PRODUCTS_ROWS={len(rows)}")
print(f"DUPLICATE_CODE_GROUP_COUNT={len(collisions)}")
print(f"WRITE_REQUESTS_MADE=0")
print(f"RO_APP_DATA_MUTATED=False")
print(f"REPORT={OUT}")
print(f"REPORT_SHA256={report['report_sha256']}")
print("RESULT=REVIEW_REQUIRED; NO RO APP DATA CREATED, UPDATED OR DELETED")
