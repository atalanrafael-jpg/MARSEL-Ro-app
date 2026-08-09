#!/usr/bin/env python3
"""MARSEL V20.30 — RO App API inventory, READ ONLY.

Fixes the V20.29 endpoint-normalization bug that stripped placeholder braces
from documented paths (for example /items/{id} -> /items/{id). Parameterized
GET paths are recorded but never probed. No write request is executed.
"""
from __future__ import annotations
import hashlib, html, json, os, re, sys, time
from urllib.parse import urljoin, urlparse, urlsplit, urldefrag
from urllib.request import Request, urlopen

VERSION="20.30"
INDEXES=[x.strip() for x in os.getenv("ROAPP_DOCS_INDEXES","https://roapp.readme.io/llms.txt,https://roappua.readme.io/llms.txt").split(",") if x.strip()]
BASE=os.getenv("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.getenv("ROAPP_API_KEY","")
OUT=os.getenv("MARSEL_API_INVENTORY_OUTPUT","marsel-api-inventory-v20-29.json")
TIMEOUT=int(os.getenv("ROAPP_TIMEOUT","15")); MAX_DOCS=int(os.getenv("MARSEL_MAX_DOCS","300"))
INTERVAL=float(os.getenv("ROAPP_MIN_REQUEST_INTERVAL","0.34")); RETRIES=int(os.getenv("ROAPP_MAX_RETRIES","2"))
BUDGET=float(os.getenv("MARSEL_INVENTORY_BUDGET_SECONDS","240"))
METHODS={"GET","POST","PUT","PATCH","DELETE"}; WRITE={"POST","PUT","PATCH","DELETE"}
API_RE=re.compile(r"https?://api\.roapp\.io/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?",re.I)
PATH_RE=re.compile(r"(?<![A-Za-z0-9_])/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?",re.I)
METHOD_RE=re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b\s*(?:[:\-]\s*)?(https?://api\.roapp\.io[^\s<>'\"`]+|/(?:v2|1\.1)(?:/[^\s<>'\"`]*)?)",re.I)
REF_ABS=re.compile(r"https?://roapp(?:ua)?\.readme\.io/reference/[A-Za-z0-9_./?=&%\-]+",re.I)
REF_REL=re.compile(r"(?:^|[\s(\"'<])(/reference/[A-Za-z0-9_./?=&%\-]+)",re.I)
HREF=re.compile(r"(?:href|src)\s*=\s*[\"']([^\"']+)[\"']",re.I)
MD=re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
PARAM=re.compile(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>")
last=0.0

def clean(s):
    # Deliberately preserve { } because they delimit path parameters.
    return html.unescape(str(s)).strip().replace("\\/","/").strip("`'\"<>[]();,.")

def fetch(url,headers=None):
    global last
    hdr=headers or {"User-Agent":f"MARSEL-Audit-V{VERSION}","Accept":"text/html,text/plain,text/markdown,application/json,application/yaml,text/yaml"}
    err=None
    for attempt in range(RETRIES+1):
        wait=INTERVAL-(time.monotonic()-last)
        if wait>0: time.sleep(wait)
        req=Request(url,headers=hdr,method="GET"); started=time.time()
        try:
            last=time.monotonic()
            with urlopen(req,timeout=TIMEOUT) as r:
                body=r.read().decode("utf-8",errors="replace")
                if r.status in {408,425,429,500,502,503,504} and attempt<RETRIES:
                    time.sleep(min(.75*(2**attempt),20)); continue
                return r.status,body,round(time.time()-started,3),None
        except Exception as e:
            err=f"{type(e).__name__}: {e}"
            if attempt>=RETRIES:return None,"",round(time.time()-started,3),err
            time.sleep(min(.75*(2**attempt),20))
    return None,"",0,err

def norm(raw):
    raw=clean(raw)
    if raw.startswith(("http://","https://")):
        p=urlparse(raw)
        if p.netloc.lower()!="api.roapp.io": return None
        raw=p.path
    raw=raw.split("#",1)[0]
    if raw in {"/v2","/v2/","/1.1","/1.1/"}:return None
    if raw.startswith(("/v2/","/1.1/")):
        raw=re.sub(r"/v2/v2/","/v2/",raw); raw=re.sub(r"/1\.1/1\.1/","/1.1/",raw)
        return raw
    return None

def method_near(text,a,b):
    win=text[max(0,a-220):min(len(text),b+220)]; ms=list(re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE)\b",win,re.I))
    if not ms:return None
    center=a-max(0,a-220); m=min(ms,key=lambda x:abs(x.start()-center))
    return m.group(1).upper() if abs(m.start()-center)<=180 else None

def add(store,method,path,evidence,source,detail):
    method=str(method).upper()
    if method not in METHODS:return
    p=norm(path)
    if not p:return
    key=(method,p); ranks={"OPENAPI_CONFIRMED":4,"DOCUMENTATION_CONFIRMED":3,"URL_CONFIRMED":2}
    if key not in store:store[key]={"method":method,"path":p,"evidence":evidence,"sources":[source] if source else [],"details":[detail] if detail else []};return
    x=store[key]
    if source and source not in x["sources"]:x["sources"].append(source)
    if detail and detail not in x["details"]:x["details"].append(detail)
    if ranks.get(evidence,0)>ranks.get(x["evidence"],0):x["evidence"]=evidence

def refs(text,base):
    out=[];seen=set(); raws=REF_ABS.findall(text)+[m.group(1) for m in REF_REL.finditer(text)]+HREF.findall(text)+MD.findall(text)
    for raw in raws:
        raw=raw.strip().split(" ",1)[0]; u,_=urldefrag(urljoin(base,raw)); p=urlparse(u)
        if p.netloc.lower() not in {"roapp.readme.io","roappua.readme.io"} or not p.path.lower().startswith("/reference/"):continue
        if u not in seen:seen.add(u);out.append(u)
    return out

def extract(text,source,ops):
    t=html.unescape(text).replace("\\/","/")
    for m in METHOD_RE.finditer(t):add(ops,m.group(1),m.group(2),"DOCUMENTATION_CONFIRMED",source,"explicit method/path")
    for m in API_RE.finditer(t):
        meth=method_near(t,m.start(),m.end());add(ops,meth or "GET",m.group(0),"DOCUMENTATION_CONFIRMED" if meth else "URL_CONFIRMED",source,"explicit API URL")
    for m in PATH_RE.finditer(t):
        p=norm(m.group(0));
        if not p:continue
        meth=method_near(t,m.start(),m.end());add(ops,meth or "GET",p,"DOCUMENTATION_CONFIRMED" if meth else "URL_CONFIRMED",source,"explicit path expression")

def build(path):
    b=urlsplit(BASE);bp=b.path.rstrip("/");np="/"+path.lstrip("/"); final=np if (bp and (np==bp or np.startswith(bp+"/"))) else bp+np
    return b._replace(path=final).geturl()

def main():
    if not KEY:print("ROAPP_API_KEY is required",file=sys.stderr);return 2
    deadline=time.monotonic()+BUDGET; links=[];seen=set(); index_results=[];ops={};pages=[]
    for idx in INDEXES:
        s,body,e,er=fetch(idx);index_results.append({"url":idx,"http":s,"elapsed_s":e,"error":er})
        if s==200:
            for u in refs(body,idx):
                if u not in seen:seen.add(u);links.append(u)
    links=links[:MAX_DOCS]
    if not links:print("No documentation reference pages discovered",file=sys.stderr);return 1
    for u in links:
        if time.monotonic()>=deadline:break
        s,body,e,er=fetch(u);found=s==200;before=len(ops)
        if found:extract(body,u,ops)
        pages.append({"documentation_url":u,"http":s,"elapsed_s":e,"error":er,"content_found":found,"path_evidence_count":len(ops)-before})
    operations=sorted(ops.values(),key=lambda x:(x["path"],x["method"]))
    gets=[x for x in operations if x["method"]=="GET"];probes=[];headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":f"MARSEL-Audit-V{VERSION}"}
    for op in gets:
        p=op["path"]
        if PARAM.search(p):probes.append({"method":"GET","path":p,"status":"NOT_PROBED","reason":"parameterized path; no identifier guessed"});continue
        if time.monotonic()>=deadline:break
        s,body,e,er=fetch(build(p),headers);probes.append({"method":"GET","path":p,"url":build(p),"http":s,"elapsed_s":e,"error":er})
    summary={"unique_confirmed_operations":len(operations),"get_operations":len(gets),"non_get_operations":len(operations)-len(gets),"get_probes_attempted":sum(1 for x in probes if x.get("status")!="NOT_PROBED"),"get_probes_http_200":sum(1 for x in probes if x.get("http")==200),"parameterized_not_probed":sum(1 for x in probes if x.get("status")=="NOT_PROBED"),"write_requests_made":0}
    report={"version":VERSION,"readonly":True,"method_policy":{"allowed":["GET"],"blocked":sorted(WRITE)},"write_requests_made":0,"ro_app_data_mutated":False,"sources":{"documentation_indexes":INDEXES,"api_base":BASE,"index_results":index_results},"documentation":{"pages_discovered":len(links),"pages_fetched":sum(1 for x in pages if x["content_found"]),"pages_with_explicit_api_path_evidence":sum(1 for x in pages if x["path_evidence_count"]>0)},"openapi_discovery":{"candidate_urls":0,"documents_checked":0,"documents_with_operations":0,"specs":[]},"operations":operations,"get_probes":probes,"summary":summary,"safety":{"write_requests_made":0,"ro_app_data_mutated":False,"write_methods_used":[],"write_methods_detected":sorted({x["method"] for x in operations if x["method"] in WRITE})},"generated_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"report_sha256":None}
    with open(OUT,"w",encoding="utf-8") as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write("\n")
    h=hashlib.sha256(open(OUT,"rb").read()).hexdigest();report["report_sha256"]=h
    with open(OUT,"w",encoding="utf-8") as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write("\n")
    print(f"GET_OPERATIONS={summary['get_operations']}");print(f"GET_PROBES_ATTEMPTED={summary['get_probes_attempted']}");print(f"GET_PROBES_HTTP_200={summary['get_probes_http_200']}");print(f"PARAMETERIZED_NOT_PROBED={summary['parameterized_not_probed']}");print("WRITE_REQUESTS_MADE=0");print("RO_APP_DATA_MUTATED=false");return 0

if __name__=="__main__":raise SystemExit(main())
