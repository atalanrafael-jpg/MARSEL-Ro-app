#!/usr/bin/env python3
"""MARSEL V22.1 — comprehensive read-only data-quality audit.

Audits every paginated row in the principal business collections exposed by the
RoApp v2 API. GET only: no POST/PUT/PATCH/DELETE requests are made.
The audit is diagnostic; it never changes RoApp data.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "30"))
PAGE_SIZE = min(int(os.environ.get("MARSEL_PAGE_SIZE", "50")), 50)
MIN_INTERVAL = max(float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34")), 0.34)
OUT = Path(os.environ.get("MARSEL_DATA_QUALITY_OUTPUT", "marsel-data-quality-v22-readonly.json"))
MAX_PAGES = int(os.environ.get("MARSEL_MAX_PAGES", "10000"))

if not KEY:
    print("ROAPP_API_KEY is required", file=sys.stderr)
    raise SystemExit(1)

HEADERS = {
    "Authorization": f"Bearer {KEY}",
    "Accept": "application/json",
    "User-Agent": "MARSEL-Data-Quality-V22-READONLY",
}

COLLECTIONS = {
    "products": "/catalog/products",
    "services": "/catalog/services",
    "orders": "/orders",
}


def extract_rows(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        value = payload.get("data")
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]
    return []


def page_info(payload: object) -> dict:
    if not isinstance(payload, dict) or not isinstance(payload.get("paging"), dict):
        return {}
    p = payload["paging"]
    return {k: p.get(k) for k in ("page", "limit", "total_pages", "count") if k in p}


def duplicate_groups(rows: list[dict], field: str) -> dict[str, int]:
    vals = [r.get(field) for r in rows]
    counts = Counter(v for v in vals if v not in (None, ""))
    return {str(k): v for k, v in counts.items() if v > 1}


def audit_collection(client: httpx.Client, name: str, path: str) -> dict:
    rows: list[dict] = []
    pages: list[dict] = []
    page = 1
    expected_total_pages = None
    expected_count = None
    last_request = 0.0

    while True:
        wait = MIN_INTERVAL - (time.monotonic() - last_request)
        if wait > 0:
            time.sleep(wait)
        started = time.monotonic()
        response = client.get(
            BASE + path,
            params={"page": page, "pageSize": PAGE_SIZE},
            headers=HEADERS,
        )
        last_request = time.monotonic()
        elapsed = round(time.monotonic() - started, 3)
        response.raise_for_status()
        payload = response.json()
        batch = extract_rows(payload)
        pi = page_info(payload)
        if expected_total_pages is None:
            expected_total_pages = pi.get("total_pages")
            expected_count = pi.get("count")
        pages.append({
            "page": page,
            "http": response.status_code,
            "elapsed_s": elapsed,
            "batch_size": len(batch),
            "paging": pi,
        })
        rows.extend(batch)

        if expected_total_pages is not None and page >= int(expected_total_pages):
            break
        # If the API does not provide total_pages, the short-page condition is
        # the only safe completion signal. Use the actual decoded batch length.
        if len(batch) < PAGE_SIZE:
            break
        page += 1
        if page > MAX_PAGES:
            raise RuntimeError(f"pagination safety limit exceeded for {name}")

    ids = [r.get("id") for r in rows]
    missing_id = sum(v in (None, "") for v in ids)
    duplicate_id = duplicate_groups(rows, "id")
    result = {
        "path": path,
        "rows_read": len(rows),
        "expected_count": expected_count,
        "count_matches_rows": expected_count is None or int(expected_count) == len(rows),
        "expected_total_pages": expected_total_pages,
        "pages_read": len(pages),
        "pagination_complete": (
            expected_total_pages is not None and len(pages) == int(expected_total_pages)
        ) or (
            expected_total_pages is None and bool(pages) and pages[-1]["batch_size"] < PAGE_SIZE
        ),
        "missing_id": missing_id,
        "duplicate_id_groups": duplicate_id,
        "duplicate_id_group_count": len(duplicate_id),
        "pages": pages,
    }

    if name in ("products", "services"):
        for field in ("code", "sku"):
            dups = duplicate_groups(rows, field)
            result[f"duplicate_{field}_groups"] = dups
            result[f"duplicate_{field}_group_count"] = len(dups)
        result["missing_title"] = sum(r.get("title") in (None, "") for r in rows)
    if name == "orders":
        dups = duplicate_groups(rows, "number")
        result["duplicate_number_groups"] = dups
        result["duplicate_number_group_count"] = len(dups)
        result["missing_number"] = sum(r.get("number") in (None, "") for r in rows)
    return result


def main() -> int:
    started = time.monotonic()
    results = {}
    with httpx.Client(timeout=TIMEOUT, follow_redirects=True) as client:
        company = client.get(BASE + "/company", headers=HEADERS)
        company.raise_for_status()
        company_payload = company.json()
        for name, path in COLLECTIONS.items():
            results[name] = audit_collection(client, name, path)

    hard_issues = []
    for name, r in results.items():
        for key in ("missing_id", "duplicate_id_group_count"):
            if r.get(key):
                hard_issues.append(f"{name}.{key}={r[key]}")
        if not r.get("count_matches_rows", True):
            hard_issues.append(f"{name}.count_mismatch={r['expected_count']}!={r['rows_read']}")
        for key in ("duplicate_code_group_count", "duplicate_sku_group_count", "duplicate_number_group_count"):
            if r.get(key):
                hard_issues.append(f"{name}.{key}={r[key]}")

    report = {
        "version": "22.1",
        "mode": "READ_ONLY",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "api_base": BASE,
        "company": {k: company_payload.get(k) for k in ("name", "country", "currency", "timezone")},
        "method_policy": {"allowed": ["GET"], "blocked": ["POST", "PUT", "PATCH", "DELETE"]},
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "collections": results,
        "hard_issues": hard_issues,
        "elapsed_s": round(time.monotonic() - started, 3),
    }
    report["summary"] = {
        "collections_audited": len(results),
        "products_rows": results["products"]["rows_read"],
        "services_rows": results["services"]["rows_read"],
        "orders_rows": results["orders"]["rows_read"],
        "products_pagination_complete": results["products"]["pagination_complete"],
        "services_pagination_complete": results["services"]["pagination_complete"],
        "orders_pagination_complete": results["orders"]["pagination_complete"],
        "hard_issue_count": len(hard_issues),
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
    }
    report["report_sha256"] = hashlib.sha256(
        json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== MARSEL V22.1 / COMPREHENSIVE DATA QUALITY / READ ONLY ===")
    for k, v in report["summary"].items():
        print(f"{k.upper()}={v}")
    print(f"HARD_ISSUES={hard_issues}")
    print(f"REPORT={OUT}")
    print(f"REPORT_SHA256={report['report_sha256']}")
    print("RESULT=PASS" if not hard_issues and all(results[n]["pagination_complete"] for n in results) else "RESULT=REVIEW_REQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
