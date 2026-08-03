#!/usr/bin/env python3
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
OUT = os.environ.get("MARSEL_AUDIT_REPORT", "marsel-audit-v5-report.json")
PAGE_SIZE = 100
MAX_PAGES = 10000

if not KEY:
    print("ERROR: ROAPP_API_KEY GitHub Secret is not configured.")
    sys.exit(2)

headers = {"Authorization": f"Bearer {KEY}", "Accept": "application/json"}
client = httpx.Client(headers=headers, timeout=30.0)


def get(path, params=None):
    r = client.get(f"{BASE}{path}", params=params or {})
    if not 200 <= r.status_code < 300:
        print(f"ERROR: GET {path} HTTP={r.status_code}")
        sys.exit(3)
    try:
        return r.json()
    except ValueError:
        print(f"ERROR: GET {path} returned non-JSON response")
        sys.exit(4)


def rows_from(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if isinstance(payload.get("orders"), list):
            return payload["orders"]
        if isinstance(payload.get("data"), list):
            return payload["data"]
    return None


def paging_from(payload):
    return payload.get("paging") if isinstance(payload, dict) else None


def count_missing(rows, predicate):
    return sum(1 for row in rows if predicate(row))


print("=== MARSEL AUDIT V5 / RO APP API / READ ONLY ===")
print(f"BASE={BASE}")

all_rows = []
seen_pages = set()
page = 1
first_paging = None

while page <= MAX_PAGES:
    if page in seen_pages:
        print("ERROR: pagination cycle detected")
        sys.exit(5)
    seen_pages.add(page)

    payload = get("/orders", {"page": page, "pageSize": PAGE_SIZE})
    batch = rows_from(payload)
    if batch is None:
        print("ERROR: Could not identify order list in API response")
        sys.exit(6)
    if page == 1:
        first_paging = paging_from(payload)

    dict_rows = [x for x in batch if isinstance(x, dict)]
    all_rows.extend(dict_rows)

    paging = paging_from(payload)
    total_pages = None
    if isinstance(paging, dict):
        for key in ("pages", "totalPages"):
            value = paging.get(key)
            if isinstance(value, int):
                total_pages = value
                break

    if total_pages is not None:
        if page >= total_pages:
            break
    elif len(batch) < PAGE_SIZE:
        break

    page += 1
else:
    print(f"ERROR: pagination exceeded MAX_PAGES={MAX_PAGES}")
    sys.exit(7)

ids = [x.get("id") for x in all_rows if x.get("id") is not None]
numbers = [x.get("number") for x in all_rows if x.get("number")]
client_ids = [x.get("client", {}).get("id") for x in all_rows if isinstance(x.get("client"), dict) and x["client"].get("id") is not None]

id_counts = Counter(ids)
number_counts = Counter(numbers)
client_counts = Counter(client_ids)

checks = {
    "duplicate_order_ids": sorted(k for k, c in id_counts.items() if c > 1),
    "duplicate_order_numbers": sorted(k for k, c in number_counts.items() if c > 1),
    "missing_id": count_missing(all_rows, lambda x: x.get("id") is None),
    "missing_number": count_missing(all_rows, lambda x: not x.get("number")),
    "missing_client": count_missing(all_rows, lambda x: not isinstance(x.get("client"), dict) or x["client"].get("id") is None),
    "missing_status": count_missing(all_rows, lambda x: not isinstance(x.get("status"), dict) or x["status"].get("id") is None),
    "missing_branch_id": count_missing(all_rows, lambda x: x.get("branch_id") is None),
    "missing_assignee_id": count_missing(all_rows, lambda x: x.get("assignee_id") is None),
    "overdue_flag_true": count_missing(all_rows, lambda x: x.get("overdue") is True),
    "status_overdue_true": count_missing(all_rows, lambda x: x.get("status_overdue") is True),
    "urgent_true": count_missing(all_rows, lambda x: x.get("urgent") is True),
}

# Consistency checks that require no additional API assumptions.
checks["distinct_client_ids_in_orders"] = len(set(client_ids))
checks["clients_reused_by_multiple_orders"] = sum(1 for c in client_counts.values() if c > 1)
checks["orders_with_null_asset"] = count_missing(all_rows, lambda x: x.get("asset") is None)
checks["orders_with_null_payer"] = count_missing(all_rows, lambda x: x.get("payer") is None)
checks["orders_with_null_resource"] = count_missing(all_rows, lambda x: x.get("resource") is None)

sample = all_rows[0] if all_rows else {}
report = {
    "audit": "MARSEL_AUDIT_V5",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "api_base": BASE,
    "scope": {
        "endpoint": "/orders",
        "page_size": PAGE_SIZE,
        "pages_scanned": page,
        "rows_scanned": len(all_rows),
        "paging_keys_page_1": sorted(first_paging.keys()) if isinstance(first_paging, dict) else [],
    },
    "order_schema": {
        "fields": sorted(sample.keys()),
        "field_types": {k: type(v).__name__ for k, v in sample.items()},
    },
    "checks": checks,
    "limitations": [
        "This audit uses only the verified /orders endpoint.",
        "It does not infer or invent undocumented RO App endpoints.",
        "A clean result here does not prove that unrelated RO App entities are error-free.",
        "No RO App data is created, updated, or deleted.",
    ],
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("HTTP /orders=200")
print(f"PAGES_SCANNED={page}")
print(f"ROWS_SCANNED={len(all_rows)}")
print(f"DUPLICATE_ORDER_IDS={len(checks['duplicate_order_ids'])}")
print(f"DUPLICATE_ORDER_NUMBERS={len(checks['duplicate_order_numbers'])}")
print(f"MISSING_CLIENT={checks['missing_client']}")
print(f"MISSING_STATUS={checks['missing_status']}")
print(f"MISSING_BRANCH_ID={checks['missing_branch_id']}")
print(f"MISSING_ASSIGNEE_ID={checks['missing_assignee_id']}")
print(f"OVERDUE_FLAG_TRUE={checks['overdue_flag_true']}")
print(f"STATUS_OVERDUE_TRUE={checks['status_overdue_true']}")
print(f"URGENT_TRUE={checks['urgent_true']}")
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
