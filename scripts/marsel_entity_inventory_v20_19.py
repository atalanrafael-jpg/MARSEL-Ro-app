#!/usr/bin/env python3
"""MARSEL V20.33 strict READ-ONLY entity inventory.

Consumes the current API inventory schema (method/path operations), normalizes
/v2-prefixed paths against the configured API base, probes only concrete GET
collection paths, and records response evidence. No writes and no identifier
inference are permitted.
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
PARAM_RE=re.compile(r"\{[^}]+\}|:[A-Za-z_][\w-]*|<[^>]+>")
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

def main():
    if not KEY: print("ROAPP_API_KEY_missing",file=sys.stderr); return 2
    if not os.path.exists(INPUT): print(f"inventory_not_found:{INPUT}",file=sys.stderr); return 1
    data=json.load(open(INPUT,encoding="utf-8")); ops=data.get("operations",[])
    paths=[]; blocked=[]
    for op in ops:
        method=str(op.get("method","")).upper()
        if method in WRITE: blocked.append(f"{method} {op.get('path','')}"); continue
        if method!="GET": continue
        p=normalize(str(op.get("path",op.get("url",""))))
        if not p or PARAM_RE.search(p): continue
        if p not in paths: paths.append(p)
    results=[]
    headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":"MARSEL-V20.33-Readonly"}
    with httpx.Client(base_url=BASE,headers=headers,timeout=TIMEOUT,follow_redirects=False) as client:
        for path in paths:
            started=time.monotonic()
            try:
                r=client.get(path)
                body=r.text[:1000]
                cls="OK" if r.status_code==200 else "AUTH_REQUIRED" if r.status_code in (401,403) else "NOT_FOUND" if r.status_code==404 else "HTTP_ERROR"
                results.append({"path":path,"method":"GET","http":r.status_code,"classification":cls,"content_type":r.headers.get("content-type",""),"latency_ms":round((time.monotonic()-started)*1000,1),"response_preview":body.replace("\n"," ")[:500]})
            except httpx.TimeoutException as e: results.append({"path":path,"method":"GET","http":None,"classification":"TIMEOUT","error":type(e).__name__})
            except httpx.HTTPError as e: results.append({"path":path,"method":"GET","http":None,"classification":"NETWORK_ERROR","error":type(e).__name__})
            time.sleep(0.2)
    counts={}
    for r in results: counts[r["classification"]]=counts.get(r["classification"],0)+1
    report={"version":"20.33","mode":"READ_ONLY","generated_at":datetime.now(timezone.utc).isoformat(),"api_base":BASE,"source_inventory":INPUT,"source_inventory_sha256":hashlib.sha256(open(INPUT,"rb").read()).hexdigest(),"collection_paths_considered":len(paths),"results":results,"classifications":counts,"write_requests":0,"ro_app_data_mutated":False,"safe_methods_used":["GET"],"write_methods_used":[],"blocked_write_methods_detected":blocked}
    with open(OUTPUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2);f.write("\n")
    print("=== MARSEL V20.33 ENTITY INVENTORY / READ ONLY ===")
    print(f"COLLECTION_PATHS_CONSIDERED={len(paths)}")
    print(f"CLASSIFICATIONS={json.dumps(counts,sort_keys=True)}")
    print("WRITE_REQUESTS=0");print("RO_APP_DATA_MUTATED=false")
    print(f"REPORT_SHA256={hashlib.sha256(open(OUTPUT,'rb').read()).hexdigest()}")
    return 0 if not blocked else 1
if __name__=="__main__": raise SystemExit(main())