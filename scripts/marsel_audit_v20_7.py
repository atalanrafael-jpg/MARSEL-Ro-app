#!/usr/bin/env python3
"""MARSEL V20.7 - read-only full-discovery pagination audit.

V20.7 fixes the V20.6 completeness blind spot: a page smaller than the
requested page size is NOT treated as the end of the dataset. It continues
pagination, detects ignored pagination parameters, and probes offset/limit
when page pagination appears ineffective. GET only; no mutations.
"""
import hashlib
import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
OUT = os.environ.get("MARSEL_AUDIT_OUTPUT", "marsel-data-discovery-v20-7.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "30"))
PAGE_SIZE = int(os.environ.get("MARSEL_PAGE_SIZE", "100"))
MAX_PAGES = int(os.environ.get("MARSEL_MAX_PAGES", "100"))
MAX_DETAIL = int(os.environ.get("MARSEL_MAX_DETAIL", "2000"))

TARGETS = [
    {"entity": "orders", "list": "/orders", "detail": "/orders/{id}"},
    {"entity": "services", "list": "/catalog/services", "detail": "/catalog/services/{id}"},
    {"entity": "products", "list": "/catalog/products", "detail": "/catalog/products/{id}"},
    {"entity": "bundles", "list": "/catalog/bundles", "detail": "/catalog/bundles/{id}"},
    {"entity": "inquiries", "list": "/inquiries", "detail": "/inquiries/{id}"},
    {"entity": "bookings", "list": "/bookings", "detail": "/bookings/{id}"},
    {"entity": "estimates", "list": "/estimates", "detail": "/estimates/{id}"},
    {"entity": "invoices", "list": "/invoices", "detail": "/invoices/{id}"},
]

VOLATILE = {"created_at", "updated_at", "createdAt", "updatedAt", "timestamp", "request_id", "requestId"}


def get(path, params=None):
    url = path if path.startswith("http") else BASE + path
    if params:
        url += ("&" if "?" in url else "?") + urlencode(params)
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Accept": "application/json",
            "User-Agent": "MARSEL-Audit-V20.7",
        },
        method="GET",
    )
    started = time.time()
    try:
        with urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read()
            return r.status, json.loads(raw.decode("utf-8")), round(time.time() - started, 3), None
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:1000]
        return e.code, None, round(time.time() - started, 3), body
    except (URLError, TimeoutError, ValueError) as e:
        return None, None, round(time.time() - started, 3), str(e)


def extract_records(payload):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    keys = ("data", "items", "results", "orders", "services", "products", "bundles", "inquiries", "bookings", "estimates", "invoices")
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return value
    for key in ("data", "result"):
        value = payload.get(key)
        if isinstance(value, dict):
            nested = extract_records(value)
            if nested:
                return nested
    return []


def record_id(item):
    if not isinstance(item, dict):
        return None
    for key in ("id", "ID", "uuid"):
        if item.get(key) is not None:
            return item[key]
    return None


