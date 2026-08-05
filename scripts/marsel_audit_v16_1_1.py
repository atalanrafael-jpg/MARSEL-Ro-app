#!/usr/bin/env python3
"""MARSEL V16.1.1 — documentation fallback, read-only, stdlib only."""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE=os.environ.get('ROAPP_API_BASE','https://api.roapp.io/v2').rstrip('/')
KEY=os.environ.get('ROAPP_API_KEY')
DOCS_INDEX=os.environ.get('ROAPP_DOCS_INDEX','https://roapp.readme.io/llms.txt')
OUT=os.environ.get('MARSEL_AUDIT_OUT','marsel-api-master-inventory-v16-1-1.json')
TIMEOUT=int(os.environ.get('ROAPP_TIMEOUT','45'))
MAX_PAGES=int(os.environ.get('MARSEL_V16_1_MAX_DOC_PAGES','200'))
UA='Mozilla/5.0 (compatible; MARSEL-AUDIT/16.1.1; +https://github.com/atalanrafael-jpg/Ro-app)'
if not KEY:
    print('ERROR: ROAPP_API_KEY is not configured'); sys.exit(2)

def fetch(url):
    req=Request(url,headers={'User-Agent':UA,'Accept':'text/plain, text/markdown, text/html, */*'})
    try:
        with urlopen(req,timeout=TIMEOUT) as r: return r.status,r.read()
    except HTTPError as e: return e.code,e.read()
    except (URLError,TimeoutError,OSError) as e: return None,str(e).encode()

def links(text):
    found=re.findall(r"https?://[^\s<>\)\]\"'`]+",text or '')
    out=[]; seen=set()
    for raw in found:
        u=raw.rstrip(".,; \t\r\n").rstrip(chr(34)+chr(39)+chr(96))
        if u not in seen: seen.add(u); out.append(u)
    return out

def title(line,url):
    m=re.search(r"\[([^\]]+)\]\((https://roapp\.readme\.io/reference/[^)]+)\)",line)
    return m.group(1).strip() if m else url.rsplit('/',1)[-1]

def methods(text): return sorted(set(x.upper() for x in re.findall(r'\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b',text or '',re.I)))
def paths(text): return sorted(set(re.findall(r'(?:https://api\.roapp\.io)?/v2/[A-Za-z0-9_./{}:-]+',text or '')))

print('=== MARSEL AUDIT V16.1.1 / DOCUMENTATION FALLBACK / READ ONLY ===')
print(f'BASE={BASE}'); print(f'DOCS_INDEX={DOCS_INDEX}')
status,body=fetch(DOCS_INDEX); print(f'DOCS_INDEX_HTTP={status}')
if status!=200:
    print('RESULT=READ_ONLY; DOCUMENTATION INDEX UNAVAILABLE; NO RO APP DATA CREATED, UPDATED OR DELETED'); sys.exit(4)
text=body.decode('utf-8','replace')
catalog=[]; seen=set()
for line in text.splitlines():
    for u in links(line):
        if '/reference/' in u and u not in seen:
            seen.add(u); catalog.append({'url':u,'title':title(line,u)})
print(f'REFERENCE_LINKS={len(catalog)}')
pages=[]; ops={}
for ref in catalog[:MAX_PAGES]:
    s,b=fetch(ref['url']); t=b.decode('utf-8','replace')
    rec={'url':ref['url'],'title':ref['title'],'http_status':s,'bytes':len(b)}
    if s==200:
        ms,ps=methods(t),paths(t); rec.update(methods=ms,paths=ps)
        for m in ms:
            for p in ps: ops[(m,p)]={'method':m,'path':p,'source':ref['url'],'title':ref['title']}
    else: rec['error']=t[:500]
    pages.append(rec)
operations=sorted(ops.values(),key=lambda x:(x['method'],x['path']))
gets=[x for x in operations if x['method']=='GET']; writes=[x for x in operations if x['method']!='GET']
print(f'DOCUMENTED_OPERATION_CANDIDATES={len(operations)}'); print(f'DOCUMENTED_GET_CANDIDATES={len(gets)}'); print(f'DOCUMENTED_WRITE_CANDIDATES={len(writes)}')
report={'audit':'MARSEL_AUDIT_V16.1.1','timestamp_utc':datetime.now(timezone.utc).isoformat(),'readonly':True,'official_docs':{'index':DOCS_INDEX,'http_status':status,'reference_count':len(catalog),'reference_pages':pages},'inventory':{'operation_candidates':len(operations),'get_candidates':len(gets),'write_candidates':len(writes),'operations':operations},'safety':{'api_requests_made':False,'get_requests_made':False,'write_requests_made':False,'updates_performed':False,'deletes_performed':False,'pii_persisted':False}}
with open(OUT,'w',encoding='utf-8') as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(f'REPORT={OUT}'); print('API_PROBES=0'); print('RESULT=READ_ONLY; DOCUMENTATION INVENTORY ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED')
