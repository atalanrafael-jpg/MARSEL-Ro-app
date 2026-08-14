#!/usr/bin/env python3
"""MARSEL V20.32 — evidence-gated entity/data-quality audit.

READ ONLY. Never guesses collection endpoints, identifiers, or write methods.
The audit may probe only endpoints explicitly confirmed by the documentation
inventory. If the documentation does not establish a collection endpoint for
an entity, that entity is reported as BLOCKED rather than guessed.
"""
from __future__ import annotations
import json, os, re, sys, time
from urllib.request import Request, urlopen

BASE=os.getenv("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.getenv("ROAPP_API_KEY","")
TIMEOUT=min(int(os.getenv("ROAPP_TIMEOUT","8")),8)
OUT=os.getenv("MARSEL_ENTITY_AUDIT_OUTPUT","marsel-entity-audit-v20-32.json")

# Only endpoints explicitly confirmed by V20.31 are eligible. Collection
# endpoints for clients/products/services/etc. are deliberately absent until
# documentation evidence establishes their exact paths.
CONFIRMED_COLLECTIONS={"orders":"/v2/orders"}
REQUIRED_ENTITIES=("clients","products","services","warehouse","employees","locations","legal_entities","custom_directories","resources")


def get(path):
    req=Request(BASE+path,headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":"MARSEL-Audit-V20.32"},method="GET")
    started=time.time()
    with urlopen(req,timeout=TIMEOUT) as r:
        body=r.read().decode("utf-8",errors="replace")
        return r.status, body, round(time.time()-started,3)


def quality(entity, payload):
    issues=[]
    data=payload.get("data") if isinstance(payload,dict) else None
    if isinstance(data,list):
        ids=[x.get("id") for x in data if isinstance(x,dict)]
        if any(x is None for x in ids): issues.append("missing_id")
        seen=set()
        dup=[]
        for x in ids:
            if x in seen: dup.append(x)
            seen.add(x)
        if dup: issues.append("duplicate_id")
        if isinstance(payload.get("paging"),dict):
            pass
    return issues


def main():
    if not KEY:
        print("ROAPP_API_KEY is required",file=sys.stderr); return 2
    results=[]
    for entity,path in CONFIRMED_COLLECTIONS.items():
        try:
            status,body,elapsed=get(path)
            try: payload=json.loads(body); valid=True
            except Exception: payload={}; valid=False
            results.append({"entity":entity,"path":path,"http":status,"elapsed_s":elapsed,"json_valid":valid,"quality_issues":quality(entity,payload) if valid else ["invalid_json"]})
        except Exception as e:
            results.append({"entity":entity,"path":path,"http":None,"error":f"{type(e).__name__}: {e}","quality_issues":["request_failed"]})
    blocked=[{"entity":e,"status":"BLOCKED","reason":"No explicit collection endpoint confirmed by current API evidence; endpoint or identifier will not be guessed."} for e in REQUIRED_ENTITIES if e not in CONFIRMED_COLLECTIONS]
    report={"version":"20.32","readonly":True,"write_requests_made":0,"ro_app_data_mutated":False,"confirmed_collection_audits":results,"blocked_entities":blocked,"completeness":"NOT_ESTABLISHED","safe_fix_status":"PREPARED_NOT_APPLIED","safety":{"write_methods_used":[],"identifiers_guessed":False}}
    with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2); f.write("\n")
    print(f"CONFIRMED_COLLECTIONS_AUDITED={len(results)}")
    print(f"BLOCKED_ENTITIES={len(blocked)}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    print("COMPLETENESS=NOT_ESTABLISHED")
    return 0

if __name__=="__main__": raise SystemExit(main())
