#!/usr/bin/env python3
"""MARSEL V20.9 - read-only data-integrity and empty-endpoint audit.

V20.9 consumes the same eight RO App resources as V20.8, but avoids the
expensive full-detail pass. It discovers list data, identifies empty
endpoints, checks pagination, validates record IDs/structure, and performs
reference-integrity checks only when a record exposes an explicitly named
reference field that can be mapped to one of the discovered target entities.

GET only. POST/PUT/PATCH/DELETE are forbidden by design.
"""
import hashlib
import json
import os
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE=os.environ.get("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.environ.get("ROAPP_API_KEY","")
OUT=os.environ.get("MARSEL_AUDIT_OUTPUT","marsel-data-integrity-v20-9.json")
TIMEOUT=int(os.environ.get("ROAPP_TIMEOUT","30"))
PAGE_SIZE=int(os.environ.get("MARSEL_PAGE_SIZE","100"))
MAX_PAGES=int(os.environ.get("MARSEL_MAX_PAGES","100"))
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
    req=Request(url,headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":"MARSEL-Audit-V20.9"},method="GET")
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
    if not isinstance(x,dict): return None
    return next((x[k] for k in ("id","ID","uuid") if x.get(k) is not None),None)

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

def flatten_refs(value,prefix=""):
    found=[]
    if isinstance(value,dict):
        for k,v in value.items():
            key=f"{prefix}.{k}" if prefix else k
            if isinstance(v,(str,int)) and re.search(r"(?:^|_)(id|ids)$|(?:Id|Ids)$",k):
                found.append((key,k,v))
            elif isinstance(v,(dict,list)):
                found.extend(flatten_refs(v,key))
    elif isinstance(value,list):
        for i,v in enumerate(value): found.extend(flatten_refs(v,f"{prefix}[{i}]"))
    return found

def infer_target(key):
    k=re.sub(r"[^a-z0-9]","",key.lower())
    for entity in ("orders","services","products","bundles","inquiries","bookings","estimates","invoices"):
        e=entity[:-1] if entity.endswith("s") else entity
        if e in k or entity in k: return entity
    return None

def main():
    if not KEY:
        print("ROAPP_API_KEY is required",file=sys.stderr); return 2
    report={"version":"20.9","readonly":True,"write_requests_made":0,"ro_app_data_mutated":False,"method_policy":{"allowed":["GET"],"forbidden":["POST","PUT","PATCH","DELETE"]},"targets":[],"reference_checks":[]}
    all_ids={t["entity"]:set() for t in TARGETS}
    total={"records":0,"empty":0,"list_failures":0,"structural_issues":0,"duplicate_id_candidates":0,"fingerprint_duplicate_candidates":0,"pagination_inconclusive":0,"reference_candidates":0,"unresolved_reference_candidates":0}
    cached=[]
    for t in TARGETS:
        rs,pages,errors,ended=collect(t); cached.append((t,rs,pages,errors,ended))
        ids=[]; seen=set(); dup=[]; fingerprints={}; structural=[]
        for i,x in enumerate(rs):
            if not isinstance(x,dict): structural.append(i); continue
            x_id=rid(x)
            if x_id is None: structural.append(i)
            elif x_id in seen: dup.append(x_id)
            else: seen.add(x_id); ids.append(x_id)
            clean={k:v for k,v in x.items() if k not in VOLATILE}
            sig=hashlib.sha256(json.dumps(clean,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
            fingerprints.setdefault(sig,[]).append(x_id)
        all_ids[t["entity"]]=set(ids)
        fp_dups=[v for v in fingerprints.values() if len(v)>1]
        findings=[]
        if not rs and not errors: findings.append({"severity":"INFO","code":"EMPTY_ENDPOINT"})
        if errors: findings.append({"severity":"ERROR","code":"LIST_REQUEST_FAILURE","count":len(errors)})
        if structural: findings.append({"severity":"WARNING","code":"STRUCTURAL_ISSUES","records":structural[:100]})
        if dup: findings.append({"severity":"WARNING","code":"DUPLICATE_ID_CANDIDATES","ids":dup[:100]})
        if fp_dups: findings.append({"severity":"WARNING","code":"DUPLICATE_FINGERPRINT_CANDIDATES","groups":fp_dups[:100]})
        if len(pages)>=MAX_PAGES and not ended:
            findings.append({"severity":"WARNING","code":"PAGINATION_INCONCLUSIVE"}); total["pagination_inconclusive"]+=1
        report["targets"].append({"entity":t["entity"],"list_endpoint":t["list"],"records_seen":len(rs),"unique_ids":len(seen),"pages":pages,"list_errors":errors,"findings":findings})
        total["records"]+=len(rs); total["empty"]+=int(not rs and not errors); total["list_failures"]+=len(errors); total["structural_issues"]+=len(structural); total["duplicate_id_candidates"]+=len(dup); total["fingerprint_duplicate_candidates"]+=len(fp_dups)
    # Reference integrity is conservative: only explicit *_id/*_ids or camelCase *Id/*Ids fields
    # whose key name clearly maps to one of the audited target entities are evaluated.
    for t,rs,_,_,_ in cached:
        for idx,x in enumerate(rs):
            for path,key,value in flatten_refs(x):
                target=infer_target(key)
                if not target: continue
                vals=value if isinstance(value,list) else [value]
                for ref in vals:
                    total["reference_candidates"]+=1
                    unresolved=ref not in all_ids.get(target,set())
                    if unresolved: total["unresolved_reference_candidates"]+=1
                    report["reference_checks"].append({"source_entity":t["entity"],"record_id":rid(x),"field":path,"reference_value":ref,"target_entity":target,"resolved":not unresolved})
    if total["unresolved_reference_candidates"]:
        report["reference_summary"]={"candidates":total["reference_candidates"],"unresolved":total["unresolved_reference_candidates"],"classification":"WARNING; verify field semantics before any write"}
    else:
        report["reference_summary"]={"candidates":total["reference_candidates"],"unresolved":0,"classification":"SAFE for discovered references; no mutation performed"}
    report["summary"]={"targets":len(TARGETS),**total,"readonly":True,"write_requests_made":0}
    with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
    print("=== MARSEL AUDIT V20.9 / DATA INTEGRITY / READ ONLY ===")
    print(f"TARGETS={len(TARGETS)}")
    print(f"LIST_RECORDS_SEEN={total['records']}")
    print(f"EMPTY_ENDPOINTS={total['empty']}")
    print(f"LIST_FAILURES={total['list_failures']}")
    print(f"STRUCTURAL_ISSUES={total['structural_issues']}")
    print(f"DUPLICATE_ID_CANDIDATES={total['duplicate_id_candidates']}")
    print(f"DUPLICATE_FINGERPRINT_CANDIDATES={total['fingerprint_duplicate_candidates']}")
    print(f"PAGINATION_INCONCLUSIVE={total['pagination_inconclusive']}")
    print(f"REFERENCE_CANDIDATES={total['reference_candidates']}")
    print(f"UNRESOLVED_REFERENCE_CANDIDATES={total['unresolved_reference_candidates']}")
    print("WRITE_REQUESTS_MADE=0")
    print(f"REPORT={OUT}")
    print("RESULT=READ_ONLY; V20.9; NO RO APP DATA CREATED, UPDATED OR DELETED")
    return 0

if __name__=="__main__": raise SystemExit(main())
