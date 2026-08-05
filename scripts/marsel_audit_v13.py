#!/usr/bin/env python3
"""MARSEL V13 — robust read-only catalog extraction from official RO App docs.

V12 proved that the official llms.txt index is reachable and contains 148
reference links, but its page parser extracted only one operation. V13 treats
that as a parser failure: it fetches each official reference page and tries
multiple representations (markdown/plain text, HTML, OpenAPI-like snippets,
JSON-LD/meta tags and canonical URLs). It never guesses an endpoint from a
page title and it probes only explicitly documented GET operations.

No POST/PUT/PATCH/DELETE requests are sent. Reports contain structural
summaries only; customer PII/free text is not persisted.
"""
import json, os, re, sys
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urljoin, urlparse
import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS_INDEX = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = os.environ.get("MARSEL_AUDIT_OUT", "marsel-api-master-inventory-v13.json")
PAGE_SIZE = int(os.environ.get("ROAPP_PAGE_SIZE", "50"))
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "45"))
MAX_PAGES = int(os.environ.get("ROAPP_MAX_PAGES", "10000"))

if not KEY:
    print("ERROR: ROAPP_API_KEY is not configured")
    sys.exit(2)

API_HEADERS = {"Authorization": f"Bearer {KEY}", "Accept": "application/json"}
DOC_HEADERS = {"Accept": "text/markdown, text/plain, text/html, application/json, */*"}
METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def request(url, params=None, headers=None):
    try:
        return httpx.get(url, params=params or {}, headers=headers or {}, timeout=TIMEOUT, follow_redirects=True)
    except Exception as exc:
        return exc


def extract_links(text):
    found, seen = [], set()
    patterns = [
        r"\[[^\]]*\]\((https?://[^)\s]+)",
        r"https?://[^\s<>\)\]\"']+",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text):
            u = m.group(1) if m.lastindex else m.group(0)
            u = u.rstrip(".,;\"'`)")
            if u not in seen:
                seen.add(u); found.append(u)
    return found


def strip_html(text):
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return unescape(re.sub(r"\s+", " ", text))


def normalize_path(raw):
    if not raw:
        return None
    raw = unescape(raw).strip().strip("`\"'<>[]()")
    raw = raw.split("?")[0].split("#")[0]
    if raw.startswith("https://api.roapp.io") or raw.startswith("http://api.roapp.io"):
        p = urlparse(raw).path
    else:
        p = raw
    if not p.startswith("/"):
        return None
    if p.startswith("/v2"):
        return p
    return "/v2" + p


def add_op(ops, seen, method, raw_path, source, evidence):
    method = method.upper()
    path = normalize_path(raw_path)
    if method not in METHODS or not path:
        return
    # Reject obvious documentation/navigation paths.
    if path.startswith("/v2/reference") or "readme" in path.lower():
        return
    key = (method, path)
    item = seen.get(key)
    if item is None:
        item = {"method": method, "path": path, "references": [], "evidence": []}
        seen[key] = item; ops.append(item)
    if source not in item["references"]:
        item["references"].append(source)
    if evidence and evidence not in item["evidence"] and len(item["evidence"]) < 8:
        item["evidence"].append(evidence[:300])


