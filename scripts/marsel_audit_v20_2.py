#!/usr/bin/env python3
"""MARSEL V20.2 — read-only API/data-reference verification.

V20.2 fixes three V20.1 audit problems:
1) list requests start with pageSize=100 and continue pagination when supported;
2) ad_campaign_id is treated as a marketing reference, not a local entity-integrity reference;
3) expected 403/404 detail probes are reported as access/not-found observations, not generic HTTP errors.
Only GET requests are made. No RO App data is created, updated or deleted.
"""
import json, os, re, sys, time
from collections import defaultdict
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl
from urllib.request import Request, urlopen
from datetime import datetime, timezone

API_BASE=os.environ.get("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.environ.get("ROAPP_API_KEY")
DOCS=os.environ.get("ROAPP_DOCS_INDEX","https://roapp.readme.io/llms.txt")
OUT="marsel-reference-verification-v20-2.json"
if not KEY: sys.exit("ROAPP_API_KEY is not configured")
H={"User-Agent":"MARSEL-REFERENCE-VERIFICATION/20.2","Accept":"application/json,text/plain,*/*"}

def get(url, api=False):
    h=dict(H)
    if api: h["Authorization"]=f"Bearer {KEY}"
    try:
        with urlopen(Request(url,headers=h),timeout=45) as r: return r.status,r.read()
    except HTTPError as e: return e.code,e.read()
    except (URLError,TimeoutError,OSError) as e: return None,str(e).encode()

def txt(v): return v.decode("utf-8","replace") if isinstance(v,bytes) else str(v)
def j(v):
    try:return json.loads(txt(v))
    except Exception:return None

def specs(v):
    out=[]
    for m in re.finditer(r"```json\s*(\{.*?\})\s*```",txt(v),re.S):
        try:
            x=json.loads(m.group(1))
            if isinstance(x,dict) and isinstance(x.get("paths"),dict):out.append(x)
        except Exception:pass
    return out

def endpoints(page):
    out=[]
    for spec in specs(page):
        server=((spec.get("servers") or [{}])[0].get("url") or API_BASE).rstrip("/")
        for path,item in (spec.get("paths") or {}).items():
            if not isinstance(item,dict) or "get" not in item:continue
            op=item["get"] if isinstance(item["get"],dict) else {}
            ps=(item.get("parameters") or [])+(op.get("parameters") or [])
            q=[]; pp=[]
            for p in ps:
                if not isinstance(p,dict) or not p.get("name"):continue
                name=p["name"]; loc=p.get("in"); sc=p.get("schema") or {}
                ex=p.get("example",sc.get("example",sc.get("default")))
                if loc=="query" and ex is not None:q.append((name,str(ex)))
                elif loc=="path":pp.append({"name":name,"example":None if ex is None else str(ex)})
            url=server+("/" if not path.startswith("/") else "")+path
            out.append({"url":url,"path":path,"operation_id":op.get("operationId"),"query":q,"path_params":pp})
    return list({(x["path"],x["operation_id"],x["url"]):x for x in out}.values())

def rows(payload):
    if isinstance(payload,list):return payload,payload
    if isinstance(payload,dict):
        for k in ("data","items","results","records","rows"):
            if isinstance(payload.get(k),list):return payload[k],payload
    return None,payload

def rid(r):
    if not isinstance(r,dict):return None
    for k in ("id","ID","uuid","uid"):
        if isinstance(r.get(k),(str,int)) and str(r[k]):return str(r[k])
    return None

def qurl(url,extra):
    p=urlsplit(url); q=dict(parse_qsl(p.query,keep_blank_values=True)); q.update(extra)
    return urlunsplit((p.scheme,p.netloc,p.path,urlencode(q),p.fragment))

def substitute(url,params):
    for k,v in params.items():url=url.replace("{"+k+"}",str(v))
    return url

def pagination(meta):
    if not isinstance(meta,dict):return None,None,None
    ms=[meta]+[meta[k] for k in ("meta","pagination") if isinstance(meta.get(k),dict)]
    total=None; nxt=None; style=None
    for m in ms:
        for k in ("total","count","total_count","totalRecords","total_records"):
            if isinstance(m.get(k),int):total=m[k];break
        for k in ("nextPageIndex","next_page_index","nextPage","next_page"):
            if isinstance(m.get(k),(int,str)) and str(m[k]):nxt=m[k];style="pageIndex";break
        if isinstance(m.get("nextPageToken"),str) and m["nextPageToken"]:nxt=m["nextPageToken"];style="pageToken"
        if isinstance(m.get("next"),str) and m["next"]:nxt=m["next"];style="url"
        if nxt is not None:break
    return total,nxt,style

def fetch_list(ep):
    base=substitute(ep["url"],{})
    if "{" in base:return [],[],0,{"status":"SKIPPED_MISSING_PATH_PARAMETER"}
    baseq=dict(ep["query"]);baseq.setdefault("pageSize","100")
    # Always request the maximum documented page size first.
    u=qurl(base,baseq);s,b=get(u,True)
    if not (s and 200<=s<300):return [],[{"url":u,"status":s,"kind":"HTTP_ERROR"}],1,{}
    rr,meta=rows(j(b))
    if rr is None:return [],[],1,{"non_list_response":True}
    allr=list(rr);total,nxt,style=pagination(meta);pages=1
    if style in ("pageIndex","pageToken"):
        while nxt is not None and pages<1000:
            time.sleep(.36); param="pageIndex" if style=="pageIndex" else "pageToken"
            s,b=get(qurl(base,{**baseq,param:str(nxt)}),True);pages+=1
            if not(s and 200<=s<300):return allr,[{"url":qurl(base,{**baseq,param:str(nxt)}),"status":s,"kind":"HTTP_ERROR"}],pages,{"total":total,"pagination_style":style}
            rr,meta=rows(j(b))
            if not rr:break
            allr.extend(rr);_,nxt,_=pagination(meta)
    elif total is not None and total>len(allr):
        page=2
        while len(allr)<total and page<1000:
            time.sleep(.36);u=qurl(base,{**baseq,"page":str(page)});s,b=get(u,True);pages+=1
            if not(s and 200<=s<300):return allr,[{"url":u,"status":s,"kind":"HTTP_ERROR"}],pages,{"total":total,"pagination_style":"page"}
            rr,_=rows(j(b))
            if not rr:break
            allr.extend(rr);page+=1
    elif len(allr)>=100:
        # If API omits pagination metadata, continue page-by-page until a short page.
        page=2
        while len(allr)%100==0 and page<1000:
            time.sleep(.36);u=qurl(base,{**baseq,"page":str(page)});s,b=get(u,True);pages+=1
            if not(s and 200<=s<300):return allr,[{"url":u,"status":s,"kind":"HTTP_ERROR"}],pages,{"pagination_style":"heuristic-page"}
            rr,_=rows(j(b))
            if not rr:break
            allr.extend(rr)
            if len(rr)<100:break
            page+=1
    return allr,[],pages,{"total":total,"pagination_style":style or ("pageSize100" if len(allr)>0 else None)}

# These are references whose authoritative target is outside the standard local entity collections.
EXTERNAL_REFERENCE_FIELDS={"ad_campaign_id","ad_campaign_ids"}
ENTITY_ALIASES={"people":"people","organizations":"organizations","services":"services","products":"products","orders":"orders","sales":"sales","employees":"employees","locations":"locations","branches":"locations","categories":"categories","uoms":"uoms","invoices":"invoices","accounts":"accounts","refunds":"refunds"}

def entity_hint(field,path):
    f=str(field).lower();p=path.lower()
    if f in EXTERNAL_REFERENCE_FIELDS:return "external:ad_campaign"
    for key in ENTITY_ALIASES:
        if key in f:return ENTITY_ALIASES[key]
    for key in ENTITY_ALIASES:
        if key in p:return ENTITY_ALIASES[key]
    return "unknown"

def ref_field(k):
    lk=str(k).lower()
    return lk.endswith("_id") or lk.endswith("_ids") or lk in {"customer","client","order","product","service","branch","employee","category","warehouse","invoice","payment","author","assignee","manager","technician","uom"}

def main():
    print("=== MARSEL AUDIT V20.2 / PAGINATION + REFERENCE CLASSIFICATION / READ ONLY ===")
    ds,db=get(DOCS);print(f"DOCS_INDEX_HTTP={ds}")
    if ds!=200:sys.exit(4)
    links=list(dict.fromkeys(re.findall(r"https://roapp\.readme\.io/reference/[^)\s]+",txt(db))))
    print(f"REFERENCE_LINKS={len(links)}")
    eps=[]
    for ref in links:
        s,b=get(ref)
        if s==200:eps.extend(endpoints(b))
    eps=list({(e["path"],e["operation_id"],e["url"]):e for e in eps}.values());print(f"GET_CANDIDATES={len(eps)}")
    lists=[e for e in eps if not e["path_params"]];details=[e for e in eps if e["path_params"]]
    ids=defaultdict(set);refs=[];stats=[];errors=[];access=[];skipped=[];seen=0
    for ep in lists:
        rr,er,pages,meta=fetch_list(ep);errors+=er;seen+=len(rr);stats.append({"path":ep["path"],"operation_id":ep["operation_id"],"records":len(rr),"pages_attempted":pages,"meta":meta})
        ent=next((v for k,v in ENTITY_ALIASES.items() if k in ep["path"].lower()),"unknown")
        for r in rr:
            x=rid(r)
            if x:ids[ent].add(x)
            if isinstance(r,dict):
                for k,v in r.items():
                    if not ref_field(k):continue
                    vals=v if isinstance(v,list) else [v]
                    for val in vals:
                        if isinstance(val,(str,int)) and str(val):refs.append({"source_path":ep["path"],"field":str(k),"value":str(val),"entity_hint":entity_hint(k,ep["path"])})
    gids=set().union(*ids.values()) if ids else set();uniq={(r["source_path"],r["field"],r["value"]):r for r in refs};results=[]
    for r in uniq.values():
        if r["entity_hint"].startswith("external:"):
            results.append({**r,"classification":"EXTERNAL_REFERENCE_NOT_AUDITED","severity":"INFO","reason":"Reference points to an external/marketing domain not covered by the standard entity collections."});continue
        ent=r["entity_hint"]
        if ent!="unknown" and r["value"] in ids.get(ent,set()):
            results.append({**r,"classification":"RESOLVED_ENTITY_MATCH","severity":"INFO","reason":"Reference matches a retrieved ID in the inferred target entity."})
        elif r["value"] in gids:
            results.append({**r,"classification":"RESOLVED_CROSS_ENTITY_ID","severity":"REVIEW","reason":"Reference exists elsewhere but not in the inferred target entity."})
        else:
            results.append({**r,"classification":"UNRESOLVED_AFTER_COLLECTION_SCAN","severity":"REVIEW","reason":"Reference not found in the complete retrieved collection set."})
    # Detail probes are observational only. 404 = not found; 403 = access/endpoint restriction, neither is a generic HTTP error.
    for ep in details:
        if len(ep["path_params"])!=1:skipped.append({"path":ep["path"],"reason":"MULTIPLE_PATH_PARAMETERS"});continue
        p=ep["path_params"][0];target=next((v for k,v in ENTITY_ALIASES.items() if k in ep["path"].lower()),"unknown")
        cand=list(ids.get(target,set()))[:3]
        if not cand and p.get("example"):cand=[p["example"]]
        if not cand:skipped.append({"path":ep["path"],"reason":"NO_SAFE_REFERENCE_ID"});continue
        for val in cand:
            u=substitute(ep["url"],{p["name"]:val});s,_=get(qurl(u,dict(ep["query"])),True)
            if s==403:access.append({"path":ep["path"],"value":val,"status":403,"classification":"ACCESS_RESTRICTION"})
            elif s==404:access.append({"path":ep["path"],"value":val,"status":404,"classification":"NOT_FOUND"})
            elif not(s and 200<=s<300):errors.append({"url":u,"status":s,"kind":"UNEXPECTED_DETAIL_HTTP_ERROR"})
    unresolved=[r for r in results if r["classification"]=="UNRESOLVED_AFTER_COLLECTION_SCAN"]
    out={"version":"20.2","timestamp_utc":datetime.now(timezone.utc).isoformat(),"readonly":True,"data_mutated":False,"write_requests_made":False,"docs_index_http":ds,"reference_links":len(links),"get_candidates":len(eps),"records_seen_after_pagination":seen,"unique_reference_values":len(uniq),"resolved_entity_match":sum(r["classification"]=="RESOLVED_ENTITY_MATCH" for r in results),"resolved_cross_entity_id":sum(r["classification"]=="RESOLVED_CROSS_ENTITY_ID" for r in results),"external_references":sum(r["classification"]=="EXTERNAL_REFERENCE_NOT_AUDITED" for r in results),"unresolved_after_readonly_verification":len(unresolved),"http_errors":len(errors),"access_restrictions":len(access),"skipped_endpoints":len(skipped),"reference_results":results,"endpoint_stats":stats,"skipped_endpoints_detail":skipped,"detail_checks":access,"http_error_detail":errors}
    with open(OUT,"w",encoding="utf-8") as f:json.dump(out,f,ensure_ascii=False,indent=2)
    print(f"RECORDS_SEEN_AFTER_PAGINATION={seen}");print(f"UNIQUE_REFERENCE_VALUES={len(uniq)}");print(f"RESOLVED_ENTITY_MATCH={out['resolved_entity_match']}");print(f"RESOLVED_CROSS_ENTITY_ID={out['resolved_cross_entity_id']}");print(f"EXTERNAL_REFERENCES={out['external_references']}");print(f"UNRESOLVED_AFTER_READONLY_VERIFICATION={len(unresolved)}");print(f"HTTP_ERRORS={len(errors)}");print(f"ACCESS_RESTRICTIONS={len(access)}");print(f"SKIPPED_ENDPOINTS={len(skipped)}");print("WRITE_REQUESTS_MADE=0");print(f"REPORT={OUT}");print("RESULT=READ_ONLY; V20.2; NO RO APP DATA CREATED, UPDATED OR DELETED")
if __name__=="__main__":main()
