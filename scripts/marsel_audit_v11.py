#!/usr/bin/env python3
"""MARSEL V11: official RO App API catalog discovery, read-only.

This version deliberately does not guess API resource paths. It downloads the
public RO App documentation index (llms.txt), records its links, and probes
only /orders using the documented page parameter. No RO App writes are made.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS_INDEX = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = "marsel-audit-v11-report.json"
PAGE_SIZE = 50

if not KEY:
    print("ERROR: ROAPP_API_KEY is not configured")
    sys.exit(2)

HEADERS = {"Authorization": f"Bearer {KEY}", "Accept": "application/json"}


def get(url, params=None, headers=None):
    try:
        return httpx.get(url, params=params or {}, headers=headers or {}, timeout=45, follow_redirects=True)
    except Exception as exc:
        return exc


def extract_links(text):
    found = []
    seen = set()
    for match in re.finditer(r"\[[^\]]*\]\((https?://[^)]+)\)", text):
        url = match.group(1).strip()
        if url not in seen:
            seen.add(url); found.append(url)
    for match in re.finditer(r"https?://[^\s<>\)]+", text):
        url = match.group(0).rstrip(".,;\"")
        if url not in seen:
            seen.add(url); found.append(url)
    return found


def rows(payload):
    if isinstance(payload, list): return payload
    if isinstance(payload, dict):
        for key in ("data", "items", "results", "orders"):
            if isinstance(payload.get(key), list): return payload[key]
    return []


def total_pages(payload):
    if not isinstance(payload, dict): return None
    for obj in (payload.get("paging"), payload.get("pagination"), payload.get("meta"), payload):
        if isinstance(obj, dict):
            for key in ("total_pages", "totalPages", "pages"):
                if isinstance(obj.get(key), int): return obj[key]
    return None


print("=== MARSEL AUDIT V11 / OFFICIAL API CATALOG / READ ONLY ===")
print(f"BASE={BASE}")
print(f"DOCS_INDEX={DOCS_INDEX}")

idx = get(DOCS_INDEX, headers={"Accept": "text/plain, text/markdown, */*"})
if isinstance(idx, Exception):
    print(f"DOCS_INDEX_ERROR={idx}"); sys.exit(3)
print(f"DOCS_INDEX_HTTP={idx.status_code}")
if idx.status_code != 200:
    print("ERROR: official docs index could not be retrieved"); sys.exit(4)

text = idx.text
links = extract_links(text)
reference_links = [u for u in links if "/reference/" in u]
print(f"DOCS_INDEX_BYTES={len(text.encode('utf-8'))}")
print(f"DOCUMENTATION_LINKS={len(links)}")
print(f"REFERENCE_LINKS={len(reference_links)}")
for url in reference_links:
    print(f"REFERENCE={url}")

# The only API probe here is the already-confirmed Orders resource.
resp = get(f"{BASE}/orders", {"page": 1, "pageSize": PAGE_SIZE}, HEADERS)
if isinstance(resp, Exception):
    print(f"ORDERS_ERROR={resp}"); sys.exit(5)
print(f"ORDERS_HTTP={resp.status_code}")
if resp.status_code != 200:
    print("ERROR: /orders unavailable"); sys.exit(6)

try:
    payload = resp.json()
except Exception:
    print("ERROR: /orders returned non-JSON"); sys.exit(7)

first_rows = rows(payload)
pages = total_pages(payload)
all_rows = list(first_rows)
if isinstance(pages, int) and pages >= 2:
    for page in range(2, pages + 1):
        r = get(f"{BASE}/orders", {"page": page, "pageSize": PAGE_SIZE}, HEADERS)
        if isinstance(r, Exception) or r.status_code != 200:
            print(f"ORDERS_PAGE_FAILED={page}"); sys.exit(8)
        all_rows.extend(rows(r.json()))

print(f"ORDERS_PAGE_SIZE={PAGE_SIZE}")
print(f"ORDERS_TOTAL_PAGES_REPORTED={pages}")
print(f"ORDERS_ROWS={len(all_rows)}")

report = {
    "audit": "MARSEL_AUDIT_V11",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "official_docs_index": {
        "url": DOCS_INDEX,
        "http_status": idx.status_code,
        "bytes": len(idx.content),
        "documentation_links": links,
        "reference_links": reference_links,
    },
    "orders": {
        "endpoint": f"{BASE}/orders",
        "http_status": resp.status_code,
        "page_size": PAGE_SIZE,
        "total_pages_reported": pages,
        "rows_scanned": len(all_rows),
    },
    "safety": {
        "writes_performed": False,
        "updates_performed": False,
        "deletes_performed": False,
        "client_names_phones_emails_excluded": True,
        "guessed_resource_paths_probed": False,
    },
}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=2)
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