def extract_operations(raw_doc, source):
    """Extract only explicit method/path evidence; never infer from titles."""
    ops, seen = [], {}
    plain = strip_html(raw_doc)
    texts = [raw_doc, plain]

    # Explicit METHOD /path patterns, including OpenAPI-style lines.
    for text in texts:
        for m in re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE)\s+(`?/(?:v2/)?[A-Za-z0-9_./{}:-]+`?)", text, re.I):
            add_op(ops, seen, m.group(1), m.group(2), source, m.group(0))

        # Full API URLs are explicit path evidence. Method is taken from the
        # nearest explicit method token; otherwise the URL is unresolved.
        for m in re.finditer(r"https?://api\.roapp\.io(?:/v2)?/[A-Za-z0-9_./{}:-]+", text, re.I):
            start = max(0, m.start() - 180)
            context = text[start:m.end()]
            mm = re.search(r"\b(GET|POST|PUT|PATCH|DELETE)\b", context, re.I)
            if mm:
                add_op(ops, seen, mm.group(1), m.group(0), source, context)

        # Common fetch/curl/axios snippets where method is explicit in nearby text.
        for m in re.finditer(r"(?:curl|fetch|axios|requests\.(?:get|post|put|patch|delete))[^\n]{0,500}", text, re.I):
            chunk = m.group(0)
            mm = re.search(r"\b(GET|POST|PUT|PATCH|DELETE)\b", chunk, re.I)
            url = re.search(r"https?://api\.roapp\.io(?:/v2)?/[A-Za-z0-9_./{}:-]+", chunk, re.I)
            if mm and url:
                add_op(ops, seen, mm.group(1), url.group(0), source, chunk)

    # HTML/OpenAPI-ish attributes and JSON blobs may contain method/path separately.
    for m in re.finditer(r'(?is)(?:method|httpMethod)["\'\s:=]+(GET|POST|PUT|PATCH|DELETE)', raw_doc):
        tail = raw_doc[m.end():m.end()+1200]
        pm = re.search(r'(?:path|url|href|endpoint)["\'\s:=]+["\']?([^"\'\s,}]+)', tail, re.I)
        if pm:
            add_op(ops, seen, m.group(1), pm.group(1), source, m.group(0) + " ... " + pm.group(0))

    return ops


def rows(payload):
    if isinstance(payload, list): return payload
    if isinstance(payload, dict):
        for key in ("data", "items", "results", "orders", "people", "organizations", "services", "products", "employees", "locations"):
            if isinstance(payload.get(key), list): return payload[key]
    return []


def total_pages(payload):
    if not isinstance(payload, dict): return None
    for obj in (payload.get("paging"), payload.get("pagination"), payload.get("meta"), payload):
        if isinstance(obj, dict):
            for key in ("total_pages", "totalPages", "pages"):
                if isinstance(obj.get(key), int): return obj[key]
    return None


def summarize(items):
    return {
        "rows": len(items),
        "sample_ids": [x.get("id") for x in items[:5] if isinstance(x, dict) and x.get("id") is not None],
        "missing_id": sum(1 for x in items if isinstance(x, dict) and x.get("id") is None),
    }


print("=== MARSEL AUDIT V13 / OFFICIAL API INVENTORY / READ ONLY ===")
print(f"BASE={BASE}")
print(f"DOCS_INDEX={DOCS_INDEX}")

idx = request(DOCS_INDEX, headers=DOC_HEADERS)
if isinstance(idx, Exception):
    print(f"DOCS_INDEX_ERROR={idx}"); sys.exit(3)
print(f"DOCS_INDEX_HTTP={idx.status_code}")
if idx.status_code != 200:
    print("ERROR: official docs index could not be retrieved"); sys.exit(4)

refs = [u for u in extract_links(idx.text) if "/reference/" in u]
# Preserve order and deduplicate.
refs = list(dict.fromkeys(refs))
print(f"REFERENCE_LINKS={len(refs)}")

catalog, all_ops, doc_errors, parser_stats = [], [], [], {
    "pages_http_200": 0,
    "pages_non_200": 0,
    "pages_with_operations": 0,
    "pages_without_operations": 0,
}

for ref in refs:
    r = request(ref, headers=DOC_HEADERS)
    entry = {"reference": ref, "http_status": None, "operations": [], "parser": "v13-multi-representation"}
    if isinstance(r, Exception):
        entry["error"] = str(r); doc_errors.append(entry); catalog.append(entry); continue
    entry["http_status"] = r.status_code
    if r.status_code != 200:
        parser_stats["pages_non_200"] += 1
        doc_errors.append(entry); catalog.append(entry); continue
    parser_stats["pages_http_200"] += 1
    ops = extract_operations(r.text, ref)
    entry["operations"] = [{"method": x["method"], "path": x["path"]} for x in ops]
    if ops: parser_stats["pages_with_operations"] += 1
    else: parser_stats["pages_without_operations"] += 1
    all_ops.extend(ops)
    catalog.append(entry)

