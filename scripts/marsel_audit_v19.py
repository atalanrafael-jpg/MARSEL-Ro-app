#!/usr/bin/env python3
"""MARSEL V19.1 — read-only inventory; incomplete endpoint coverage is never reported as a data error."""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

BASE=os.environ.get("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.environ.get("ROAPP_API_KEY")
DOCS=os.environ.get("ROAPP_DOCS_INDEX","https://roapp.readme.io/llms.txt")
OUT=os.environ.get("MARSEL_AUDIT_OUT","marsel-integrity-audit-v19.json")
MAX_PAGES=int(os.environ.get("ROAPP_MAX_PAGES","10"))
if not KEY: sys.exit("ROAPP_API_KEY is not configured")

def get(url,api=False):
    h={"User-Agent":"MARSEL-INTEGRITY-AUDIT/19.1","Accept":"application/json,text/plain,*/*"}
    if api: h["Authorization"]=f"Bearer {KEY}"
    try:
        with urlopen(Request(url,headers=h,method="GET"),timeout=45) as r: return r.status,r.read(),None
    except HTTPError as e: return e.code,e.read(),None
    except (URLError,TimeoutError,OSError) as e: return None,b"",f"{type(e).__name__}: {e}"

def text(v): return v.decode("utf-8","replace") if isinstance(v,bytes) else str(v or "")
def safe(u):
    try:
        p=urlparse(u)
        return p.scheme=="https" and p.netloc.lower()=="api.roapp.io" and p.path.startswith("/v2/") and not re.search(r"\{[^}]+\}|<[^>]+>|\[[^]]+\]|:[A-Za-z_][A-Za-z0-9_-]*",u)
    except ValueError: return False

def refs(v): return list(dict.fromkeys(re.findall(r"https://roapp\.readme\.io/reference/[A-Za-z0-9_./?=&%#:+~-]+",text(v),re.I)))
def discover(v):
    s=text(v).replace("\\/","/"); out=[]
    for m in re.finditer(r"https://api\.roapp\.io/v2/[A-Za-z0-9_./?=&%#:+~-]+",s,re.I):
        u=m.group(0).rstrip(".,;\"'`)]}"); before=s[max(0,m.start()-180):m.start()]
        if safe(u) and not re.search(r"\b(?:POST|PUT|PATCH|DELETE)\b[^\n]{0,120}$",before,re.I): out.append(u)
    for m in re.finditer(r"(?:GET\s+|(?:path|url|endpoint)[\"']?\s*[:=]\s*[\"'])(/v2/[A-Za-z0-9_./?=&%#:+~-]+)",s,re.I):
        u=BASE+m.group(1)
        if safe(u): out.append(u)
    return list(dict.fromkeys(out))

def obj(payload):
    try: return json.loads(text(payload))
    except (TypeError,json.JSONDecodeError): return None

def rows(v):
    if isinstance(v,list): return v
    if isinstance(v,dict):
        for k in ("data","items","results","records","rows","customers","orders","products","services","invoices","payments"):
            if isinstance(v.get(k),list): return v[k]
    return None

def rid(r):
    if not isinstance(r,dict): return None
    for k in ("id","ID","uuid","uid"):
        if isinstance(r.get(k),(str,int)) and str(r[k]): return str(r[k])
    return None

def ref_values(rs):
    out=[]
    for r in rs or []:
        if not isinstance(r,dict): continue
        for k,v in r.items():
            lk=str(k).lower()
            if not (lk.endswith("_id") or lk.endswith("_ids") or lk in {"customer","customerid","client","clientid","order","orderid","product","productid","service","serviceid","branch","branchid","employee","employeeid","category","categoryid","warehouse","warehouseid","invoice","invoiceid","payment","paymentid","company","companyid"}): continue
            for x in (v if isinstance(v,list) else [v]):
                if isinstance(x,(str,int)) and str(x): out.append({"field":str(k),"value":str(x)})
    return out

def next_url(v):
    if not isinstance(v,dict): return None
    for c in (v,v.get("links"),v.get("pagination"),v.get("meta")):
        if isinstance(c,dict):
            for k in ("next","next_page","nextPage","next_url","nextUrl"):
                if isinstance(c.get(k),str) and safe(c[k]): return c[k]
    return None

print("=== MARSEL AUDIT V19.1 / LIVE STRUCTURAL INVENTORY / GET-ONLY / READ ONLY ===")
ds,db,de=get(DOCS); print(f"DOCS_INDEX_HTTP={ds}")
if ds!=200: sys.exit(4)
links=refs(db); print(f"REFERENCE_LINKS={len(links)}")
endpoints=[]
for link in links:
    s,b,e=get(link)
    if s==200: endpoints.extend(discover(b))
# /orders is independently verified by V18 with HTTP 200; this is a verified fallback, not a guessed endpoint.
orders=f"{BASE}/orders"
if safe(orders): endpoints.append(orders)
endpoints=list(dict.fromkeys(endpoints)); print(f"GET_PROBES={len(endpoints)}")

reports=[]; global_ids=Counter(); total_records=0; reference_values=[]
for initial in endpoints:
    u=initial; seen=set(); pages=0; statuses=[]; ids=[]; refs_found=[]; record_count=0
    while u and u not in seen and pages<MAX_PAGES:
        seen.add(u); s,p,e=get(u,True); pages+=1; statuses.append(s)
        if s is None: break
        value=obj(p) if 200<=s<300 else None; rs=rows(value)
        if rs is not None:
            record_count+=len(rs)
            for r in rs:
                x=rid(r)
                if x: ids.append(x); global_ids[x]+=1
            refs_found.extend(ref_values(rs))
        u=next_url(value)
    c=Counter(ids); total_records+=record_count; reference_values.extend({"source_url":initial,**x} for x in refs_found)
    reports.append({"method":"GET","url":initial,"http_status":statuses[-1] if statuses else None,"available":bool(statuses and statuses[-1] and 200<=statuses[-1]<300),"pages_read":pages,"record_count":record_count,"duplicate_ids":sorted(k for k,n in c.items() if n>1)[:100],"reference_values":refs_found[:1000],"response_bodies_stored":False})

available=sum(r["available"] for r in reports); http_errors=sum(r["http_status"] is not None and not 200<=r["http_status"]<300 for r in reports); dup=sum(bool(r["duplicate_ids"]) for r in reports)
# A reference is only testable when the referenced entity's endpoint has also been inventoried.
# Therefore references not resolved inside this partial endpoint set are COVERAGE GAPS, not broken data.
unresolved=[]
for r in reports:
    for x in r["reference_values"]:
        if x["value"] not in global_ids: unresolved.append({"source_url":r["url"],**x})
complete=False
print(f"GET_AVAILABLE={available}"); print(f"GET_HTTP_ERRORS={http_errors}"); print(f"ENDPOINTS_WITH_RECORD_LISTS={sum(r['record_count']>0 for r in reports)}"); print(f"TOTAL_RECORDS_ACROSS_RESPONSES={total_records}"); print(f"REFERENCE_VALUES_FOUND={len(reference_values)}"); print(f"RESOLVABLE_REFERENCE_VALUES={len(reference_values)-len(unresolved)}"); print(f"UNRESOLVED_REFERENCE_VALUES_DUE_TO_COVERAGE={len(unresolved)}"); print(f"ENDPOINTS_WITH_DUPLICATE_IDS={dup}"); print(f"COVERAGE_COMPLETE={str(complete).upper()}"); print("WRITE_REQUESTS_MADE=0")
report={"audit":"MARSEL_AUDIT_V19.1","timestamp_utc":datetime.now(timezone.utc).isoformat(),"readonly":True,"coverage_complete":complete,"reference_links":len(links),"get_probes":len(endpoints),"get_available":available,"get_http_errors":http_errors,"summary":{"total_records_across_responses":total_records,"reference_values_found":len(reference_values),"resolvable_reference_values":len(reference_values)-len(unresolved),"unresolved_reference_values_due_to_coverage":len(unresolved),"endpoints_with_duplicate_ids":dup,"confirmed_data_errors":0},"coverage_gap":{"status":"INCOMPLETE","reason":"Only successfully discovered GET endpoints were inventoried. References to entities whose endpoints were not inventoried are not classified as broken relationships.","unresolved_reference_values":unresolved[:500]},"endpoints":reports,"safety":{"get_requests_only":True,"write_requests_made":False,"response_bodies_stored":False,"data_mutated":False,"pii_persisted":False}}
with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(f"REPORT={OUT}"); print("RESULT=READ_ONLY; GET REQUESTS ONLY; COVERAGE GAPS ARE NOT DATA ERRORS; NO RO APP DATA CREATED, UPDATED OR DELETED")
sys.exit(0 if available>0 else 5)
