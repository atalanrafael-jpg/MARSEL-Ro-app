#!/usr/bin/env python3
"""MARSEL V15 — documentation-first RO App API inventory, read-only.

V14 proved that scraping explicit HTTP method/path pairs is too narrow for the
RO App ReadMe catalog. V15 therefore treats every reference entry as a
DOCUMENTED OPERATION based on its title, while separately extracting explicit
HTTP method/path evidence when present. It never invents an endpoint from a
title. Only endpoints with explicit GET evidence are eligible for probing.

Safety: only GET requests are probed. No POST/PUT/PATCH/DELETE requests are
sent and no customer payload/free text is persisted.
"""
import json, os, re, sys
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urlparse
import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS_INDEX = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = os.environ.get("MARSEL_AUDIT_OUT", "marsel-api-master-inventory-v15.json")
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
    out, seen = [], set()
    for u in re.findall(r"https?://[^\s<>\)\]\"'`]+", text):
        u = u.rstrip(".,;\"'`)")
        if u not in seen:
            seen.add(u); out.append(u)
    return out


def title_from_index_line(line):
    m = re.search(r"\[([^\]]+)\]\(https://roapp\.readme\.io/reference/[^)]+\)", line)
    return m.group(1).strip() if m else None


def description_from_index_line(line):
    m = re.search(r"\):\s*(.+)$", line)
    return m.group(1).strip() if m else None


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
    return p if p.startswith("/v2") else "/v2" + p


def extract_ops(text):
    found = []
    bodies = [text, html_to_text(text)]
    for body in bodies:
        patterns = [
            r"(?im)(?<![A-Z])(GET|POST|PUT|PATCH|DELETE)\s+(`?https?://api\.roapp\.io(?:/v2)?/[^\s`\"']+|`?/(?:v2/)?[A-Za-z0-9_.:/{}-]+`?)",
            r"(?is)\b(GET|POST|PUT|PATCH|DELETE)\b.{0,300}?((?:https?://api\.roapp\.io)?(?:/v2)?/[A-Za-z0-9_.:/{}-]+)",
            r'(?is)["\'](?:method|httpMethod)["\']\s*[:=]\s*["\'](GET|POST|PUT|PATCH|DELETE)["\'].{0,2000}?["\'](?:path|url|endpoint|href)["\']\s*[:=]\s*["\']([^"\']+)',
            r'(?is)["\'](?:path|url|endpoint|href)["\']\s*[:=]\s*["\']([^"\']+)["\'].{0,2000}?["\'](?:method|httpMethod)["\']\s*[:=]\s*["\'](GET|POST|PUT|PATCH|DELETE)'
        ]
        for i, pattern in enumerate(patterns):
            for m in re.finditer(pattern, body):
                if i == 3:
                    method, raw = m.group(2), m.group(1)
                else:
                    method, raw = m.group(1), m.group(2)
                path = normalize_path(raw)
                if path and (method.upper(), path) not in found:
                    found.append((method.upper(), path, m.group(0)[:500]))
        for m in re.finditer(r"(?is)(?:curl|fetch|axios|requests\.(?:get|post|put|patch|delete))[^\n]{0,1200}", body):
            chunk = m.group(0)
            url = re.search(r"https?://api\.roapp\.io(?:/v2)?/[A-Za-z0-9_.:/{}-]+", chunk)
            meth = re.search(r"\b(GET|POST|PUT|PATCH|DELETE)\b", chunk, re.I)
            if not meth:
                fn = re.search(r"requests\.(get|post|put|patch|delete)", chunk, re.I)
                if fn: meth = fn
            if url and meth:
                item = (meth.group(1).upper(), normalize_path(url.group(0)), chunk[:500])
                if item[1] and item[:2] not in [(x[0], x[1]) for x in found]:
                    found.append(item)
    return found


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


def summary(items):
    return {"rows": len(items), "sample_ids": [x.get("id") for x in items[:5] if isinstance(x, dict) and x.get("id") is not None], "missing_id": sum(1 for x in items if isinstance(x, dict) and x.get("id") is None)}


def classify_title(title):
    t = title.lower()
    if t.startswith(("get ", "retrieve ", "getting started")) or t.startswith("get "):
        return "GET_DOCUMENTED"
    if t.startswith(("create ", "add ", "update ", "delete ", "change ", "merge ")):
        return "WRITE_DOCUMENTED"
    if "webhook" in t or t == "mcp":
        return "INTEGRATION_DOCUMENTED"
    return "DOCUMENTED"

print("=== MARSEL AUDIT V15 / DOCUMENTATION-FIRST API INVENTORY / READ ONLY ===")
print(f"BASE={BASE}")
print(f"DOCS_INDEX={DOCS_INDEX}")
idx = get(DOCS_INDEX, headers=DOC_HEADERS)
if isinstance(idx, Exception): print(f"DOCS_INDEX_ERROR={idx}"); sys.exit(3)
print(f"DOCS_INDEX_HTTP={idx.status_code}")
if idx.status_code != 200: sys.exit(4)

# Parse the catalog as markdown lines so the documentation title is preserved
# even when the individual ReadMe reference page cannot be fetched.
refs = []
for line in idx.text.splitlines():
    for u in unique_links(line):
        if "/reference/" in u:
            title = title_from_index_line(line) or u.rsplit("/",1)[-1].removesuffix(".md")
            refs.append({"url":u, "title":title, "description":description_from_index_line(line)})
seen=set(); catalog=[]
for x in refs:
    if x["url"] not in seen: seen.add(x["url"]); catalog.append(x)
print(f"REFERENCE_LINKS={len(catalog)}")

