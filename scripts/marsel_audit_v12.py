#!/usr/bin/env python3
"""MARSEL V12: build a read-only inventory from the official RO App API catalog.

The script discovers documented reference pages from llms.txt, fetches each
public reference page, extracts documented HTTP methods and API paths, then
probes only documented GET endpoints. It never sends POST/PUT/PATCH/DELETE.
For paginated GET resources it scans pages when the response exposes a page
count. Response records are summarized without storing customer PII.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlparse
import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS_INDEX = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = os.environ.get("MARSEL_AUDIT_OUT", "marsel-api-master-inventory-v12.json")
PAGE_SIZE = int(os.environ.get("ROAPP_PAGE_SIZE", "50"))
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "45"))

if not KEY:
    print("ERROR: ROAPP_API_KEY is not configured")
    sys.exit(2)

API_HEADERS = {"Authorization": f"Bearer {KEY}", "Accept": "application/json"}
DOC_HEADERS = {"Accept": "text/plain, text/markdown, text/html, */*"}


def get(url, params=None, headers=None):
    try:
        return httpx.get(url, params=params or {}, headers=headers or {}, timeout=TIMEOUT, follow_redirects=True)
    except Exception as exc:
        return exc


def extract_links(text):
    found, seen = [], set()
    for m in re.finditer(r"\[[^\]]*\]\((https?://[^)]+)\)", text):
        u = m.group(1).strip()
        if u not in seen:
            seen.add(u); found.append(u)
    for m in re.finditer(r"https?://[^\s<>\)]+", text):
        u = m.group(0).rstrip(".,;\"")
        if u not in seen:
            seen.add(u); found.append(u)
    return found


def clean_path(path):
    path = path.strip().strip('`"\'')
    path = path.split("?")[0]
    if not path.startswith("/"):
        return None
    if not path.startswith("/v2"):
        path = "/v2" + path
    return path


def extract_api_operations(doc):
    """Extract method/path pairs from common ReadMe/OpenAPI rendering patterns."""
    ops, seen = [], set()
    patterns = [
        r"\b(GET|POST|PUT|PATCH|DELETE)\s+(`?/[A-Za-z0-9_./{}:-]+`?)",
        r"(?:curl|fetch|axios)[^\n]{0,300}?https?://[^\s\"']+",
        r"https?://api\.roapp\.io(?:/v2)?/[A-Za-z0-9_./{}:-]+",
    ]
    for pat in patterns:
        for m in re.finditer(pat, doc, re.I):
            if m.lastindex == 2:
                method, raw = m.group(1).upper(), m.group(2)
                p = clean_path(raw)
            else:
                raw = m.group(0)
                method = "GET" if "/reference/" in raw else None
                u = re.search(r"https?://api\.roapp\.io((?:/v2)?/[A-Za-z0-9_./{}:-]+)", raw)
                p = clean_path(u.group(1)) if u else None
            if p and method:
                key = (method, p)
                if key not in seen:
                    seen.add(key); ops.append({"method": method, "path": p})
    return ops


def rows(payload):
    if isinstance(payload, list): return payload
    if isinstance(payload, dict):
        for key in ("data", "items", "results", "orders", "people", "organizations", "services", "products"):
            if isinstance(payload.get(key), list): return payload[key]
    return []


def total_pages(payload):
    if not isinstance(payload, dict): return None
    for obj in (payload.get("paging"), payload.get("pagination"), payload.get("meta"), payload):
        if isinstance(obj, dict):
            for key in ("total_pages", "totalPages", "pages"):
                if isinstance(obj.get(key), int): return obj[key]
    return None


def total_count(payload):
    if not isinstance(payload, dict): return None
    for obj in (payload.get("paging"), payload.get("pagination"), payload.get("meta"), payload):
        if isinstance(obj, dict):
            for key in ("total", "total_count", "totalCount", "count"):
                if isinstance(obj.get(key), int): return obj[key]
    return None


def summarize_rows(items):
    # Do not persist customer names, phones, emails, comments, or free text.
    return {
        "rows": len(items),
        "sample_ids": [x.get("id") for x in items[:5] if isinstance(x, dict) and x.get("id") is not None],
        "missing_id": sum(1 for x in items if isinstance(x, dict) and x.get("id") is None),
    }


print("=== MARSEL AUDIT V12 / OFFICIAL API INVENTORY / READ ONLY ===")
print(f"BASE={BASE}")
print(f"DOCS_INDEX={DOCS_INDEX}")

idx = get(DOCS_INDEX, headers=DOC_HEADERS)
if isinstance(idx, Exception):
    print(f"DOCS_INDEX_ERROR={idx}"); sys.exit(3)
print(f"DOCS_INDEX_HTTP={idx.status_code}")
if idx.status_code != 200:
    print("ERROR: official docs index could not be retrieved"); sys.exit(4)

links = extract_links(idx.text)
refs = [u for u in links if "/reference/" in u]
print(f"DOCUMENTATION_LINKS={len(links)}")
print(f"REFERENCE_LINKS={len(refs)}")

catalog, operations, doc_errors = [], [], []
for ref in refs:
    r = get(ref, headers=DOC_HEADERS)
    entry = {"reference": ref, "http_status": None, "operations": []}
    if isinstance(r, Exception):
        entry["error"] = str(r); doc_errors.append(entry); catalog.append(entry); continue
    entry["http_status"] = r.status_code
    if r.status_code == 200:
        entry["operations"] = extract_api_operations(r.text)
        for op in entry["operations"]:
            operations.append({"reference": ref, **op})
    else:
        doc_errors.append(entry)
    catalog.append(entry)

# Deduplicate documented operations while retaining all source references.
unique = {}
for op in operations:
    key = (op["method"], op["path"])
    unique.setdefault(key, {"method": op["method"], "path": op["path"], "references": []})
    if op["reference"] not in unique[key]["references"]:
        unique[key]["references"].append(op["reference"])

get_ops = [v for v in unique.values() if v["method"] == "GET"]
print(f"DOCUMENTED_OPERATIONS={len(unique)}")
print(f"DOCUMENTED_GET_OPERATIONS={len(get_ops)}")

results = []
for op in get_ops:
    path = op["path"]
    url = BASE + (path[3:] if path.startswith("/v2") else path)
    result = {"method": "GET", "path": path, "url": url, "references": op["references"]}
    first = get(url, {"page": 1, "pageSize": PAGE_SIZE}, API_HEADERS)
    if isinstance(first, Exception):
        result.update({"available": False, "error": str(first)})
        results.append(result); continue
    result["http_status"] = first.status_code
    result["available"] = first.status_code == 200
    if first.status_code != 200:
        results.append(result); continue
    try:
        payload = first.json()
    except Exception:
        result.update({"available": False, "error": "non_json_response"})
        results.append(result); continue

    items = rows(payload)
    pages = total_pages(payload)
    result["page_size"] = PAGE_SIZE
    result["total_pages_reported"] = pages
    result["total_count_reported"] = total_count(payload)
    result["rows_first_page"] = len(items)
    result["summary_first_page"] = summarize_rows(items)
    result["pages_scanned"] = 1
    result["rows_scanned"] = len(items)

    # Scan all documented pages, bounded by the server-reported page count.
    if isinstance(pages, int) and 2 <= pages <= 10000:
        for page in range(2, pages + 1):
            rr = get(url, {"page": page, "pageSize": PAGE_SIZE}, API_HEADERS)
            if isinstance(rr, Exception) or rr.status_code != 200:
                result["pagination_complete"] = False
                result["failed_page"] = page
                break
            try:
                pp = rr.json()
            except Exception:
                result["pagination_complete"] = False
                result["failed_page"] = page
                break
            result["rows_scanned"] += len(rows(pp))
            result["pages_scanned"] = page
        else:
            result["pagination_complete"] = True
    else:
        result["pagination_complete"] = pages in (None, 1)
    results.append(result)

report = {
    "audit": "MARSEL_AUDIT_V12",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "official_docs": {
        "index": DOCS_INDEX,
        "http_status": idx.status_code,
        "reference_count": len(refs),
        "catalog": catalog,
        "documentation_errors": doc_errors,
    },
    "api_catalog": {
        "documented_operations": list(unique.values()),
        "documented_get_operations": get_ops,
        "get_results": results,
    },
    "safety": {
        "writes_performed": False,
        "updates_performed": False,
        "deletes_performed": False,
        "non_get_endpoints_called": False,
        "pii_persisted": False,
    },
}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=2)

available = sum(1 for x in results if x.get("available"))
print(f"GET_RESULTS={len(results)}")
print(f"GET_AVAILABLE={available}")
print(f"GET_UNAVAILABLE={len(results)-available}")
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
