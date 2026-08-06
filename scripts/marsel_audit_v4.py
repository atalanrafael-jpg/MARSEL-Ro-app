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


def nested_id(obj, key):
    value = obj.get(key)
    return value.get("id") if isinstance(value, dict) else None


def nested_name(obj, key):
    value = obj.get(key)
    return value.get("name") if isinstance(value, dict) else None


def parse_date(value):
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def order_summary(x):
    return {
        "id": x.get("id"),
        "number": x.get("number"),
        "status_id": nested_id(x, "status"),
        "status_name": nested_name(x, "status"),
        "order_type_id": nested_id(x, "order_type"),
        "order_type_name": nested_name(x, "order_type"),
        "client_id": nested_id(x, "client"),
        "manager_id": x.get("manager_id"),
        "assignee_id": x.get("assignee_id"),
        "branch_id": x.get("branch_id"),
        "due_date": x.get("due_date"),
        "overdue": x.get("overdue"),
        "status_overdue": x.get("status_overdue"),
        "urgent": x.get("urgent"),
        "created_at": x.get("created_at"),
        "modified_at": x.get("modified_at"),
        "done_at": x.get("done_at"),
        "closed_at": x.get("closed_at"),
    }


print("=== MARSEL AUDIT V4.1 / RO APP API / READ ONLY ===")
print(f"BASE={BASE}")

first = get("/orders", {"page": 1, "pageSize": PAGE_SIZE})
rows = extract_rows(first, ["orders"])
if rows is None:
    print("ERROR: Could not identify order list in API response")
    sys.exit(5)

paging = first.get("paging") if isinstance(first, dict) else None
sample = rows[0] if rows and isinstance(rows[0], dict) else {}

total_pages = None
if isinstance(paging, dict):
    for key in ("total_pages", "totalPages", "pages"):
        value = paging.get(key)
        if isinstance(value, int) and value >= 1:
            total_pages = value
            break

report = {
    "audit": "MARSEL_AUDIT_V4.1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "write_methods_used": 0,
    "delete_methods_used": 0,
    "api_base": BASE,
    "orders": {
        "http_status": 200,
        "page_size": PAGE_SIZE,
        "first_page_count": len(rows),
        "paging_keys": sorted(paging.keys()) if isinstance(paging, dict) else [],
        "total_pages_reported": total_pages,
        "order_fields": sorted(sample.keys()),
        "field_types": {k: safe_type(v) for k, v in sample.items()},
        "null_fields_in_sample": sorted(k for k, v in sample.items() if v is None),
    },
    "checks": {},
    "details": {},
}

all_rows = [x for x in rows if isinstance(x, dict)]
page = 2
while page <= MAX_PAGES:
    if total_pages is not None and page > total_pages:
        break
    payload = get("/orders", {"page": page, "pageSize": PAGE_SIZE})
    batch = extract_rows(payload, ["orders"])
    if not batch:
        break
    all_rows.extend(x for x in batch if isinstance(x, dict))
    new_paging = payload.get("paging") if isinstance(payload, dict) else None
    if isinstance(new_paging, dict):
        for key in ("total_pages", "totalPages", "pages"):
            value = new_paging.get(key)
            if isinstance(value, int) and value >= 1:
                total_pages = value
                break
    else:
        break
    page += 1

pages_scanned = min(page - 1, MAX_PAGES)
report["orders"]["pages_scanned"] = pages_scanned
report["orders"]["rows_scanned"] = len(all_rows)
report["orders"]["pagination_complete"] = total_pages is not None and pages_scanned >= total_pages
report["orders"]["max_pages_reached"] = pages_scanned >= MAX_PAGES

ids = [x.get("id") for x in all_rows if x.get("id") is not None]
numbers = [x.get("number") for x in all_rows if x.get("number")]
duplicate_ids = sorted(k for k, c in Counter(ids).items() if c > 1)
duplicate_numbers = sorted(k for k, c in Counter(numbers).items() if c > 1)

missing_assignee = [x for x in all_rows if x.get("assignee_id") is None]
now = datetime.now(timezone.utc)
malformed_dates = Counter()
past_due = []
active_past_due = []
closed_past_due = []
due_missing = []
overdue_mismatches = []
status_overdue_mismatches = []

# Closed status IDs are discovered from the API response rather than hard-coded.
closed_status_ids = {
    nested_id(x, "status")
    for x in all_rows
    if nested_name(x, "status") and nested_name(x, "status").strip().lower() == "закрыт"
}

for x in all_rows:
    for field in (
        "created_at", "modified_at", "due_date", "done_at", "closed_at",
        "scheduled_for", "scheduled_to", "warranty_date",
    ):
        value = x.get(field)
        if value not in (None, "") and parse_date(value) is None:
            malformed_dates[field] += 1

    due_raw = x.get("due_date")
    due = parse_date(due_raw)
    summary = order_summary(x)
    if due_raw in (None, ""):
        due_missing.append(summary)
    elif due is None:
        continue
    elif due < now:
        past_due.append(summary)
        if nested_id(x, "status") in closed_status_ids:
            closed_past_due.append(summary)
        else:
            active_past_due.append(summary)

        if x.get("overdue") is not True:
            overdue_mismatches.append(summary)
    elif x.get("overdue") is True:
        overdue_mismatches.append(summary)

    if x.get("status_overdue") is True and x.get("overdue") is not True:
        status_overdue_mismatches.append(summary)

