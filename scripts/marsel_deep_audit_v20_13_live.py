#!/usr/bin/env python3
import json, os, re, hashlib
from collections import Counter, defaultdict
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
BASE=os.environ.get('ROAPP_API_BASE','https://api.roapp.io/v2').rstrip('/'); KEY=os.environ.get('ROAPP_API_KEY',''); OUT=os.environ.get('MARSEL_DEEP_AUDIT_OUTPUT','marsel-deep-audit-v20-13.json'); SIZE=int(os.environ.get('MARSEL_PAGE_SIZE','100')); MAX=int(os.environ.get('MARSEL_MAX_PAGES','1000'))
T=[('orders','/orders'),('services','/catalog/services'),('products','/catalog/products'),('bundles','/catalog/bundles'),('inquiries','/inquiries'),('bookings','/bookings'),('estimates','/estimates'),('invoices','/invoices')]
def req(path,page):
 u=BASE+path+'?'+urlencode({'page':page,'limit':SIZE}); r=Request(u,headers={'Authorization':'Bearer '+KEY,'Accept':'application/json','User-Agent':'MARSEL-V20.13'},method='GET')
 try:
  with urlopen(r,timeout=30) as x:return x.status,json.loads(x.read().decode()),None
 except HTTPError as e:return e.code,None,e.read().decode(errors='replace')[:1000]
 except (URLError,TimeoutError,ValueError) as e:return None,None,str(e)
def rows(x):
 if isinstance(x,list):return x
 if not isinstance(x,dict):return []
 for k in ('data','items','results','orders','services','products','bundles','inquiries','bookings','estimates','invoices'):
  if isinstance(x.get(k),list):return x[k]
 for k in ('data','result'):
  if isinstance(x.get(k),dict):
   z=rows(x[k])
   if z:return z
 return []
def ident(x):return x.get('id',x.get('ID',x.get('uuid'))) if isinstance(x,dict) else None
def norm(v):return re.sub(r'\s+',' ',str(v).strip().casefold()) if v not in (None,'') else ''
def main():
 if not KEY:raise SystemExit('ROAPP_API_KEY is required')
 out={'version':'20.13','readonly':True,'write_requests_made':0,'ro_app_data_mutated':False,'method_policy':{'allowed':['GET'],'forbidden':['POST','PUT','PATCH','DELETE']},'entities':{},'change_set':[]}; total=0; fails=[]
 for e,p in T:
  a=[]; pages=0
  for n in range(1,MAX+1):
   h,d,err=req(p,n)
   if h!=200:
    if h==404 and a:break
    fails.append({'entity':e,'page':n,'http':h,'error':err});break
   r=rows(d); pages+=1
   if not r:break
   a+=r
   if len(r)<SIZE:break
  total+=len(a); ids=[ident(x) for x in a]; c=Counter(i for i in ids if i is not None); b={k:defaultdict(list) for k in ('name','title','code','sku','barcode')}
  for x in a:
   if isinstance(x,dict):
    for k in b:
     v=norm(x.get(k))
     if v:b[k][v].append(ident(x))
  def dm(d):return {k:v for k,v in d.items() if len(v)>1}
  ent={'records':len(a),'pages':pages,'missing_id':sum(i is None for i in ids),'duplicate_ids':{str(k):v for k,v in c.items() if v>1},'field_presence':{k:sum(isinstance(x,dict) and x.get(k) not in (None,'') for x in a) for k in ('id','name','title','code','sku','barcode','cost','price','status','client_id','manager_id','assignee_id','branch_id','category_id','created_at','updated_at','due_date')},'duplicate_name_or_title':dm({**b['name'],**b['title']}),'duplicate_code':dm(b['code']),'duplicate_sku':dm(b['sku']),'duplicate_barcode':dm(b['barcode']),'status_counts':dict(Counter(str(x.get('status')) for x in a if isinstance(x,dict) and x.get('status') is not None)),'zero_cost':sum(isinstance(x,dict) and str(x.get('cost','')) in ('0','0.0','0.00','0.000') for x in a),'empty_code':sum(isinstance(x,dict) and not norm(x.get('code')) for x in a),'empty_sku':sum(isinstance(x,dict) and not norm(x.get('sku')) for x in a),'empty_barcode':sum(isinstance(x,dict) and not norm(x.get('barcode')) for x in a)}; out['entities'][e]=ent
  for reason,key in [('DUPLICATE_ID','duplicate_ids'),('DUPLICATE_NAME_OR_TITLE','duplicate_name_or_title'),('DUPLICATE_CODE','duplicate_code'),('DUPLICATE_SKU','duplicate_sku'),('DUPLICATE_BARCODE','duplicate_barcode')]:
   for k,v in ent[key].items():out['change_set'].append({'action':'MANUAL_REVIEW','reason':reason,'entity':e,'key':k,'ids':v})
 out['request_failures']=fails; out['summary']={'entities':len(T),'records':total,'request_failures':len(fails),'change_set_items':len(out['change_set']),'automatic_writes':0}; out['summary']['deep_audit_sha256']=hashlib.sha256(json.dumps(out,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 with open(OUT,'w',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
 print('=== MARSEL V20.13 / DEEP AUDIT / READ ONLY ==='); print('ENTITIES=',len(T)); print('RECORDS=',total); print('REQUEST_FAILURES=',len(fails)); print('CHANGE_SET_ITEMS=',len(out['change_set'])); print('WRITE_REQUESTS_MADE=0'); print('DEEP_AUDIT_SHA256=',out['summary']['deep_audit_sha256']); print('RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED')
 if fails:raise SystemExit(1)
if __name__=='__main__':main()
