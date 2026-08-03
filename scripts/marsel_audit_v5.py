#!/usr/bin/env python3
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone, date

import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
OUT = os.environ.get("MARSEL_AUDIT_V5_REPORT", "marsel-audit-v5-report.json")
PAGE_SIZE = int(os.environ.get("MARSEL_AUDIT_PAGE_SIZE", "100"))
MAX_PAGES = int(os.environ.get("MARSEL_AUDIT_MAX_PAGES", "10000"))

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


def rows_from(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if isinstance(payload.get("orders"), list):
            return payload["orders"]
        if isinstance(payload.get("data"), list):
            return payload["data"]
    return None


def total_pages_from(payload):
    paging = payload.get("paging") if isinstance(payload, dict) else None
    if isinstance(paging, dict):
        for key in ("total_pages", "totalPages", "pages"):
            value = paging.get(key)
            if isinstance(value, int) and value >= 1:
                return value
    return None


def parse_date(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None


def safe_order(x):
    client = x.get("client") if isinstance(x.get("client"), dict) else {}
    status = x.get("status") if isinstance(x.get("status"), dict) else {}
    order_type = x.get("order_type") if isinstance(x.get("order_type"), dict) else {}
    return {
        "id": x.get("id"),
        "number": x.get("number"),
        "status_id": status.get("id"),
        "status_name": status.get("name"),
        "order_type_id": order_type.get("id"),
        "order_type_name": order_type.get("name"),
        "client_id": client.get("id"),
        "branch_id": x.get("branch_id"),
        "assignee_id": x.get("assignee_id"),
        "manager_id": x.get("manager_id"),
        "created_at": x.get("created_at"),
        "modified_at": x.get("modified_at"),
        "due_date": x.get("due_date"),
        "closed_at": x.get("closed_at"),
        "done_at": x.get("done_at"),
        "overdue": x.get("overdue"),
        "status_overdue": x.get("status_overdue"),
        "urgent": x.get("urgent"),
    }

print("=== MARSEL AUDIT V5 / RO APP API / READ ONLY ===")
print(f"BASE={BASE}")

first = get("/orders", {"page": 1, "pageSize": PAGE_SIZE})
rows = rows_from(first)
if rows is None:
    print("ERROR: Could not identify order list in API response")
    sys.exit(5)

total_pages = total_pages_from(first)
all_rows = [x for x in rows if isinstance(x, dict)]
page = 2
while page <= MAX_PAGES:
    if total_pages is not None and page > total_pages:
        break
    payload = get("/orders", {"page": page, "pageSize": PAGE_SIZE})
    batch = rows_from(payload)
    if not batch:
        break
    all_rows.extend(x for x in batch if isinstance(x, dict))
    new_total = total_pages_from(payload)
    if new_total is not None:
        total_pages = new_total
    else:
        break
    page += 1

pages_scanned = min(page - 1, MAX_PAGES)
complete = total_pages is not None and pages_scanned >= total_pages

def duplicate_values(values):
    return sorted(k for k, c in Counter(values).items() if c > 1)

missing_assignee = [safe_order(x) for x in all_rows if x.get("assignee_id") is None]
overdue_flagged = [safe_order(x) for x in all_rows if x.get("overdue") is True]
status_overdue_flagged = [safe_order(x) for x in all_rows if x.get("status_overdue") is True]

today = datetime.now(timezone.utc).date()
for item in overdue_flagged:
    due = parse_date(item.get("due_date"))
    closed = item.get("closed_at") is not None or item.get("done_at") is not None
    item["diagnostic_due_date_before_today"] = bool(due and due < today)
    item["diagnostic_closed_or_done"] = closed
    item["diagnostic_reason"] = (
        "closed_or_done_but_overdue_flag_true" if closed else
        "due_date_before_today" if due and due < today else
        "no_due_date" if due is None else
        "overdue_flag_without_past_due_date"
    )

report = {
    "audit": "MARSEL_AUDIT_V5",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "api_base": BASE,
    "orders": {
        "http_status": 200,
        "page_size": PAGE_SIZE,
        "total_pages_reported": total_pages,
        "pages_scanned": pages_scanned,
        "rows_scanned": len(all_rows),
        "pagination_complete": complete,
    },
    "checks": {
        "duplicate_order_ids": duplicate_values([x.get("id") for x in all_rows if x.get("id") is not None]),
        "duplicate_order_numbers": duplicate_values([x.get("number") for x in all_rows if x.get("number")]),
        "missing_assignee_id_count": len(missing_assignee),
        "overdue_flag_true_count": len(overdue_flagged),
        "status_overdue_true_count": len(status_overdue_flagged),
    },
    "missing_assignee_orders": missing_assignee,
    "overdue_orders": overdue_flagged,
    "status_overdue_orders": status_overdue_flagged,
    "safety": {
        "personal_client_name_phone_email_excluded": True,
        "writes_performed": False,
        "deletes_performed": False,
        "updates_performed": False,
    },
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("HTTP /orders=200")
print(f"TOTAL_PAGES_REPORTED={total_pages}")
print(f"PAGES_SCANNED={pages_scanned}")
print(f"ROWS_SCANNED={len(all_rows)}")
print(f"PAGINATION_COMPLETE={complete}")
print(f"MISSING_ASSIGNEE_ID={len(missing_assignee)}")
print(f"OVERDUE_FLAG_TRUE={len(overdue_flagged)}")
print(f"STATUS_OVERDUE_TRUE={len(status_overdue_flagged)}")
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
