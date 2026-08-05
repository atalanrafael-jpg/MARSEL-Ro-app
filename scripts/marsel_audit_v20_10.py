#!/usr/bin/env python3
"""MARSEL V20.10 - targeted read-only API diagnostics.

Purpose: explain the LIST failures and empty endpoints observed by V20.9
without performing a full DETAIL scan and without mutating RO App data.

The diagnostic probes only GET requests. It records exact HTTP status,
response-body excerpts, response shape, and timing. For successful list
endpoints it compares conservative pagination variants (page/page_size,
page/limit, offset/limit) to distinguish endpoint emptiness from pagination
or parameter incompatibility. No writes are possible in this program.
"""
import hashlib
import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE=os.environ.get("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.environ.get("ROAPP_API_KEY","")
OUT=os.environ.get("MARSEL_AUDIT_OUTPUT","marsel-api-diagnostics-v20-10.json")
TIMEOUT=int(os.environ.get("ROAPP_TIMEOUT","30"))
PAGE_SIZE=int(os.environ.get("MARSEL_PAGE_SIZE","100"))
TARGETS=[
 {"entity":"orders","list":"/orders"},
 {"entity":"services","list":"/catalog/services"},
 {"entity":"products","list":"/catalog/products"},
 {"entity":"bundles","list":"/catalog/bundles"},
 {"entity":"inquiries","list":"/inquiries"},
 {"entity":"bookings","list":"/bookings"},
 {"entity":"estimates","list":"/estimates"},
 {"entity":"invoices","list":"/invoices"},
]

# Explicitly GET-only. This is also asserted in the report and workflow.
FORBIDDEN={"POST","PUT","PATCH","DELETE"}

def get(path,params=None):
    url=path if path.startswith("http") else BASE+path
    if params:
        url += ("&" if "?" in url else "?")+urlencode(params,doseq=True)
    req=Request(url,headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":"MARSEL-Audit-V20.10"},method="GET")
    started=time.time()
    try:
        with urlopen(req,timeout=TIMEOUT) as r:
            raw=r.read().decode("utf-8",errors="replace")
            try: payload=json.loads(raw)
            except ValueError: payload=None
            return {"http":r.status,"elapsed_s":round(time.time()-started,3),"json":payload,"body_excerpt":raw[:2000],"error":None,"url":url}
    except HTTPError as e:
        raw=e.read().decode("utf-8",errors="replace")[:2000]
        try: payload=json.loads(raw)
        except ValueError: payload=None
        return {"http":e.code,"elapsed_s":round(time.time()-started,3),"json":payload,"body_excerpt":raw,"error":"HTTPError","url":url}
    except (URLError,TimeoutError,ValueError) as e:
        return {"http":None,"elapsed_s":round(time.time()-started,3),"json":None,"body_excerpt":"","error":str(e)[:1000],"url":url}

def records(payload):
    if isinstance(payload,list): return payload
    if not isinstance(payload,dict): return []
    for k in ("data","items","results","orders","services","products","bundles","inquiries","bookings","estimates","invoices"):
        v=payload.get(k)
        if isinstance(v,list): return v
    for k in ("data","result"):
        v=payload.get(k)
        if isinstance(v,dict):
            r=records(v)
            if r: return r
    return []

def shape(payload):
    if isinstance(payload,list): return "list"
    if isinstance(payload,dict): return "dict"
    return type(payload).__name__

def rid(x):
    if not isinstance(x,dict): return None
    for k in ("id","ID","uuid"):
        if x.get(k) is not None: return x[k]
    return None

def next_hint(payload):
    if not isinstance(payload,dict): return None
    keys=("has_next","hasNext","next","next_page","nextPage","total","total_count","totalCount","count")
    return {k:payload[k] for k in keys if k in payload}

def summarize_probe(probe):
    rs=records(probe.get("json")) if probe.get("http")==200 else []
    ids=[rid(x) for x in rs]
    return {"http":probe.get("http"),"elapsed_s":probe.get("elapsed_s"),"shape":shape(probe.get("json")),"records":len(rs),"sample_ids":ids[:10],"pagination_hints":next_hint(probe.get("json")),"error":probe.get("error"),"body_excerpt":probe.get("body_excerpt",""),"url":probe.get("url")}

def main():
    if not KEY:
        print("ROAPP_API_KEY is required",file=sys.stderr); return 2
    report={"version":"20.10","readonly":True,"write_requests_made":0,"ro_app_data_mutated":False,"method_policy":{"allowed":["GET"],"forbidden":sorted(FORBIDDEN)},"targets":[]}
    totals={"targets":len(TARGETS),"baseline_ok":0,"baseline_failures":0,"baseline_empty":0,"parameter_variant_successes":0,"parameter_variant_failures":0,"parameter_variant_nonempty":0}
    variants=[
        ("page_page_size",{"page":1,"page_size":PAGE_SIZE}),
        ("page_limit",{"page":1,"limit":PAGE_SIZE}),
        ("offset_limit",{"offset":0,"limit":PAGE_SIZE}),
        ("plain",None),
    ]
    for t in TARGETS:
        probes=[]
        for name,params in variants:
            p=get(t["list"],params)
            s=summarize_probe(p); s["variant"]=name; s["params"]=params or {}
            probes.append(s)
            if p.get("http")==200:
                totals["parameter_variant_successes"]+=1
                if s["records"]>0: totals["parameter_variant_nonempty"]+=1
            else: totals["parameter_variant_failures"]+=1
        baseline=next(x for x in probes if x["variant"]=="page_page_size")
        if baseline["http"]==200:
            totals["baseline_ok"]+=1
            if baseline["records"]==0: totals["baseline_empty"]+=1
        else: totals["baseline_failures"]+=1
        status="NONEMPTY"
        if baseline["http"]!=200: status="BASELINE_FAILURE"
        elif baseline["records"]==0 and any(x["http"]==200 and x["records"]>0 for x in probes): status="PARAMETER_SENSITIVE"
        elif baseline["records"]==0: status="EMPTY_ACROSS_PROBES"
        report["targets"].append({"entity":t["entity"],"endpoint":t["list"],"classification":status,"probes":probes})
    report["summary"]={**totals,"readonly":True,"write_requests_made":0}
    with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
    print("=== MARSEL AUDIT V20.10 / TARGETED API DIAGNOSTICS / READ ONLY ===")
    print(f"TARGETS={totals['targets']}")
    print(f"BASELINE_OK={totals['baseline_ok']}")
    print(f"BASELINE_FAILURES={totals['baseline_failures']}")
    print(f"BASELINE_EMPTY={totals['baseline_empty']}")
    print(f"PARAMETER_VARIANT_SUCCESSES={totals['parameter_variant_successes']}")
    print(f"PARAMETER_VARIANT_FAILURES={totals['parameter_variant_failures']}")
    print(f"PARAMETER_VARIANT_NONEMPTY={totals['parameter_variant_nonempty']}")
    print("WRITE_REQUESTS_MADE=0")
    print(f"REPORT={OUT}")
    print("RESULT=READ_ONLY; V20.10; NO RO APP DATA CREATED, UPDATED OR DELETED")
    return 0

if __name__=="__main__": raise SystemExit(main())
