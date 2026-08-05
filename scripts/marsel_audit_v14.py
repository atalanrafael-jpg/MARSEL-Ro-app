#!/usr/bin/env python3
"""MARSEL V14 — official RO App API catalog, read-only.

V13 showed that the documentation index is reachable but many reference pages
were not parsed into operations. V14 deliberately separates discovery from
probing and fetches each reference in several representations, including the
explicit .md representation exposed by ReadMe/llms.txt. It extracts only
explicit HTTP method + endpoint evidence and never infers a write operation.

Safety: only GET requests are probed against the RO App API. No POST/PUT/PATCH/
DELETE requests are sent and no customer payload/free text is persisted.
"""
import json, os, re, sys
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urlparse
import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS_INDEX = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = os.environ.get("MARSEL_AUDIT_OUT", "marsel-api-master-inventory-v14.json")
PAGE_SIZE = int(os.environ.get("ROAPP_PAGE_SIZE", "50"))
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "45"))
MAX_PAGES = int(os.environ.get("ROAPP_MAX_PAGES", "10000"))

if not KEY:
    print("ERROR: ROAPP_API_KEY is not configured")
    sys.exit(2)

API_HEADERS = {"Authorization": f"Bearer {KEY}", "Accept": "application/json"}
DOC_HEADERS = {"Accept": "text/markdown, text/plain, text/html, application/json, */*"}
METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE")


def get(url, params=None, headers=None):
    try:
        return httpx.get(url, params=params or {}, headers=headers or {}, timeout=TIMEOUT, follow_redirects=True)
    except Exception as exc:
        return exc


def unique_links(text):
    urls = re.findall(r"https?://[^\s<>\)\]\"'`]+", text)
    out = []
    seen = set()
    for u in urls:
        u = u.rstrip(".,;\"'`)")
        if u not in seen:
            seen.add(u); out.append(u)
    return out


def html_to_text(text):
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return unescape(re.sub(r"\s+", " ", text))


def normalize_path(raw):
    if not raw:
        return None
    raw = unescape(raw).strip().strip("`\"'<>[]()")
    raw = raw.split("?")[0].split("#")[0]
    if raw.startswith("http://") or raw.startswith("https://"):
        p = urlparse(raw).path
    else:
        p = raw
    if not p.startswith("/"):
        return None
    if p.startswith("/v2"):
        return p
    return "/v2" + p


def add_op(store, method, raw_path, ref, evidence, confidence="explicit"):
    method = method.upper()
    path = normalize_path(raw_path)
    if method not in METHODS or not path:
        return
    if "/reference/" in path or "readme" in path.lower():
        return
    key = (method, path)
    item = store.setdefault(key, {"method": method, "path": path, "confidence": confidence, "references": [], "evidence": []})
    if ref not in item["references"]:
        item["references"].append(ref)
    if evidence:
        evidence = re.sub(r"\s+", " ", evidence).strip()
        if evidence not in item["evidence"] and len(item["evidence"]) < 10:
            item["evidence"].append(evidence[:500])