operations=[]
explicit=[]
unresolved=[]
for ref in catalog:
    entry={"reference":ref["url"],"title":ref["title"],"description":ref["description"],"documentation_class":classify_title(ref["title"]),"endpoint_evidence":[],"page_fetches":[]}
    candidates=[ref["url"]]
    if ref["url"].endswith(".md"): candidates.append(ref["url"][:-3])
    for candidate in dict.fromkeys(candidates):
        r=get(candidate,headers=DOC_HEADERS)
        if isinstance(r,Exception): entry["page_fetches"].append({"url":candidate,"status":None,"error":str(r)}); continue
        entry["page_fetches"].append({"url":candidate,"status":r.status_code,"bytes":len(r.content)})
        if r.status_code==200:
            for method,path,evidence in extract_ops(r.text):
                item={"method":method,"path":path,"reference":ref["url"],"title":ref["title"],"evidence":evidence}
                explicit.append(item); entry["endpoint_evidence"].append(item)
            if entry["endpoint_evidence"]: break
    if entry["documentation_class"] in ("GET_DOCUMENTED","WRITE_DOCUMENTED"):
        operations.append(entry)
    if not entry["endpoint_evidence"]: unresolved.append(entry)

# Deduplicate explicit endpoint evidence.
uniq={}
for x in explicit: uniq[(x["method"],x["path"])]=x
explicit=list(uniq.values())
get_ops=[x for x in explicit if x["method"]=="GET"]
write_ops=[x for x in explicit if x["method"]!="GET"]

results=[]
for op in get_ops:
    url=BASE+(op["path"][3:] if op["path"].startswith("/v2") else op["path"])
    result={"method":"GET","path":op["path"],"url":url,"reference":op["reference"],"title":op["title"]}
    r=get(url,{"page":1,"pageSize":PAGE_SIZE},API_HEADERS)
    if isinstance(r,Exception): result.update({"classification":"unavailable","available":False,"error":str(r)}); results.append(result); continue
    result["http_status"]=r.status_code
    if r.status_code!=200: result.update({"classification":"unavailable","available":False}); results.append(result); continue
    try: payload=r.json()
    except Exception: result.update({"classification":"unavailable","available":False,"error":"non_json_response"}); results.append(result); continue
    items=rows(payload); pages=total_pages(payload)
    result.update({"classification":"available","available":True,"page_size":PAGE_SIZE,"total_pages_reported":pages,"rows_first_page":len(items),"rows_scanned":len(items),"pages_scanned":1,"summary_first_page":summary(items)})
    if isinstance(pages,int) and 2<=pages<=MAX_PAGES:
        complete=True
        for page in range(2,pages+1):
            rr=get(url,{"page":page,"pageSize":PAGE_SIZE},API_HEADERS)
            if isinstance(rr,Exception) or rr.status_code!=200: result.update({"classification":"partial","pagination_complete":False,"failed_page":page}); complete=False; break
            try: pp=rr.json()
            except Exception: result.update({"classification":"partial","pagination_complete":False,"failed_page":page}); complete=False; break
            result["rows_scanned"]+=len(rows(pp)); result["pages_scanned"]=page
        if complete: result["pagination_complete"]=True
    else: result["pagination_complete"]=pages in (None,1)
    results.append(result)

report={"audit":"MARSEL_AUDIT_V15","timestamp_utc":datetime.now(timezone.utc).isoformat(),"readonly":True,
"official_docs":{"index":DOCS_INDEX,"http_status":idx.status_code,"reference_count":len(catalog),"catalog":catalog,"unresolved_pages":unresolved},
"documentation_inventory":{"documented_operations":operations,"documented_operation_count":len(operations),"documented_get_by_title":sum(1 for x in operations if x["documentation_class"]=="GET_DOCUMENTED"),"documented_write_by_title":sum(1 for x in operations if x["documentation_class"]=="WRITE_DOCUMENTED")},
"endpoint_inventory":{"explicit_endpoint_count":len(explicit),"explicit_get_count":len(get_ops),"explicit_write_count":len(write_ops),"explicit_endpoints":explicit,"get_probe_results":results},
"classifications":{"get_results":len(results),"get_available":sum(1 for x in results if x.get("available")),"get_unavailable":sum(1 for x in results if x.get("classification")=="unavailable"),"get_partial":sum(1 for x in results if x.get("classification")=="partial"),"unresolved_reference_pages":len(unresolved)},
"safety":{"writes_performed":False,"updates_performed":False,"deletes_performed":False,"non_get_endpoints_called":False,"pii_persisted":False}}
with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(f"DOCUMENTED_OPERATION_ENTRIES={len(operations)}")
print(f"DOCUMENTED_GET_BY_TITLE={report['documentation_inventory']['documented_get_by_title']}")
print(f"DOCUMENTED_WRITE_BY_TITLE={report['documentation_inventory']['documented_write_by_title']}")
print(f"EXPLICIT_ENDPOINTS={len(explicit)}")
print(f"EXPLICIT_GET_ENDPOINTS={len(get_ops)}")
print(f"EXPLICIT_WRITE_ENDPOINTS={len(write_ops)}")
print(f"GET_RESULTS={len(results)}")
print(f"GET_AVAILABLE={sum(1 for x in results if x.get('available'))}")
print(f"GET_UNAVAILABLE={sum(1 for x in results if x.get('classification')=='unavailable')}")
print(f"GET_PARTIAL={sum(1 for x in results if x.get('classification')=='partial')}")
print(f"UNRESOLVED_REFERENCE_PAGES={len(unresolved)}")
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
