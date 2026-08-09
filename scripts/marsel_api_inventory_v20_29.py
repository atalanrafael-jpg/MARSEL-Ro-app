#!/usr/bin/env python3
"""MARSEL V20.30 — RO App API inventory, READ ONLY.

Evidence-first inventory from official RO App ReadMe indexes. Only explicit
API URLs/paths found in fetched documentation are eligible for GET probing.
No write method is ever called and parameterized identifiers are never guessed.
"""
from __future__ import annotations
import hashlib, html, json, os, re, sys, time
from urllib.parse import urljoin, urlparse, urlsplit
from urllib.request import Request, urlopen

VERSION = "20.30"
DEFAULT_INDEXES = ("https://roapp.readme.io/llms.txt", "https://roappua.readme.io/llms.txt")
DOCS_INDEXES = [x.strip() for x in os.environ.get("ROAPP_DOCS_INDEXES", ",".join(DEFAULT_INDEXES)).split(",") if x.strip()]
BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
OUT = os.environ.get("MARSEL_API_INVENTORY_OUTPUT", "marsel-api-inventory-v20-30.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "10"))
MAX_DOCS = int(os.environ.get("MARSEL_MAX_DOCS", "60"))
MIN_INTERVAL = float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.20"))
MAX_RETRIES = int(os.environ.get("ROAPP_MAX_RETRIES", "0"))
RETRY_BASE = float(os.environ.get("ROAPP_RETRY_BASE_SECONDS", "0.5"))
METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
TITLE_METHODS = {"get":"GET","create":"POST","add":"POST","update":"PUT","delete":"DELETE","merge":"POST","change":"PATCH"}
API_URL_RE = re.compile(r"https?://api\.roapp\.io/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?", re.I)
PATH_RE = re.compile(r"/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?", re.I)
HREF_RE = re.compile(r"(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.I)
_last = 0.0

def fetch(url, headers=None):
    global _last
    hdr = headers or {"User-Agent": f"MARSEL-Audit-V{VERSION}", "Accept": "text/html,text/plain,text/markdown,application/json,application/yaml,text/yaml"}
    last = None
    for attempt in range(MAX_RETRIES + 1):
        wait = MIN_INTERVAL - (time.monotonic() - _last)
        if wait > 0: time.sleep(wait)
        req = Request(url, headers=hdr, method="GET")
        started = time.time()
        try:
            _last = time.monotonic()
            with urlopen(req, timeout=TIMEOUT) as r:
                body = r.read().decode("utf-8", errors="replace")
                return r.status, body, round(time.time()-started,3), None
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
            if attempt >= MAX_RETRIES: return None, "", round(time.time()-started,3), last
        time.sleep(min(RETRY_BASE*(2**attempt), 10.0))
    return None, "", 0, last or "request failed"

def clean(s): return html.unescape(str(s)).strip().replace("\\/","/").strip("`'\"<>[](){};,.:")

def normalize_path(raw):
    raw = clean(raw)
    if raw.startswith(("http://","https://")):
        p=urlparse(raw)
        if p.netloc.lower()!="api.roapp.io": return None
        raw=p.path
    raw=raw.split("#",1)[0]
    if raw in {"/v2","/v2/","/1.1","/1.1/"}: return None
    if raw.startswith(("/v2/","/1.1/")):
        raw=re.sub(r"/v2/v2/","/v2/",raw); raw=re.sub(r"/1\.1/1\.1/","/1.1/",raw); return raw
    return None

def nearby_method(text,start,end):
    win=text[max(0,start-1000):min(len(text),end+1000)]
    ms=list(re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE)\b",win,re.I))
    if not ms:return None
    center=start-max(0,start-1000); return min(ms,key=lambda m:abs(m.start()-center)).group(1).upper()

def title_method(title): return TITLE_METHODS.get(title.strip().split(None,1)[0].casefold() if title.strip() else "")

def add(store,method,path,evidence,source,detail):
    if method not in METHODS:return
    p=normalize_path(path)
    if not p:return
    key=(method,p); rank={"OPENAPI_CONFIRMED":4,"DOCUMENTATION_CONFIRMED":3,"URL_CONFIRMED":2}
    if key not in store: store[key]={"method":method,"path":p,"evidence":evidence,"sources":[source] if source else [],"details":[detail] if detail else []}; return
    item=store[key]
    if source and source not in item["sources"]:item["sources"].append(source)
    if detail and detail not in item["details"]:item["details"].append(detail)
    if rank[evidence]>rank[item["evidence"]]:item["evidence"]=evidence

def extract_paths(text,source,store):
    t=html.unescape(text).replace("\\/","/")
    for m in API_URL_RE.finditer(t): add(store,nearby_method(t,m.start(),m.end()) or "GET",m.group(0),"DOCUMENTATION_CONFIRMED",source,"explicit API URL")
    for m in HREF_RE.finditer(t):
        p=normalize_path(urljoin(source,clean(m.group(1))))
        if p:add(store,nearby_method(t,m.start(),m.end()) or "GET",p,"DOCUMENTATION_CONFIRMED",source,"HTML API link")
    for m in PATH_RE.finditer(t):
        p=normalize_path(m.group(0)); method=nearby_method(t,m.start(),m.end())
        if p and method:add(store,method,p,"DOCUMENTATION_CONFIRMED",source,"explicit path expression")

def build_url(path):
    b=urlsplit(BASE); bp=b.path.rstrip("/"); np="/"+path.lstrip("/"); final=np if (bp and (np==bp or np.startswith(bp+"/"))) else bp+np; return b._replace(path=final).geturl()

def has_placeholder(p): return bool(re.search(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>",p))

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def main():
    if not KEY: print("ROAPP_API_KEY is required",file=sys.stderr); return 2
    links=[]; seen=set(); index_results=[]
    for index_url in DOCS_INDEXES:
        status,index,elapsed,err=fetch(index_url); index_results.append({"url":index_url,"http":status,"elapsed_s":elapsed,"error":err})
        if status!=200:continue
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+/reference/[^)]+)\)",index):
            title,href=m.groups(); u=urljoin(index_url,clean(href))
            if u not in seen:seen.add(u); links.append({"title":html.unescape(title).strip(),"url":u})
    links=links[:MAX_DOCS]
    if not links: print("No documentation reference pages discovered",file=sys.stderr); return 1
    ops={}; pages=[]; deadline=time.monotonic()+float(os.environ.get("MARSEL_INVENTORY_BUDGET_SECONDS","240"))
    for link in links:
        if time.monotonic()>=deadline: break
        responses=[]; found=False
        for u in dict.fromkeys([link["url"],link["url"][:-3] if link["url"].endswith(".md") else link["url"]]):
            if time.monotonic()>=deadline: break
            s,body,e,er=fetch(u); responses.append({"url":u,"http":s,"elapsed_s":e,"error":er})
            if s==200: found=True; extract_paths(body,u,ops)
        pages.append({"title":link["title"],"documentation_url":link["url"],"responses":responses,"content_found":found,"title_method":title_method(link["title"]),"path_evidence_count":sum(1 for x in ops.values() if link["url"] in x["sources"])})
    probes=[]; seen_get=set(); headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":f"MARSEL-Audit-V{VERSION}"}
    for op in sorted(ops.values(),key=lambda x:(x["path"],x["method"])):
        if op["method"]!="GET":continue
        if has_placeholder(op["path"]):probes.append({"method":"GET","path":op["path"],"status":"NOT_PROBED","reason":"parameterized path; no identifier guessed"});continue
        if op["path"] in seen_get:continue
        seen_get.add(op["path"]); u=build_url(op["path"]); s,body,e,er=fetch(u,headers); item={"method":"GET","path":op["path"],"url":u,"http":s,"elapsed_s":e,"error":er}
        if s==200:
            try:
                d=json.loads(body); item["json_valid"]=True; item["json_type"]=type(d).__name__; item["top_level_keys"]=sorted(d.keys())[:50] if isinstance(d,dict) else None
            except json.JSONDecodeError:item["json_valid"]=False; item["error"]="successful HTTP response is not valid JSON"
        else:item["json_valid"]=None
        probes.append(item)
    report={"version":VERSION,"readonly":True,"method_policy":{"allowed":["GET"],"blocked":["POST","PUT","PATCH","DELETE"]},"write_requests_made":0,"ro_app_data_mutated":False,"sources":{"documentation_indexes":DOCS_INDEXES,"api_base":BASE,"index_results":index_results},"documentation":{"pages_discovered":len(links),"pages_fetched":sum(1 for p in pages if p["content_found"]),"pages_with_explicit_api_path_evidence":sum(1 for p in pages if p["path_evidence_count"]>0)},"operations":sorted(ops.values(),key=lambda x:(x["path"],x["method"])),"get_probes":probes,"summary":{"unique_confirmed_operations":len(ops),"get_operations":sum(1 for x in ops.values() if x["method"]=="GET"),"non_get_operations":sum(1 for x in ops.values() if x["method"]!="GET"),"get_probes_attempted":sum(1 for p in probes if p.get("status")!="NOT_PROBED"),"get_probes_http_200":sum(1 for p in probes if p.get("http")==200),"parameterized_not_probed":sum(1 for p in probes if p.get("status")=="NOT_PROBED"),"write_requests_made":0},"contract_state":{"completeness_claim":"NOT_ESTABLISHED","title_method_classification_is_not_url_evidence":True,"parameterized_identifiers_guessed":False},"safety":{"status":"PASS","write_requests_made":0,"ro_app_data_mutated":False},"reference_pages":[{"title":p["title"],"documentation_url":p["documentation_url"],"title_method":p["title_method"],"content_found":p["content_found"],"path_evidence_count":p["path_evidence_count"]} for p in pages],"generated_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
    with open(OUT,"w",encoding="utf-8") as f:json.dump(report,f,ensure_ascii=False,indent=2,sort_keys=True)
    report["report_sha256"]=sha(OUT)
    with open(OUT,"w",encoding="utf-8") as f:json.dump(report,f,ensure_ascii=False,indent=2,sort_keys=True)
    print(f"V{VERSION}_INVENTORY=PASS"); print(f"REFERENCE_PAGES={len(links)}"); print(f"FETCHED_PAGES={report['documentation']['pages_fetched']}"); print(f"CONFIRMED_OPERATIONS={len(ops)}"); print(f"GET_PROBES_ATTEMPTED={report['summary']['get_probes_attempted']}"); print("WRITE_REQUESTS_MADE=0"); print("RO_APP_DATA_MUTATED=false"); print(f"REPORT_SHA256={report['report_sha256']}")
    return 0

if __name__=="__main__":raise SystemExit(main())
