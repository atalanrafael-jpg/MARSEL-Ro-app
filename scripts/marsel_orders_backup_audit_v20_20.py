#!/usr/bin/env python3
"""MARSEL V20.20 — current orders backup + data audit, READ ONLY.

Uses only GET /orders. Produces a timestamped JSON backup and a deterministic
SHA-256 manifest. No write HTTP methods are present or used.

The RO App /orders response uses nested objects for client, status and total
and assignee/manager IDs for employee responsibility. The audit therefore
checks the actual response schema instead of looking only for legacy flat
field names such as client_id/status_id/total_price/employee_id.
"""
import hashlib, json, os, sys, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from cryptography.fernet import Fernet
import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "30"))
PAGE_SIZE = int(os.environ.get("ROAPP_PAGE_SIZE", "50"))
OUT = Path(os.environ.get("MARSEL_BACKUP_OUTPUT", "marsel-orders-backup-v20-20.json"))
BACKUP_ENCRYPTION_KEY = os.environ.get("MARSEL_BACKUP_ENCRYPTION_KEY", "")
if not KEY:
    print("ROAPP_API_KEY is required", file=sys.stderr)
    raise SystemExit(1)
if not BACKUP_ENCRYPTION_KEY:
    print("MARSEL_BACKUP_ENCRYPTION_KEY is required", file=sys.stderr)
    raise SystemExit(1)
try:
    FERNET = Fernet(BACKUP_ENCRYPTION_KEY.encode("utf-8"))
except Exception:
    print("MARSEL_BACKUP_ENCRYPTION_KEY must be a valid Fernet key", file=sys.stderr)
    raise SystemExit(1)
if PAGE_SIZE < 1 or PAGE_SIZE > 50:
    raise SystemExit("ROAPP_PAGE_SIZE must be 1..50")

headers = {
    "Authorization": f"Bearer {KEY}",
    "Accept": "application/json",
    "User-Agent": "MARSEL-V20.20-Readonly-Backup",
}

orders = []
pages = 0
http_errors = 0
with httpx.Client(timeout=TIMEOUT) as client:
    page = 1
    while True:
        try:
            r = client.get(f"{BASE}/orders", headers=headers, params={"page": page, "limit": PAGE_SIZE})
            if r.status_code != 200:
                http_errors += 1
                print(f"PAGE={page} HTTP={r.status_code}", file=sys.stderr)
                raise SystemExit(1)
            payload = r.json()
        except Exception as exc:
            print(f"PAGE={page} ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
            raise SystemExit(1)
        rows = payload.get("data") if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            print("Invalid /orders response: data is not a list", file=sys.stderr)
            raise SystemExit(1)
        orders.extend(x for x in rows if isinstance(x, dict))
        pages += 1
        if len(rows) < PAGE_SIZE:
            break
        page += 1
        time.sleep(0.35)

def nested(obj, *keys):
    value = obj
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value

def present(value):
    return value not in (None, "", [])

def first_present(order, *paths):
    for path in paths:
        value = nested(order, *path)
        if present(value):
            return value
    return None

ids = [x.get("id") for x in orders if present(x.get("id"))]
status_ids = [
    value for value in (first_present(x, ("status", "id"), ("status_id",)) for x in orders)
    if present(value)
]
client_ids = [
    value for value in (first_present(x, ("client", "id"), ("client_id",)) for x in orders)
    if present(value)
]
id_counts = Counter(ids)
status_names = Counter(
    nested(x, "status", "name") for x in orders if present(nested(x, "status", "name"))
)
order_type_names = Counter(
    nested(x, "order_type", "name") for x in orders if present(nested(x, "order_type", "name"))
)

def missing_id():
    return sum(1 for x in orders if not present(x.get("id")))

def missing_client():
    return sum(1 for x in orders if not present(first_present(x, ("client", "id"), ("client_id",))))

def missing_status():
    return sum(1 for x in orders if not present(first_present(x, ("status", "id"), ("status_id",))))

def missing_total():
    return sum(1 for x in orders if not present(first_present(x, ("total",), ("total_price",), ("estimated_price",))))

def missing_employee():
    return sum(1 for x in orders if not present(first_present(
        x, ("assignee_id",), ("manager_id",), ("employee_id",), ("created_by_id",)
    )))

summary = {
    "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
    "endpoint": "/orders",
    "pages_read": pages,
    "orders_total": len(orders),
    "unique_order_ids": len(set(ids)),
    "duplicate_order_id_groups": sum(1 for c in id_counts.values() if c > 1),
    "orders_missing_id": missing_id(),
    "orders_missing_client": missing_client(),
    "orders_missing_status": missing_status(),
    "orders_missing_total_price": missing_total(),
    "orders_missing_employee": missing_employee(),
    "status_counts": dict(sorted(status_names.items(), key=lambda kv: kv[0])),
    "order_type_counts": dict(sorted(order_type_names.items(), key=lambda kv: kv[0])),
    "client_id_count": len(set(client_ids)),
    "http_errors": http_errors,
    "write_requests_made": 0,
    "ro_app_data_mutated": False,
}

report = {
    "version": "20.20",
    "readonly": True,
    "api_base": BASE,
    "summary": summary,
    "orders": orders,
}
canonical = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
report["sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
plaintext_backup = json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")
encrypted_backup = FERNET.encrypt(plaintext_backup)
OUT.write_bytes(encrypted_backup)

print("=== MARSEL V20.20 / ORDERS BACKUP + DATA AUDIT / READ ONLY ===")
for key, value in summary.items():
    print(f"{key}={value}")
print(f"BACKUP={OUT}")
print(f"SHA256={report['sha256']}")
print("WRITE_REQUESTS_MADE=0")
print("RO_APP_DATA_MUTATED=False")
print("RESULT=PASS" if not http_errors else "RESULT=FAIL")
