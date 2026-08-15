#!/usr/bin/env python3
"""MARSEL full read-only backup controller.

Consumes canonical V20.31 inventory and reads only explicitly documented GET
endpoints. Collection responses are paginated to the first short page; valid
singleton/object responses are captured as one record. Any HTTP/schema/
pagination failure makes the backup incomplete. No write request is possible
in this program.
"""
from __future__ import annotations
import hashlib, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
INVENTORY = Path(os.environ.get("MARSEL_INVENTORY_INPUT", "marsel-api-inventory-v20-31.json"))
OUT = Path(os.environ.get("MARSEL_FULL_BACKUP_OUTPUT", "marsel-full-readonly-backup-v1.json"))
PAGE_SIZE = min(max(int(os.environ.get("ROAPP_PAGE_SIZE", "50")), 1), 50)
MAX_PAGES = int(os.environ.get("MARSEL_MAX_PAGES_PER_ENDPOINT", "10000"))
INTERVAL = max(float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34")), 0.34)
if not KEY:
    raise SystemExit("ROAPP_API_KEY is required")
if not INVENTORY.exists():
    raise SystemExit(f"inventory missing: {INVENTORY}")
inv = json.loads(INVENTORY.read_text(encoding="utf-8"))

items = []
def walk(x):
    if isinstance(x, dict):
        method = str(x.get("method", "")).upper()
        path = x.get("path") or x.get("endpoint") or x.get("url")
        evidence = str(x.get("evidence", "")).upper()
        if method == "GET" and isinstance(path, str) and path.startswith("/") and "DOCUMENTATION_CONFIRMED" in evidence:
            items.append(x)
        for v in x.values():
            walk(v)
    elif isinstance(x, list):
        for v in x:
            walk(v)
walk(inv)

paths = []
for x in items:
    p = x.get("path") or x.get("endpoint") or x.get("url")
    if isinstance(p, str) and "{" not in p and "}" not in p:
        p = p.split("?")[0]
        if p not in paths:
            paths.append(p)

headers = {
    "Authorization": f"Bearer {KEY}",
    "Accept": "application/json",
    "User-Agent": "MARSEL-Full-Readonly-Backup-v3",
}
results = []
write_requests = 0

with httpx.Client(timeout=20) as c:
    for p in sorted(paths):
        rows = []
        page = 1
        endpoint_ok = True
        endpoint_error = None
        response_kind = None
        pages_read = 0
        while page <= MAX_PAGES:
            try:
                r = c.get(BASE + p, headers=headers, params={"page": page, "limit": PAGE_SIZE})
                if r.status_code != 200:
                    endpoint_ok = False
                    endpoint_error = f"HTTP {r.status_code}: {r.text[:500]}"
                    break
                payload = r.json()
                if isinstance(payload, dict):
                    data = payload.get("data")
                    if not isinstance(data, list):
                        data = payload.get("items")
                    if isinstance(data, list):
                        response_kind = "collection"
                    else:
                        # Documented GET endpoints may legitimately return a
                        # singleton object (company/license/etc.). Capture it
                        # instead of incorrectly classifying it as a failed
                        # collection response.
                        data = [payload]
                        response_kind = "singleton"
                elif isinstance(payload, list):
                    data = payload
                    response_kind = "collection"
                else:
                    endpoint_ok = False
                    endpoint_error = "response is neither a JSON object nor a JSON list"
                    break

                rows.extend(x for x in data if isinstance(x, dict))
                pages_read += 1
                if response_kind == "singleton" or len(data) < PAGE_SIZE:
                    break
                page += 1
                time.sleep(INTERVAL)
            except Exception as e:
                endpoint_ok = False
                endpoint_error = f"{type(e).__name__}: {e}"
                break
        else:
            endpoint_ok = False
            endpoint_error = f"pagination exceeded MARSEL_MAX_PAGES_PER_ENDPOINT={MAX_PAGES}"

        result = {
            "path": p,
            "ok": endpoint_ok,
            "response_kind": response_kind,
            "pages_read": pages_read,
            "records": len(rows),
            "data": rows if endpoint_ok else [],
            "error": endpoint_error,
        }
        results.append(result)
        print(f"ENDPOINT path={p} ok={endpoint_ok} kind={response_kind} pages={pages_read} records={len(rows)}")
        if endpoint_error:
            print(f"ENDPOINT_ERROR path={p} error={endpoint_error}")
        time.sleep(INTERVAL)

failed = [x for x in results if not x["ok"]]
complete = bool(paths) and not failed
report = {
    "version": "3",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "inventory": str(INVENTORY),
    "documented_get_endpoints": paths,
    "successful_endpoints": len(results) - len(failed),
    "failed_endpoints": len(failed),
    "total_records": sum(x["records"] for x in results),
    "write_requests_made": write_requests,
    "ro_app_data_mutated": False,
    "complete": complete,
    "results": results,
}
canonical = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
report["sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"DOCUMENTED_GET_ENDPOINTS={len(paths)}")
print(f"SUCCESS={len(results)-len(failed)} FAILED={len(failed)} RECORDS={report['total_records']}")
print("WRITE_REQUESTS_MADE=0")
print("RO_APP_DATA_MUTATED=False")
print("RESULT=PASS" if complete else "RESULT=INCOMPLETE")
if not complete:
    raise SystemExit(2)