def normalize(value):
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in sorted(value.items()) if k not in VOLATILE}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def fingerprint(value):
    raw = json.dumps(normalize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def page_signature(records):
    ids = [record_id(x) for x in records]
    if all(x is not None for x in ids) and ids:
        return "ids:" + hashlib.sha256(json.dumps(ids, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    return "records:" + hashlib.sha256(json.dumps([fingerprint(x) for x in records], separators=(",", ":")).encode()).hexdigest()


def pagination_metadata(payload):
    if not isinstance(payload, dict):
        return []
    keys = ("next", "next_page", "nextPage", "has_next", "hasNext", "total", "count", "page", "current_page", "currentPage", "pages", "total_pages", "totalPages", "offset", "limit")
    return [{k: payload[k]} for k in keys if k in payload]


def explicit_has_next(payload):
    if not isinstance(payload, dict):
        return None
    for key in ("has_next", "hasNext"):
        if isinstance(payload.get(key), bool):
            return payload[key]
    for key in ("next", "next_page", "nextPage"):
        if key in payload:
            return payload[key] not in (None, False, "", 0)
    return None


def next_url_from_payload(payload):
    if not isinstance(payload, dict):
        return None
    for key in ("next", "next_url", "nextUrl"):
        value = payload.get(key)
        if isinstance(value, str) and value.startswith("http"):
            return value
    return None


def classify(status):
    return {
        200: "OK", 401: "AUTH_FAILURE", 403: "ACCESS_DENIED", 404: "NOT_FOUND", 429: "RATE_LIMIT"
    }.get(status, "SERVER_ERROR" if status and status >= 500 else "UNEXPECTED_HTTP")


def collect_entity(target):
    records = []
    pages = []
    errors = []
    signatures = set()
    page_param_effective = None
    next_metadata_seen = False
    explicit_end = False
    pagination_mode = "page/page_size"

    for page in range(1, MAX_PAGES + 1):
        status, payload, elapsed, error = get(target["list"], {"page": page, "page_size": PAGE_SIZE})
        recs = extract_records(payload) if status == 200 and payload is not None else []
        meta = pagination_metadata(payload)
        has_next = explicit_has_next(payload)
        if meta:
            next_metadata_seen = True
        sig = page_signature(recs) if recs else None
        repeated = sig in signatures if sig else False
        if sig:
            signatures.add(sig)

        pages.append({
            "request": {"page": page, "page_size": PAGE_SIZE},
            "http": status,
            "elapsed_s": elapsed,
            "records": len(recs),
            "metadata": meta,
            "has_next": has_next,
            "page_signature": sig,
            "repeated_page": repeated,
        })

        if status != 200 or payload is None:
            errors.append({"mode": "page", "page": page, "http": status, "error": error})
            break

        if page == 1:
            first_ids = [record_id(x) for x in recs]
        elif recs:
            current_ids = [record_id(x) for x in recs]
            if first_ids and current_ids != first_ids:
                page_param_effective = True
            elif first_ids and current_ids == first_ids:
                page_param_effective = False

        records.extend(recs)

        if not recs:
            explicit_end = True
            break
        if repeated:
            break
        if has_next is False:
            explicit_end = True
            break
        next_url = next_url_from_payload(payload)
        if next_url:
            pagination_mode = "next_url"
            status2, payload2, elapsed2, error2 = get(next_url)
            recs2 = extract_records(payload2) if status2 == 200 and payload2 is not None else []
            pages.append({
                "request": {"next_url": next_url},
                "http": status2,
                "elapsed_s": elapsed2,
                "records": len(recs2),
                "metadata": pagination_metadata(payload2),
                "has_next": explicit_has_next(payload2),
                "page_signature": page_signature(recs2) if recs2 else None,
                "repeated_page": False,
            })
            if status2 != 200:
                errors.append({"mode": "next_url", "http": status2, "error": error2})
                break
            records.extend(recs2)
            if not recs2:
                explicit_end = True
                break
            break

    # If page pagination was demonstrably ineffective, probe offset/limit.
    offset_probe = []
    if page_param_effective is False and records:
        pagination_mode = "offset/limit_probe"
        seen_offsets = set()
        for offset in range(0, MAX_PAGES * PAGE_SIZE, PAGE_SIZE):
            if offset in seen_offsets:
                break
            seen_offsets.add(offset)
            status, payload, elapsed, error = get(target["list"], {"offset": offset, "limit": PAGE_SIZE})
            recs = extract_records(payload) if status == 200 and payload is not None else []
            sig = page_signature(recs) if recs else None
            offset_probe.append({"offset": offset, "limit": PAGE_SIZE, "http": status, "elapsed_s": elapsed, "records": len(recs), "signature": sig})
            if status != 200 or not recs:
                break
            if offset > 0 and sig == offset_probe[0].get("signature"):
                break
            records.extend(recs)

    return {
        "records": records,
        "pages": pages,
        "errors": errors,
        "offset_probe": offset_probe,
        "pagination_mode": pagination_mode,
        "page_param_effective": page_param_effective,
        "next_metadata_seen": next_metadata_seen,
        "explicit_end": explicit_end,
    }


def main():
    if not KEY:
        print("ROAPP_API_KEY is required", file=sys.stderr)
        return 2

    report = {
        "version": "20.7",
        "readonly": True,
        "write_requests_made": False,
        "ro_app_data_mutated": False,
        "method_policy": {"allowed": ["GET"], "forbidden": ["POST", "PUT", "PATCH", "DELETE"]},
        "completeness_policy": {
            "short_page_is_not_end": True,
            "page_pagination_is_tested_beyond_page_one": True,
            "ignored_page_parameter_is_detected": True,
            "offset_limit_fallback_probe": True,
        },
        "targets": [],
    }
    totals = {"records": 0, "detail": 0, "empty": 0, "structural_issues": 0, "duplicate_candidates": 0, "pagination_inconclusive": 0}

    for target in TARGETS:
        result = collect_entity(target)
        all_records = result["records"]
        seen_ids = set()
        duplicate_ids = []
        missing_ids = []
        structural = []
        fp_map = {}
        for idx, item in enumerate(all_records):
            rid = record_id(item)
            if rid is None:
                missing_ids.append(idx)
            elif rid in seen_ids:
                duplicate_ids.append(rid)
            else:
                seen_ids.add(rid)
            fp_map.setdefault(fingerprint(item), []).append(rid)
            if not isinstance(item, dict):
                structural.append({"index": idx, "issue": "record_not_object"})
        fp_dupes = [ids for ids in fp_map.values() if len(ids) > 1]

        detail = []
        ids = [record_id(x) for x in all_records if record_id(x) is not None]
        for rid in ids[:MAX_DETAIL]:
            status, _, elapsed, error = get(target["detail"].format(id=rid))
            detail.append({"source_id": rid, "http": status, "classification": classify(status), "elapsed_s": elapsed, "error": error})

        findings = []
        if not all_records and not result["errors"]:
            findings.append({"severity": "INFO", "code": "EMPTY_ENDPOINT", "message": "HTTP 200 returned no records in inspected pages; this is not classified as an error."})
        if duplicate_ids:
            findings.append({"severity": "WARNING", "code": "DUPLICATE_IDS", "count": len(duplicate_ids), "ids": duplicate_ids[:100]})
        if fp_dupes:
            findings.append({"severity": "WARNING", "code": "DUPLICATE_FINGERPRINTS", "groups": fp_dupes[:100]})
        if structural:
            findings.append({"severity": "WARNING", "code": "STRUCTURAL_ANOMALIES", "items": structural[:100]})
        detail_fail = [x for x in detail if x["classification"] != "OK"]
        if detail_fail:
            findings.append({"severity": "WARNING", "code": "DETAIL_CHECK_FAILURES", "count": len(detail_fail), "items": detail_fail[:100]})
        if result["page_param_effective"] is False:
            findings.append({"severity": "WARNING", "code": "PAGE_PARAMETER_IGNORED", "message": "Page 2 repeated page 1; offset/limit fallback was probed."})
        if len(result["pages"]) >= MAX_PAGES and not result["explicit_end"]:
            findings.append({"severity": "WARNING", "code": "PAGINATION_INCONCLUSIVE", "message": "Maximum page budget reached without an explicit end indicator."})
            totals["pagination_inconclusive"] += 1

        entry = {
            "entity": target["entity"],
            "list_endpoint": target["list"],
            "detail_endpoint": target["detail"],
            "pagination": {
                "mode": result["pagination_mode"],
                "page_param_effective": result["page_param_effective"],
                "next_metadata_seen": result["next_metadata_seen"],
                "explicit_end": result["explicit_end"],
                "pages": result["pages"],
                "offset_probe": result["offset_probe"],
            },
            "records_seen": len(all_records),
            "unique_ids": len(seen_ids),
            "missing_id_records": len(missing_ids),
            "duplicate_id_candidates": len(duplicate_ids),
            "duplicate_fingerprint_groups": len(fp_dupes),
            "detail_checks": detail,
            "list_errors": result["errors"],
            "findings": findings,
        }
        report["targets"].append(entry)
        totals["records"] += len(all_records)
        totals["detail"] += len(detail)
        totals["empty"] += int(not all_records and not result["errors"])
        totals["structural_issues"] += len(structural)
        totals["duplicate_candidates"] += len(duplicate_ids) + len(fp_dupes)

    report["summary"] = {"targets": len(TARGETS), **totals, "write_requests_made": 0, "readonly": True}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    print("=== MARSEL AUDIT V20.7 / FULL DISCOVERY + PAGINATION / READ ONLY ===")
    print(f"TARGETS={len(TARGETS)}")
    print(f"LIST_RECORDS_SEEN={totals['records']}")
    print(f"DETAIL_CHECKS={totals['detail']}")
    print(f"EMPTY_ENDPOINTS={totals['empty']}")
    print(f"DUPLICATE_CANDIDATES={totals['duplicate_candidates']}")
    print(f"STRUCTURAL_ISSUES={totals['structural_issues']}")
    print(f"PAGINATION_INCONCLUSIVE={totals['pagination_inconclusive']}")
    print("WRITE_REQUESTS_MADE=0")
    print(f"REPORT={OUT}")
    print("RESULT=READ_ONLY; V20.7; NO RO APP DATA CREATED, UPDATED OR DELETED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
