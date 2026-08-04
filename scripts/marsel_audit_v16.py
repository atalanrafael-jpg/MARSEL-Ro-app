#!/usr/bin/env python3
"""MARSEL V16 — OpenAPI-first RO App API discovery, read-only."""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlparse
import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS_INDEX = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = os.environ.get("MARSEL_AUDIT_OUT", "marsel-api-master-inventory-v16.json")
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "45"))
PAGE_SIZE = int(os.environ.get("ROAPP_PAGE_SIZE", "50"))
MAX_DOC_PAGES = int(os.environ.get("MARSEL_V16_MAX_DOC_PAGES", "200"))

if not KEY:
    print("ERROR: ROAPP_API_KEY is not configured")
    sys.exit(2)

API_HEADERS = {"Authorization": f"Bearer {KEY}", "Accept": "application/json"}
DOC_HEADERS = {"Accept": "text/markdown, text/plain, text/html, application/json, */*"}


def get(url, params=None, headers=None):
    try:
        return httpx.get(url, params=params or {}, headers=headers or {}, timeout=TIMEOUT, follow_redirects=True)
    except Exception as exc:
        return exc


def links(text):
    out, seen = [], set()
    for raw in re.findall(r"https?://[^\s<>\)\]\"'`]+", text or ""):
        # Keep the quote/backtick characters inside a properly terminated Python string.
        u = raw.rstrip(".,;\"'`")
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def title_from_line(line):
    m = re.search(r"\[([^\]]+)\]\(https://roapp\.readme\.io/reference/[^)]+\)", line)
    return m.group(1).strip() if m else None


def is_openapi_url(url):
    p = urlparse(url)
    s = (p.path + "?" + p.query).lower()
    return any(x in s for x in ("openapi", "swagger", "api-docs")) or (p.path.lower().endswith((".yaml", ".yml", ".json")) and any(x in p.path.lower() for x in ("api", "spec", "swagger")))


def extract_spec_links(text):
    return [u for u in links(text) if is_openapi_url(u)]


def parse_openapi(text):
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and ("openapi" in obj or "swagger" in obj) and isinstance(obj.get("paths"), dict):
            return obj, "json"
    except Exception:
        pass
    try:
        import yaml
        obj = yaml.safe_load(text)
        if isinstance(obj, dict) and ("openapi" in obj or "swagger" in obj) and isinstance(obj.get("paths"), dict):
            return obj, "yaml"
    except Exception:
        pass
    return None, None


def method_inventory(spec):
    methods = {"get":0,"post":0,"put":0,"patch":0,"delete":0,"head":0,"options":0,"trace":0}
    paths = []
    for raw_path, item in spec.get("paths", {}).items():
        if not isinstance(item, dict):
            continue
        entry = {"path": raw_path, "methods": []}
        for method in methods:
            if method in item:
                methods[method] += 1
                entry["methods"].append(method.upper())
        if entry["methods"]:
            paths.append(entry)
    return methods, paths


def api_url(path):
    if path.startswith("http://") or path.startswith("https://"):
        return path
    p = path if path.startswith("/") else "/" + path
    if p.startswith("/v2"):
        return BASE.split("/v2",1)[0] + p
    return BASE + p


def response_shape(payload):
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        for k in ("data","items","results","orders","people","organizations","services","products","employees","locations"):
            if isinstance(payload.get(k), list):
                return len(payload[k])
    return 0


print("=== MARSEL AUDIT V16 / OPENAPI-FIRST API DISCOVERY / READ ONLY ===")
print(f"BASE={BASE}")
print(f"DOCS_INDEX={DOCS_INDEX}")
idx = get(DOCS_INDEX, headers=DOC_HEADERS)
if isinstance(idx, Exception):
    print(f"DOCS_INDEX_ERROR={idx}")
    sys.exit(3)
print(f"DOCS_INDEX_HTTP={idx.status_code}")
if idx.status_code != 200:
    sys.exit(4)

catalog=[]; seen=set()
for line in idx.text.splitlines():
    for u in links(line):
        if "/reference/" in u and u not in seen:
            seen.add(u); catalog.append({"url":u,"title":title_from_line(line) or u.rsplit("/",1)[-1]})
print(f"REFERENCE_LINKS={len(catalog)}")

spec_candidates=[]; candidate_seen=set()
for u in extract_spec_links(idx.text):
    if u not in candidate_seen:
        candidate_seen.add(u); spec_candidates.append({"url":u,"source":"llms_index"})

