#!/usr/bin/env python3
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
OUT = os.environ.get("MARSEL_AUDIT_REPORT", "marsel-audit-v4-report.json")

if not KEY:
    print("ERROR: ROAPP_API_KEY GitHub Secret is not configured.")
    sys.exit(2)

headers = {"Authorization": f"Bearer {KEY}", "Accept": "application/json"}


def get(path, params=None):
    r = httpx.get(f"{BASE}{path}", params=params or {}, headers=headers, timeout=30.0)
    if not 200 <= r.status_code < 300:
        print(f"ERROR: GET {path} HTTP={r.status_code}")
        sys.exit(3)
    try:
        return r.json()
    except ValueError:
        print(f"ERROR: GET {path} returned non-JSON response")
        sys.exit(4)


def extract_rows(payload, preferred):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in preferred:
            if isinstance(payload.get(key), list):
                return payload[key]
        if isinstance(payload.get("data"), list):
            return payload["data"]
    return None


def safe_type(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int) and not isinstance(v, bool):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "list"
    if isinstance(v, dict):
        return "object"
    return type(v).__name__


print("=== MARSEL AUDIT V4 / RO APP API / READ ONLY ===")
print(f"BASE={BASE}")

first = get("/orders", {"page": 1, "pageSize": 100})
rows = extract_rows(first, ["orders"])
if rows is None:
    print("ERROR: Could not identify order list in API response")
    sys.exit(5)

paging = first.get("paging") if isinstance(first, dict) else None
sample = rows[0] if rows and isinstance(rows[0], dict) else {}

report = {
    "audit": "MARSEL_AUDIT_V4",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "api_base": BASE,
    "orders": {
        "http_status": 200,
        "sample_count": len(rows),
        "paging_keys": sorted(paging.keys()) if isinstance(paging, dict) else [],
        "order_fields": sorted(sample.keys()),
        "field_types": {k: safe_type(v) for k, v in sample.items()},
        "null_fields_in_sample": sorted(k for k, v in sample.items() if v is None),
    },
    "checks": {},
}

# Paginate only if the API exposes a usable total/pages indicator.
all_rows = list(rows)
page = 2
max_pages = 1000
while isinstance(paging, dict) and page <= max_pages:
    total_pages = paging.get("pages") or paging.get("totalPages")
    if isinstance(total_pages, int) and page > total_pages:
        break
    if not total_pages and len(rows) < 100:
        break
    payload = get("/orders", {"page": page, "pageSize": 100})
    batch = extract_rows(payload, ["orders"])
    if not batch:
        break
    all_rows.extend(x for x in batch if isinstance(x, dict))
    new_paging = payload.get("paging") if isinstance(payload, dict) else None
    if not isinstance(new_paging, dict):
        break
    paging = new_paging
    page += 1

report["orders"]["rows_scanned"] = len(all_rows)

ids = [x.get("id") for x in all_rows if x.get("id") is not None]
numbers = [x.get("number") for x in all_rows if x.get("number")]
report["checks"]["duplicate_order_ids"] = sorted(k for k, c in Counter(ids).items() if c > 1)
report["checks"]["duplicate_order_numbers"] = sorted(k for k, c in Counter(numbers).items() if c > 1)
report["checks"]["missing_id"] = sum(1 for x in all_rows if x.get("id") is None)
report["checks"]["missing_number"] = sum(1 for x in all_rows if not x.get("number"))
report["checks"]["missing_client"] = sum(1 for x in all_rows if not isinstance(x.get("client"), dict) or x["client"].get("id") is None)
report["checks"]["missing_status"] = sum(1 for x in all_rows if not isinstance(x.get("status"), dict) or x["status"].get("id") is None)
report["checks"]["missing_branch_id"] = sum(1 for x in all_rows if x.get("branch_id") is None)
report["checks"]["missing_assignee_id"] = sum(1 for x in all_rows if x.get("assignee_id") is None)
report["checks"]["overdue_flag_true"] = sum(1 for x in all_rows if x.get("overdue") is True)
report["checks"]["status_overdue_true"] = sum(1 for x in all_rows if x.get("status_overdue") is True)
report["checks"]["urgent_true"] = sum(1 for x in all_rows if x.get("urgent") is True)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"HTTP /orders=200")
print(f"ROWS_SCANNED={len(all_rows)}")
print(f"DUPLICATE_ORDER_IDS={len(report['checks']['duplicate_order_ids'])}")
print(f"DUPLICATE_ORDER_NUMBERS={len(report['checks']['duplicate_order_numbers'])}")
print(f"MISSING_CLIENT={report['checks']['missing_client']}")
print(f"MISSING_STATUS={report['checks']['missing_status']}")
print(f"MISSING_BRANCH_ID={report['checks']['missing_branch_id']}")
print(f"MISSING_ASSIGNEE_ID={report['checks']['missing_assignee_id']}")
print(f"OVERDUE_FLAG_TRUE={report['checks']['overdue_flag_true']}")
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