# Merge duplicate method/path pairs and retain every official source reference.
unique = {}
for op in all_ops:
    key = (op["method"], op["path"])
    dst = unique.setdefault(key, {"method": op["method"], "path": op["path"], "references": [], "evidence": []})
    for x in op["references"]:
        if x not in dst["references"]: dst["references"].append(x)
    for x in op["evidence"]:
        if x not in dst["evidence"] and len(dst["evidence"]) < 8: dst["evidence"].append(x)

ops = list(unique.values())
get_ops = [x for x in ops if x["method"] == "GET"]
write_ops = [x for x in ops if x["method"] != "GET"]
print(f"DOCUMENTED_OPERATIONS={len(ops)}")
print(f"DOCUMENTED_GET_OPERATIONS={len(get_ops)}")
print(f"DOCUMENTED_WRITE_OPERATIONS={len(write_ops)}")

results = []
for op in get_ops:
    path = op["path"]
    url = BASE + (path[3:] if path.startswith("/v2") else path)
    result = {"method":"GET", "path":path, "url":url, "references":op["references"]}
    first = request(url, {"page":1, "pageSize":PAGE_SIZE}, API_HEADERS)
    if isinstance(first, Exception):
        result.update({"classification":"unavailable","available":False,"error":str(first)})
        results.append(result); continue
    result["http_status"] = first.status_code
    if first.status_code != 200:
        result.update({"classification":"unavailable","available":False})
        results.append(result); continue
    try: payload = first.json()
    except Exception:
        result.update({"classification":"unavailable","available":False,"error":"non_json_response"})
        results.append(result); continue
    items = rows(payload)
    pages = total_pages(payload)
    result.update({"classification":"available","available":True,"page_size":PAGE_SIZE,"total_pages_reported":pages,"rows_first_page":len(items),"summary_first_page":summarize(items),"pages_scanned":1,"rows_scanned":len(items)})
    if isinstance(pages, int) and 2 <= pages <= MAX_PAGES:
        ok=True
        for page in range(2,pages+1):
            rr=request(url,{"page":page,"pageSize":PAGE_SIZE},API_HEADERS)
            if isinstance(rr,Exception) or rr.status_code != 200:
                result.update({"classification":"partial","pagination_complete":False,"failed_page":page}); ok=False; break
            try: pp=rr.json()
            except Exception:
                result.update({"classification":"partial","pagination_complete":False,"failed_page":page}); ok=False; break
            result["rows_scanned"] += len(rows(pp)); result["pages_scanned"] = page
        if ok: result["pagination_complete"] = True
    else:
        result["pagination_complete"] = pages in (None,1)
    results.append(result)

report={
    "audit":"MARSEL_AUDIT_V13",
    "timestamp_utc":datetime.now(timezone.utc).isoformat(),
    "readonly":True,
    "official_docs":{"index":DOCS_INDEX,"http_status":idx.status_code,"reference_count":len(refs),"catalog":catalog,"documentation_errors":doc_errors,"parser_stats":parser_stats},
    "api_catalog":{"documented_operations":ops,"documented_get_operations":get_ops,"documented_write_operations":write_ops,"get_results":results},
    "classifications":{"documented":len(ops),"parseable":len(ops),"probeable":len(get_ops),"available":sum(1 for x in results if x.get("available")),"unavailable":sum(1 for x in results if x.get("classification")=="unavailable"),"partial":sum(1 for x in results if x.get("classification")=="partial"),"unresolved":len(refs)-parser_stats["pages_with_operations"]},
    "safety":{"writes_performed":False,"updates_performed":False,"deletes_performed":False,"non_get_endpoints_called":False,"pii_persisted":False}
}
with open(OUT,"w",encoding="utf-8") as fh: json.dump(report,fh,ensure_ascii=False,indent=2)

print(f"GET_RESULTS={len(results)}")
print(f"GET_AVAILABLE={sum(1 for x in results if x.get('available'))}")
print(f"GET_UNAVAILABLE={sum(1 for x in results if x.get('classification')=='unavailable')}")
print(f"GET_PARTIAL={sum(1 for x in results if x.get('classification')=='partial')}")
print(f"UNRESOLVED_REFERENCE_PAGES={report['classifications']['unresolved']}")
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
