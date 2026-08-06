#!/usr/bin/env python3
"""MARSEL V20.9 — cross-entity integrity audit, READ ONLY.

Re-reads the verified V20.8 target set using GET only and checks IDs,
foreign-key references, required fields, duplicate identifiers and
obvious data anomalies. It produces findings only; it never mutates RO App.
"""
import hashlib, json, os, sys, time
from collections import Counter, defaultdict
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE=os.environ.get("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.environ.get("ROAPP_API_KEY","")
OUT=os.environ.get("MARSEL_AUDIT_OUTPUT","marsel-integrity-audit-v20-9.json")
TIMEOUT=int(os.environ.get("ROAPP_TIMEOUT","30")); PAGE_SIZE=int(os.environ.get("MARSEL_PAGE_SIZE","100")); MAX_PAGES=int(os.environ.get("MARSEL_MAX_PAGES","100"))
TARGETS=[
 ("orders","/orders","/orders/{id}"),("services","/catalog/services","/catalog/services/{id}"),("products","/catalog/products","/catalog/products/{id}"),("bundles","/catalog/bundles","/catalog/bundles/{id}"),
 ("inquiries","/inquiries","/inquiries/{id}"),("bookings","/bookings","/bookings/{id}"),("estimates","/estimates","/estimates/{id}"),("invoices","/invoices","/invoices/{id}")]


def get(path, params=None):
    url=path if path.startswith("http") else BASE+path
    if params: url += ("&" if "?" in url else "?")+urlencode(params)
    req=Request(url,headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":"MARSEL-Audit-V20.9"},method="GET")
    t=time.time()
    try:
        with urlopen(req,timeout=TIMEOUT) as r: return r.status,json.loads(r.read().decode()),round(time.time()-t,3),None
    except HTTPError as e: return e.code,None,round(time.time()-t,3),e.read().decode(errors="replace")[:500]
    except (URLError,TimeoutError,ValueError) as e: return None,None,round(time.time()-t,3),str(e)

def records(p):
    if isinstance(p,list): return p
    if not isinstance(p,dict): return []
    for k in ("data","items","results","orders","services","products","bundles","inquiries","bookings","estimates","invoices"):
        if isinstance(p.get(k),list): return p[k]
    for k in ("data","result"):
        if isinstance(p.get(k),dict):
            r=records(p[k])
            if r: return r
    return []

def rid(x):
    return next((x.get(k) for k in ("id","ID","uuid") if isinstance(x,dict) and x.get(k) is not None),None)

def next_page(p):
    if not isinstance(p,dict): return None
    for k in ("has_next","hasNext"):
        if isinstance(p.get(k),bool): return p[k]
    for k in ("next","next_page","nextPage"):
        if k in p: return p[k] not in (None,False,"",0)
    return None

def collect(t):
    all_rows=[]; pages=[]; errors=[]; seen=set()
    for page in range(1,MAX_PAGES+1):
        s,p,elapsed,err=get(t[1],{"page":page,"page_size":PAGE_SIZE}); rows=records(p) if s==200 else []
        ids=[rid(x) for x in rows]; sig=hashlib.sha256(json.dumps(ids,separators=(",",":"),default=str).encode()).hexdigest() if rows else None
        repeated=sig in seen if sig else False
        if sig: seen.add(sig)
        pages.append({"page":page,"http":s,"records":len(rows),"elapsed_s":elapsed,"repeated_page":repeated,"has_next":next_page(p)})
        if s!=200: errors.append({"page":page,"http":s,"error":err}); break
        all_rows.extend(rows)
        if not rows or repeated or next_page(p) is False: break
    return all_rows,pages,errors

def main():
    if not KEY: print("ROAPP_API_KEY is required",file=sys.stderr); return 2
    report={"version":"20.9","readonly":True,"write_requests_made":0,"ro_app_data_mutated":False,"method_policy":{"allowed":["GET"],"forbidden":["POST","PUT","PATCH","DELETE"]},"targets":[],"findings":[]}
    data={}; total_requests=0
    for entity,listing,detail in TARGETS:
        rows,pages,errors=collect((entity,listing,detail)); total_requests += sum(1 for _ in pages)
        ids=[rid(x) for x in rows if rid(x) is not None]; counts=Counter(str(x) for x in ids); dup_ids=[x for x,n in counts.items() if n>1]
        details={}; detail_failures=[]
        for x in dict.fromkeys(ids):
            s,p,e,err=get(detail.format(id=x)); total_requests += 1
            details[str(x)]={"http":s,"ok":s==200}
            if s!=200: detail_failures.append({"id":x,"http":s,"error":err})
        data[entity]={"rows":rows,"ids":set(str(x) for x in ids),"pages":pages,"errors":errors,"details":details}
        if errors: report["findings"].append({"severity":"CRITICAL","code":"LIST_ENDPOINT_FAILURE","entity":entity,"errors":errors})
        if detail_failures: report["findings"].append({"severity":"CRITICAL","code":"DETAIL_ENDPOINT_FAILURE","entity":entity,"items":detail_failures[:100]})
        if dup_ids: report["findings"].append({"severity":"WARNING","code":"DUPLICATE_ID","entity":entity,"ids":dup_ids[:100]})
        if not rows and not errors: report["findings"].append({"severity":"INFO","code":"EMPTY_ENDPOINT","entity":entity})

    # Reference checks use only fields actually present in the live payload.
    ref_rules={
      "orders": [("client_id",("contacts","clients","people")),("manager_id",("employees",)),("assignee_id",("employees",)),("branch_id",("branches",))],
      "invoices": [("client_id",("contacts","clients","people")),("order_id",("orders",))],
      "bookings": [("client_id",("contacts","clients","people")),("employee_id",("employees",))],
      "estimates": [("client_id",("contacts","clients","people")),("order_id",("orders",))],
    }
    # V20.9 does not guess undocumented entity endpoints. If a reference target is not
    # in the verified target set, mark it UNVERIFIED rather than a false orphan.
    for entity,rules in ref_rules.items():
        if entity not in data: continue
        for field,target_names in rules:
            present=[]
            for row in data[entity]["rows"]:
                if isinstance(row,dict) and row.get(field) not in (None,""): present.append(row.get(field))
            if not present: continue
            available=None; target=None
            for name in target_names:
                if name in data: available=data[name]["ids"]; target=name; break
            if available is None:
                report["findings"].append({"severity":"INFO","code":"REFERENCE_UNVERIFIED","entity":entity,"field":field,"target_candidates":list(target_names),"count":len(present)})
            else:
                missing=[v for v in present if str(v) not in available]
                if missing: report["findings"].append({"severity":"WARNING","code":"ORPHAN_REFERENCE_CANDIDATE","entity":entity,"field":field,"target":target,"count":len(missing),"values":list(dict.fromkeys(missing))[:100]})

    # Required-field checks are conservative: only flag fields that are clearly part of the payload model.
    required={"orders":["id"],"products":["id"],"services":["id"],"invoices":["id"]}
    for entity,fields in required.items():
        for field in fields:
            missing=sum(1 for r in data.get(entity,{}).get("rows",[]) if not isinstance(r,dict) or r.get(field) in (None,""))
            if missing: report["findings"].append({"severity":"WARNING","code":"MISSING_REQUIRED_FIELD","entity":entity,"field":field,"count":missing})

    report["summary"]={"targets":len(TARGETS),"records":sum(len(x["rows"]) for x in data.values()),"api_requests":total_requests,"findings":len(report["findings"]),"critical":sum(f["severity"]=="CRITICAL" for f in report["findings"]),"warnings":sum(f["severity"]=="WARNING" for f in report["findings"]),"unverified":sum(f["code"]=="REFERENCE_UNVERIFIED" for f in report["findings"]),"write_requests_made":0,"readonly":True}
    payload=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode(); report["summary"]["report_sha256"]=hashlib.sha256(payload).hexdigest()
    with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
    print("=== MARSEL V20.9 / INTEGRITY / READ ONLY ===")
    for k,v in report["summary"].items(): print(f"{k.upper()}={v}")
    print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
    return 0

if __name__=="__main__": raise SystemExit(main())
