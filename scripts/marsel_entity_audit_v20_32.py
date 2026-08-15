#!/usr/bin/env python3
"""MARSEL V20.34 — evidence-gated entity/data-quality audit.

READ ONLY. Never guesses collection endpoints, identifiers, or write methods.
The audit may probe only collection paths already verified by a canonical
READ-ONLY data-quality component. This deliberately separates two claims:
(1) a route is safe to probe because another canonical audit verified it live;
(2) the route is contract-confirmed by official documentation. This script
must never promote the first claim into the second.

V20.34 also reuses the already verified products/services/orders collection
paths instead of redundantly treating products and services as blocked.
Parameterized entities remain BLOCKED until their collection endpoint is
explicitly evidenced; identifiers are never guessed.
"""
from __future__ import annotations
import json, os, sys, time
from urllib.request import Request, urlopen

BASE=os.getenv("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.getenv("ROAPP_API_KEY","")
TIMEOUT=min(int(os.getenv("ROAPP_TIMEOUT","8")),8)
OUT=os.getenv("MARSEL_ENTITY_AUDIT_OUTPUT","marsel-entity-audit-v20-34.json")

# These paths are already exercised by the canonical READ-ONLY data-quality
# audit. They are safe-live evidence, not a claim of complete API contract.
VERIFIED_LIVE_COLLECTIONS={
    "orders":"/orders",
    "products":"/catalog/products",
    "services":"/catalog/services",
}
REQUIRED_ENTITIES=("clients","products","services","warehouse","employees","locations","legal_entities","custom_directories","resources")


def normalize_request_path(path: str) -> str:
    p = "/" + path.lstrip("/")
    base_path = "/v2"
    if BASE.endswith(base_path) and p == base_path:
        return "/"
    if BASE.endswith(base_path) and p.startswith(base_path + "/"):
        return p[len(base_path):]
    return p


def get(path):
    request_path = normalize_request_path(path)
    req=Request(BASE+request_path,headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":"MARSEL-Audit-V20.34"},method="GET")
    started=time.time()
    with urlopen(req,timeout=TIMEOUT) as r:
        body=r.read().decode("utf-8",errors="replace")
        return r.status, body, round(time.time()-started,3), request_path


def quality(entity, payload):
    issues=[]
    data=payload.get("data") if isinstance(payload,dict) else None
    if isinstance(data,list):
        ids=[x.get("id") for x in data if isinstance(x,dict)]
        if any(x is None for x in ids): issues.append("missing_id")
        seen=set(); dup=[]
        for x in ids:
            if x in seen: dup.append(x)
            seen.add(x)
        if dup: issues.append("duplicate_id")
    return issues


def main():
    if not KEY:
        print("ROAPP_API_KEY is required",file=sys.stderr); return 2
    results=[]
    for entity,path in VERIFIED_LIVE_COLLECTIONS.items():
        try:
            status,body,elapsed,request_path=get(path)
            try: payload=json.loads(body); valid=True
            except Exception: payload={}; valid=False
            results.append({
                "entity":entity,
                "path":path,
                "request_path":request_path,
                "http":status,
                "elapsed_s":elapsed,
                "json_valid":valid,
                "quality_issues":quality(entity,payload) if valid else ["invalid_json"],
                "evidence_source":"canonical_read_only_data_quality",
                "contract_claim":"NOT_ESTABLISHED_BY_THIS_AUDIT"
            })
        except Exception as e:
            results.append({
                "entity":entity,
                "path":path,
                "request_path":normalize_request_path(path),
                "http":None,
                "error":f"{type(e).__name__}: {e}",
                "quality_issues":["request_failed"],
                "evidence_source":"canonical_read_only_data_quality",
                "contract_claim":"NOT_ESTABLISHED_BY_THIS_AUDIT"
            })
    verified={r["entity"] for r in results if r.get("http") == 200 and not r.get("quality_issues")}
    blocked=[{
        "entity":e,
        "status":"BLOCKED",
        "reason":"No safe collection endpoint is currently evidenced by the canonical live audit; endpoint or identifier will not be guessed."
    } for e in REQUIRED_ENTITIES if e not in verified]
    report={
        "version":"20.34",
        "readonly":True,
        "write_requests_made":0,
        "ro_app_data_mutated":False,
        "verified_live_collection_audits":results,
        "confirmed_collection_audits":results,
        "blocked_entities":blocked,
        "completeness":"NOT_ESTABLISHED",
        "safe_fix_status":"PREPARED_NOT_APPLIED",
        "safety":{"write_methods_used":[],"identifiers_guessed":False},
        "contract_scope_note":"Live verification is not equivalent to official API contract confirmation; API completeness remains NOT_ESTABLISHED."
    }
    with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2); f.write("\n")
    print(f"VERIFIED_LIVE_COLLECTIONS_AUDITED={len(results)}")
    print(f"BLOCKED_ENTITIES={len(blocked)}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    print("COMPLETENESS=NOT_ESTABLISHED")
    return 0

if __name__=="__main__": raise SystemExit(main())
