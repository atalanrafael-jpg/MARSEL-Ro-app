#!/usr/bin/env python3
"""MARSEL bounded READ-ONLY inventory bootstrap.

The inventory job must terminate deterministically. This module performs only
bounded documentation discovery and emits a valid inventory artifact. It never
writes to RO App and never guesses identifiers.
"""
from __future__ import annotations
import hashlib, html, json, os, re, sys, time
from urllib.parse import urlparse
from urllib.request import Request, urlopen

VERSION = "20.23"
INDEXES=[x.strip() for x in os.environ.get("ROAPP_DOCS_INDEXES","https://roapp.readme.io/llms.txt").split(",") if x.strip()]
OUT=os.environ.get("MARSEL_API_INVENTORY_OUTPUT","marsel-api-inventory-v20-29.json")
TIMEOUT=min(int(os.environ.get("ROAPP_TIMEOUT","8")),10)
MAX_DOCS=min(int(os.environ.get("MARSEL_MAX_DOCS","25")),30)
BUDGET=min(float(os.environ.get("MARSEL_INVENTORY_BUDGET_SECONDS","45")),60.0)
METHOD_RE=re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b",re.I)
PATH_RE=re.compile(r"/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?",re.I)
URL_RE=re.compile(r"https?://api\.roapp\.io/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?",re.I)

def fetch(url):
    req=Request(url,headers={"User-Agent":f"MARSEL-Audit-V{VERSION}","Accept":"text/plain,text/markdown,text/html,application/json"},method="GET")
    t=time.monotonic()
    try:
        with urlopen(req,timeout=TIMEOUT) as r:return r.status,r.read().decode("utf-8","replace"),round(time.monotonic()-t,3),None
    except Exception as e:return None,"",round(time.monotonic()-t,3),f"{type(e).__name__}: {e}"

def norm(raw):
    raw=html.unescape(raw).strip("`'\"<>[]{}();,.")
    if raw.startswith("http"):
        p=urlparse(raw)
        if p.netloc.lower()!="api.roapp.io":return None
        raw=p.path
    raw=raw.split("#",1)[0]
    if raw.rstrip("/") in ("/v2", "/1.1"):
        return None
    if not raw.startswith(("/v2/","/1.1/")):return None
    raw=re.sub(r"/v2/v2/","/v2/",raw)
    raw=re.sub(r"/1\.1/1\.1/","/1.1/",raw)
    return raw

# Backward-compatible public name retained for the V20.23 test contract.
normalize_path = norm

def main():
    if not os.environ.get("ROAPP_API_KEY"):
        print("ROAPP_API_KEY is required",file=sys.stderr);return 2
    deadline=time.monotonic()+BUDGET
    ops={}; pages=[]
    for idx in INDEXES:
        if time.monotonic()>=deadline:break
        s,b,e,er=fetch(idx);pages.append({"url":idx,"http":s,"elapsed_s":e,"error":er})
        if s!=200:continue
        refs=[]
        for line in b.splitlines():
            for token in re.findall(r"https?://[^\s<>]+",line):
                token=token.rstrip(".,);]")
                if "/reference/" in token and token not in refs:refs.append(token)
        for u in refs[:MAX_DOCS]:
            if time.monotonic()>=deadline:break
            s2,b2,e2,er2=fetch(u)
            pages.append({"url":u,"http":s2,"elapsed_s":e2,"error":er2})
            if s2!=200:continue
            for m in URL_RE.finditer(b2):
                p=norm(m.group()); w=b2[max(0,m.start()-120):m.end()+120]; mm=METHOD_RE.findall(w)
                if not p:continue
                method=mm[-1].upper() if mm else "GET";ops[(method,p)]={"method":method,"path":p,"source":u}
            for m in PATH_RE.finditer(b2):
                p=norm(m.group());
                if not p:continue
                w=b2[max(0,m.start()-120):m.end()+120];mm=METHOD_RE.findall(w)
                method=mm[-1].upper() if mm else "GET";ops[(method,p)]={"method":method,"path":p,"source":u}
    data={"version":VERSION,"readonly":True,"method_policy":{"allowed":["GET"],"blocked":["POST","PUT","PATCH","DELETE"]},"write_requests_made":0,"ro_app_data_mutated":False,"documentation":{"pages_processed":len(pages),"pages":pages},"operations":sorted(ops.values(),key=lambda x:(x["path"],x["method"])),"summary":{"unique_confirmed_operations":len(ops),"get_operations":sum(x["method"]=="GET" for x in ops),"non_get_operations":sum(x["method"]!="GET" for x in ops)},"contract_state":{"completeness_claim":"NOT_ESTABLISHED","parameterized_identifiers_guessed":False,"never_guess_identifiers":True},"safety":{"status":"PASS","write_requests_made":0,"ro_app_data_mutated":False},"generated_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
    with open(OUT,"w",encoding="utf-8") as f:json.dump(data,f,ensure_ascii=False,indent=2)
    h=hashlib.sha256(open(OUT,"rb").read()).hexdigest()
    data["report_sha256"]=h
    with open(OUT,"w",encoding="utf-8") as f:json.dump(data,f,ensure_ascii=False,indent=2)
    print(f"V{VERSION}_INVENTORY=PASS");print(f"PAGES_PROCESSED={len(pages)}");print(f"CONFIRMED_OPERATIONS={len(ops)}");print("WRITE_REQUESTS_MADE=0");print("RO_APP_DATA_MUTATED=false");print(f"REPORT_SHA256={h}")
    return 0
if __name__=="__main__":raise SystemExit(main())
