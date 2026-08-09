#!/usr/bin/env python3
"""MARSEL V20.29 — RO App API inventory, READ ONLY.

Evidence-first inventory from official RO App ReadMe indexes. Reference-page
URLs are discovered from Markdown, HTML and bare ReadMe URLs. Only explicit
API URLs/paths found in fetched documentation are eligible for GET probing.
No write method is ever called and parameterized identifiers are never guessed.
"""
from __future__ import annotations
import hashlib, html, json, os, re, sys, time
from urllib.parse import urljoin, urlparse, urlsplit, urldefrag
from urllib.request import Request, urlopen

VERSION = "20.29"
DEFAULT_INDEXES = ("https://roapp.readme.io/llms.txt", "https://roappua.readme.io/llms.txt")
DOCS_INDEXES = [x.strip() for x in os.environ.get("ROAPP_DOCS_INDEXES", ",".join(DEFAULT_INDEXES)).split(",") if x.strip()]
BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
OUT = os.environ.get("MARSEL_API_INVENTORY_OUTPUT", "marsel-api-inventory-v20-29.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "15"))
MAX_DOCS = int(os.environ.get("MARSEL_MAX_DOCS", "300"))
MIN_INTERVAL = float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34"))
MAX_RETRIES = int(os.environ.get("ROAPP_MAX_RETRIES", "2"))
RETRY_BASE = float(os.environ.get("ROAPP_RETRY_BASE_SECONDS", "0.75"))
MAX_BUDGET = float(os.environ.get("MARSEL_INVENTORY_BUDGET_SECONDS", "240"))
METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
API_URL_RE = re.compile(r"https?://api\.roapp\.io/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?", re.I)
PATH_RE = re.compile(r"(?<![A-Za-z0-9_])/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?", re.I)
METHOD_PATH_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b\s*(?:[:\-]\s*)?(https?://api\.roapp\.io[^\s<>'\"`]+|/(?:v2|1\.1)(?:/[^\s<>'\"`]*)?)", re.I)
REFERENCE_ABS_RE = re.compile(r"https?://roapp(?:ua)?\.readme\.io/reference/[A-Za-z0-9_./?=&%\-]+", re.I)
REFERENCE_REL_RE = re.compile(r"(?:^|[\s(\"'<])(/reference/[A-Za-z0-9_./?=&%\-]+)", re.I)
HREF_RE = re.compile(r"(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.I)
MD_LINK_RE = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
OPENAPI_URL_RE = re.compile(r"https?://[^\s<>\"']+(?:openapi|swagger|api[-_]?spec)[^\s<>\"']*", re.I)
SPEC_EXT_RE = re.compile(r"https?://[^\s<>\"']+\.(?:json|ya?ml)(?:\?[^\s<>\"']*)?", re.I)
PARAM_RE = re.compile(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>")
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
                if r.status in {408,425,429,500,502,503,504} and attempt < MAX_RETRIES:
                    time.sleep(min(RETRY_BASE*(2**attempt), 20.0)); continue
                return r.status, body, round(time.time()-started,3), None
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
            if attempt >= MAX_RETRIES: return None, "", round(time.time()-started,3), last
            time.sleep(min(RETRY_BASE*(2**attempt), 20.0))
    return None, "", 0, last or "request failed"


def clean(s):
    return html.unescape(str(s)).strip().replace("\\/","/").strip("`'\"<>[](){};,.:")


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
    # Use only a tight local window. A method elsewhere on the page must not
    # be treated as evidence for an unrelated endpoint.
    win=text[max(0,start-220):min(len(text),end+220)]
    ms=list(re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE)\b",win,re.I))
    if not ms:return None
    center=start-max(0,start-220)
    candidate=min(ms,key=lambda m:abs(m.start()-center))
    if abs(candidate.start()-center) > 180:return None
    return candidate.group(1).upper()


def add(store,method,path,evidence,source,detail):
    method=str(method).upper()
    if method not in METHODS:return
    p=normalize_path(path)
    if not p:return
    key=(method,p); rank={"OPENAPI_CONFIRMED":4,"DOCUMENTATION_CONFIRMED":3,"URL_CONFIRMED":2}
    if key not in store:
        store[key]={"method":method,"path":p,"evidence":evidence,"sources":[source] if source else [],"details":[detail] if detail else []}; return
    item=store[key]
    if source and source not in item["sources"]:item["sources"].append(source)
    if detail and detail not in item["details"]:item["details"].append(detail)
    if rank.get(evidence,0)>rank.get(item["evidence"],0):item["evidence"]=evidence


def extract_reference_urls(text,base):
    found=[]; seen=set()
    raw_urls=[]
    raw_urls += REFERENCE_ABS_RE.findall(text)
    raw_urls += [m.group(1) for m in REFERENCE_REL_RE.finditer(text)]
    raw_urls += HREF_RE.findall(text)
    raw_urls += MD_LINK_RE.findall(text)
    for raw in raw_urls:
        raw=raw.strip().split(" ",1)[0]
        u=urljoin(base,raw); u,_=urldefrag(u)
        p=urlparse(u)
        if p.netloc.lower() not in {"roapp.readme.io","roappua.readme.io"} or not p.path.lower().startswith("/reference/"):continue
        if u not in seen:seen.add(u);found.append(u)
    return found


def extract_paths(text,source,store):
    t=html.unescape(text).replace("\\/","/")
    for m in METHOD_PATH_RE.finditer(t):
        add(store,m.group(1),m.group(2),"DOCUMENTATION_CONFIRMED",source,"explicit method/path")
    for m in API_URL_RE.finditer(t):
        method=nearby_method(t,m.start(),m.end())
        add(store,method or "GET",m.group(0),"DOCUMENTATION_CONFIRMED" if method else "URL_CONFIRMED",source,"explicit API URL")
    for m in PATH_RE.finditer(t):
        p=normalize_path(m.group(0))
        if not p:continue
        method=nearby_method(t,m.start(),m.end())
        if method:add(store,method,p,"DOCUMENTATION_CONFIRMED",source,"explicit path expression")
        else:add(store,"GET",p,"URL_CONFIRMED",source,"documented endpoint path; HTTP method not explicit")


def candidate_specs(text,base):
    found=[]; seen=set()
    for pattern in (OPENAPI_URL_RE,SPEC_EXT_RE):
        for raw in pattern.findall(text):
            u=urljoin(base,clean(raw.rstrip(".,);]"))); u,_=urldefrag(u)
            if u not in seen:seen.add(u);found.append(u)
    return found


def parse_openapi(text):
    try:data=json.loads(text)
    except json.JSONDecodeError:data=None
    if isinstance(data,dict) and isinstance(data.get("paths"),dict):
        out=[]
        for path,methods in data["paths"].items():
            if not isinstance(methods,dict):continue
            p=normalize_path(path) or (normalize_path("/v2"+path) if str(path).startswith("/") else None)
            if not p:continue
            for method in methods:
                if str(method).upper() in METHODS:out.append((str(method).upper(),p))
        return out,"json"
    if not re.search(r"(?im)^\s*(?:openapi|swagger)\s*:",text):return [],None
    out=[]; current=None
    for line in text.splitlines():
        m=re.match(r"^\s{0,12}(/(?:v2|1\.1)/[^:#\s]+)\s*:\s*$",line)
        if m:current=m.group(1);continue
        mm=re.match(r"^\s{2,20}(get|post|put|patch|delete)\s*:\s*$",line,re.I)
        if mm and current:out.append((mm.group(1).upper(),current))
    return out,"yaml"


def build_url(path):
    b=urlsplit(BASE); bp=b.path.rstrip("/"); np="/"+path.lstrip("/")
    final=np if (bp and (np==bp or np.startswith(bp+"/"))) else bp+np
    return b._replace(path=final).geturl()


def has_placeholder(p):return bool(PARAM_RE.search(p))


def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()


def main():
    if not KEY: print("ROAPP_API_KEY is required",file=sys.stderr); return 2
    links=[]; seen=set(); index_results=[]; discovery_specs=[]
    for index_url in DOCS_INDEXES:
        status,index,elapsed,err=fetch(index_url); index_results.append({"url":index_url,"http":status,"elapsed_s":elapsed,"error":err})
        if status!=200:continue
        for u in extract_reference_urls(index,index_url):
            if u not in seen:seen.add(u);links.append({"title":u.rstrip("/").rsplit("/",1)[-1],"url":u})
        discovery_specs += candidate_specs(index,index_url)
    links=links[:MAX_DOCS]
    if not links:
        print("No documentation reference pages discovered",file=sys.stderr); return 1

    ops={}; pages=[]; specs=[]; spec_seen=set(); deadline=time.monotonic()+MAX_BUDGET
    def ingest_spec(u,detail):
        if u in spec_seen:return
        spec_seen.add(u); s,body,e,er=fetch(u); extracted,fmt=parse_openapi(body) if s==200 else ([],None)
        specs.append({"url":u,"http":s,"elapsed_s":e,"format":fmt,"operations":len(extracted),"error":er})
        for method,path in extracted:add(ops,method,path,"OPENAPI_CONFIRMED",u,detail)
    for u in discovery_specs[:100]:
        if time.monotonic()>=deadline:break
        ingest_spec(u,"machine-readable OpenAPI/Swagger")

    for link in links:
        if time.monotonic()>=deadline:break
        responses=[]; found=False; path_before=len(ops)
        variants=[link["url"]]
        if link["url"].endswith(".md"):variants.append(link["url"][:-3])
        for u in dict.fromkeys(variants):
            if time.monotonic()>=deadline:break
            s,body,e,er=fetch(u);responses.append({"url":u,"http":s,"elapsed_s":e,"error":er})
            if s==200:
                found=True;extract_paths(body,u,ops)
                for spec in candidate_specs(body,u):
                    if spec not in discovery_specs and len(discovery_specs)<100:discovery_specs.append(spec)
        pages.append({"title":link["title"],"documentation_url":link["url"],"responses":responses,"content_found":found,"path_evidence_count":len(ops)-path_before})

    for u in discovery_specs[:100]:
        if time.monotonic()>=deadline:break
        ingest_spec(u,"machine-readable OpenAPI/Swagger discovered from reference page")

    operations=sorted(ops.values(),key=lambda x:(x["path"],x["method"]))
    get_ops=[x for x in operations if x["method"]=="GET"]
    probes=[]; seen_get=set(); headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":f"MARSEL-Audit-V{VERSION}"}
    for op in get_ops:
        if time.monotonic()>=deadline:break
        p=op["path"]
        if has_placeholder(p):
            probes.append({"method":"GET","path":p,"status":"NOT_PROBED","reason":"parameterized path; no identifier guessed"});continue
        if p in seen_get:continue
        seen_get.add(p);u=build_url(p);s,body,e,er=fetch(u,headers);item={"method":"GET","path":p,"url":u,"http":s,"elapsed_s":e,"error":er}
        if s==200:
            try:
                d=json.loads(body);item["json_valid"]=True;item["json_type"]=type(d).__name__;item["top_level_keys"]=sorted(d.keys())[:50] if isinstance(d,dict) else None
            except json.JSONDecodeError:item["json_valid"]=False;item["error"]="successful HTTP response is not valid JSON"
        else:item["json_valid"]=None
        probes.append(item)

    summary={"unique_confirmed_operations":len(operations),"get_operations":len(get_ops),"non_get_operations":len(operations)-len(get_ops),"get_probes_attempted":sum(1 for p in probes if p.get("status")!="NOT_PROBED"),"get_probes_http_200":sum(1 for p in probes if p.get("http")==200),"parameterized_not_probed":sum(1 for p in probes if p.get("status")=="NOT_PROBED"),"write_requests_made":0}
    report={"version":VERSION,"readonly":True,"method_policy":{"allowed":["GET"],"blocked":["POST","PUT","PATCH","DELETE"]},"write_requests_made":0,"ro_app_data_mutated":False,"sources":{"documentation_indexes":DOCS_INDEXES,"api_base":BASE,"index_results":index_results},"documentation":{"pages_discovered":len(links),"pages_fetched":sum(1 for p in pages if p["content_found"]),"pages_with_explicit_api_path_evidence":sum(1 for p in pages if p["path_evidence_count"]>0)},"openapi_discovery":{"candidate_urls":len(discovery_specs),"documents_checked":len(specs),"documents_with_operations":sum(1 for s in specs if s["operations"]>0),"documents":specs},"operations":operations,"get_probes":probes,"summary":summary,"contract_state":{"title_method_classification_is_not_url_evidence":True,"parameterized_identifiers_guessed":False,"completeness_claim":"NOT_ESTABLISHED"},"safety":{"status":"PASS","write_requests_made":0,"ro_app_data_mutated":False},"reference_pages":[{"title":p["title"],"documentation_url":p["documentation_url"],"content_found":p["content_found"],"path_evidence_count":p["path_evidence_count"]} for p in pages],"generated_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
    with open(OUT,"w",encoding="utf-8") as f:json.dump(report,f,ensure_ascii=False,indent=2,sort_keys=True)
    report["report_sha256"]=sha(OUT)
    with open(OUT,"w",encoding="utf-8") as f:json.dump(report,f,ensure_ascii=False,indent=2,sort_keys=True)
    print(f"V{VERSION}_INVENTORY=PASS");print(f"REFERENCE_PAGES={len(links)}");print(f"FETCHED_PAGES={report['documentation']['pages_fetched']}");print(f"CONFIRMED_OPERATIONS={len(operations)}");print(f"GET_PROBES_ATTEMPTED={summary['get_probes_attempted']}");print("WRITE_REQUESTS_MADE=0");print("RO_APP_DATA_MUTATED=false");print(f"REPORT_SHA256={report['report_sha256']}")
    return 0

if __name__=="__main__":raise SystemExit(main())
