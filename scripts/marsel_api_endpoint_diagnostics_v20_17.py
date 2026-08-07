#!/usr/bin/env python3
"""MARSEL V20.17 — READ-ONLY endpoint diagnostics.

Diagnoses every concrete GET endpoint from the API inventory and explicitly
classifies non-200 responses. No write HTTP methods are used.
"""
import hashlib, json, os, sys, time
from pathlib import Path
import httpx

BASE=os.environ.get('ROAPP_API_BASE','https://api.roapp.io/v2').rstrip('/')
KEY=os.environ.get('ROAPP_API_KEY','')
TIMEOUT=float(os.environ.get('ROAPP_TIMEOUT','30'))
INVENTORY=Path(os.environ.get('MARSEL_API_INVENTORY_INPUT','marsel-api-inventory-v20-14.json'))
OUT=Path(os.environ.get('MARSEL_ENDPOINT_DIAGNOSTICS_OUTPUT','marsel-endpoint-diagnostics-v20-17.json'))
if not KEY:
    print('ROAPP_API_KEY is required', file=sys.stderr); raise SystemExit(1)
headers={'Authorization':f'Bearer {KEY}','Accept':'application/json','User-Agent':'MARSEL-V20.17-Readonly'}

def concrete_paths():
    if not INVENTORY.exists(): return []
    data=json.loads(INVENTORY.read_text(encoding='utf-8'))
    out=[]
    for op in data.get('operations',[]):
        if 'GET' not in op.get('methods',[]): continue
        for p in op.get('paths',[]):
            if p.startswith('/') and not any(x in p for x in ('{','}',':')): out.append(p)
    return sorted(set(out))

def classify(status):
    if status==200: return 'OK'
    if status in (401,403): return 'AUTH_OR_PERMISSION'
    if status==404: return 'NOT_FOUND'
    if status==405: return 'METHOD_NOT_ALLOWED'
    if status==408: return 'TIMEOUT'
    if status==409: return 'CONFLICT'
    if status==429: return 'RATE_LIMIT'
    if status is not None and 500<=status<=599: return 'SERVER_ERROR'
    if status is not None and 400<=status<=499: return 'CLIENT_ERROR'
    return 'UNKNOWN'

paths=concrete_paths(); results=[]
with httpx.Client(timeout=TIMEOUT) as client:
    for path in paths:
        t=time.time()
        try:
            r=client.get(BASE+path,headers=headers)
            item={'path':path,'http':r.status_code,'classification':classify(r.status_code),'elapsed_s':round(time.time()-t,3)}
            c=r.headers.get('content-type','')
            item['content_type']=c
            if r.status_code!=200:
                item['response_preview']=r.text[:300].replace('\n',' ')
            results.append(item)
        except httpx.TimeoutException as e:
            results.append({'path':path,'http':None,'classification':'TIMEOUT','error':type(e).__name__})
        except Exception as e:
            results.append({'path':path,'http':None,'classification':'CLIENT_EXCEPTION','error':f'{type(e).__name__}: {e}'})
        time.sleep(0.35)

counts={}
for x in results: counts[x['classification']]=counts.get(x['classification'],0)+1
report={'version':'20.17','readonly':True,'write_requests_made':0,'ro_app_data_mutated':False,'api_base':BASE,'endpoints':results,'summary':{'paths':len(results),'classifications':counts,'non_200':sum(x.get('http')!=200 for x in results),'network_errors':sum(x.get('http') is None for x in results)}}
report['report_sha256']=hashlib.sha256(json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('=== MARSEL V20.17 / ENDPOINT DIAGNOSTICS / READ ONLY ===')
for x in results: print(f"{x['path']} HTTP={x.get('http')} CLASS={x['classification']}")
print('SUMMARY='+json.dumps(report['summary'],ensure_ascii=False,sort_keys=True))
print('WRITE_REQUESTS=0'); print('RO_APP_DATA_MUTATED=False'); print(f'REPORT={OUT}'); print(f"REPORT_SHA256={report['report_sha256']}")
if report['summary']['network_errors'] or report['summary']['non_200']:
    print('RESULT=REVIEW_REQUIRED')
else: print('RESULT=PASS')
