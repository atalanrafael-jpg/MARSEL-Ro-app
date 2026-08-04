#!/usr/bin/env python3
"""MARSEL V16.2 — title-driven official API catalog, read-only, stdlib only."""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE=os.environ.get('ROAPP_API_BASE','https://api.roapp.io/v2').rstrip('/')
KEY=os.environ.get('ROAPP_API_KEY')
DOCS_INDEX=os.environ.get('ROAPP_DOCS_INDEX','https://roapp.readme.io/llms.txt')
OUT=os.environ.get('MARSEL_AUDIT_OUT','marsel-api-master-inventory-v16-2.json')
TIMEOUT=int(os.environ.get('ROAPP_TIMEOUT','45'))
UA='Mozilla/5.0 (compatible; MARSEL-AUDIT/16.2; +https://github.com/atalanrafael-jpg/Ro-app)'

if not KEY:
    print('ERROR: ROAPP_API_KEY is not configured'); sys.exit(2)

def fetch(url):
    req=Request(url, headers={'User-Agent':UA,'Accept':'text/plain, text/markdown, text/html, */*'})
    try:
        with urlopen(req, timeout=TIMEOUT) as r: return r.status, r.read()
    except HTTPError as e: return e.code, e.read()
    except (URLError, TimeoutError, OSError) as e: return None, str(e).encode()

def catalog_links(text):
    out=[]; seen=set()
    for m in re.finditer(r'\[([^\]]+)\]\((https://roapp\.readme\.io/reference/[^)]+)\)', text or ''):
        title=m.group(1).strip(); url=m.group(2).strip()
        if url not in seen:
            seen.add(url); out.append({'title':title,'url':url})
    return out

def classify(title):
    t=title.lower().strip()
    if t.startswith(('get ','getting started','webhooks guide','mcp')): return 'GET' if t.startswith('get ') else 'DOC'
    if t.startswith(('create ','add ','change ','update ','merge ')): return 'WRITE'
    if t.startswith('delete '): return 'DELETE'
    return 'UNKNOWN'

def entity(title):
    t=re.sub(r"^(Get|Create|Add|Delete|Update|Change|Merge)\s+",'',title,flags=re.I)
    t=re.sub(r"\s+(by\s+(ID|Id)|by\s+id)$",'',t,flags=re.I)
    t=re.sub(r"\s+Items?$",'',t,flags=re.I)
    return t.strip()

print('=== MARSEL AUDIT V16.2 / OFFICIAL TITLE CATALOG / READ ONLY ===')
print(f'BASE={BASE}'); print(f'DOCS_INDEX={DOCS_INDEX}')
status, body=fetch(DOCS_INDEX); print(f'DOCS_INDEX_HTTP={status}')
if status != 200:
    print('RESULT=READ_ONLY; DOCUMENTATION INDEX UNAVAILABLE; NO RO APP DATA CREATED, UPDATED OR DELETED'); sys.exit(4)
text=body.decode('utf-8','replace')
refs=catalog_links(text)
print(f'REFERENCE_LINKS={len(refs)}')
entries=[]
for r in refs:
    kind=classify(r['title'])
    entries.append({'title':r['title'],'url':r['url'],'classification':kind,'entity':entity(r['title'])})
get_entries=[x for x in entries if x['classification']=='GET']
write_entries=[x for x in entries if x['classification'] in ('WRITE','DELETE')]
unknown=[x for x in entries if x['classification']=='UNKNOWN']
docs=[x for x in entries if x['classification']=='DOC']
# Deduplicate entities while preserving counts for audit usefulness.
entities={}
for x in entries:
    if x['classification'] in ('GET','WRITE','DELETE'):
        e=entities.setdefault(x['entity'],{'entity':x['entity'],'GET':0,'WRITE':0,'DELETE':0,'operations':[]})
        e[x['classification']]+=1; e['operations'].append(x['title'])
print(f'CATALOG_ENTRIES={len(entries)}')
print(f'GET_ENTRIES={len(get_entries)}')
print(f'WRITE_ENTRIES={len(write_entries)}')
print(f'UNKNOWN_ENTRIES={len(unknown)}')
print(f'DOC_ENTRIES={len(docs)}')
print(f'ENTITIES={len(entities)}')
report={
 'audit':'MARSEL_AUDIT_V16.2',
 'timestamp_utc':datetime.now(timezone.utc).isoformat(),
 'readonly':True,
 'official_docs':{'index':DOCS_INDEX,'http_status':status,'reference_count':len(refs)},
 'inventory':{'catalog_entries':entries,'get_entries':get_entries,'write_entries':write_entries,'unknown_entries':unknown,'doc_entries':docs,'entities':sorted(entities.values(),key=lambda x:x['entity'].lower())},
 'safety':{'api_requests_made':False,'get_requests_made':False,'write_requests_made':False,'updates_performed':False,'deletes_performed':False,'pii_persisted':False}
}
with open(OUT,'w',encoding='utf-8') as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(f'REPORT={OUT}')
print('API_PROBES=0')
print('RESULT=READ_ONLY; OFFICIAL DOCUMENTATION CATALOG ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED')
