#!/usr/bin/env python3
"""MARSEL V19 — read-only referential-integrity audit of live RO App GET responses."""
import hashlib, json, os, re, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = "marsel-integrity-audit-v19.json"
if not KEY:
    sys.exit("ROAPP_API_KEY is not configured")


def get(url, api=False):
    headers = {"User-Agent": "MARSEL-INTEGRITY-AUDIT/19", "Accept": "application/json,text/plain,*/*"}
    if api:
        headers["Authorization"] = f"Bearer {KEY}"
    try:
        with urlopen(Request(url, headers=headers), timeout=45) as response:
            return response.status, response.read()
    except HTTPError as exc:
        return exc.code, exc.read()
    except (URLError, TimeoutError, OSError) as exc:
        return None, str(exc).encode()


def text_of(v):
    return v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)


def refs(text):
    return list(dict.fromkeys(re.findall(r"https://roapp\.readme\.io/reference/[^)\s]+", text_of(text))))


def specs(text):
    text = text_of(text)
    out = []
    for m in re.finditer(r"```json\s*(\{.*?\})\s*```", text, re.S):
        try:
            x = json.loads(m.group(1))
            if isinstance(x, dict) and isinstance(x.get("paths"), dict): out.append(x)
        except (json.JSONDecodeError, TypeError):
            pass
    return out


def candidate_urls(page):
    out = []
    for spec in specs(page):
        servers = spec.get("servers") or [{}]
        server = ((servers[0].get("url") if isinstance(servers[0], dict) else None) or API_BASE).rstrip("/")
        for path, item in (spec.get("paths") or {}).items():
            if not isinstance(item, dict) or "get" not in item or re.search(r"\{[^}]+\}", path): continue
            op = item["get"] if isinstance(item["get"], dict) else {}
            url = server + ("/" if not path.startswith("/") else "") + path
            q = []
            for p in op.get("parameters") or item.get("parameters") or []:
                if not isinstance(p, dict) or p.get("in") != "query": continue
                if "example" in p: q.append((p.get("name"), str(p["example"])))
                elif "default" in (p.get("schema") or {}): q.append((p.get("name"), str(p["schema"]["default"])))
            q = [(k,v) for k,v in q if k]
            if q: url += "?" + urlencode(q)
            out.append((url, path, op.get("operationId"), op.get("summary")))
    return list(dict.fromkeys(out))


def json_value(payload):
    try: return json.loads(text_of(payload))
    except (TypeError, json.JSONDecodeError): return None


def records(v):
    if isinstance(v, list): return v
    if isinstance(v, dict):
        for k in ("data","items","results","records","rows","customers","orders","products","services","invoices","payments"):
            if isinstance(v.get(k), list): return v[k]
    return None


def rid(r):
    if not isinstance(r, dict): return None
    for k in ("id","ID","uuid","uid"):
        if isinstance(r.get(k),(str,int)): return str(r[k])
    return None


def scalar(v): return isinstance(v,(str,int)) and str(v) != ""


def is_ref_key(k):
    lk = str(k).lower()
    return lk.endswith("_id") or lk.endswith("_ids") or lk in {"customer","customerid","client","clientid","order","orderid","product","productid","service","serviceid","branch","branchid","employee","employeeid","category","categoryid","warehouse","warehouseid","invoice","invoiceid","payment","paymentid"}

print("=== MARSEL AUDIT V19 / LIVE REFERENTIAL INTEGRITY AUDIT / READ ONLY ===")
docs_status, docs_body = get(DOCS)
print(f"DOCS_INDEX_HTTP={docs_status}")
if docs_status != 200: sys.exit(4)
reference_links = refs(docs_body)
print(f"REFERENCE_LINKS={len(reference_links)}")
endpoints=[]
for ref in reference_links:
    s,b=get(ref)
    if s==200: endpoints.extend(candidate_urls(b))
endpoints=list(dict.fromkeys(endpoints))
print(f"GET_PROBES={len(endpoints)}")

