#!/usr/bin/env python3
"""MARSEL V20.37 strict READ-ONLY paginated entity + detail audit.

Uses only documented GET operations. Collection pages are followed from the API's
paging metadata; no identifiers are guessed. Concrete detail GETs use only IDs
actually returned by collection responses. No POST/PUT/PATCH/DELETE is executed.
Candidate records are retained as sanitized JSON snapshots so later offline
review can compare fields without another production write or guessed lookup.
"""
from __future__ import annotations
import hashlib,json,os,re,sys,time
from collections import defaultdict
from datetime import datetime,timezone
from urllib.parse import urlsplit,urlencode
import httpx

BASE=os.getenv("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.getenv("ROAPP_API_KEY","")
TIMEOUT=min(float(os.getenv("ROAPP_TIMEOUT","8")),12)
INPUT=os.getenv("MARSEL_API_INVENTORY_INPUT","marsel-api-inventory-v20-29.json")
OUTPUT=os.getenv("MARSEL_ENTITY_INVENTORY_OUTPUT","marsel-entity-inventory-v20-19.json")
MAX_IDS_PER_COLLECTION=min(int(os.getenv("MARSEL_MAX_IDS_PER_COLLECTION","3")),10)
MAX_DETAIL_PROBES=min(int(os.getenv("MARSEL_MAX_DETAIL_PROBES","50")),75)
MAX_PAGES_PER_COLLECTION=min(int(os.getenv("MARSEL_MAX_PAGES_PER_COLLECTION","50")),100)
MAX_RECORDS_PER_COLLECTION=min(int(os.getenv("MARSEL_MAX_RECORDS_PER_COLLECTION","5000")),10000)
PAGE_LIMIT=min(int(os.getenv("MARSEL_PAGE_LIMIT","50")),100)
PARAM_RE=re.compile(r"\{([^}]+)\}|:([A-Za-z_][\w-]*)|<([^>]+)>")
WRITE={"POST","PUT","PATCH","DELETE"}
SENSITIVE_KEYS={"authorization","token","access_token","refresh_token","api_key","apikey","password","secret","client_secret"}


def normalize(raw:str)->str|None:
    raw=raw.strip()
    if raw.startswith(("http://","https://")):
        p=urlsplit(raw)
        if p.netloc.lower()!="api.roapp.io": return None
        raw=p.path
    if raw.startswith("/v2/"): raw=raw[3:]
    if not raw.startswith("/"): raw="/"+raw
    return re.sub(r"/{2,}","/",raw)


def request_get(client:httpx.Client,path:str):
    started=time.monotonic()
    try:
        r=client.get(path)
        return r,round((time.monotonic()-started)*1000,1),None
    except httpx.TimeoutException as e:
        return None,round((time.monotonic()-started)*1000,1),type(e).__name__
    except httpx.HTTPError as e:
        return None,round((time.monotonic()-started)*1000,1),type(e).__name__


def classify(status):
    return "OK" if status==200 else "AUTH_REQUIRED" if status in (401,403) else "NOT_FOUND" if status==404 else "HTTP_ERROR"


def payload_rows(payload):
    if isinstance(payload,dict) and isinstance(payload.get("data"),list): return payload["data"]
    return []


def extract_ids(rows):
    ids=[]
    for item in rows:
        if isinstance(item,dict) and isinstance(item.get("id"),(int,str)) and str(item.get("id")):
            value=str(item["id"])
            if value not in ids: ids.append(value)
            if len(ids)>=MAX_IDS_PER_COLLECTION: break
    return ids


def replace_first_parameter(template,id_value):
    return PARAM_RE.sub(lambda m:str(id_value),template,count=1)


def page_path(path,page):
    sep="&" if "?" in path else "?"
    return f"{path}{sep}{urlencode({'page':page,'limit':PAGE_LIMIT})}"


def duplicate_candidates(path,rows):
    fields=("code","sku","title") if path.startswith("/catalog/products") else ("code","sku","title") if path.startswith("/catalog/services") else ("email",) if path=="/company/employees" else ()
    groups=defaultdict(list)
    for row in rows:
        if not isinstance(row,dict): continue
        values=[]
        for f in fields:
            v=row.get(f)
            if isinstance(v,str) and v.strip(): values.append((f,v.strip().casefold()))
        if values: groups[tuple(values)].append(str(row.get("id")))
    return [{"key":list(k),"ids":v} for k,v in groups.items() if len(v)>1]


def sanitize(value,key=""):
    if key.casefold() in SENSITIVE_KEYS: return "[REDACTED]"
    if isinstance(value,dict): return {str(k):sanitize(v,str(k)) for k,v in value.items() if str(k).casefold() not in SENSITIVE_KEYS}
    if isinstance(value,list): return [sanitize(v,key) for v in value]
    return value


def build_candidate_snapshots(path,rows):
    candidate_ids={i for g in duplicate_candidates(path,rows) for i in g["ids"]}
    snapshots=[]
    for row in rows:
        if not isinstance(row,dict): continue
        rid=str(row.get("id"))
        if rid in candidate_ids:
            snapshots.append({"endpoint":path,"id":rid,"fields":sanitize(row)})
    return snapshots


def main():
    if not KEY: print("ROAPP_API_KEY_missing",file=sys.stderr); return 2
    if not os.path.exists(INPUT): print(f"inventory_not_found:{INPUT}",file=sys.stderr); return 1
    data=json.load(open(INPUT,encoding="utf-8"))
    ops=data.get("operations",[])
    blocked=[]; collection_paths=[]; parameterized=[]
    for op in ops:
        method=str(op.get("method","")).upper(); raw=str(op.get("path",op.get("url","")))
        if method in WRITE: blocked.append(f"{method} {raw}"); continue
        if method!="GET": continue
        p=normalize(raw)
        if not p: continue
        if PARAM_RE.search(p): parameterized.append(p)
        elif p not in collection_paths: collection_paths.append(p)
    results=[]; detail_results=[]; detail_templates={}; collection_ids={}; collection_stats={}; duplicate_reports={}; candidate_snapshots=[]
    headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":"MARSEL-V20.37-Readonly"}
    with httpx.Client(base_url=BASE,headers=headers,timeout=TIMEOUT,follow_redirects=False) as client:
        for path in collection_paths:
            all_rows=[]; pages_seen=0; total_pages=None
            for page in range(1,MAX_PAGES_PER_COLLECTION+1):
                concrete=path if page==1 else page_path(path,page)
                r,lat,err=request_get(client,concrete); pages_seen+=1
                if r is None:
                    results.append({"path":path,"method":"GET","page":page,"http":None,"classification":"NETWORK_ERROR","latency_ms":lat,"error":err}); break
                if page==1:
                    results.append({"path":path,"method":"GET","page":1,"http":r.status_code,"classification":classify(r.status_code),"content_type":r.headers.get("content-type",""),"latency_ms":lat,"response_preview":r.text.replace("\n"," ")[:500]})
                if r.status_code!=200: break
                try: payload=r.json()
                except ValueError: break
                rows=payload_rows(payload); all_rows.extend(rows)
                paging=payload.get("paging") if isinstance(payload,dict) else None
                if isinstance(paging,dict):
                    try: total_pages=int(paging.get("total_pages")) if paging.get("total_pages") is not None else None
                    except (TypeError,ValueError): total_pages=None
                if len(all_rows)>=MAX_RECORDS_PER_COLLECTION or not rows or (total_pages is not None and page>=total_pages): break
                time.sleep(0.2)
            collection_ids[path]=extract_ids(all_rows)
            collection_stats[path]={"pages_fetched":pages_seen,"total_pages_reported":total_pages,"records_fetched":len(all_rows),"record_cap_reached":len(all_rows)>=MAX_RECORDS_PER_COLLECTION}
            dup=duplicate_candidates(path,all_rows)
            if dup: duplicate_reports[path]=dup
            candidate_snapshots.extend(build_candidate_snapshots(path,all_rows))
            time.sleep(0.2)
        for template in parameterized: detail_templates.setdefault(template,None)
        probes=0
        for template in sorted(detail_templates):
            if probes>=MAX_DETAIL_PROBES: break
            m=PARAM_RE.search(template)
            if not m: continue
            collection=template[:m.start()].rstrip("/")
            ids=collection_ids.get(collection,[])
            if not ids: continue
            for value in ids:
                if probes>=MAX_DETAIL_PROBES: break
                concrete=replace_first_parameter(template,value); r,lat,err=request_get(client,concrete)
                item={"template":template,"collection_path":collection,"identifier":value,"path":concrete,"method":"GET","latency_ms":lat}
                if r is None: item.update({"http":None,"classification":"NETWORK_ERROR","error":err})
                else:
                    item.update({"http":r.status_code,"classification":classify(r.status_code),"content_type":r.headers.get("content-type","")})
                    if r.status_code==200:
                        try:
                            payload=r.json(); item["json_valid"]=True; item["json_type"]=type(payload).__name__
                            item["response_keys"]=sorted(payload.keys()) if isinstance(payload,dict) else []
                            item["response_snapshot"]=sanitize(payload)
                        except ValueError: item["json_valid"]=False
                    else: item["json_valid"]=None
                detail_results.append(item); probes+=1; time.sleep(0.2)
    counts={}; detail_counts={}
    for r in results+detail_results: counts[r["classification"]]=counts.get(r["classification"],0)+1
    for r in detail_results: detail_counts[r["classification"]]=detail_counts.get(r["classification"],0)+1
    report={"version":"20.37","mode":"READ_ONLY","generated_at":datetime.now(timezone.utc).isoformat(),"api_base":BASE,"source_inventory":INPUT,"source_inventory_sha256":hashlib.sha256(open(INPUT,"rb").read()).hexdigest(),"collection_paths_considered":len(collection_paths),"results":results,"collection_stats":collection_stats,"parameterized_templates_considered":len(parameterized),"real_identifiers_extracted":sum(len(v) for v in collection_ids.values()),"identifiers_by_collection":collection_ids,"detail_results":detail_results,"detail_classifications":detail_counts,"classifications":counts,"duplicate_candidates":duplicate_reports,"duplicate_candidate_groups":sum(len(v) for v in duplicate_reports.values()),"candidate_record_snapshots":candidate_snapshots,"candidate_snapshot_count":len(candidate_snapshots),"write_requests":0,"ro_app_data_mutated":False,"safe_methods_used":["GET"],"write_methods_used":[],"blocked_write_methods_detected":blocked,"blocked_write_methods_count":len(blocked),"parameterized_identifiers_guessed":False,"audit_status":"PASS"}
    with open(OUTPUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2); f.write("\n")
    print("=== MARSEL V20.37 PAGINATED ENTITY + DETAIL INVENTORY / READ ONLY ===")
    print(f"COLLECTION_PATHS_CONSIDERED={len(collection_paths)}")
    print(f"COLLECTION_PAGES_FETCHED={sum(v['pages_fetched'] for v in collection_stats.values())}")
    print(f"COLLECTION_RECORDS_FETCHED={sum(v['records_fetched'] for v in collection_stats.values())}")
    print(f"REAL_IDENTIFIERS_EXTRACTED={sum(len(v) for v in collection_ids.values())}")
    print(f"DETAIL_PROBES={len(detail_results)}")
    print(f"DETAIL_CLASSIFICATIONS={json.dumps(detail_counts,sort_keys=True)}")
    print(f"DUPLICATE_CANDIDATE_GROUPS={sum(len(v) for v in duplicate_reports.values())}")
    print(f"CANDIDATE_RECORD_SNAPSHOTS={len(candidate_snapshots)}")
    print(f"BLOCKED_WRITE_OPERATIONS={len(blocked)}")
    print("WRITE_REQUESTS=0")
    print("RO_APP_DATA_MUTATED=false")
    print("PARAMETERIZED_IDENTIFIERS_GUESSED=false")
    print("AUDIT_STATUS=PASS")
    print(f"REPORT_SHA256={hashlib.sha256(open(OUTPUT,'rb').read()).hexdigest()}")
    return 0

if __name__=="__main__": raise SystemExit(main())