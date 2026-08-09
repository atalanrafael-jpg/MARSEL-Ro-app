#!/usr/bin/env python3
"""MARSEL V21.1 — offline semantic duplicate review.

Consumes only a verified read-only entity-inventory artifact. It never calls
RO App and never performs mutations. Candidate records are compared using the
fields captured by V20.37; no candidate becomes a confirmed duplicate merely
because a title/code/SKU matches.
"""
from __future__ import annotations
import hashlib,json,os
from pathlib import Path
from typing import Any

INPUT=Path(os.environ.get("MARSEL_ENTITY_INVENTORY_INPUT","marsel-entity-inventory-v20-19.json"))
OUTPUT=Path(os.environ.get("MARSEL_SEMANTIC_REVIEW_OUTPUT","marsel-semantic-review-v21-1.json"))


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()


def load()->dict[str,Any]: return json.loads(INPUT.read_text(encoding="utf-8"))


def classify_endpoint(endpoint:str)->str:
    if endpoint.startswith("/catalog/products"): return "PRODUCT"
    if endpoint.startswith("/catalog/services"): return "SERVICE"
    if endpoint.endswith("/categories"): return "CATEGORY"
    if "employee" in endpoint.lower() or "staff" in endpoint.lower(): return "EMPLOYEE"
    return "OTHER"


def flatten_fields(value:Any,prefix="",out=None):
    out={} if out is None else out
    if isinstance(value,dict):
        for k,v in value.items():
            p=f"{prefix}.{k}" if prefix else str(k)
            flatten_fields(v,p,out)
    elif isinstance(value,list):
        out[prefix]=f"[list:{len(value)}]"
    else:
        out[prefix]=value
    return out


def norm(v:Any):
    if isinstance(v,str): return " ".join(v.casefold().split())
    return v


def compare_snapshots(items):
    if len(items)<2: return {"decision":"INSUFFICIENT_DATA","differences":[]}
    flattened=[flatten_fields(x.get("fields") or {}) for x in items]
    keys=sorted(set().union(*(x.keys() for x in flattened)))
    differences=[]
    identical=[]
    for key in keys:
        vals=[norm(x.get(key)) for x in flattened]
        if len(set(json.dumps(v,ensure_ascii=False,sort_keys=True,default=str) for v in vals))==1:
            identical.append(key)
        else:
            differences.append({"field":key,"values":vals})
    return {"decision":"MANUAL_REVIEW_REQUIRED","identical_fields":identical,"differences":differences}


def main()->int:
    d=load()
    assert d.get("version") in ("20.36","20.37"), "unexpected evidence version"
    assert d.get("mode")=="READ_ONLY"
    assert d.get("write_requests")==0
    assert d.get("ro_app_data_mutated") is False
    assert d.get("parameterized_identifiers_guessed") is False
    assert d.get("audit_status")=="PASS"

    candidates=d.get("duplicate_candidates") or {}
    snapshots=d.get("candidate_record_snapshots") or []
    by_id={(x.get("endpoint"),str(x.get("id"))):x for x in snapshots}
    review=[]
    for endpoint,groups in candidates.items():
        for group in groups or []:
            ids=[str(x) for x in (group.get("ids") or [])]
            records=[by_id.get((endpoint,i)) for i in ids]
            records=[x for x in records if x]
            comparison=compare_snapshots(records)
            review.append({
                "endpoint":endpoint,
                "entity_type":classify_endpoint(endpoint),
                "candidate_key":group.get("key") or [],
                "ids":ids,
                "id_count":len(ids),
                "record_snapshots_available":len(records),
                "comparison":comparison,
                "classification":"MANUAL_REVIEW_REQUIRED",
                "reason":"candidate grouping is not proof of duplicate business records",
                "safe_next_check":"verify business identity, SKU/article, category, active/archive state, price, unit, stock, cost and relationship references before any merge/delete decision",
            })

    by_type={}
    for item in review:
        t=item["entity_type"]; by_type[t]=by_type.get(t,0)+1
    report={
        "version":"21.1",
        "status":"PASS",
        "mode":"READ_ONLY_OFFLINE",
        "source":str(INPUT),
        "source_sha256":sha256(INPUT),
        "source_evidence_version":d.get("version"),
        "source_audit_status":d.get("audit_status"),
        "source_metrics":{
            "collection_paths_considered":d.get("collection_paths_considered"),
            "collection_pages_fetched":sum(x.get("pages_fetched",0) for x in (d.get("collection_stats") or {}).values()),
            "collection_records_fetched":sum(x.get("records_fetched",0) for x in (d.get("collection_stats") or {}).values()),
            "real_identifiers_extracted":d.get("real_identifiers_extracted"),
            "detail_probes":len(d.get("detail_results") or []),
            "candidate_snapshot_count":d.get("candidate_snapshot_count",len(snapshots)),
        },
        "duplicate_candidate_groups":len(review),
        "candidate_groups_by_entity_type":by_type,
        "duplicate_candidates":review,
        "confirmed_duplicates":0,
        "writes_performed":0,
        "ro_app_data_mutated":False,
        "next_gate":"field-level comparison is now captured; next gate is relationship/orphan analysis and backup before any production write",
    }
    OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    report["report_sha256"]=sha256(OUTPUT)
    OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("=== MARSEL V21.1 SEMANTIC REVIEW / READ ONLY ===")
    print("STATUS=PASS")
    print(f"DUPLICATE_CANDIDATE_GROUPS={len(review)}")
    print(f"BY_ENTITY_TYPE={json.dumps(by_type,sort_keys=True)}")
    print(f"SNAPSHOTS_AVAILABLE={len(snapshots)}")
    print("CONFIRMED_DUPLICATES=0")
    print("WRITES_PERFORMED=0")
    print("RO_APP_DATA_MUTATED=False")
    print(f"REPORT_SHA256={report['report_sha256']}")
    return 0

if __name__=="__main__": raise SystemExit(main())