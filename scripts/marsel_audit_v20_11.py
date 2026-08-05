#!/usr/bin/env python3
"""MARSEL V20.11 — canonical endpoint and pagination mapping, READ ONLY."""
import json, os, sys, time, hashlib
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError

BASE=os.environ.get('ROAPP_API_BASE','https://api.roapp.io/v2').rstrip('/')
KEY=os.environ.get('ROAPP_API_KEY','')
OUT=os.environ.get('MARSEL_AUDIT_OUTPUT','marsel-api-resolution-v20-11.json')
TIMEOUT=int(os.environ.get('ROAPP_TIMEOUT','30'))
MAX_PAGES=int(os.environ.get('MARSEL_MAX_PAGES','100'))
PAGE_SIZE=int(os.environ.get('MARSEL_PAGE_SIZE','100'))
TARGETS=[
 ('orders','/orders'),('services','/catalog/services'),('products','/catalog/products'),('bundles','/catalog/bundles'),
 ('inquiries','/inquiries'),('bookings','/bookings'),('estimates','/estimates'),('invoices','/invoices')]
VARIANTS=[
 {}, {'page':1,'page_size':PAGE_SIZE},{'page':1,'limit':PAGE_SIZE},{'offset':0,'limit':PAGE_SIZE},
 {'page':1,'size':PAGE_SIZE},{'page':0,'page_size':PAGE_SIZE},{'offset':0,'page_size':PAGE_SIZE}
]

def get(path,params):
    url=BASE+path
    if params: url+='?'+urlencode(params)
    req=Request(url,headers={'Authorization':f'Bearer {KEY}','Accept':'application/json','User-Agent':'MARSEL-Audit-V20.11'},method='GET')
    t=time.time()
    try:
        with urlopen(req,timeout=TIMEOUT) as r:
            raw=r.read().decode('utf-8'); return {'http':r.status,'elapsed_s':round(time.time()-t,3),'json':json.loads(raw),'error':None}
    except HTTPError as e:
        return {'http':e.code,'elapsed_s':round(time.time()-t,3),'json':None,'error':e.read().decode('utf-8',errors='replace')[:2000]}
    except (URLError,TimeoutError,ValueError) as e:
        return {'http':None,'elapsed_s':round(time.time()-t,3),'json':None,'error':str(e)}

def rows(x):
    if isinstance(x,list): return x
    if not isinstance(x,dict): return []
    for k in ('data','items','results','orders','services','products','bundles','inquiries','bookings','estimates','invoices'):
        if isinstance(x.get(k),list): return x[k]
    for k in ('data','result'):
        if isinstance(x.get(k),dict):
            r=rows(x[k])
            if r:return r
    return []

def ident(x):
    return x.get('id',x.get('ID',x.get('uuid'))) if isinstance(x,dict) else None

def page_hint(x):
    if not isinstance(x,dict): return None
    for k in ('has_next','hasNext'):
        if isinstance(x.get(k),bool): return x[k]
    for k in ('next','next_page','nextPage'):
        if k in x:return bool(x[k])
    return None

def main():
    if not KEY: print('ROAPP_API_KEY is required',file=sys.stderr); return 2
    report={'version':'20.11','readonly':True,'write_requests_made':0,'ro_app_data_mutated':False,'method_policy':{'allowed':['GET'],'forbidden':['POST','PUT','PATCH','DELETE']},'targets':[]}
    for entity,path in TARGETS:
        variants=[]
        for p in VARIANTS:
            r=get(path,p); rs=rows(r['json']) if r['http']==200 else []
            variants.append({'params':p,'http':r['http'],'elapsed_s':r['elapsed_s'],'records':len(rs),'ids_sample':[ident(x) for x in rs[:5]],'page_hint':page_hint(r['json']),'error':r['error']})
        successes=[v for v in variants if v['http']==200]
        nonempty=[v for v in successes if v['records']>0]
        # Determine best candidate by largest observed page and then explicit pagination parameters.
        best=max(nonempty or successes or variants,key=lambda v:(v['records'],len(v['params'])))
        p=best['params']; seen=[]; page_results=[]; repeated=False
        if best['http']==200 and p is not None:
            base={k:v for k,v in p.items() if k not in ('page','offset')}
            for page in range(1,MAX_PAGES+1):
                q=dict(base); q['page']=page
                r=get(path,q); rs=rows(r['json']) if r['http']==200 else []
                ids=[ident(x) for x in rs]
                sig=hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest() if ids else None
                repeated=sig in seen if sig else False
                if sig:seen.append(sig)
                page_results.append({'page':page,'params':q,'http':r['http'],'records':len(rs),'first_ids':ids[:5],'last_ids':ids[-5:],'page_hint':page_hint(r['json']),'repeated_page':repeated,'error':r['error']})
                if r['http']!=200 or not rs or repeated or page_hint(r['json']) is False: break
        report['targets'].append({'entity':entity,'endpoint':path,'variants':variants,'selected_variant':best,'pagination_probe':page_results})
    report['summary']={'targets':len(TARGETS),'readonly':True,'write_requests_made':0}
    with open(OUT,'w',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print('=== MARSEL AUDIT V20.11 / ENDPOINT RESOLUTION / READ ONLY ===')
    print(f'TARGETS={len(TARGETS)}')
    print(f'VARIANTS_TESTED={len(TARGETS)*len(VARIANTS)}')
    print(f'WRITE_REQUESTS_MADE=0')
    print(f'REPORT={OUT}')
    print('RESULT=READ_ONLY; V20.11; NO RO APP DATA CREATED, UPDATED OR DELETED')
    return 0
if __name__=='__main__':raise SystemExit(main())
