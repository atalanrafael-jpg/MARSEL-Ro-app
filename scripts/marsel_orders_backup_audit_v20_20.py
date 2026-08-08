#!/usr/bin/env python3
"""MARSEL V20.20 — current orders backup + data audit, READ ONLY.

Uses only GET /orders. Produces a timestamped JSON backup and a deterministic
SHA-256 manifest. No write HTTP methods are present or used.
"""
import hashlib, json, os, sys, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "30"))
PAGE_SIZE = int(os.environ.get("ROAPP_PAGE_SIZE", "50"))
OUT = Path(os.environ.get("MARSEL_BACKUP_OUTPUT", "marsel-orders-backup-v20-20.json"))
if not KEY:
    print("ROAPP_API_KEY is required", file=sys.stderr)
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

ids = [x.get("id") for x in orders if x.get("id") is not None]
status_ids = [x.get("status_id") for x in orders if x.get("status_id") is not None]
client_ids = [x.get("client_id") for x in orders if x.get("client_id") is not None]
id_counts = Counter(ids)

def missing(field):
    return sum(1 for x in orders if x.get(field) in (None, ""))

summary = {
    "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
    "endpoint": "/orders",
    "pages_read": pages,
    "orders_total": len(orders),
    "unique_order_ids": len(set(ids)),
    "duplicate_order_id_groups": sum(1 for c in id_counts.values() if c > 1),
    "orders_missing_id": missing("id"),
    "orders_missing_client": missing("client_id"),
    "orders_missing_status": missing("status_id"),
    "orders_missing_total_price": missing("total_price"),
    "orders_missing_employee": missing("employee_id"),
    "status_counts": dict(sorted(Counter(status_ids).items(), key=lambda kv: str(kv[0]))),
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
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print("=== MARSEL V20.20 / ORDERS BACKUP + DATA AUDIT / READ ONLY ===")
for key, value in summary.items():
    print(f"{key}={value}")
print(f"BACKUP={OUT}")
print(f"SHA256={report['sha256']}")
print("WRITE_REQUESTS_MADE=0")
print("RO_APP_DATA_MUTATED=False")
print("RESULT=PASS" if not http_errors else "RESULT=FAIL")
