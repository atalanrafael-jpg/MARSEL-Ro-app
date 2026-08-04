#!/usr/bin/env python3
"""MARSEL V19.1 — read-only classification of unresolved references."""
import json, os, re, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = "marsel-unresolved-references-v19-1.json"
if not KEY:
    sys.exit("ROAPP_API_KEY is not configured")


def get(url, api=False):
    headers = {"User-Agent": "MARSEL-UNRESOLVED-REFERENCES/19.1", "Accept": "application/json,text/plain,*/*"}
    if api:
        headers["Authorization"] = f"Bearer {KEY}"
    try:
        with urlopen(Request(url, headers=headers), timeout=45) as r:
            return r.status, r.read()
    except HTTPError as e:
        return e.code, e.read()
    except (URLError, TimeoutError, OSError) as e:
        return None, str(e).encode()


def text(v):
    return v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)


def json_value(v):
    try: return json.loads(text(v))
    except (TypeError, json.JSONDecodeError): return None


def specs(v):
    s = text(v); out=[]
    for m in re.finditer(r"```json\s*(\{.*?\})\s*```", s, re.S):
        try:
            x=json.loads(m.group(1))
            if isinstance(x,dict) and isinstance(x.get("paths"),dict): out.append(x)
        except (json.JSONDecodeError,TypeError): pass
    return out


def candidate_urls(page):
    out=[]
    for spec in specs(page):
        servers=spec.get("servers") or [{}]
        server=((servers[0].get("url") if isinstance(servers[0],dict) else None) or API_BASE).rstrip("/")
        for path,item in (spec.get("paths") or {}).items():
            if not isinstance(item,dict) or "get" not in item or re.search(r"\{[^}]+\}",path): continue
            op=item["get"] if isinstance(item["get"],dict) else {}
            url=server+("/" if not path.startswith("/") else "")+path
            q=[]
            for p in op.get("parameters") or item.get("parameters") or []:
                if not isinstance(p,dict) or p.get("in")!="query": continue
                if "example" in p: q.append((p.get("name"),str(p["example"])))
                elif "default" in (p.get("schema") or {}): q.append((p.get("name"),str(p["schema"]["default"])))
            q=[x for x in q if x[0]]
            if q: url += "?"+urlencode(q)
            out.append((url,path,op.get("operationId"),op.get("summary")))
    return list(dict.fromkeys(out))


def records(v):
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


def is_ref_key(k):
    lk=str(k).lower()
    return lk.endswith("_id") or lk.endswith("_ids") or lk in {"customer","customerid","client","clientid","order","orderid","product","productid","service","serviceid","branch","branchid","employee","employeeid","category","categoryid","warehouse","warehouseid","invoice","invoiceid","payment","paymentid"}


def entity_hint(field, source):
    x=(str(field)+" "+str(source)).lower()
    for key,label in (("customer","customer"),("client","client"),("order","order"),("product","product"),("service","service"),("branch","branch"),("employee","employee"),("category","category"),("warehouse","warehouse"),("invoice","invoice"),("payment","payment")):
        if key in x: return label
    return "unknown"

print("=== MARSEL AUDIT V19.1 / UNRESOLVED REFERENCE CLASSIFICATION / READ ONLY ===")
status, body=get(DOCS)
print(f"DOCS_INDEX_HTTP={status}")
if status!=200: sys.exit(4)
links=list(dict.fromkeys(re.findall(r"https://roapp\\.readme\\.io/reference/[^)\\s]+",text(body))))
print(f"REFERENCE_LINKS={len(links)}")
endpoints=[]
for ref in links:
    s,b=get(ref)
    if s==200: endpoints.extend(candidate_urls(b))
endpoints=list(dict.fromkeys(endpoints))
print(f"GET_PROBES={len(endpoints)}")

records_by_path=defaultdict(list); ids=Counter(); refs=[]; http_errors=[]
for url,path,opid,summary in endpoints:
    s,p=get(url,True)
    if not(s and 200<=s<300):
        http_errors.append({"path":path,"status":s}); continue
    value=json_value(p); rs=records(value)
    if rs is None: continue
    for r in rs:
        x=rid(r)
        if x: ids[x]+=1; records_by_path[path].append((x,r))
        if isinstance(r,dict):
            for k,v in r.items():
                if not is_ref_key(k): continue
                vals=v if isinstance(v,list) else [v]
                for val in vals:
                    if isinstance(val,(str,int)) and str(val):
                        refs.append({"source_path":path,"field":str(k),"value":str(val),"entity_hint":entity_hint(k,path)})

unresolved=[r for r in refs if r["value"] not in ids]
# Conservative classification: no mutation and no claim that an unresolved reference is a database defect.
for i,r in enumerate(unresolved,1):
    r["reference_id"]=f"UR-{i:03d}"
    r["resolved_in_successful_get_lists"]=False
    r["classification"]="UNRESOLVED_NEEDS_REVIEW"
    r["severity"]="UNKNOWN"
    r["reason"]="Reference value was not found in the ID index built from successful GET list responses. This does not by itself prove that the source record is corrupt."
    r["recommended_action"]="Inspect the source field and determine whether the value is a valid cross-resource ID, a special/system value, or an orphaned reference before any write operation."

report={"audit":"MARSEL_AUDIT_V19.1","timestamp_utc":datetime.now(timezone.utc).isoformat(),"readonly":True,"docs_index_http":status,"reference_links":len(links),"get_probes":len(endpoints),"get_http_errors":len(http_errors),"unresolved_count":len(unresolved),"unresolved_references":unresolved,"http_errors":http_errors,"safety":{"write_requests_made":False,"data_mutated":False,"response_bodies_stored":False}}
with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(f"UNRESOLVED_REFERENCES={len(unresolved)}")
print("WRITE_REQUESTS_MADE=0")
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; CLASSIFICATION ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