def extract_from_text(text, ref, store):
    variants = [text, html_to_text(text)]
    for body in variants:
        # Markdown / OpenAPI / shell: GET /v2/foo, `GET /foo`, etc.
        for m in re.finditer(r"(?im)(?<![A-Z])(GET|POST|PUT|PATCH|DELETE)\s+(`?https?://api\.roapp\.io(?:/v2)?/[^\s`\"']+|`?/(?:v2/)?[A-Za-z0-9_.:/{}-]+`?)", body):
            add_op(store, m.group(1), m.group(2), ref, m.group(0))

        # ReadMe frequently renders endpoint cards as METHOD + URL on adjacent lines.
        for m in re.finditer(r"(?is)\b(GET|POST|PUT|PATCH|DELETE)\b.{0,240}?((?:https?://api\.roapp\.io)?(?:/v2)?/[A-Za-z0-9_.:/{}-]+)", body):
            add_op(store, m.group(1), m.group(2), ref, m.group(0))

        # JSON/OpenAPI-ish structures: {"method":"GET","path":"/foo"}
        for m in re.finditer(r'(?is)["\'](?:method|httpMethod)["\']\s*[:=]\s*["\'](GET|POST|PUT|PATCH|DELETE)["\'].{0,1500}?["\'](?:path|url|endpoint|href)["\']\s*[:=]\s*["\']([^"\']+)', body):
            add_op(store, m.group(1), m.group(2), ref, m.group(0))

        # Method/path JSON order reversed.
        for m in re.finditer(r'(?is)["\'](?:path|url|endpoint|href)["\']\s*[:=]\s*["\']([^"\']+)["\'].{0,1500}?["\'](?:method|httpMethod)["\']\s*[:=]\s*["\'](GET|POST|PUT|PATCH|DELETE)', body):
            add_op(store, m.group(2), m.group(1), ref, m.group(0))

        # cURL/fetch/axios examples. Method must be explicit or the function name
        # itself supplies it (requests.get/post/etc.).
        for m in re.finditer(r"(?is)(?:curl|fetch|axios|requests\.(?:get|post|put|patch|delete))[^\n]{0,900}", body):
            chunk = m.group(0)
            url = re.search(r"https?://api\.roapp\.io(?:/v2)?/[A-Za-z0-9_.:/{}-]+", chunk)
            meth = re.search(r"\b(GET|POST|PUT|PATCH|DELETE)\b", chunk, re.I)
            if not meth:
                fn = re.search(r"requests\.(get|post|put|patch|delete)", chunk, re.I)
                if fn: meth = fn
            if url and meth:
                add_op(store, meth.group(1), url.group(0), ref, chunk)


def md_candidates(ref):
    p = urlparse(ref)
    if p.netloc != "roapp.readme.io" or "/reference/" not in p.path:
        return []
    base = "https://roapp.readme.io" + p.path
    candidates = [base]
    if not base.endswith(".md"):
        candidates.append(base + ".md")
    return list(dict.fromkeys(candidates))


