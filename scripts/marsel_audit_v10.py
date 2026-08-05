#!/usr/bin/env python3
import json, os, sys
from collections import Counter
from datetime import datetime, timezone
import httpx

BASE=os.environ.get('ROAPP_API_BASE','https://api.roapp.io/v2').rstrip('/')
KEY=os.environ.get('ROAPP_API_KEY')
OUT='marsel-audit-v10-report.json'
PAGE_SIZE=int(os.environ.get('MARSEL_AUDIT_PAGE_SIZE','100'))
if not KEY:
    print('ERROR: ROAPP_API_KEY is not configured'); sys.exit(2)
H={'Authorization':f'Bearer {KEY}','Accept':'application/json'}
CANDIDATES=['/clients','/customers','/users','/employees','/staff','/branches','/statuses','/order-statuses','/order-types','/products','/services','/warehouses','/categories']

def request(path, params=None):
    try:
        r=httpx.get(BASE+path,params=params or {},headers=H,timeout=30)
        return r
    except Exception as e:
        return e

def rows(p):
    if isinstance(p,list): return p
    if isinstance(p,dict):
        for k in ('data','items','results','orders','clients','customers','users','employees','branches','statuses','order_types','products','services','warehouses','categories'):
            if isinstance(p.get(k),list): return p[k]
    return []

def total_pages(p):
    if not isinstance(p,dict): return None
    candidates=[p.get('paging'),p.get('pagination'),p.get('meta')]
    for x in candidates:
        if isinstance(x,dict):
            for k in ('total_pages','totalPages','pages'):
                if isinstance(x.get(k),int): return x[k]
    for k in ('total_pages','totalPages','pages'):
        if isinstance(p.get(k),int): return p[k]
    return None

def fetch_collection(path):
    r=request(path,{'page':1,'pageSize':PAGE_SIZE})
    if isinstance(r,Exception): return {'http_status':None,'error':str(r),'rows':[],'pages':0,'available':False}
    if r.status_code != 200: return {'http_status':r.status_code,'rows':[],'pages':0,'available':False}
    try: p=r.json()
    except Exception: return {'http_status':200,'rows':[],'pages':0,'available':True,'json_error':True}
    data=rows(p); tp=total_pages(p)
    if isinstance(tp,int) and tp >= 1:
        for n in range(2,tp+1):
            rr=request(path,{'page':n,'pageSize':PAGE_SIZE})
            if not isinstance(rr,Exception) and rr.status_code==200:
                try: data += rows(rr.json())
                except Exception: pass
    return {'http_status':200,'rows':data,'pages':tp or 1,'available':True}

def id_value(x):
    if not isinstance(x,dict): return None
    return x.get('id')

def duplicate_values(data,key):
    vals=[x.get(key) for x in data if isinstance(x,dict) and x.get(key) is not None]
    return [v for v,c in Counter(vals).items() if c>1]

def order_audit(data):
    now=datetime.now(timezone.utc)
    dup_ids=duplicate_values(data,'id'); dup_numbers=duplicate_values(data,'number')
    missing=[]; broken_refs=[]; active_missing=[]; historical_missing=[]; future_overdue=[]; past_not_flagged=[]
    for x in data:
        if not isinstance(x,dict): continue
        if x.get('id') is None: missing.append({'number':x.get('number'),'reason':'missing_id'})
        for key in ('branch_id','assignee_id','manager_id'):
            if key in x and x.get(key) is not None and not isinstance(x.get(key),(int,str)): broken_refs.append({'id':x.get('id'),'field':key,'value_type':type(x.get(key)).__name__})
        closed=x.get('closed_at') is not None; done=x.get('done_at') is not None
        if x.get('assignee_id') is None:
            (historical_missing if (closed or done) else active_missing).append({'id':x.get('id'),'number':x.get('number'),'status':x.get('status'),'closed_at':x.get('closed_at'),'done_at':x.get('done_at')})
        due=x.get('due_date')
        try: due_dt=datetime.fromisoformat(due.replace('Z','+00:00')) if isinstance(due,str) else None
        except Exception: due_dt=None
        if due_dt is not None and not closed and not done:
            if due_dt>now and x.get('overdue') is True: future_overdue.append({'id':x.get('id'),'number':x.get('number'),'due_date':due,'overdue':True})
            if due_dt<=now and x.get('overdue') is not True: past_not_flagged.append({'id':x.get('id'),'number':x.get('number'),'due_date':due,'overdue':x.get('overdue')})
    return {'rows':len(data),'duplicate_ids':dup_ids,'duplicate_numbers':dup_numbers,'missing_id':missing,'broken_reference_types':broken_refs,'active_missing_assignee':active_missing,'historical_missing_assignee':historical_missing,'future_due_overdue_flag':future_overdue,'past_due_not_flagged':past_not_flagged}

print('=== MARSEL AUDIT V10 / RO APP API / READ ONLY ===')
print(f'BASE={BASE}')
collections={}
for path in ['/orders']+CANDIDATES:
    result=fetch_collection(path); collections[path]=result
    print(f'ENDPOINT {path} HTTP={result.get("http_status")} AVAILABLE={result.get("available")} ROWS={len(result.get("rows",[]))}')
orders=collections['/orders']
if not orders.get('available'):
    print('ERROR: /orders is unavailable'); sys.exit(3)
order_findings=order_audit(orders['rows'])
print(f'ORDERS_ROWS={order_findings["rows"]}')
print(f'ORDER_DUPLICATE_IDS={len(order_findings["duplicate_ids"])}')
print(f'ORDER_DUPLICATE_NUMBERS={len(order_findings["duplicate_numbers"])}')
print(f'ORDER_MISSING_ID={len(order_findings["missing_id"])}')
print(f'ORDER_ACTIVE_MISSING_ASSIGNEE={len(order_findings["active_missing_assignee"])}')
print(f'ORDER_HISTORICAL_MISSING_ASSIGNEE={len(order_findings["historical_missing_assignee"])}')
print(f'ORDER_FUTURE_DUE_OVERDUE_FLAG={len(order_findings["future_due_overdue_flag"])}')
print(f'ORDER_PAST_DUE_NOT_FLAGGED={len(order_findings["past_due_not_flagged"])}')
summary={}
for path,r in collections.items():
    if path=='/orders': continue
    data=r.get('rows',[])
    summary[path]={'http_status':r.get('http_status'),'available':r.get('available'),'pages':r.get('pages'),'rows':len(data),'duplicate_ids':duplicate_values(data,'id'),'missing_id_count':sum(1 for x in data if isinstance(x,dict) and x.get('id') is None)}
report={'audit':'MARSEL_AUDIT_V10','timestamp_utc':datetime.now(timezone.utc).isoformat(),'readonly':True,'endpoint_probe':summary,'orders':order_findings,'safety':{'writes_performed':False,'updates_performed':False,'deletes_performed':False,'client_names_phones_emails_excluded':True},'interpretation_rule':'HTTP 404/405/other non-200 means endpoint was not confirmed; it is not treated as proof that the entity does not exist.'}
with open(OUT,'w',encoding='utf-8') as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(f'REPORT={OUT}')
print('RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED')
