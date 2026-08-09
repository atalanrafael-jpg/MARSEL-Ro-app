#!/usr/bin/env python3
"""MARSEL V20.33 — Live GET-only API probe.

The API inventory may contain documented non-GET operations for inventory
completeness. This probe never executes them. Only concrete GET paths are
probed; parameterized identifiers are never guessed. HTTP 4xx/5xx responses
are recorded as endpoint evidence and do not fail the audit. The probe fails
only for transport/execution errors or an actual write request.
"""
from __future__ import annotations
import hashlib,json,os,re,sys,time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request,urlopen
from urllib.parse import urlsplit

VERSION="20.33"
INVENTORY=Path(os.environ.get("MARSEL_API_INVENTORY_INPUT","marsel-api-inventory-v20-29.json"))
OUT=Path(os.environ.get("MARSEL_LIVE_PROBE_OUTPUT","marsel-live-probe-v20-29.json"))
BASE=os.environ.get("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.environ.get("ROAPP_API_KEY","")
TIMEOUT=min(int(os.environ.get("ROAPP_TIMEOUT","15")),20)
MIN_INTERVAL=max(float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL","0.34")),0.1)
PARAM_RE=re.compile(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>")
WRITE_METHODS={"POST","PUT","PATCH","DELETE"}
_last=0.0

def digest(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for c in iter(lambda:f.read(1024*1024),b""):h.update(c)
 return h.hexdigest()

def wait_rate_limit():
 global _last
 d=MIN_INTERVAL-(time.monotonic()-_last)
 if d>0:time.sleep(d)

def build_url(path):
 bp=urlsplit(BASE); base_path=bp.path.rstrip("/"); np="/"+path.lstrip("/")
 fp=np if base_path and (np==base_path or np.startswith(base_path+"/")) else base_path+np
 return bp._replace(path=fp).geturl()

def probe(url):
 global _last
 wait_rate_limit()
 req=Request(url,headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":f"MARSEL-Audit-V{VERSION}"},method="GET")
 started=time.time();_last=time.monotonic()
 try:
  with urlopen(req,timeout=TIMEOUT) as r:
   body=r.read().decode("utf-8",errors="replace")
   return {"http":r.status,"elapsed_s":round(time.time()-started,3),"content_type":r.headers.get("Content-Type",""),"body":body[:2_000_000]}
 except HTTPError as e:
  body=e.read().decode("utf-8",errors="replace")[:10000]
  return {"http":e.code,"elapsed_s":round(time.time()-started,3),"content_type":e.headers.get("Content-Type","") if e.headers else "","body":body,"error":"HTTPError"}
 except Exception as e:
  return {"http":None,"elapsed_s":round(time.time()-started,3),"content_type":"","body":"","error":f"{type(e).__name__}: {e}"}

def shape(v,d=0):
 if d>=3:return "..."
 if isinstance(v,dict):return {k:shape(v[k],d+1) for k in sorted(v)[:100]}
 if isinstance(v,list):return {"type":"array","items":shape(v[0],d+1) if v else "empty"}
 return "null" if v is None else type(v).__name__

def main():
 if not KEY:return print("ROAPP_API_KEY is required",file=sys.stderr) or 2
 if not INVENTORY.exists():return print(f"inventory not found: {INVENTORY}",file=sys.stderr) or 1
 try:inv=json.loads(INVENTORY.read_text(encoding="utf-8"))
 except Exception as e:return print(f"invalid inventory JSON: {e}",file=sys.stderr) or 1
 ops=inv.get("operations",[]); probes=[]; execution_errors=[];seen=set(); skipped_non_get=[]
 for op in ops:
  method=str(op.get("method","")).upper();path=str(op.get("path",""))
  if method in WRITE_METHODS:
   skipped_non_get.append({"method":method,"path":path,"reason":"documented_non_get_operation_not_executed"})
   continue
  if method!="GET":
   skipped_non_get.append({"method":method,"path":path,"reason":"non_get_operation_not_executed"})
   continue
  if not path or PARAM_RE.search(path):
   probes.append({"method":"GET","path":path,"status":"NOT_PROBED","reason":"parameterized_or_empty_path"});continue
  if path in seen:continue
  seen.add(path);url=build_url(path);r=probe(url)
  item={"method":"GET","path":path,"url":url,"http":r.get("http"),"elapsed_s":r.get("elapsed_s"),"content_type":r.get("content_type"),"error":r.get("error")}
  body=r.get("body","")
  if r.get("http") in {200,201,202,204}:
   if body.strip():
    try:
     p=json.loads(body);item.update({"json_valid":True,"json_type":type(p).__name__,"shape":shape(p)})
     if isinstance(p,dict):item["top_level_keys"]=sorted(p.keys())[:100]
     elif isinstance(p,list):item["array_length"]=len(p)
    except json.JSONDecodeError:
     item.update({"json_valid":False,"error":"successful HTTP response is not valid JSON"});execution_errors.append(f"non-JSON success: GET {path}")
  else:
   item.update({"json_valid":None,"classification":"HTTP_ERROR_OR_UNAVAILABLE","error_body_sample":body[:500] if body else r.get("error")})
   if r.get("http") is None:execution_errors.append(f"transport error: GET {path}: {r.get('error')}")
  probes.append(item)
 successful=[p for p in probes if p.get("http") in {200,201,202,204}]
 valid=[p for p in successful if p.get("json_valid") is True]
 notp=[p for p in probes if p.get("status")=="NOT_PROBED"]
 http_errors=[p for p in probes if isinstance(p.get("http"),int) and p["http"]>=400]
 status="PASS" if not execution_errors and probes else "FAIL"
 report={"version":VERSION,"status":status,"readonly":True,"method_policy":{"allowed":["GET"],"blocked":sorted(WRITE_METHODS)},"inventory_sha256":digest(INVENTORY),"metrics":{"inventory_operations":len(ops),"get_paths_probed":len([p for p in probes if p.get("status")!="NOT_PROBED"]),"successful_responses":len(successful),"valid_json_responses":len(valid),"parameterized_not_probed":len(notp),"http_error_responses":len(http_errors),"transport_errors":sum(1 for p in probes if p.get("http") is None),"non_get_operations_skipped":len(skipped_non_get)},"probes":probes,"skipped_non_get_operations":skipped_non_get,"contract_state":{"live_response_schema":"CHECKED_FOR_PROBED_CONCRETE_GETS","field_types":"OBSERVED_FOR_PROBED_JSON","pagination_behavior":"OBSERVED_ONLY_WHEN_RETURNED","http_error_shapes":"OBSERVED_ONLY_WHEN_RETURNED","parameterized_identifiers_guessed":False,"completeness_claim":"NOT_ESTABLISHED"},"safety":{"write_requests_made":0,"ro_app_data_mutated":False},"errors":execution_errors,"generated_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
 OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8");report["report_sha256"]=digest(OUT);OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print(f"V{VERSION}_LIVE_PROBE={status}");print(f"SUCCESSFUL_RESPONSES={len(successful)}");print(f"VALID_JSON_RESPONSES={len(valid)}");print(f"PARAMETERIZED_NOT_PROBED={len(notp)}");print(f"HTTP_ERROR_RESPONSES={len(http_errors)}");print(f"NON_GET_OPERATIONS_SKIPPED={len(skipped_non_get)}");print("WRITE_REQUESTS_MADE=0");print("RO_APP_DATA_MUTATED=false");print(f"REPORT_SHA256={report['report_sha256']}")
 return 0 if status=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())
