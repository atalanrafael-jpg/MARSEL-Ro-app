#!/usr/bin/env python3
"""MARSEL V20.36 — targeted official RO App warehouse contract audit, READ ONLY.

Purpose: close the warehouse contract only from explicit evidence in the official
RO App ReadMe indexes/reference pages. No endpoint is guessed and no write method
is called. GET collection and stock routes are probed only when the documentation
explicitly binds GET to the path.
"""
from __future__ import annotations
import hashlib, html, json, os, re, time
from urllib.parse import urljoin, urldefrag, urlparse
from urllib.request import Request, urlopen

KEY=os.getenv("ROAPP_API_KEY","")
BASE=os.getenv("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
TIMEOUT=8
MIN_INTERVAL=0.34
INDEXES=("https://roapp.readme.io/llms.txt","https://roappua.readme.io/llms.txt")
METHOD_PATH_RE=re.compile(r"\bGET\b\s*(?:[:\-]\s*)?(https?://api\.roapp\.io[^\s<>'\"`]+|/(?:v2|1\.1)(?:/[^\s<>'\"`]*)?)",re.I)
PATH_GET_RE=re.compile(r"\bGET\b[^\n]{0,220}(?:(/v2/(?:warehouse|warehouses|stock)[A-Za-z0-9_./{}:\-?=&\[\]$%]*)|(https?://api\.roapp\.io/(?:v2|1\.1)/(?:warehouse|warehouses|stock)[A-Za-z0-9_./{}:\-?=&\[\]$%]*))",re.I)
REF_RE=re.compile(r"https?://roapp(?:ua)?\.readme\.io/reference/[A-Za-z0-9_./?=&%\-]+",re.I)

def clean(x): return html.unescape(str(x)).strip().replace('\\/','/').strip('`\'\"<>[]();,.')
def norm(x):
    x=clean(x)
    if x.startswith('http'):
        u=urlparse(x)
        if u.netloc.lower()!='api.roapp.io': return None
        x=u.path
    if x.startswith('/v2/'): return x
    if x.startswith('/1.1/'): return x
    return None

def get(url,headers=None):
    time.sleep(MIN_INTERVAL)
    req=Request(url,headers=headers or {"User-Agent":"MARSEL-Warehouse-Contract-V20.36","Accept":"text/plain,text/html,text/markdown"},method='GET')
    t=time.time()
    try:
        with urlopen(req,timeout=TIMEOUT) as r: return r.status,r.read().decode('utf-8',errors='replace'),round(time.time()-t,3),None
    except Exception as e: return None,'',round(time.time()-t,3),f'{type(e).__name__}: {e}'

def main():
    if not KEY: raise SystemExit('ROAPP_API_KEY is required')
    refs=[];seen=set(); index_results=[]
    for idx in INDEXES:
        s,b,e,er=get(idx)
        index_results.append({'url':idx,'http':s,'elapsed_s':e,'error':er})
        if s==200:
            for u in REF_RE.findall(b):
                u,_=urldefrag(u)
                if u not in seen: seen.add(u); refs.append(u)
    warehouse_refs=[]; all_evidence=[]
    for u in refs:
        s,b,e,er=get(u)
        if s!=200: continue
        low=b.lower()
        if 'warehouse' not in low and 'stock' not in low: continue
        warehouse_refs.append({'url':u,'http':s,'elapsed_s':e})
        for m in METHOD_PATH_RE.finditer(b):
            p=norm(m.group(1) or m.group(2))
            if p and any(x in p.lower() for x in ('warehouse','warehouses','stock')):
                all_evidence.append({'method':'GET','path':p,'source':u,'detail':'explicit GET/path evidence'})
        for m in PATH_GET_RE.finditer(b):
            p=norm(m.group(1) or m.group(2))
            if p: all_evidence.append({'method':'GET','path':p,'source':u,'detail':'explicit same-line GET/path evidence'})
    unique={ (x['method'],x['path']):x for x in all_evidence }
    headers={'Authorization':f'Bearer {KEY}','Accept':'application/json','User-Agent':'MARSEL-Warehouse-Contract-V20.36'}
    probes=[]
    for x in sorted(unique.values(),key=lambda z:z['path']):
        p=x['path']
        if re.search(r'\{[^}]+\}|:[A-Za-z_]|<[^>]+>',p):
            probes.append({**x,'status':'NOT_PROBED','reason':'parameterized; identifier not guessed'}); continue
        u=BASE+p.replace('/v2','',1) if p.startswith('/v2') else BASE+p
        s,b,e,er=get(u,headers)
        row={**x,'url':u,'http':s,'elapsed_s':e,'error':er}
        if s==200:
            try: row['json_valid']=True; row['json_type']=type(json.loads(b)).__name__
            except json.JSONDecodeError: row['json_valid']=False
        probes.append(row)
    confirmed=[p for p in probes if p.get('http')==200 and p.get('json_valid') is True]
    result='PASS' if confirmed else 'NOT_VERIFIED'
    report={'version':'20.36','mode':'READ_ONLY','result':result,'readonly':True,'write_requests_made':0,'ro_app_data_mutated':False,'official_indexes':index_results,'warehouse_reference_pages':warehouse_refs,'explicit_get_contracts':sorted(unique.values(),key=lambda z:z['path']),'probes':probes,'confirmed_live_gets':confirmed}
    raw=json.dumps(report,ensure_ascii=False,indent=2).encode(); report['report_sha256']=hashlib.sha256(raw).hexdigest()
    out=os.getenv('WAREHOUSE_CONTRACT_OUTPUT','marsel-warehouse-contract-v20-36.json'); json.dump(report,open(out,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    print(f'WAREHOUSE_CONTRACT_RESULT={result}')
    print(f'WAREHOUSE_REFERENCE_PAGES={len(warehouse_refs)}')
    print(f'WAREHOUSE_EXPLICIT_GET_CONTRACTS={len(unique)}')
    print(f'WAREHOUSE_CONFIRMED_LIVE_GETS={len(confirmed)}')
    print('WRITE_REQUESTS_MADE=0')
    print('RO_APP_DATA_MUTATED=false')
    return 0
if __name__=='__main__': raise SystemExit(main())
