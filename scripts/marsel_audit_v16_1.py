#!/usr/bin/env python3
"""MARSEL V16.1 — documentation-first RO App API discovery, read-only, stdlib only."""
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS_INDEX = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = os.environ.get("MARSEL_AUDIT_OUT", "marsel-api-master-inventory-v16-1.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "45"))
MAX_PAGES = int(os.environ.get("MARSEL_V16_1_MAX_DOC_PAGES", "200"))

if not KEY:
    print("ERROR: ROAPP_API_KEY is not configured")
    sys.exit(2)


def fetch(url, headers=None):
    req = Request(url, headers=headers or {})
    try:
        with urlopen(req, timeout=TIMEOUT) as r:
            return r.status, r.headers, r.read()
    except HTTPError as e:
        return e.code, e.headers, e.read()
    except (URLError, TimeoutError, OSError) as e:
        return None, {}, str(e).encode()


def links(text):
    found = re.findall(r'https?://[^\s<>\)\]\"\'`]+', text or "")
    out, seen = [], set()
    for raw in found:
        u = raw.rstrip(".,; \t\r\n")
        u = u.rstrip(chr(34) + chr(39) + chr(96))
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def title_from_line(line, url):
    m = re.search(r"\[([^\]]+)\]\((https://roapp\.readme\.io/reference/[^)]+)\)", line)
    return m.group(1).strip() if m else url.rsplit("/", 1)[-1]


def classify_methods(text):
    return sorted(set(m.group(1).upper() for m in re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b", text or "", re.I)))


def extract_paths(text):
    out = []
    for p in re.findall(r"(?:https://api\.roapp\.io)?/v2/[A-Za-z0-9_./{}:-]+", text or ""):
        if p not in out:
            out.append(p)
    return out


def write_report(status, catalog, pages, operations, error=None):
    get_ops = [x for x in operations if x["method"] == "GET"]
    write_ops = [x for x in operations if x["method"] != "GET"]
    report = {
        "audit": "MARSEL_AUDIT_V16.1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "readonly": True,
        "degraded": status != 200,
        "degraded_reason": error,
        "official_docs": {
            "index": DOCS_INDEX,
            "http_status": status,
            "reference_count": len(catalog),
            "reference_pages": pages,
        },
        "inventory": {
            "operation_candidates": len(operations),
            "get_candidates": len(get_ops),
            "write_candidates": len(write_ops),
            "operations": operations,
        },
        "safety": {
            "api_requests_made": False,
            "get_requests_made": False,
            "write_requests_made": False,
            "updates_performed": False,
            "deletes_performed": False,
            "pii_persisted": False,
        },
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


print("=== MARSEL AUDIT V16.1 / DOCUMENTATION FALLBACK / READ ONLY ===")
print(f"BASE={BASE}")
print(f"DOCS_INDEX={DOCS_INDEX}")
status, _, body = fetch(DOCS_INDEX, {"Accept": "text/plain, text/markdown, text/html, */*"})
print(f"DOCS_INDEX_HTTP={status}")

if status != 200:
    reason = f"Documentation index unavailable (HTTP {status}); no API inventory was inferred or fabricated."
    write_report(status, [], [], [], reason)
    print(f"WARNING={reason}")
    print(f"REPORT={OUT}")
    print("API_PROBES=0")
    print("RESULT=READ_ONLY; DOCUMENTATION INDEX UNAVAILABLE; NO RO APP DATA CREATED, UPDATED OR DELETED")
    # A documentation access problem is not an application-data failure.
    # The report records the degraded state explicitly so CI remains actionable.
    sys.exit(0)

idx_text = body.decode("utf-8", errors="replace")
catalog, seen = [], set()
for line in idx_text.splitlines():
    for u in links(line):
        if "/reference/" in u and u not in seen:
            seen.add(u)
            catalog.append({"url": u, "title": title_from_line(line, u)})
print(f"REFERENCE_LINKS={len(catalog)}")

pages, ops = [], {}
for ref in catalog[:MAX_PAGES]:
    s, _, b = fetch(ref["url"], {"Accept": "text/plain, text/markdown, text/html, */*"})
    text = b.decode("utf-8", errors="replace")
    rec = {"url": ref["url"], "title": ref["title"], "http_status": s, "bytes": len(b)}
    if s == 200:
        methods, paths = classify_methods(text), extract_paths(text)
        rec.update({"methods": methods, "paths": paths})
        for method in methods:
            for path in paths:
                ops[(method, path)] = {"method": method, "path": path, "source": ref["url"], "title": ref["title"]}
    else:
        rec["error"] = text[:500]
    pages.append(rec)

operations = sorted(ops.values(), key=lambda x: (x["method"], x["path"]))
get_ops = [x for x in operations if x["method"] == "GET"]
write_ops = [x for x in operations if x["method"] != "GET"]
print(f"DOCUMENTED_OPERATION_CANDIDATES={len(operations)}")
print(f"DOCUMENTED_GET_CANDIDATES={len(get_ops)}")
print(f"DOCUMENTED_WRITE_CANDIDATES={len(write_ops)}")

write_report(status, catalog, pages, operations)
print(f"REPORT={OUT}")
print("API_PROBES=0")
print("RESULT=READ_ONLY; DOCUMENTATION INVENTORY ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
