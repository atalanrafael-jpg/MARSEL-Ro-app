#!/usr/bin/env python3
"""MARSEL V20.6 - full read-only data-quality discovery.
No POST/PUT/PATCH/DELETE requests are made. V20.6 extends V20.5 with
pagination evidence, structural checks, duplicate candidates, empty-endpoint
classification, and list->detail verification.
"""
import hashlib, json, os, sys, time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlencode

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
OUT = os.environ.get("MARSEL_AUDIT_OUTPUT", "marsel-data-discovery-v20-6.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "30"))
PAGE_SIZE = int(os.environ.get("MARSEL_PAGE_SIZE", "100"))
MAX_PAGES = int(os.environ.get("MARSEL_MAX_PAGES", "5"))
MAX_DETAIL = int(os.environ.get("MARSEL_MAX_DETAIL", "500"))
TARGETS = [
 {"entity":"orders","list":"/orders","detail":"/orders/{id}"},
 {"entity":"services","list":"/catalog/services","detail":"/catalog/services/{id}"},
 {"entity":"products","list":"/catalog/products","detail":"/catalog/products/{id}"},
 {"entity":"bundles","list":"/catalog/bundles","detail":"/catalog/bundles/{id}"},
 {"entity":"inquiries","list":"/inquiries","detail":"/inquiries/{id}"},
 {"entity":"bookings","list":"/bookings","detail":"/bookings/{id}"},
 {"entity":"estimates","list":"/estimates","detail":"/estimates/{id}"},
 {"entity":"invoices","list":"/invoices","detail":"/invoices/{id}"},
]
VOLATILE = {"created_at","updated_at","createdAt","updatedAt","timestamp","request_id","requestId"}

def get(path, params=None):
    url = BASE + path
    if params: url += ("&" if "?" in url else "?") + urlencode(params)
    req = Request(url, headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":"MARSEL-Audit-V20.6"}, method="GET")
    started=time.time()
    try:
        with urlopen(req, timeout=TIMEOUT) as r:
            raw=r.read(); return r.status,json.loads(raw.decode("utf-8")),round(time.time()-started,3),None
    except HTTPError as e:
        body=e.read().decode("utf-8",errors="replace")[:1000]; return e.code,None,round(time.time()-started,3),body
    except (URLError,TimeoutError,ValueError) as e:
        return None,None,round(time.time()-started,3),str(e)

def extract_records(payload):
    if isinstance(payload,list): return payload
    if not isinstance(payload,dict): return []
    keys=("data","items","results","orders","services","products","bundles","inquiries","bookings","estimates","invoices")
    for k in keys:
        v=payload.get(k)
        if isinstance(v,list): return v
    for k in ("data","result"):
        v=payload.get(k)
        if isinstance(v,dict):
            x=extract_records(v)
            if x:return x
    return []

def record_id(item):
    if not isinstance(item,dict): return None
    for k in ("id","ID","uuid"):
        if item.get(k) is not None:return item[k]
    return None

def normalize(v):
    if isinstance(v,dict): return {k:normalize(x) for k,x in sorted(v.items()) if k not in VOLATILE}
    if isinstance(v,list): return [normalize(x) for x in v]
    return v

def fingerprint(item):
    raw=json.dumps(normalize(item),ensure_ascii=False,sort_keys=True,separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def pagination_evidence(payload, records, page):
    if not isinstance(payload,dict): return {"page":page,"records":len(records),"has_next":len(records)>=PAGE_SIZE,"evidence": "record_count_reached_page_size" if len(records)>=PAGE_SIZE else "no_next_indicator"}
    candidates=[]
    for k in ("next","next_page","nextPage","has_next","hasNext","total","count","page","current_page","currentPage","pages","total_pages","totalPages"):
        if k in payload:candidates.append({k:payload[k]})
    return {"page":page,"records":len(records),"metadata":candidates,"has_next":len(records)>=PAGE_SIZE,"evidence":"metadata_present" if candidates else ("record_count_reached_page_size" if len(records)>=PAGE_SIZE else "no_pagination_metadata")}

def main():
    if not KEY: print("ROAPP_API_KEY is required",file=sys.stderr); return 2
    report={"version":"20.6","readonly":True,"write_requests_made":False,"ro_app_data_mutated":False,"method_policy":{"allowed":["GET"],"forbidden":["POST","PUT","PATCH","DELETE"]},"targets":[],"summary":{}}
    totals={"records":0,"detail":0,"empty":0,"structural_issues":0,"duplicate_candidates":0}
    for t in TARGETS:
        entity=t["entity"]; all_records=[]; pages=[]; errors=[]; status_counts={}; seen_ids=set(); duplicate_ids=[]; missing_ids=[]
        for page in range(1,MAX_PAGES+1):
            status,payload,elapsed,error=get(t["list"],{"page":page,"page_size":PAGE_SIZE})
            status_counts[str(status)]=status_counts.get(str(status),0)+1
            if status!=200 or payload is None:
                errors.append({"page":page,"http":status,"error":error}); break
            recs=extract_records(payload); pages.append(pagination_evidence(payload,recs,page)); all_records.extend(recs)
            if len(recs)<PAGE_SIZE: break
        fp_map={}; structural=[]
        for idx,item in enumerate(all_records):
            rid=record_id(item)
            if rid is None: missing_ids.append(idx)
            elif rid in seen_ids: duplicate_ids.append(rid)
            else: seen_ids.add(rid)
            fp=fingerprint(item); fp_map.setdefault(fp,[]).append(rid)
            if not isinstance(item,dict): structural.append({"index":idx,"issue":"record_not_object"})
            elif rid is None: structural.append({"index":idx,"issue":"missing_id"})
        fp_dupes=[ids for ids in fp_map.values() if len(ids)>1]
        detail=[]
        ids=[record_id(x) for x in all_records if record_id(x) is not None][:MAX_DETAIL]
        for rid in ids:
            ds,dp,de,derr=get(t["detail"].format(id=rid)); cls={200:"OK",401:"AUTH_FAILURE",403:"ACCESS_DENIED",404:"NOT_FOUND",429:"RATE_LIMIT"}.get(ds,"SERVER_ERROR" if ds and ds>=500 else "UNEXPECTED_HTTP")
            detail.append({"source_id":rid,"detail_path":t["detail"].format(id=rid),"http":ds,"classification":cls,"elapsed_s":de,"error":derr})
        detail_fail=[x for x in detail if x["classification"]!="OK"]
        findings=[]
        if not all_records and not errors: findings.append({"severity":"INFO","code":"EMPTY_ENDPOINT","message":"Endpoint returned HTTP 200 but no records in inspected pages; absence is not classified as an error without schema/business evidence."})
        if duplicate_ids: findings.append({"severity":"WARNING","code":"DUPLICATE_IDS","count":len(duplicate_ids),"ids":duplicate_ids[:100]})
        if fp_dupes: findings.append({"severity":"WARNING","code":"DUPLICATE_FINGERPRINTS","groups":fp_dupes[:100]})
        if structural: findings.append({"severity":"WARNING","code":"STRUCTURAL_ANOMALIES","items":structural[:100]})
        if detail_fail: findings.append({"severity":"WARNING","code":"DETAIL_CHECK_FAILURES","count":len(detail_fail),"items":detail_fail[:100]})
        entry={"entity":entity,"list_endpoint":t["list"],"detail_endpoint":t["detail"],"pages":pages,"records_seen":len(all_records),"unique_ids":len(seen_ids),"missing_id_records":len(missing_ids),"duplicate_id_candidates":len(duplicate_ids),"duplicate_fingerprint_groups":len(fp_dupes),"detail_checks":detail,"list_errors":errors,"status_counts":status_counts,"findings":findings}
        report["targets"].append(entry)
        totals["records"]+=len(all_records); totals["detail"]+=len(detail); totals["empty"]+=int(not all_records and not errors); totals["structural_issues"]+=len(structural); totals["duplicate_candidates"]+=len(duplicate_ids)+len(fp_dupes)
    report["summary"]={"targets":len(TARGETS),**totals,"write_requests_made":0,"readonly":True}
    with open(OUT,"w",encoding="utf-8") as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print("=== MARSEL AUDIT V20.6 / FULL DISCOVERY + DATA QUALITY / READ ONLY ===")
    print(f"TARGETS={len(TARGETS)}")
    print(f"LIST_RECORDS_SEEN={totals['records']}")
    print(f"DETAIL_CHECKS={totals['detail']}")
    print(f"EMPTY_ENDPOINTS={totals['empty']}")
    print(f"DUPLICATE_CANDIDATES={totals['duplicate_candidates']}")
    print(f"STRUCTURAL_ISSUES={totals['structural_issues']}")
    print("WRITE_REQUESTS_MADE=0")
    print(f"REPORT={OUT}")
    print("RESULT=READ_ONLY; V20.6; NO RO APP DATA CREATED, UPDATED OR DELETED")
    return 0
if __name__=="__main__":sys.exit(main())
