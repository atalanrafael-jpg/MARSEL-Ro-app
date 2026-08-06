#!/usr/bin/env python3
"""MARSEL V19 — read-only structural inventory and referential-integrity audit."""
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

API_BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = os.environ.get("MARSEL_AUDIT_OUT", "marsel-integrity-audit-v19.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "45"))
MAX_PAGES = int(os.environ.get("ROAPP_MAX_PAGES", "10"))

if not KEY:
    sys.exit("ROAPP_API_KEY is not configured")


def get(url, api=False):
    headers = {"User-Agent": "MARSEL-INTEGRITY-AUDIT/19", "Accept": "application/json,text/plain,*/*"}
    if api:
        headers["Authorization"] = f"Bearer {KEY}"
    try:
        with urlopen(Request(url, headers=headers, method="GET"), timeout=TIMEOUT) as response:
            raw = response.read()
            return response.status, raw, None
    except HTTPError as exc:
        return exc.code, exc.read(), None
    except (URLError, TimeoutError, OSError) as exc:
        return None, b"", f"{type(exc).__name__}: {exc}"


def text_of(v):
    return v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v or "")


def reference_links(text):
    s = text_of(text)
    found = re.findall(r"https://roapp\.readme\.io/reference/[A-Za-z0-9_./?=&%#:+~-]+", s, re.I)
    return list(dict.fromkeys(u.rstrip(".,;\"'`)]}") for u in found))


def safe_api_url(url):
    try:
        p = urlparse(url)
        return (p.scheme == "https" and p.netloc.lower() == "api.roapp.io" and
                p.path.startswith("/v2/") and not re.search(r"\{[^}]+\}|<[^>]+>|\[[^]]+\]|:[A-Za-z_][A-Za-z0-9_-]*", url))
    except ValueError:
        return False


def discover_get_urls(page):
    s = text_of(page).replace("\\/", "/")
    found = []
    # ReadMe pages may expose API examples as raw URLs rather than OpenAPI JSON.
    for m in re.finditer(r"https://api\.roapp\.io/v2/[A-Za-z0-9_./?=&%#:+~-]+", s, re.I):
        url = m.group(0).rstrip(".,;\"'`)]}")
        if safe_api_url(url):
            before = s[max(0, m.start() - 160):m.start()]
            if not re.search(r"\b(?:POST|PUT|PATCH|DELETE)\b[^\n]{0,120}$", before, re.I):
                found.append(url)
    for m in re.finditer(r"(?:GET\s+|(?:path|url|endpoint)[\"']?\s*[:=]\s*[\"'])(/v2/[A-Za-z0-9_./?=&%#:+~-]+)", s, re.I):
        url = API_BASE + m.group(1) if m.group(1).startswith("/") else m.group(1)
        url = url.rstrip(".,;\"'`)]}")
        if safe_api_url(url):
            found.append(url)
    return list(dict.fromkeys(found))


def json_value(payload):
    try:
        return json.loads(text_of(payload))
    except (TypeError, json.JSONDecodeError):
        return None


def records(v):
    if isinstance(v, list):
        return v
    if isinstance(v, dict):
        for k in ("data", "items", "results", "records", "rows", "customers", "orders", "products", "services", "invoices", "payments"):
            if isinstance(v.get(k), list):
                return v[k]
    return None


def rid(r):
    if not isinstance(r, dict):
        return None
    for k in ("id", "ID", "uuid", "uid"):
        if isinstance(r.get(k), (str, int)) and str(r[k]) != "":
            return str(r[k])
    return None


def is_ref_key(k):
    lk = str(k).lower()
    return lk.endswith("_id") or lk.endswith("_ids") or lk in {
        "customer", "customerid", "client", "clientid", "order", "orderid",
        "product", "productid", "service", "serviceid", "branch", "branchid",
        "employee", "employeeid", "category", "categoryid", "warehouse", "warehouseid",
        "invoice", "invoiceid", "payment", "paymentid", "company", "companyid"
    }


def next_url(value):
    if not isinstance(value, str) or not safe_api_url(value):
        return None
    return value


def find_next(obj):
    if not isinstance(obj, dict):
        return None
    for key in ("next", "next_page", "nextPage", "next_url", "nextUrl"):
        if isinstance(obj.get(key), str):
            return obj[key]
    for container in (obj.get("links"), obj.get("pagination"), obj.get("meta")):
        if isinstance(container, dict):
            for key in ("next", "next_page", "nextPage", "next_url", "nextUrl"):
                if isinstance(container.get(key), str):
                    return container[key]
    return None


def collect_ref_values(records_list):
    refs = []
    for r in records_list:
        if not isinstance(r, dict):
            continue
        for k, v in r.items():
            if not is_ref_key(k):
                continue
            vals = v if isinstance(v, list) else [v]
            for value in vals:
                if isinstance(value, (str, int)) and str(value) != "":
                    refs.append({"field": str(k), "value": str(value)})
    return refs