def rows(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "items", "results", "orders", "people", "organizations", "services", "products", "employees", "locations"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []


def total_pages(payload):
    if not isinstance(payload, dict):
        return None
    for obj in (payload.get("paging"), payload.get("pagination"), payload.get("meta"), payload):
        if isinstance(obj, dict):
            for key in ("total_pages", "totalPages", "pages"):
                if isinstance(obj.get(key), int):
                    return obj[key]
    return None


def safe_summary(items):
    return {"rows": len(items), "sample_ids": [x.get("id") for x in items[:5] if isinstance(x, dict) and x.get("id") is not None], "missing_id": sum(1 for x in items if isinstance(x, dict) and x.get("id") is None)}


print("=== MARSEL AUDIT V14 / OFFICIAL API CATALOG / READ ONLY ===")
print(f"BASE={BASE}")
print(f"DOCS_INDEX={DOCS_INDEX}")
idx = get(DOCS_INDEX, headers=DOC_HEADERS)
if isinstance(idx, Exception):
    print(f"DOCS_INDEX_ERROR={idx}"); sys.exit(3)
print(f"DOCS_INDEX_HTTP={idx.status_code}")
if idx.status_code != 200:
    print("ERROR: official docs index could not be retrieved"); sys.exit(4)

refs = [u for u in unique_links(idx.text) if "/reference/" in u]
refs = list(dict.fromkeys(refs))
print(f"REFERENCE_LINKS={len(refs)}")

ops_store = {}
page_catalog = []
stats = {"index_200": True, "page_200": 0, "page_non_200": 0, "page_md_200": 0, "page_with_ops": 0, "page_without_ops": 0}

for ref in refs:
    entry = {"reference": ref, "representations": [], "operations": []}
    reps = md_candidates(ref)
    # Prefer explicit .md representation, then the normal reference URL.
    if len(reps) == 2:
        reps = [reps[1], reps[0]]
    for candidate in reps:
        r = get(candidate, headers=DOC_HEADERS)
        rep = {"url": candidate, "http_status": None, "operations_found": 0}
        if isinstance(r, Exception):
            rep["error"] = str(r)
            entry["representations"].append(rep)
            continue
        rep["http_status"] = r.status_code
        if r.status_code == 200:
            stats["page_200"] += 1
            if candidate.endswith(".md"): stats["page_md_200"] += 1
            before = len(ops_store)
            extract_from_text(r.text, ref, ops_store)
            rep["operations_found"] = len(ops_store) - before
            if rep["operations_found"]:
                entry["representations"].append(rep)
                break
        else:
            stats["page_non_200"] += 1
        entry["representations"].append(rep)
    entry["operations"] = [{"method": k[0], "path": k[1]} for k,v in ops_store.items() if ref in v["references"]]
    if entry["operations"]: stats["page_with_ops"] += 1
    else: stats["page_without_ops"] += 1
    page_catalog.append(entry)

ops = list(ops_store.values())
get_ops = [x for x in ops if x["method"] == "GET"]
write_ops = [x for x in ops if x["method"] != "GET"]
print(f"DOCUMENTED_OPERATIONS={len(ops)}")
print(f"DOCUMENTED_GET_OPERATIONS={len(get_ops)}")
print(f"DOCUMENTED_WRITE_OPERATIONS={len(write_ops)}")

results = []
for op in get_ops:
    path = op["path"]
    api_path = path[3:] if path.startswith("/v2") else path
    url = BASE + api_path
    result = {"method":"GET", "path":path, "url":url, "references":op["references"]}
    r = get(url, {"page":1,"pageSize":PAGE_SIZE}, API_HEADERS)
    if isinstance(r, Exception):
        result.update({"classification":"unavailable","available":False,"error":str(r)})
        results.append(result); continue
    result["http_status"] = r.status_code
    if r.status_code != 200:
        result.update({"classification":"unavailable","available":False})
        results.append(result); continue
    try: payload = r.json()
    except Exception:
        result.update({"classification":"unavailable","available":False,"error":"non_json_response"})
        results.append(result); continue
    items = rows(payload); pages = total_pages(payload)
    result.update({"classification":"available","available":True,"page_size":PAGE_SIZE,"total_pages_reported":pages,"rows_first_page":len(items),"summary_first_page":safe_summary(items),"pages_scanned":1,"rows_scanned":len(items)})
    if isinstance(pages,int) and 2 <= pages <= MAX_PAGES:
        complete=True
        for page in range(2,pages+1):
            rr=get(url,{"page":page,"pageSize":PAGE_SIZE},API_HEADERS)
            if isinstance(rr,Exception) or rr.status_code != 200:
                result.update({"classification":"partial","pagination_complete":False,"failed_page":page}); complete=False; break
            try: pp=rr.json()
            except Exception:
                result.update({"classification":"partial","pagination_complete":False,"failed_page":page}); complete=False; break
            result["rows_scanned"] += len(rows(pp)); result["pages_scanned"] = page
        if complete: result["pagination_complete"] = True
    else:
        result["pagination_complete"] = pages in (None,1)
    results.append(result)

report = {
    "audit":"MARSEL_AUDIT_V14",
    "timestamp_utc":datetime.now(timezone.utc).isoformat(),
    "readonly":True,
    "official_docs":{"index":DOCS_INDEX,"http_status":idx.status_code,"reference_count":len(refs),"page_catalog":page_catalog,"stats":stats},
    "api_catalog":{"documented_operations":ops,"documented_get_operations":get_ops,"documented_write_operations":write_ops,"get_results":results},
    "classifications":{"documented":len(ops),"probeable":len(get_ops),"available":sum(1 for x in results if x.get("available")),"unavailable":sum(1 for x in results if x.get("classification")=="unavailable"),"partial":sum(1 for x in results if x.get("classification")=="partial"),"unresolved_reference_pages":sum(1 for x in page_catalog if not x["operations"])},
    "safety":{"writes_performed":False,"updates_performed":False,"deletes_performed":False,"non_get_endpoints_called":False,"pii_persisted":False}
}
with open(OUT,"w",encoding="utf-8") as fh:
    json.dump(report,fh,ensure_ascii=False,indent=2)

print(f"GET_RESULTS={len(results)}")
print(f"GET_AVAILABLE={sum(1 for x in results if x.get('available'))}")
print(f"GET_UNAVAILABLE={sum(1 for x in results if x.get('classification')=='unavailable')}")
print(f"GET_PARTIAL={sum(1 for x in results if x.get('classification')=='partial')}")
print(f"UNRESOLVED_REFERENCE_PAGES={report['classifications']['unresolved_reference_pages']}")
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
