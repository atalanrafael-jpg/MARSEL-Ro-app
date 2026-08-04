#!/usr/bin/env python3
"""MARSEL V17.2 — metadata-only inspection of live GET responses."""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_BASE=os.environ.get("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.environ.get("ROAPP_API_KEY")
DOCS=os.environ.get("ROAPP_DOCS_INDEX","https://roapp.readme.io/llms.txt")
OUT="marsel-live-api-metadata-v17-2.json"
if not KEY: sys.exit("ROAPP_API_KEY is not configured")

def get(url, api=False):
    h={"User-Agent":"MARSEL-LIVE-AUDIT/17.2","Accept":"application/json,text/plain,*/*"}
    if api: h["Authorization"]=f"Bearer {KEY}"
    try:
        with urlopen(Request(url,headers=h),timeout=45) as r: return r.status,r.read()
    except HTTPError as e: return e.code,e.read()
    except (URLError,TimeoutError,OSError) as e: return None,str(e).encode()

def refs(text):
    return list(dict.fromkeys(re.findall(r'https://roapp\\.readme\\.io/reference/[^)\\s]+',text)))

def specs(text):
    out=[]
    for m in re.finditer(r'```json\\s*(\\{.*?\\})\\s*```',text,re.S):
        try:
            x=json.loads(m.group(1))
            if isinstance(x,dict) and isinstance(x.get('paths'),dict): out.append(x)
        except Exception: pass
    return out

def candidate_urls(page):
    out=[]
    for s in specs(page):
        server=((s.get('servers') or [{}])[0].get('url') or API_BASE).rstrip('/')
        for path,item in (s.get('paths') or {}).items():
            if not isinstance(item,dict) or 'get' not in item or re.search(r'\\{[^}]+\\}',path): continue
            op=item['get']; url=server+('/' if not path.startswith('/') else '')+path
            params=op.get('parameters') or item.get('parameters') or []
            q=[]
            for p in params:
                if p.get('in')=='query' and 'example' in p: q.append((p.get('name'),str(p['example'])))
                elif p.get('in')=='query' and 'default' in (p.get('schema') or {}): q.append((p.get('name'),str(p['schema']['default'])))
            if q: url+='?'+urlencode(q)
            out.append((url,path,op.get('operationId'),op.get('summary')))
    return list(dict.fromkeys(out))

def shape(payload):
    try: x=json.loads(payload.decode('utf-8','replace'))
    except Exception: return {'json':False,'top_type':None,'keys':[],'list_length':None}
    if isinstance(x,dict): return {'json':True,'top_type':'object','keys':sorted(map(str,x.keys()))[:100],'list_length':None}
    if isinstance(x,list): return {'json':True,'top_type':'array','keys':[],'list_length':len(x)}
    return {'json':True,'top_type':type(x).__name__,'keys':[],'list_length':None}

print('=== MARSEL AUDIT V17.2 / LIVE GET RESPONSE METADATA / READ ONLY ===')
st,body=get(DOCS); print(f'DOCS_INDEX_HTTP={st}')
if st!=200: sys.exit(4)
r=refs(body.decode('utf-8','replace')); print(f'REFERENCE_LINKS={len(r)}')
eps=[]
for u in r:
    s,p=get(u)
    if s==200: eps.extend(candidate_urls(p))
eps=list(dict.fromkeys(eps)); print(f'GET_PROBES={len(eps)}')
rows=[]
for url,path,op,summary in eps:
    s,p=get(url,True); meta=shape(p)
    # Never store response bodies or values.
    rows.append({'method':'GET','path':path,'operation_id':op,'summary':summary,'http_status':s,'response_bytes':len(p),'available':bool(s and 200<=s<300),'metadata':meta})
print(f'GET_AVAILABLE={sum(x["available"] for x in rows)}')
print(f'GET_HTTP_ERRORS={sum(x["http_status"] is not None and not 200<=x["http_status"]<300 for x in rows)}')
print('WRITE_REQUESTS_MADE=0')
report={'audit':'MARSEL_AUDIT_V17.2','timestamp_utc':datetime.now(timezone.utc).isoformat(),'readonly':True,'endpoints':rows,'safety':{'write_requests_made':False,'response_bodies_stored':False,'data_mutated':False}}
with open(OUT,'w',encoding='utf-8') as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(f'REPORT={OUT}')
print('RESULT=READ_ONLY; GET REQUESTS ONLY; RESPONSE BODIES NOT STORED; NO RO APP DATA CREATED, UPDATED OR DELETED')