page_results=[]
for ref in catalog[:MAX_DOC_PAGES]:
    r=get(ref["url"], headers=DOC_HEADERS)
    rec={"reference":ref["url"],"title":ref["title"],"status":None,"bytes":0,"spec_links":[]}
    if isinstance(r, Exception):
        rec["error"]=str(r); page_results.append(rec); continue
    rec["status"]=r.status_code; rec["bytes"]=len(r.content)
    if r.status_code == 200:
        found=extract_spec_links(r.text)
        rec["spec_links"]=found
        for u in found:
            if u not in candidate_seen:
                candidate_seen.add(u); spec_candidates.append({"url":u,"source":ref["url"]})
    page_results.append(rec)

print(f"OPENAPI_CANDIDATES={len(spec_candidates)}")

validated=[]
for c in spec_candidates:
    r=get(c["url"], headers=DOC_HEADERS)
    rec={"url":c["url"],"source":c["source"],"status":None,"valid":False}
    if isinstance(r, Exception): rec["error"]=str(r); validated.append(rec); continue
    rec["status"]=r.status_code; rec["content_type"]=r.headers.get("content-type",""); rec["bytes"]=len(r.content)
    if r.status_code == 200:
        spec, fmt=parse_openapi(r.text)
        if spec:
            methods, paths=method_inventory(spec)
            rec.update({"valid":True,"format":fmt,"version":spec.get("openapi") or spec.get("swagger"),"path_count":len(paths),"method_counts":methods,"paths":paths})
    validated.append(rec)

valid_specs=[x for x in validated if x.get("valid")]
print(f"OPENAPI_VALID_SPECS={len(valid_specs)}")

all_ops={}
for spec in valid_specs:
    for p in spec["paths"]:
        for method in p["methods"]:
            all_ops[(method,p["path"])]={"method":method,"path":p["path"],"source":spec["url"]}
ops=list(all_ops.values())
get_ops=[x for x in ops if x["method"]=="GET"]
write_ops=[x for x in ops if x["method"]!="GET"]
print(f"OPENAPI_ENDPOINTS={len(ops)}")
print(f"OPENAPI_GET_ENDPOINTS={len(get_ops)}")
print(f"OPENAPI_WRITE_ENDPOINTS={len(write_ops)}")

probe=[]
for op in get_ops:
    if re.search(r"\{[^}]+\}", op["path"]):
        probe.append({**op,"classification":"template_not_probed","available":None}); continue
    url=api_url(op["path"])
    r=get(url,{"page":1,"pageSize":PAGE_SIZE},API_HEADERS)
    rec={**op,"url":url,"http_status":None,"classification":"unavailable","available":False}
    if isinstance(r,Exception): rec["error"]=str(r)
    else:
        rec["http_status"]=r.status_code
        if r.status_code==200:
            try:
                payload=r.json(); rec.update({"classification":"available","available":True,"rows_first_page":response_shape(payload)})
            except Exception:
                rec["classification"]="non_json"
    probe.append(rec)

report={
 "audit":"MARSEL_AUDIT_V16",
 "timestamp_utc":datetime.now(timezone.utc).isoformat(),
 "readonly":True,
 "official_docs":{"index":DOCS_INDEX,"http_status":idx.status_code,"reference_count":len(catalog),"reference_fetches":page_results},
 "openapi_discovery":{"candidates":spec_candidates,"validated":validated,"valid_spec_count":len(valid_specs),"status":"FOUND" if valid_specs else "OPENAPI_NOT_FOUND"},
 "openapi_inventory":{"endpoint_count":len(ops),"get_count":len(get_ops),"write_count":len(write_ops),"endpoints":ops},
 "get_probes":probe,
 "safety":{"writes_performed":False,"updates_performed":False,"deletes_performed":False,"non_get_endpoints_called":False,"pii_persisted":False}
}
with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(f"REPORT={OUT}")
print(f"OPENAPI_STATUS={report['openapi_discovery']['status']}")
print(f"GET_PROBES={len(probe)}")
print(f"GET_AVAILABLE={sum(1 for x in probe if x.get('available') is True)}")
print(f"GET_UNAVAILABLE={sum(1 for x in probe if x.get('classification')=='unavailable')}")
print(f"GET_TEMPLATE_NOT_PROBED={sum(1 for x in probe if x.get('classification')=='template_not_probed')}")
print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
