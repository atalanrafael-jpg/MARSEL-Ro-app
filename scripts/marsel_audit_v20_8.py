#!/usr/bin/env python3
"""MARSEL V20.8 - full-detail read-only audit.

V20.8 keeps the V20.7 GET-only discovery model but removes the 2,000-detail
cap for the normal target set. It verifies every discovered record ID up to
MARSEL_MAX_DETAIL (default 5,000), records pagination/detail failures, and
never issues mutation methods.
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
OUT=os.environ.get("MARSEL_AUDIT_OUTPUT","marsel-data-discovery-v20-8.json")
TIMEOUT=int(os.environ.get("ROAPP_TIMEOUT","30"))
PAGE_SIZE=int(os.environ.get("MARSEL_PAGE_SIZE","100"))
MAX_PAGES=int(os.environ.get("MARSEL_MAX_PAGES","100"))
MAX_DETAIL=int(os.environ.get("MARSEL_MAX_DETAIL","5000"))
TARGETS=[
 {"entity":"orders","list":"/orders","detail":"/orders/{id}"},
 {"entity":"services","list":"/catalog/services","detail":"/catalog/services/{id}"},
 {"entity":"products","list":"/catalog/products","detail":"/catalog/products/{id}"},
 {"entity":"bundles","list":"/catalog/bundles","detail":"/catalog/bundles/{id}"},
 {"entity":"inquiries","list":"/inquiries","detail":"/inquiries/{id}"},
 {"entity":"bookings","list":"/bookings","detail":"/bookings/{id}"},
 {"entity":"estimates","list":"/estimates","detail":"/estimates/{id}"},
 {"entity":"invoices","list":"/invoices","detail":"/invoices/{id}"},
]
VOLATILE={"created_at","updated_at","createdAt","updatedAt","timestamp","request_id","requestId"}

def get(path,params=None):
    url=path if path.startswith("http") else BASE+path
    if params: url += ("&" if "?" in url else "?")+urlencode(params)
    req=Request(url,headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":"MARSEL-Audit-V20.8"},method="GET")
    t=time.time()
    try:
        with urlopen(req,timeout=TIMEOUT) as r:
            return r.status,json.loads(r.read().decode("utf-8")),round(time.time()-t,3),None
    except HTTPError as e:
        return e.code,None,round(time.time()-t,3),e.read().decode("utf-8",errors="replace")[:1000]
    except (URLError,TimeoutError,ValueError) as e:
        return None,None,round(time.time()-t,3),str(e)

def records(payload):
    if isinstance(payload,list): return payload
    if not isinstance(payload,dict): return []
    for k in ("data","items","results","orders","services","products","bundles","inquiries","bookings","estimates","invoices"):
        v=payload.get(k)
        if isinstance(v,list): return v
    for k in ("data","result"):
        v=payload.get(k)
        if isinstance(v,dict):
            x=records(v)
            if x: return x
    return []

def rid(x):
    return next((x[k] for k in ("id","ID","uuid") if isinstance(x,dict) and x.get(k) is not None),None)

def norm(x):
    if isinstance(x,dict): return {k:norm(v) for k,v in sorted(x.items()) if k not in VOLATILE}
    if isinstance(x,list): return [norm(v) for v in x]
    return x

def fp(x):
    return hashlib.sha256(json.dumps(norm(x),ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def has_next(p):
    if not isinstance(p,dict): return None
    for k in ("has_next","hasNext"):
        if isinstance(p.get(k),bool): return p[k]
    for k in ("next","next_page","nextPage"):
        if k in p: return p[k] not in (None,False,"",0)
    return None

def collect(t):
    out=[]; pages=[]; errors=[]; seen_sigs=set(); ended=False
    for page in range(1,MAX_PAGES+1):
        s,p,e,err=get(t["list"],{"page":page,"page_size":PAGE_SIZE})
        rs=records(p) if s==200 and p is not None else []
        sig=hashlib.sha256(json.dumps([rid(x) for x in rs],ensure_ascii=False,separators=(",",":")).encode()).hexdigest() if rs else None
        repeated=sig in seen_sigs if sig else False
        if sig: seen_sigs.add(sig)
        pages.append({"page":page,"http":s,"elapsed_s":e,"records":len(rs),"has_next":has_next(p),"repeated_page":repeated})
        if s!=200 or p is None:
            errors.append({"page":page,"http":s,"error":err}); break
        out.extend(rs)
        hn=has_next(p)
        if not rs or hn is False or repeated:
            ended=True; break
    return out,pages,errors,ended

def main():
    if not KEY: print("ROAPP_API_KEY is required",file=sys.stderr); return 2
    report={"version":"20.8","readonly":True,"write_requests_made":0,"ro_app_data_mutated":False,"method_policy":{"allowed":["GET"],"forbidden":["POST","PUT","PATCH","DELETE"]},"targets":[]}
    total={"records":0,"details":0,"detail_failures":0,"empty":0,"duplicate_candidates":0,"structural_issues":0,"pagination_inconclusive":0}
    for t in TARGETS:
        rs,pages,errors,ended=collect(t)
        ids=[]; seen=set(); dup=[]; structural=[]; groups={}
        for i,x in enumerate(rs):
            if not isinstance(x,dict): structural.append(i); continue
            x_id=rid(x)
            if x_id is None: structural.append(i)
            elif x_id in seen: dup.append(x_id)
            else: seen.add(x_id); ids.append(x_id)
            groups.setdefault(fp(x),[]).append(x_id)
        fp_dups=[v for v in groups.values() if len(v)>1]
        checks=[]
        for x_id in ids[:MAX_DETAIL]:
            s,_,e,err=get(t["detail"].format(id=x_id))
            checks.append({"source_id":x_id,"http":s,"elapsed_s":e,"ok":s==200,"error":err})
        fails=[x for x in checks if not x["ok"]]
        findings=[]
        if not rs and not errors: findings.append({"severity":"INFO","code":"EMPTY_ENDPOINT"})
        if dup or fp_dups: findings.append({"severity":"WARNING","code":"DUPLICATE_CANDIDATES","id_duplicates":dup[:100],"fingerprint_groups":fp_dups[:100]})
        if structural: findings.append({"severity":"WARNING","code":"STRUCTURAL_ISSUES","records":structural[:100]})
        if fails: findings.append({"severity":"WARNING","code":"DETAIL_CHECK_FAILURES","count":len(fails),"items":fails[:100]})
        if len(pages)>=MAX_PAGES and not ended: findings.append({"severity":"WARNING","code":"PAGINATION_INCONCLUSIVE"}); total["pagination_inconclusive"]+=1
        report["targets"].append({"entity":t["entity"],"list_endpoint":t["list"],"detail_endpoint":t["detail"],"records_seen":len(rs),"unique_ids":len(seen),"detail_checks":checks,"list_errors":errors,"pages":pages,"findings":findings})
        total["records"]+=len(rs); total["details"]+=len(checks); total["detail_failures"]+=len(fails); total["empty"]+=int(not rs and not errors); total["duplicate_candidates"]+=len(dup)+len(fp_dups); total["structural_issues"]+=len(structural)
    report["summary"]={"targets":len(TARGETS),**total,"readonly":True,"write_requests_made":0}
    with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
    print("=== MARSEL AUDIT V20.8 / FULL DETAIL / READ ONLY ===")
    print(f"TARGETS={len(TARGETS)}")
    print(f"LIST_RECORDS_SEEN={total['records']}")
    print(f"DETAIL_CHECKS={total['details']}")
    print(f"DETAIL_FAILURES={total['detail_failures']}")
    print(f"EMPTY_ENDPOINTS={total['empty']}")
    print(f"DUPLICATE_CANDIDATES={total['duplicate_candidates']}")
    print(f"STRUCTURAL_ISSUES={total['structural_issues']}")
    print(f"PAGINATION_INCONCLUSIVE={total['pagination_inconclusive']}")
    print("WRITE_REQUESTS_MADE=0")
    print(f"REPORT={OUT}")
    print("RESULT=READ_ONLY; V20.8; NO RO APP DATA CREATED, UPDATED OR DELETED")
    return 0

if __name__=="__main__": raise SystemExit(main())
