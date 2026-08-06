#!/usr/bin/env python3
"""MARSEL V20.13 — deep audit of V20.12 inventory, READ ONLY."""
import json, os, re, hashlib
from collections import Counter, defaultdict

INPUT=os.environ.get('MARSEL_INVENTORY_INPUT','marsel-full-inventory-v20-12.json')
OUT=os.environ.get('MARSEL_DEEP_AUDIT_OUTPUT','marsel-deep-audit-v20-13.json')

FIELDS=['id','name','title','code','sku','barcode','cost','price','status','client_id','manager_id','assignee_id','branch_id','category_id','created_at','updated_at','due_date']

def norm(v):
    if v is None: return ''
    return re.sub(r'\s+',' ',str(v).strip().casefold())

def ident(x):
    return x.get('id',x.get('ID',x.get('uuid'))) if isinstance(x,dict) else None

def rows_from_target(t):
    rows=[]
    for p in t.get('pages',[]):
        rows.extend(p.get('records_data',[]) or [])
    return rows

def main():
    with open(INPUT,encoding='utf-8') as f: inv=json.load(f)
    assert inv.get('version')=='20.12' and inv.get('readonly') is True
    assert inv.get('write_requests_made')==0 and inv.get('ro_app_data_mutated') is False
    targets=inv.get('targets',[])
    result={'version':'20.13','readonly':True,'write_requests_made':0,'ro_app_data_mutated':False,'source_inventory_sha256':inv.get('summary',{}).get('inventory_sha256'),'entities':{},'change_set':[],'summary':{}}
    total=0
    for t in targets:
        entity=t.get('entity'); rows=rows_from_target(t); total+=len(rows)
        ids=[ident(x) for x in rows]
        id_counts=Counter(x for x in ids if x is not None)
        duplicate_ids={k:v for k,v in id_counts.items() if v>1}
        missing_id=sum(x is None for x in ids)
        field_presence={f:sum(isinstance(x,dict) and x.get(f) not in (None,'') for x in rows) for f in FIELDS}
        exact_name=defaultdict(list); exact_code=defaultdict(list); exact_sku=defaultdict(list); exact_barcode=defaultdict(list)
        for x in rows:
            if not isinstance(x,dict): continue
            for f, bucket in [('name',exact_name),('title',exact_name),('code',exact_code),('sku',exact_sku),('barcode',exact_barcode)]:
                v=norm(x.get(f))
                if v: bucket[v].append(ident(x))
        def dupmap(d): return {k:v for k,v in d.items() if len(v)>1}
        costs=Counter(str(x.get('cost')) for x in rows if isinstance(x,dict))
        statuses=Counter(str(x.get('status')) for x in rows if isinstance(x,dict) and x.get('status') is not None)
        entity_out={'records':len(rows),'missing_id':missing_id,'duplicate_ids':duplicate_ids,'field_presence':field_presence,'duplicate_name_or_title':dupmap(exact_name),'duplicate_code':dupmap(exact_code),'duplicate_sku':dupmap(exact_sku),'duplicate_barcode':dupmap(exact_barcode),'status_counts':dict(statuses),'cost_counts':dict(costs),'zero_cost':sum(isinstance(x,dict) and str(x.get('cost','')) in ('0','0.0','0.00','0.000') for x in rows),'empty_code':sum(isinstance(x,dict) and not norm(x.get('code')) for x in rows),'empty_sku':sum(isinstance(x,dict) and not norm(x.get('sku')) for x in rows),'empty_barcode':sum(isinstance(x,dict) and not norm(x.get('barcode')) for x in rows)}
        result['entities'][entity]=entity_out
        for kind,key in [('DUPLICATE_ID','duplicate_ids'),('DUPLICATE_NAME_OR_TITLE','duplicate_name_or_title'),('DUPLICATE_CODE','duplicate_code'),('DUPLICATE_SKU','duplicate_sku'),('DUPLICATE_BARCODE','duplicate_barcode')]:
            for value, ids2 in entity_out[key].items(): result['change_set'].append({'action':'MANUAL_REVIEW','reason':kind,'entity':entity,'key':value,'ids':ids2})
    result['summary']={'entities':len(targets),'records':total,'change_set_items':len(result['change_set']),'manual_review_items':len(result['change_set']),'automatic_writes':0}
    payload=json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    result['summary']['deep_audit_sha256']=hashlib.sha256(payload).hexdigest()
    with open(OUT,'w',encoding='utf-8') as f: json.dump(result,f,ensure_ascii=False,indent=2)
    print('=== MARSEL V20.13 / DEEP AUDIT / READ ONLY ===')
    print(f"ENTITIES={len(targets)}")
    print(f"RECORDS={total}")
    print(f"CHANGE_SET_ITEMS={len(result['change_set'])}")
    print('WRITE_REQUESTS_MADE=0')
    print(f"SOURCE_INVENTORY_SHA256={result['source_inventory_sha256']}")
    print(f"DEEP_AUDIT_SHA256={result['summary']['deep_audit_sha256']}")
    print('RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED')

if __name__=='__main__': main()
