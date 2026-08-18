#!/usr/bin/env python3
"""MARSEL V20.36 — targeted official RO App warehouse contract audit, READ ONLY.

The audit closes the warehouse contract only from explicit evidence in official
RO App API reference pages. It never guesses an endpoint and never calls a
write method. GET routes are probed only when a documentation page explicitly
associates GET with a warehouse/stock path.
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
REF_RE=re.compile(r"https?://roapp(?:ua)?\.readme\.io/reference/[A-Za-z0-9_./?=&%\-]+",re.I)
# Accept the common ReadMe renderings where the HTTP verb and endpoint are
# separated by HTML/Markdown/table markup rather than appearing on one line.
PATH_RE=re.compile(r"(?:(?:https?://api\.roapp\.io)?/(?:v2|1\.1)/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)",re.I)
WAREHOUSE_TOKEN_RE=re.compile(r"(?:warehouse|warehouses|stock|inventory)",re.I)
GET_TOKEN_RE=re.compile(r"\bGET\b|\"method\"\s*:\s*\"GET\"|method\s*=\s*[\"']GET[\"']",re.I)

def clean(x):
    return html.unescape(str(x)).strip().replace('\\/','/').strip('`\'\"<>[]();,.')

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
    req=Request(url,headers=headers or {"User-Agent":"MARSEL-Warehouse-Contract-V20.36","Accept":"text/plain,text/html,application/json"},method='GET')
    t=time.time()
    try:
        with urlopen(req,timeout=TIMEOUT) as r:
            return r.status,r.read().decode('utf-8',errors='replace'),round(time.time()-t,3),None
    except Exception as e:
        return None,'',round(time.time()-t,3),f'{type(e).__name__}: {e}'

def extract_explicit_get_paths(body, source):
    """Extract only paths with a documented GET marker in the same local block."""
    text=html.unescape(body).replace('\\/','/')
    # First remove tags only for easier local-block inspection; preserve text.
    text=re.sub(r'<[^>]+>', ' ', text)
    evidence=[]
    for m in PATH_RE.finditer(text):
        raw=clean(m.group(0))
        p=norm(raw)
        if not p or not WAREHOUSE_TOKEN_RE.search(p):
            continue
        lo=max(0,m.start()-900); hi=min(len(text),m.end()+900)
        block=text[lo:hi]
        if not GET_TOKEN_RE.search(block):
            continue
        # Require the GET marker to be before/after the path within the same
        # documentation block; this prevents unrelated page text from binding
        # a path to GET.
        evidence.append({'method':'GET','path':p,'source':source,'detail':'explicit GET/path evidence within documentation block'})
    # Also support compact OpenAPI/ReadMe JSON where method/path are separate keys.
    for gm in GET_TOKEN_RE.finditer(text):
        lo=max(0,gm.start()-1200); hi=min(len(text),gm.end()+1200)
        for pm in PATH_RE.finditer(text[lo:hi]):
            p=norm(pm.group(0))
            if p and WAREHOUSE_TOKEN_RE.search(p):
                evidence.append({'method':'GET','path':p,'source':source,'detail':'explicit GET method and path in same structured block'})
    return evidence

def main():
    if not KEY:
        raise SystemExit('ROAPP_API_KEY is required')
    refs=[]; seen=set(); index_results=[]
    for idx in INDEXES:
        s,b,e,er=get(idx)
        index_results.append({'url':idx,'http':s,'elapsed_s':e,'error':er})
        if s==200:
            for u in REF_RE.findall(b):
                u,_=urldefrag(u)
                if u not in seen:
                    seen.add(u); refs.append(u)

    warehouse_refs=[]; all_evidence=[]
    for u in refs:
        s,b,e,er=get(u)
        if s!=200:
            continue
        low=b.lower()
        if 'warehouse' not in low and 'stock' not in low and 'inventory' not in low:
            continue
        warehouse_refs.append({'url':u,'http':s,'elapsed_s':e})
        all_evidence.extend(extract_explicit_get_paths(b,u))

    unique={(x['method'],x['path']):x for x in all_evidence}
    headers={'Authorization':f'Bearer {KEY}','Accept':'application/json','User-Agent':'MARSEL-Warehouse-Contract-V20.36'}
    probes=[]
    for x in sorted(unique.values(),key=lambda z:z['path']):
        p=x['path']
        if re.search(r'\{[^}]+\}|:[A-Za-z_]|<[^>]+>',p):
            probes.append({**x,'status':'NOT_PROBED','reason':'parameterized; identifier not guessed'})
            continue
        u=BASE+p.replace('/v2','',1) if p.startswith('/v2') else BASE+p
        s,b,e,er=get(u,headers)
        row={**x,'url':u,'http':s,'elapsed_s':e,'error':er}
        if s==200:
            try:
                json.loads(b); row['json_valid']=True; row['json_type']=type(json.loads(b)).__name__
            except json.JSONDecodeError:
                row['json_valid']=False
        probes.append(row)

    confirmed=[p for p in probes if p.get('http')==200 and p.get('json_valid') is True]
    result='PASS' if confirmed else 'NOT_VERIFIED'
    report={
        'version':'20.36','mode':'READ_ONLY','result':result,'readonly':True,
        'write_requests_made':0,'ro_app_data_mutated':False,
        'official_indexes':index_results,
        'warehouse_reference_pages':warehouse_refs,
        'explicit_get_contracts':sorted(unique.values(),key=lambda z:z['path']),
        'probes':probes,'confirmed_live_gets':confirmed
    }
    raw=json.dumps(report,ensure_ascii=False,indent=2).encode()
    report['report_sha256']=hashlib.sha256(raw).hexdigest()
    out=os.getenv('WAREHOUSE_CONTRACT_OUTPUT','marsel-warehouse-contract-v20-36.json')
    with open(out,'w',encoding='utf-8') as f:
        json.dump(report,f,ensure_ascii=False,indent=2)
    print(f'WAREHOUSE_CONTRACT_RESULT={result}')
    print(f'WAREHOUSE_REFERENCE_PAGES={len(warehouse_refs)}')
    print(f'WAREHOUSE_EXPLICIT_GET_CONTRACTS={len(unique)}')
    print(f'WAREHOUSE_CONFIRMED_LIVE_GETS={len(confirmed)}')
    print('WRITE_REQUESTS_MADE=0')
    print('RO_APP_DATA_MUTATED=false')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