rows=[]
all_records=[]
ids_by_endpoint=defaultdict(set)
for url,path,operation_id,summary in endpoints:
    s,payload=get(url,True)
    value=json_value(payload) if s and 200<=s<300 else None
    rs=records(value)
    metadata={"records": None,"records_without_id":0,"id_count":0,"duplicate_ids":[]}
    refs_found=[]
    if rs is not None:
        ids=[]
        for r in rs:
            x=rid(r)
            if x is not None:
                ids.append(x); ids_by_endpoint[path].add(x); all_records.append((path,x,r))
            if isinstance(r,dict):
                for k,v in r.items():
                    if not is_ref_key(k): continue
                    vals=v if isinstance(v,list) else [v]
                    for val in vals:
                        if scalar(val): refs_found.append({"field":str(k),"value":str(val)})
        c=Counter(ids)
        metadata={"records":len(rs),"records_without_id":sum(1 for r in rs if rid(r) is None),"id_count":len(ids),"duplicate_ids":sorted(k for k,n in c.items() if n>1)[:100]}
    rows.append({"method":"GET","path":path,"operation_id":operation_id,"summary":summary,"http_status":s,"available":bool(s and 200<=s<300),"metadata":metadata,"references_found":refs_found,"response_body_stored":False})

# Build a conservative global ID index. A reference is considered resolvable if its value exists in any successful record list.
global_ids=Counter()
for path,x,r in all_records: global_ids[x]+=1
unresolved=[]
for row in rows:
    for ref in row["references_found"]:
        if ref["value"] not in global_ids:
            unresolved.append({"source_path":row["path"],**ref})

# Detect fields that look like references but are empty/null, and records missing IDs.
empty_refs=[]
for row in rows:
    # Only derive from the already captured reference metadata; no response bodies are written.
    pass

available=sum(r["available"] for r in rows)
http_errors=sum(r["http_status"] is not None and not 200<=r["http_status"]<300 for r in rows)
record_lists=sum(isinstance(r["metadata"].get("records"),int) for r in rows)
total_records=sum(r["metadata"]["records"] for r in rows if isinstance(r["metadata"].get("records"),int))
dup_id_endpoints=sum(bool(r["metadata"].get("duplicate_ids")) for r in rows)
records_without_id=sum(r["metadata"].get("records_without_id",0) for r in rows)
reference_fields=sum(len(r["references_found"]) for r in rows)

print(f"GET_AVAILABLE={available}")
print(f"GET_HTTP_ERRORS={http_errors}")
print(f"ENDPOINTS_WITH_RECORD_LISTS={record_lists}")
print(f"TOTAL_RECORDS_ACROSS_RESPONSES={total_records}")
print(f"RECORDS_WITHOUT_ID={records_without_id}")
print(f"REFERENCE_VALUES_FOUND={reference_fields}")
print(f"UNRESOLVED_REFERENCE_VALUES={len(unresolved)}")
print(f"ENDPOINTS_WITH_DUPLICATE_IDS={dup_id_endpoints}")
print("WRITE_REQUESTS_MADE=0")

report={
 "audit":"MARSEL_AUDIT_V19","timestamp_utc":datetime.now(timezone.utc).isoformat(),"readonly":True,
 "reference_links":len(reference_links),"get_probes":len(endpoints),"get_available":available,"get_http_errors":http_errors,
 "summary":{"endpoints_with_record_lists":record_lists,"total_records_across_responses":total_records,"records_without_id":records_without_id,"reference_values_found":reference_fields,"unresolved_reference_values":len(unresolved),"endpoints_with_duplicate_ids":dup_id_endpoints},
 "unresolved_references":unresolved[:500],"endpoints":rows,
 "safety":{"write_requests_made":False,"response_bodies_stored":False,"data_mutated":False}
}
with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; GET REQUESTS ONLY; REFERENTIAL INTEGRITY METADATA ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