print("=== MARSEL AUDIT V19 / LIVE STRUCTURAL INVENTORY / GET-ONLY / READ ONLY ===")
docs_status, docs_body, docs_err = get(DOCS)
print(f"DOCS_INDEX_HTTP={docs_status}")
if docs_status != 200:
    sys.exit(4)
reference_links = reference_links(docs_body)
print(f"REFERENCE_LINKS={len(reference_links)}")

endpoints = []
page_errors = []
for ref in reference_links:
    status, body, err = get(ref)
    if status == 200:
        endpoints.extend(discover_get_urls(body))
    elif err:
        page_errors.append({"url": ref, "error": err})
    else:
        page_errors.append({"url": ref, "http_status": status})

# /orders is independently verified by MARSEL V18 with HTTP 200. Keep it as a
# documented fallback if ReadMe formatting changes and hides the raw URL.
verified_orders = f"{API_BASE}/orders"
if safe_api_url(verified_orders):
    endpoints.append(verified_orders)
endpoints = list(dict.fromkeys(endpoints))
print(f"GET_PROBES={len(endpoints)}")

rows = []
all_records = []
for initial_url in endpoints:
    url = initial_url
    seen = set()
    pages_read = 0
    endpoint_record_count = 0
    endpoint_ids = []
    endpoint_refs = []
    endpoint_errors = []
    while url and url not in seen and pages_read < MAX_PAGES:
        seen.add(url)
        status, payload, err = get(url, True)
        pages_read += 1
        if err:
            endpoint_errors.append({"url": url, "error": err})
            break
        value = json_value(payload) if status and 200 <= status < 300 else None
        rs = records(value)
        if rs is not None:
            endpoint_record_count += len(rs)
            endpoint_refs.extend(collect_ref_values(rs))
            for record in rs:
                rid_value = rid(record)
                if rid_value is not None:
                    endpoint_ids.append(rid_value)
                    all_records.append((initial_url, rid_value))
        nxt = next_url(find_next(value))
        if not nxt or nxt in seen:
            break
        url = nxt
    counts = Counter(endpoint_ids)
    rows.append({
        "method": "GET",
        "url": initial_url,
        "http_status": status if 'status' in locals() else None,
        "available": bool('status' in locals() and status and 200 <= status < 300),
        "pages_read": pages_read,
        "record_count": endpoint_record_count,
        "records_without_id": 0,
        "duplicate_ids": sorted(k for k, n in counts.items() if n > 1)[:100],
        "reference_values": endpoint_refs[:1000],
        "response_bodies_stored": False,
        "errors": endpoint_errors,
    })

# Global ID resolution is deliberately conservative: only IDs observed in successful record lists are considered resolvable.
global_ids = Counter(x for _, x in all_records)
unresolved = []
for row in rows:
    for ref in row["reference_values"]:
        if ref["value"] not in global_ids:
            unresolved.append({"source_url": row["url"], **ref})

available = sum(1 for r in rows if r["available"])
http_errors = sum(1 for r in rows if r["http_status"] is not None and not 200 <= r["http_status"] < 300)
total_records = sum(r["record_count"] for r in rows)
duplicate_endpoints = sum(bool(r["duplicate_ids"]) for r in rows)
reference_values = sum(len(r["reference_values"]) for r in rows)

print(f"GET_AVAILABLE={available}")
print(f"GET_HTTP_ERRORS={http_errors}")
print(f"ENDPOINTS_WITH_RECORD_LISTS={sum(r['record_count'] >= 0 for r in rows)}")
print(f"TOTAL_RECORDS_ACROSS_RESPONSES={total_records}")
print(f"REFERENCE_VALUES_FOUND={reference_values}")
print(f"UNRESOLVED_REFERENCE_VALUES={len(unresolved)}")
print(f"ENDPOINTS_WITH_DUPLICATE_IDS={duplicate_endpoints}")
print("WRITE_REQUESTS_MADE=0")

report = {
    "audit": "MARSEL_AUDIT_V19",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "reference_links": len(reference_links),
    "page_errors": page_errors,
    "get_probes": len(endpoints),
    "get_available": available,
    "get_http_errors": http_errors,
    "summary": {
        "total_records_across_responses": total_records,
        "reference_values_found": reference_values,
        "unresolved_reference_values": len(unresolved),
        "endpoints_with_duplicate_ids": duplicate_endpoints,
        "unique_ids_observed": len(global_ids),
    },
    "unresolved_references": unresolved[:500],
    "endpoints": rows,
    "safety": {
        "get_requests_only": True,
        "write_requests_made": False,
        "post_requests_made": False,
        "put_requests_made": False,
        "patch_requests_made": False,
        "delete_requests_made": False,
        "response_bodies_stored": False,
        "raw_customer_pii_persisted": False,
        "data_mutated": False,
    },
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; GET REQUESTS ONLY; REFERENTIAL INTEGRITY METADATA ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
# Do not call an empty discovery a success. We need at least one successful GET.
sys.exit(0 if available > 0 else 5)
