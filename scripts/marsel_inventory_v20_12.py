#!/usr/bin/env python3
"""MARSEL V20.12 — full list inventory, READ ONLY.

Uses the endpoint/pagination contract established by V20.11:
  - non-empty entities: page + limit=100
  - empty entities: page + page_size=100
No POST/PUT/PATCH/DELETE requests are made.

The resulting JSON is written only to the GitHub Actions workspace and uploaded
as an artifact by the workflow; it is never committed to the repository.
"""
import hashlib
import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
OUT = os.environ.get("MARSEL_INVENTORY_OUTPUT", "marsel-full-inventory-v20-12.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "30"))
PAGE_SIZE = int(os.environ.get("MARSEL_PAGE_SIZE", "100"))
MAX_PAGES = int(os.environ.get("MARSEL_MAX_PAGES", "1000"))
TARGETS = [
    ("orders", "/orders"),
    ("services", "/catalog/services"),
    ("products", "/catalog/products"),
    ("bundles", "/catalog/bundles"),
    ("inquiries", "/inquiries"),
    ("bookings", "/bookings"),
    ("estimates", "/estimates"),
    ("invoices", "/invoices"),
]


def get(path, params):
    url = BASE + path
    if params:
        url += "?" + urlencode(params)
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Accept": "application/json",
            "User-Agent": "MARSEL-Audit-V20.12",
        },
        method="GET",
    )
    started = time.time()
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            raw = response.read()
            payload = json.loads(raw.decode("utf-8"))
            return response.status, payload, round(time.time() - started, 3), None
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:2000]
        return exc.code, None, round(time.time() - started, 3), body
    except (URLError, TimeoutError, ValueError) as exc:
        return None, None, round(time.time() - started, 3), str(exc)


def rows(payload):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in (
        "data", "items", "results", "orders", "services", "products",
        "bundles", "inquiries", "bookings", "estimates", "invoices",
    ):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    for key in ("data", "result"):
        value = payload.get(key)
        if isinstance(value, dict):
            nested = rows(value)
            if nested:
                return nested
    return []


def ident(item):
    if not isinstance(item, dict):
        return None
    for key in ("id", "ID", "uuid"):
        if item.get(key) is not None:
            return item[key]
    return None


def stable_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value):
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def main():
    if not KEY:
        print("ROAPP_API_KEY is required", file=sys.stderr)
        return 2
    if PAGE_SIZE <= 0 or MAX_PAGES <= 0:
        print("MARSEL_PAGE_SIZE and MARSEL_MAX_PAGES must be positive", file=sys.stderr)
        return 2

    report = {
        "version": "20.12",
        "readonly": True,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "method_policy": {
            "allowed": ["GET"],
            "forbidden": ["POST", "PUT", "PATCH", "DELETE"],
        },
        "contract": {
            "pagination": "page + limit=100 for populated endpoints",
            "empty_endpoint_probe": "page + page_size=100",
            "max_pages": MAX_PAGES,
        },
        "targets": [],
    }

    total_records = 0
    total_pages = 0
    failures = 0

    for entity, path in TARGETS:
        # V20.11 established that page=1&limit=100 is the canonical populated
        # endpoint contract. Probe page 1 first; if empty, retain the empty
        # classification without inventing records.
        status, payload, elapsed, error = get(path, {"page": 1, "limit": PAGE_SIZE})
        first_rows = rows(payload) if status == 200 else []
        if status == 200 and not first_rows:
            status2, payload2, elapsed2, error2 = get(path, {"page": 1, "page_size": PAGE_SIZE})
            if status2 == 200 and rows(payload2):
                status, payload, elapsed, error = status2, payload2, elapsed2, error2
                first_rows = rows(payload2)
                params_mode = "page_size"
            else:
                params_mode = "limit"
        else:
            params_mode = "limit"

        records = []
        pages = []
        seen_page_hashes = set()
        page = 1
        terminal = None

        while page <= MAX_PAGES:
            params = {"page": page, params_mode: PAGE_SIZE}
            if page == 1 and status is not None:
                current_status, current_payload, current_elapsed, current_error = status, payload, elapsed, error
            else:
                current_status, current_payload, current_elapsed, current_error = get(path, params)
            current_rows = rows(current_payload) if current_status == 200 else []
            ids = [ident(item) for item in current_rows]
            page_hash = sha256_json(ids) if ids else None
            repeated = bool(page_hash and page_hash in seen_page_hashes)
            if page_hash:
                seen_page_hashes.add(page_hash)

            pages.append({
                "page": page,
                "params": params,
                "http": current_status,
                "records": len(current_rows),
                "first_ids": ids[:5],
                "last_ids": ids[-5:],
                "repeated_page": repeated,
                "elapsed_s": current_elapsed,
                "error": current_error,
            })

            if current_status != 200:
                terminal = "non_200"
                break
            if not current_rows:
                terminal = "empty_page"
                break
            if repeated:
                terminal = "repeated_page"
                break

            records.extend(current_rows)
            if len(current_rows) < PAGE_SIZE:
                terminal = "short_page"
                break
            page += 1

        if page > MAX_PAGES:
            terminal = "max_pages_reached"

        ids = [ident(item) for item in records]
        unique_ids = {value for value in ids if value is not None}
        missing_ids = sum(value is None for value in ids)
        duplicate_ids = len(ids) - len(unique_ids) - missing_ids
        record_sha = sha256_json(records)
        entry = {
            "entity": entity,
            "endpoint": path,
            "pagination_mode": params_mode,
            "records": records,
            "records_seen": len(records),
            "unique_ids": len(unique_ids),
            "missing_id_records": missing_ids,
            "duplicate_id_candidates": max(0, duplicate_ids),
            "pages": pages,
            "terminal_condition": terminal,
            "inventory_sha256": record_sha,
        }
        report["targets"].append(entry)
        total_records += len(records)
        total_pages += len(pages)
        failures += sum(1 for item in pages if item["http"] not in (200, None))

    report["summary"] = {
        "targets": len(TARGETS),
        "records": total_records,
        "pages": total_pages,
        "request_failures": failures,
        "readonly": True,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "inventory_sha256": sha256_json(report["targets"]),
    }

    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("=== MARSEL V20.12 / FULL INVENTORY / READ ONLY ===")
    print(f"TARGETS={len(TARGETS)}")
    print(f"RECORDS={total_records}")
    print(f"PAGES={total_pages}")
    print(f"REQUEST_FAILURES={failures}")
    print("WRITE_REQUESTS_MADE=0")
    print(f"INVENTORY_SHA256={report['summary']['inventory_sha256']}")
    print(f"REPORT={OUT}")
    print("RESULT=READ_ONLY; V20.12; NO RO APP DATA CREATED, UPDATED OR DELETED")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
