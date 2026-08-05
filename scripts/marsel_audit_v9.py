#!/usr/bin/env python3
import json, os, sys
from datetime import datetime, timezone
import httpx

BASE=os.environ.get('ROAPP_API_BASE','https://api.roapp.io/v2').rstrip('/')
KEY=os.environ.get('ROAPP_API_KEY')
OUT='marsel-audit-v9-report.json'
PAGE_SIZE=int(os.environ.get('MARSEL_AUDIT_PAGE_SIZE','100'))
if not KEY:
    print('ERROR: ROAPP_API_KEY is not configured'); sys.exit(2)
H={'Authorization':f'Bearer {KEY}','Accept':'application/json'}

def get(path, params):
    r=httpx.get(BASE+path,params=params,headers=H,timeout=30)
    if r.status_code != 200:
        print(f'ERROR HTTP {r.status_code} GET {path}'); sys.exit(3)
    return r.json()

def rows(p):
    if isinstance(p,list): return p
    if isinstance(p,dict):
        for k in ('orders','data','items'):
            if isinstance(p.get(k),list): return p[k]
    return []

def pages(p):
    x=p.get('paging',{}) if isinstance(p,dict) else {}
    for k in ('total_pages','totalPages','pages'):
        if isinstance(x.get(k),int): return x[k]
    return None

def dt(v):
    if not isinstance(v,str): return None
    try: return datetime.fromisoformat(v.replace('Z','+00:00'))
    except Exception: return None

def compact(x, reason):
    s=x.get('status') if isinstance(x.get('status'),dict) else {}
    t=x.get('order_type') if isinstance(x.get('order_type'),dict) else {}
    return {'id':x.get('id'),'number':x.get('number'),'status_id':s.get('id'),'status_name':s.get('name'),'order_type_id':t.get('id'),'order_type_name':t.get('name'),'branch_id':x.get('branch_id'),'assignee_id':x.get('assignee_id'),'manager_id':x.get('manager_id'),'created_at':x.get('created_at'),'modified_at':x.get('modified_at'),'due_date':x.get('due_date'),'closed_at':x.get('closed_at'),'done_at':x.get('done_at'),'overdue':x.get('overdue'),'status_overdue':x.get('status_overdue'),'diagnostic_reason':reason}

print('=== MARSEL AUDIT V9 / RO APP API / READ ONLY ===')
print(f'BASE={BASE}')
p=get('/orders',{'page':1,'pageSize':PAGE_SIZE}); total=pages(p); data=rows(p)
if total is None: print('ERROR: API did not report total pages'); sys.exit(4)
for n in range(2,total+1): data += rows(get('/orders',{'page':n,'pageSize':PAGE_SIZE}))
now=datetime.now(timezone.utc)
active_missing=[compact(x,'active_order_missing_assignee') for x in data if x.get('assignee_id') is None and x.get('closed_at') is None and x.get('done_at') is None]
historical_missing=[compact(x,'closed_or_done_order_missing_assignee') for x in data if x.get('assignee_id') is None and (x.get('closed_at') is not None or x.get('done_at') is not None)]
future_flag=[]
past_not_flagged=[]
for x in data:
    due=dt(x.get('due_date'))
    if due is None or x.get('closed_at') is not None or x.get('done_at') is not None: continue
    if due > now and x.get('overdue') is True: future_flag.append(compact(x,'overdue_true_while_due_datetime_is_future'))
    if due <= now and x.get('overdue') is not True: past_not_flagged.append(compact(x,'due_datetime_passed_while_overdue_not_true'))
report={'audit':'MARSEL_AUDIT_V9','timestamp_utc':now.isoformat(),'readonly':True,'orders':{'http_status':200,'page_size':PAGE_SIZE,'total_pages_reported':total,'pages_scanned':total,'rows_scanned':len(data),'pagination_complete':True},'findings':{'active_missing_assignee':active_missing,'historical_missing_assignee':historical_missing,'future_due_overdue_flag':future_flag,'past_due_not_flagged':past_not_flagged},'counts':{'active_missing_assignee':len(active_missing),'historical_missing_assignee':len(historical_missing),'future_due_overdue_flag':len(future_flag),'past_due_not_flagged':len(past_not_flagged)},'safety':{'writes_performed':False,'updates_performed':False,'deletes_performed':False,'client_names_phones_emails_excluded':True}}
with open(OUT,'w',encoding='utf-8') as f: json.dump(report,f,ensure_ascii=False,indent=2)
print('HTTP /orders=200'); print(f'TOTAL_PAGES_REPORTED={total}'); print(f'PAGES_SCANNED={total}'); print(f'ROWS_SCANNED={len(data)}'); print('PAGINATION_COMPLETE=True')
print(f'ACTIVE_MISSING_ASSIGNEE={len(active_missing)}'); print(f'HISTORICAL_MISSING_ASSIGNEE={len(historical_missing)}'); print(f'FUTURE_DUE_OVERDUE_FLAG={len(future_flag)}'); print(f'PAST_DUE_NOT_FLAGGED={len(past_not_flagged)}')
print('--- ACTIVE_MISSING_ASSIGNEE_DETAILS ---')
for x in active_missing: print(json.dumps(x,ensure_ascii=False,separators=(',',':')))
print('--- FUTURE_DUE_OVERDUE_DETAILS ---')
for x in future_flag: print(json.dumps(x,ensure_ascii=False,separators=(',',':')))
print('--- PAST_DUE_NOT_FLAGGED_DETAILS ---')
for x in past_not_flagged: print(json.dumps(x,ensure_ascii=False,separators=(',',':')))
print(f'REPORT={OUT}'); print('RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED')