report["checks"]["duplicate_order_ids"] = duplicate_ids
report["checks"]["duplicate_order_numbers"] = duplicate_numbers
report["checks"]["missing_id"] = sum(1 for x in all_rows if x.get("id") is None)
report["checks"]["missing_number"] = sum(1 for x in all_rows if not x.get("number"))
report["checks"]["missing_client"] = sum(1 for x in all_rows if not isinstance(x.get("client"), dict) or x["client"].get("id") is None)
report["checks"]["missing_status"] = sum(1 for x in all_rows if not isinstance(x.get("status"), dict) or x["status"].get("id") is None)
report["checks"]["missing_order_type"] = sum(1 for x in all_rows if not isinstance(x.get("order_type"), dict) or x["order_type"].get("id") is None)
report["checks"]["missing_branch_id"] = sum(1 for x in all_rows if x.get("branch_id") is None)
report["checks"]["missing_assignee_id"] = len(missing_assignee)
report["checks"]["missing_manager_id"] = sum(1 for x in all_rows if x.get("manager_id") is None)
report["checks"]["missing_total"] = sum(1 for x in all_rows if x.get("total") in (None, ""))
report["checks"]["overdue_flag_true"] = sum(1 for x in all_rows if x.get("overdue") is True)
report["checks"]["status_overdue_true"] = sum(1 for x in all_rows if x.get("status_overdue") is True)
report["checks"]["urgent_true"] = sum(1 for x in all_rows if x.get("urgent") is True)
report["checks"]["malformed_date_counts"] = dict(sorted(malformed_dates.items()))
report["checks"]["records_with_due_date_in_past"] = len(past_due)
report["checks"]["active_records_with_due_date_in_past"] = len(active_past_due)
report["checks"]["closed_records_with_due_date_in_past"] = len(closed_past_due)
report["checks"]["records_missing_due_date"] = len(due_missing)
report["checks"]["overdue_flag_inconsistencies"] = len(overdue_mismatches)
report["checks"]["status_overdue_inconsistencies"] = len(status_overdue_mismatches)

report["details"]["missing_assignee"] = [order_summary(x) for x in missing_assignee]
report["details"]["active_past_due"] = active_past_due
report["details"]["closed_past_due"] = closed_past_due
report["details"]["missing_due_date"] = due_missing
report["details"]["overdue_inconsistencies"] = overdue_mismatches
report["details"]["status_overdue_inconsistencies"] = status_overdue_mismatches
report["details"]["closed_status_ids_detected"] = sorted(x for x in closed_status_ids if x is not None)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("HTTP /orders=200")
print(f"PAGE_SIZE={PAGE_SIZE}")
print(f"TOTAL_PAGES_REPORTED={total_pages if total_pages is not None else 'unknown'}")
print(f"PAGES_SCANNED={pages_scanned}")
print(f"ROWS_SCANNED={len(all_rows)}")
print(f"PAGINATION_COMPLETE={report['orders']['pagination_complete']}")
print(f"DUPLICATE_ORDER_IDS={len(duplicate_ids)}")
print(f"DUPLICATE_ORDER_NUMBERS={len(duplicate_numbers)}")
print(f"MISSING_CLIENT={report['checks']['missing_client']}")
print(f"MISSING_STATUS={report['checks']['missing_status']}")
print(f"MISSING_ORDER_TYPE={report['checks']['missing_order_type']}")
print(f"MISSING_BRANCH_ID={report['checks']['missing_branch_id']}")
print(f"MISSING_ASSIGNEE_ID={report['checks']['missing_assignee_id']}")
print(f"MISSING_MANAGER_ID={report['checks']['missing_manager_id']}")
print(f"MISSING_TOTAL={report['checks']['missing_total']}")
print(f"OVERDUE_FLAG_TRUE={report['checks']['overdue_flag_true']}")
print(f"ACTIVE_PAST_DUE={report['checks']['active_records_with_due_date_in_past']}")
print(f"CLOSED_PAST_DUE={report['checks']['closed_records_with_due_date_in_past']}")
print(f"MISSING_DUE_DATE={report['checks']['records_missing_due_date']}")
print(f"OVERDUE_INCONSISTENCIES={report['checks']['overdue_flag_inconsistencies']}")
print(f"STATUS_OVERDUE_INCONSISTENCIES={report['checks']['status_overdue_inconsistencies']}")
print(f"MALFORMED_DATE_FIELDS={len(malformed_dates)}")
print(f"REPORT={OUT}")
print("READONLY=True")
print("WRITE_METHODS_USED=0")
print("DELETE_METHODS_USED=0")
print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
