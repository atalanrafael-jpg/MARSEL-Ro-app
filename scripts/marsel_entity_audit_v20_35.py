#!/usr/bin/env python3
"""MARSEL V20.35 — read-only entity audit from canonical API evidence."""
from __future__ import annotations
import json, os, re, sys, time
from urllib.request import Request, urlopen
BASE=os.getenv("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.getenv("ROAPP_API_KEY","")
INV=os.getenv("MARSEL_API_INVENTORY_OUTPUT","marsel-unified-api-inventory.json")
OUT=os.getenv("MARSEL_ENTITY_AUDIT_OUTPUT","marsel-entity-audit-v20-35.json")
TIMEOUT=min(int(os.getenv("ROAPP_TIMEOUT","8")),8)
PARAM=re.compile(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>")
TARGETS={"people":"/v2/contacts/people","employees":"/v2/company/employees","locations":"/v2/company/locations","legal_entities":"/v2/company/legal-entities","warehouse":None,"custom_directories":None,"resources":None}
def norm(p): return "/"+p.lstrip("/")[3:] if p.startswith("/v2/") else "/"+p.lstrip("/")
def get(path):
 r=Request(BASE+norm(path),headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":"MARSEL-Audit-V20.35"},method="GET"); t=time.time()
 with urlopen(r,timeout=TIMEOUT) as x: return x.status,x.read().decode("utf-8",errors="replace"),round(time.time()-t,3)
def main():
 if not KEY: print("ROAPP_API_KEY is required",file=sys.stderr); return 2
 inv=json.load(open(INV,encoding="utf-8")); ops=inv.get("operations",[])
 confirmed=[o.get("path") for o in ops if str(o.get("method")).upper()=="GET" and o.get("evidence") in {"DOCUMENTATION_CONFIRMED","OPENAPI_CONFIRMED"} and o.get("path") and not PARAM.search(o.get("path"))]
 results=[]; resolved=[]
 for entity,expected in TARGETS.items():
  candidates=[p for p in confirmed if expected and norm(p)==norm(expected)]
  if not candidates:
   results.append({"entity":entity,"status":"BLOCKED","reason":"No non-parameterized contract-confirmed GET collection route; endpoint will not be guessed."}); continue
  path=candidates[0]
  try:
   status,body,elapsed=get(path); payload=json.loads(body); data=payload.get("data") if isinstance(payload,dict) else None; issues=[]
   if isinstance(data,list) and any(not isinstance(x,dict) or x.get("id") is None for x in data): issues.append("missing_id")
   row={"entity":entity,"path":path,"http":status,"elapsed_s":elapsed,"json_valid":True,"quality_issues":issues,"contract_claim":"DOCUMENTATION_OR_OPENAPI_CONFIRMED"}
   if status==200 and not issues: resolved.append(entity)
   results.append(row)
  except Exception as exc: results.append({"entity":entity,"path":path,"http":None,"error":f"{type(exc).__name__}: {exc}","quality_issues":["request_failed"]})
 blocked=[r for r in results if r.get("status")=="BLOCKED"]; failed=[r for r in results if r.get("http") not in (None,200) or r.get("quality_issues")]
 report={"version":"20.35","readonly":True,"write_requests_made":0,"ro_app_data_mutated":False,"confirmed_collection_audits":results,"verified_live_collection_audits":[r for r in results if r.get("http")==200 and not r.get("quality_issues")],"blocked_entities":blocked,"failed_entities":failed,"resolved_entities":sorted(resolved),"completeness":"ESTABLISHED_FOR_AUDITED_COLLECTIONS" if not blocked and not failed else "NOT_ESTABLISHED","safe_fix_status":"PREPARED_NOT_APPLIED","safety":{"write_methods_used":[],"identifiers_guessed":False}}
 json.dump(report,open(OUT,"w",encoding="utf-8"),ensure_ascii=False,indent=2); print(f"VERIFIED_LIVE_COLLECTIONS_AUDITED={len(report['verified_live_collection_audits'])}"); print(f"BLOCKED_ENTITIES={len(blocked)}"); print(f"FAILED_ENTITIES={len(failed)}"); print(f"RESOLVED_ENTITIES={','.join(sorted(resolved)) or 'NONE'}"); print("WRITE_REQUESTS_MADE=0"); print("RO_APP_DATA_MUTATED=false"); print(f"COMPLETENESS={report['completeness']}"); return 0
if __name__=="__main__": raise SystemExit(main())
