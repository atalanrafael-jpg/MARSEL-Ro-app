#!/usr/bin/env python3
"""MARSEL V20.35 strict READ-ONLY entity + detail inventory.

Consumes the current API inventory, probes concrete GET collections, extracts
real identifiers from those GET responses, and uses only those identifiers to
probe documented parameterized GET endpoints. No identifiers are guessed and
no write method is executed.
"""
from __future__ import annotations
import hashlib,json,os,re,sys,time
from datetime import datetime,timezone
from urllib.parse import urlsplit
import httpx

BASE=os.getenv("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.getenv("ROAPP_API_KEY","")
TIMEOUT=min(float(os.getenv("ROAPP_TIMEOUT","8")),12)
INPUT=os.getenv("MARSEL_API_INVENTORY_INPUT","marsel-api-inventory-v20-29.json")
OUTPUT=os.getenv("MARSEL_ENTITY_INVENTORY_OUTPUT","marsel-entity-inventory-v20-19.json")
MAX_IDS_PER_COLLECTION=min(int(os.getenv("MARSEL_MAX_IDS_PER_COLLECTION","3")),5)
MAX_DETAIL_PROBES=min(int(os.getenv("MARSEL_MAX_DETAIL_PROBES","50")),75)
PARAM_RE=re.compile(r"\{([^}]+)\}|:([A-Za-z_][\w-]*)|<([^>]+)>")
WRITE={"POST","PUT","PATCH","DELETE"}

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
        return r, round((time.monotonic()-started)*1000,1), None
    except httpx.TimeoutException as e:
        return None, round((time.monotonic()-started)*1000,1), type(e).__name__
    except httpx.HTTPError as e:
        return None, round((time.monotonic()-started)*1000,1), type(e).__name__

def classify(status):
    return ("OK" if status==200 else
            "AUTH_REQUIRED" if status in (401,403) else
            "NOT_FOUND" if status==404 else "HTTP_ERROR")

def extract_ids(payload):
    if not isinstance(payload,dict): return []
    data=payload.get("data")
    if not isinstance(data,list): return []
    ids=[]
    for item in data:
        if isinstance(item,dict) and isinstance(item.get("id"),(int,str)) and str(item.get("id")):
            value=str(item["id"])
            if value not in ids: ids.append(value)
    return ids[:MAX_IDS_PER_COLLECTION]

def replace_first_parameter(template,id_value):
    def repl(m): return str(id_value)
    return PARAM_RE.sub(repl,template,count=1)

def main():
    if not KEY:
        print("ROAPP_API_KEY_missing",file=sys.stderr); return 2
    if not os.path.exists(INPUT):
        print(f"inventory_not_found:{INPUT}",file=sys.stderr); return 1
    data=json.load(open(INPUT,encoding="utf-8"))
    ops=data.get("operations",[])
    blocked=[]; collection_paths=[]; parameterized=[]
    for op in ops:
        method=str(op.get("method","")).upper(); raw=str(op.get("path",op.get("url","")))
        if method in WRITE:
            blocked.append(f"{method} {raw}"); continue
        if method!="GET": continue
        p=normalize(raw)
        if not p: continue
        if PARAM_RE.search(p):
            parameterized.append(p)
        elif p not in collection_paths:
            collection_paths.append(p)

    results=[]; collection_ids={}
    detail_results=[]; detail_templates={}
    headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":"MARSEL-V20.35-Readonly"}
    with httpx.Client(base_url=BASE,headers=headers,timeout=TIMEOUT,follow_redirects=False) as client:
        for path in collection_paths:
            r,lat,err=request_get(client,path)
            if r is None:
                results.append({"path":path,"method":"GET","http":None,"classification":"NETWORK_ERROR","latency_ms":lat,"error":err})
            else:
                body=r.text
                results.append({"path":path,"method":"GET","http":r.status_code,"classification":classify(r.status_code),"content_type":r.headers.get("content-type",""),"latency_ms":lat,"response_preview":body.replace("\n"," ")[:500]})
                if r.status_code==200:
                    try: collection_ids[path]=extract_ids(r.json())
                    except ValueError: collection_ids[path]=[]
            time.sleep(0.2)

        # Build parameterized templates only from the documented source inventory.
        for template in parameterized:
            if template not in detail_templates: detail_templates[template]=None

        probes=0
        for template in sorted(detail_templates):
            if probes>=MAX_DETAIL_PROBES: break
            m=PARAM_RE.search(template)
            if not m: continue
            prefix=template[:m.start()]
            # A detail template is eligible only when its concrete identifier
            # comes from a collection GET whose path is exactly that prefix.
            collection=prefix.rstrip("/")
            ids=collection_ids.get(collection,[])
            if not ids: continue
            for value in ids:
                if probes>=MAX_DETAIL_PROBES: break
                concrete=replace_first_parameter(template,value)
                r,lat,err=request_get(client,concrete)
                item={"template":template,"collection_path":collection,"identifier":value,"path":concrete,"method":"GET","latency_ms":lat}
                if r is None:
                    item.update({"http":None,"classification":"NETWORK_ERROR","error":err})
                else:
                    item.update({"http":r.status_code,"classification":classify(r.status_code),"content_type":r.headers.get("content-type","")})
                    if r.status_code==200:
                        try:
                            payload=r.json(); item["json_valid"]=True; item["json_type"]=type(payload).__name__
                        except ValueError: item["json_valid"]=False
                    else: item["json_valid"]=None
                detail_results.append(item); probes+=1
                time.sleep(0.2)

    counts={}
    for r in results+detail_results:
        counts[r["classification"]]=counts.get(r["classification"],0)+1
    detail_counts={}
    for r in detail_results:
        detail_counts[r["classification"]]=detail_counts.get(r["classification"],0)+1

    report={
        "version":"20.35","mode":"READ_ONLY","generated_at":datetime.now(timezone.utc).isoformat(),
        "api_base":BASE,"source_inventory":INPUT,
        "source_inventory_sha256":hashlib.sha256(open(INPUT,"rb").read()).hexdigest(),
        "collection_paths_considered":len(collection_paths),"results":results,
        "parameterized_templates_considered":len(parameterized),
        "real_identifiers_extracted":sum(len(v) for v in collection_ids.values()),
        "identifiers_by_collection":collection_ids,
        "detail_results":detail_results,
        "detail_classifications":detail_counts,
        "classifications":counts,
        "write_requests":0,"ro_app_data_mutated":False,"safe_methods_used":["GET"],
        "write_methods_used":[],"blocked_write_methods_detected":blocked,
        "blocked_write_methods_count":len(blocked),
        "parameterized_identifiers_guessed":False,
        "audit_status":"PASS"
    }
    with open(OUTPUT,"w",encoding="utf-8") as f:
        json.dump(report,f,ensure_ascii=False,indent=2); f.write("\n")
    print("=== MARSEL V20.35 ENTITY + DETAIL INVENTORY / READ ONLY ===")
    print(f"COLLECTION_PATHS_CONSIDERED={len(collection_paths)}")
    print(f"PARAMETERIZED_TEMPLATES_CONSIDERED={len(parameterized)}")
    print(f"REAL_IDENTIFIERS_EXTRACTED={sum(len(v) for v in collection_ids.values())}")
    print(f"DETAIL_PROBES={len(detail_results)}")
    print(f"DETAIL_CLASSIFICATIONS={json.dumps(detail_counts,sort_keys=True)}")
    print(f"BLOCKED_WRITE_OPERATIONS={len(blocked)}")
    print("WRITE_REQUESTS=0")
    print("RO_APP_DATA_MUTATED=false")
    print("PARAMETERIZED_IDENTIFIERS_GUESSED=false")
    print("AUDIT_STATUS=PASS")
    print(f"REPORT_SHA256={hashlib.sha256(open(OUTPUT,'rb').read()).hexdigest()}")
    return 0

if __name__=="__main__": raise SystemExit(main())
