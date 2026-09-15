import json, os, time, hashlib
from datetime import datetime, timezone
import httpx

BASE=os.getenv('ROAPP_API_BASE','https://api.roapp.io/v2').rstrip('/')
KEY=os.environ['ROAPP_API_KEY']
OUT=os.getenv('MARSEL_CATEGORY_AUDIT_OUTPUT','marsel-roapp-category-audit-readonly.json')
PRODUCTS='/catalog/products'
CATEGORIES='/catalog/products/categories'

headers={'Authorization':f'Bearer {KEY}','Accept':'application/json'}
client=httpx.Client(headers=headers,timeout=float(os.getenv('ROAPP_TIMEOUT','30')))
try:
    r=client.get(BASE+PRODUCTS,params={'page':1})
    r.raise_for_status(); first=r.json()
    paging=first.get('paging') or {}
    total=int(paging.get('total') or 0)
    pages=int(paging.get('pages') or 1)
    rows=list(first.get('data') or [])
    for page in range(2,pages+1):
        time.sleep(float(os.getenv('ROAPP_MIN_REQUEST_INTERVAL','0.34')))
        rr=client.get(BASE+PRODUCTS,params={'page':page})
        rr.raise_for_status(); rows.extend(rr.json().get('data') or [])
    ids=sorted({int(x['category_id']) for x in rows if x.get('category_id') is not None})
    categories=[]; failures=[]
    for cid in ids:
        time.sleep(float(os.getenv('ROAPP_MIN_REQUEST_INTERVAL','0.34')))
        cr=client.get(f'{BASE}{CATEGORIES}/{cid}')
        rec={'id':cid,'http_status':cr.status_code}
        if cr.is_success:
            try: rec['data']=cr.json()
            except Exception: rec['json_parse_error']=True
        else:
            try: rec['error']=cr.json()
            except Exception: rec['error_text']=cr.text[:500]
            failures.append(cid)
        categories.append(rec)
    evidence={
      'system':'ROAPP','status':'PASS' if not failures else 'PARTIAL',
      'generated_at_utc':datetime.now(timezone.utc).isoformat(),
      'mode':'READ_ONLY','api_base':BASE,
      'product_path':PRODUCTS,'category_path':f'{CATEGORIES}/{{id}}','method':'GET',
      'write_requests_made':0,'ro_app_data_mutated':False,
      'product_expected_count':total,'product_rows_read':len(rows),'product_pages_read':pages,
      'category_ids_used':ids,'category_records_read':len(categories),
      'category_failures':failures,'categories':categories
    }
    canonical=json.dumps(evidence,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    evidence['sha256']=hashlib.sha256(canonical).hexdigest()
    with open(OUT,'w',encoding='utf-8') as f: json.dump(evidence,f,ensure_ascii=False,indent=2)
finally:
    client.close()
