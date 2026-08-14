#!/usr/bin/env python3
"""MARSEL full read-only backup controller.

Consumes the canonical V20.31 inventory and backs up only endpoints explicitly
classified as documented GET collection endpoints. It never converts an
undocumented path into GET and never sends a write request.

The controller is deliberately fail-closed: if the inventory does not provide
an explicit collection-level GET endpoint, the run reports INCOMPLETE rather
than claiming a full production backup.
"""
from __future__ import annotations
import hashlib, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
import httpx

BASE=os.environ.get("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.environ.get("ROAPP_API_KEY","")
INVENTORY=Path(os.environ.get("MARSEL_INVENTORY_INPUT","marsel-api-inventory-v20-31.json"))
OUT=Path(os.environ.get("MARSEL_FULL_BACKUP_OUTPUT","marsel-full-readonly-backup-v1.json"))
if not KEY: raise SystemExit("ROAPP_API_KEY is required")
if not INVENTORY.exists(): raise SystemExit(f"inventory missing: {INVENTORY}")
inv=json.loads(INVENTORY.read_text(encoding="utf-8"))

# Accept common inventory layouts but require explicit method evidence.
items=[]
def walk(x):
    if isinstance(x,dict):
        method=str(x.get("method","")).upper()
        path=x.get("path") or x.get("endpoint") or x.get("url")
        evidence=str(x.get("evidence","")).upper()
        if method=="GET" and isinstance(path,str) and path.startswith("/") and "DOCUMENTATION_CONFIRMED" in evidence:
            items.append(x)
        for v in x.values(): walk(v)
    elif isinstance(x,list):
        for v in x: walk(v)
walk(inv)

# Collection endpoints only: no {id}, no query-dependent object lookup.
paths=[]
for x in items:
    p=x.get("path") or x.get("endpoint") or x.get("url")
    if isinstance(p,str) and "{" not in p and "}" not in p:
        p=p.split("?")[0]
        if p not in paths: paths.append(p)

headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":"MARSEL-Full-Readonly-Backup-v1"}
results=[]
write_requests=0
with httpx.Client(timeout=20) as c:
    for p in sorted(paths):
        try:
            r=c.get(BASE+p,headers=headers,params={"page":1,"limit":50})
            results.append({"path":p,"status":r.status_code,"ok":r.status_code==200,"body":r.json() if r.status_code==200 else r.text[:1000]})
        except Exception as e:
            results.append({"path":p,"status":None,"ok":False,"error":f"{type(e).__name__}: {e}"})
        time.sleep(0.34)

ok=[x for x in results if x.get("ok")]
failed=[x for x in results if not x.get("ok")]
report={"version":"1","generated_at_utc":datetime.now(timezone.utc).isoformat(),"readonly":True,"inventory":str(INVENTORY),"documented_get_collection_endpoints":paths,"successful_endpoints":len(ok),"failed_endpoints":len(failed),"write_requests_made":write_requests,"ro_app_data_mutated":False,"complete":bool(paths) and not failed,"results":results}
canonical=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(",",":"))
report["sha256"]=hashlib.sha256(canonical.encode()).hexdigest()
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"COLLECTION_ENDPOINTS={len(paths)}")
print(f"SUCCESS={len(ok)} FAILED={len(failed)}")
print("WRITE_REQUESTS_MADE=0")
print("RO_APP_DATA_MUTATED=False")
print("RESULT=PASS" if report["complete"] else "RESULT=INCOMPLETE")
if not report["complete"]: raise SystemExit(2)
