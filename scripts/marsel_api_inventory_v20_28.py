#!/usr/bin/env python3
"""MARSEL V20.28 — RO App API inventory, READ ONLY.

Combines explicit API evidence from ReadMe reference pages with operation-title
classification. Titles are never converted into guessed URL paths; only explicit
API URLs/paths are eligible for live GET probing.
"""
from __future__ import annotations
import hashlib, html, json, os, re, sys, time
from urllib.parse import urljoin, urlparse, urlsplit
from urllib.request import Request, urlopen

VERSION="20.28"
DOCS_INDEX=os.environ.get("ROAPP_DOCS_INDEX","https://roapp.readme.io/llms.txt")
BASE=os.environ.get("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.environ.get("ROAPP_API_KEY","")
OUT=os.environ.get("MARSEL_API_INVENTORY_OUTPUT","marsel-api-inventory-v20-28.json")
TIMEOUT=int(os.environ.get("ROAPP_TIMEOUT","30")); MAX_DOCS=int(os.environ.get("MARSEL_MAX_DOCS","300"))
MIN_INTERVAL=float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL","0.34")); MAX_RETRIES=int(os.environ.get("ROAPP_MAX_RETRIES","3")); RETRY_BASE=float(os.environ.get("ROAPP_RETRY_BASE_SECONDS","0.75"))
METHODS={"GET","POST","PUT","PATCH","DELETE"}
TITLE_METHODS={"get":"GET","create":"POST","add":"POST","update":"PUT","delete":"DELETE","merge":"POST","change":"PATCH"}
METHOD_PATH_RE=re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b\s*(?:[:\-]\s*)?(https?://api\.roapp\.io[^\s<>'\"`]+|/(?:v2|1\.1)(?:/[^\s<>'\"`]*)?)",re.I)
FULL_API_RE=re.compile(r"https?://api\.roapp\.io[^\s<>'\"`]+",re.I)
PATH_RE=re.compile(r"/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$]+)?",re.I)
HREF_RE=re.compile(r"(?:href|src)\s*=\s*[\"']([^\"']+)[\"']",re.I)
_last=0.0

def fetch(url,headers=None):
 global _last
 hdr=headers or {"User-Agent":f"MARSEL-Audit-V{VERSION}","Accept":"text/plain,text/markdown,text/html,application/json,application/yaml,text/yaml"}
 last=None
 for attempt in range(MAX_RETRIES+1):
  wait=MIN_INTERVAL-(time.monotonic()-_last)
  if wait>0: time.sleep(wait)
  req=Request(url,headers=hdr,method="GET"); started=time.time()
  try:
   _last=time.monotonic()
   with urlopen(req,timeout=TIMEOUT) as r:
    body=r.read().decode("utf-8",errors="replace"); status=r.status
    if status not in {408,425,429,500,502,503,504} or attempt>=MAX_RETRIES: return status,body,round(time.time()-started,3),None
  except Exception as exc:
   last=f"{type(exc).__name__}: {exc}"
   if attempt>=MAX_RETRIES: return None,"",round(time.time()-started,3),last
  time.sleep(min(RETRY_BASE*(2**attempt),30.0))
 return None,"",0,last or "request failed"

def clean(s): return html.unescape(str(s)).strip().replace("\\/","/").strip("`'\"<>[](){};,.:")
def normalize_path(raw):
 raw=clean(raw)
 if raw.startswith(("http://","https://")):
  p=urlparse(raw)
  if p.netloc.lower()!="api.roapp.io": return None
  raw=p.path
 raw=raw.split("#",1)[0]
 if raw in {"/v2","/v2/","/1.1","/1.1/"}: return None
 if raw.startswith(("/v2/","/1.1/")):
  raw=re.sub(r"/v2/v2/","/v2/",raw); raw=re.sub(r"/1\.1/1.1/","/1.1/",raw); return raw
 return None

def title_method(title):
 first=title.strip().split(None,1)[0].casefold() if title.strip() else ""
 return TITLE_METHODS.get(first)

def add(store,method,path,evidence,source,detail):
 if method not in METHODS: return
 p=normalize_path(path)
 if not p:return
 key=(method,p); rank={"OPENAPI_CONFIRMED":4,"DOCUMENTATION_CONFIRMED":3,"URL_CONFIRMED":2}
 if key not in store: store[key]={"method":method,"path":p,"evidence":evidence,"sources":[source] if source else [],"details":[detail] if detail else []}; return
 item=store[key]
 if source and source not in item["sources"]:item["sources"].append(source)
 if detail and detail not in item["details"]:item["details"].append(detail)
 if rank[evidence]>rank[item["evidence"]]:item["evidence"]=evidence

def extract_paths(text,source,store):
 t=html.unescape(text).replace("\\/","/")
 for m in METHOD_PATH_RE.finditer(t): add(store,m.group(1).upper(),m.group(2),"DOCUMENTATION_CONFIRMED",source,"explicit method/path")
 for m in FULL_API_RE.finditer(t):
  p=normalize_path(m.group(0))
  if not p:continue
  win=t[max(0,m.start()-800):m.end()+200]; ms=list(re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE)\b",win,re.I)); method=ms[-1].group(1).upper() if ms else "GET"
  add(store,method,p,"DOCUMENTATION_CONFIRMED" if ms else "URL_CONFIRMED",source,"full API URL")
 for m in HREF_RE.finditer(t):
  p=normalize_path(m.group(1))
  if not p:continue
  win=t[max(0,m.start()-800):m.end()+200]; ms=list(re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE)\b",win,re.I)); method=ms[-1].group(1).upper() if ms else "GET"
  add(store,method,p,"DOCUMENTATION_CONFIRMED" if ms else "URL_CONFIRMED",source,"HTML API link")
 for m in PATH_RE.finditer(t):
  p=normalize_path(m.group(0))
  if not p:continue
  win=t[max(0,m.start()-800):m.end()+200]; ms=list(re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE)\b",win,re.I)); method=ms[-1].group(1).upper() if ms else "GET"
  add(store,method,p,"DOCUMENTATION_CONFIRMED" if ms else "URL_CONFIRMED",source,"path expression")

def build_url(path):
 b=urlsplit(BASE); bp=b.path.rstrip("/"); np="/"+path.lstrip("/")
 if bp and (np==bp or np.startswith(bp+"/")): final=np
 else: final=bp+np
 return b._replace(path=final).geturl()

def has_placeholder(p): return bool(re.search(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>",p))
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()

def main():
 if not KEY: print("ROAPP_API_KEY is required",file=sys.stderr); return 2
 st,index,_,err=fetch(DOCS_INDEX)
 if st!=200: print(f"DOCS_INDEX_HTTP={st}",file=sys.stderr); print(err or "documentation index unavailable",file=sys.stderr); return 1
 links=[];seen=set()
 for m in re.finditer(r"\[([^\]]+)\]\(([^)]+/reference/[^)]+)\)",index):
  title,href=m.groups();u=urljoin(DOCS_INDEX,clean(href))
  if u not in seen:seen.add(u);links.append({"title":html.unescape(title).strip(),"url":u})
 links=links[:MAX_DOCS]
 ops={}; pages=[]
 for link in links:
  variants=[link["url"]]+([link["url"][:-3]] if link["url"].endswith(".md") else [])
  bodies=[];responses=[]
  for u in dict.fromkeys(variants):
   s,body,e,er=fetch(u);responses.append({"url":u,"http":s,"elapsed_s":e,"error":er})
   if s==200:bodies.append(body);extract_paths(body,u,ops)
  method=title_method(link["title"]); explicit_methods=sorted({x["method"] for x in ops.values() if link["url"] in x["sources"]})
  pages.append({"title":link["title"],"documentation_url":link["url"],"responses":responses,"content_found":bool(bodies),"title_method":method,"explicit_methods":explicit_methods,"path_evidence_count":sum(1 for x in ops.values() if link["url"] in x["sources"])})
 probes=[];seen_get=set();headers={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":f"MARSEL-Audit-V{VERSION}"}
 for op in sorted(ops.values(),key=lambda x:(x["path"],x["method"])):
  if op["method"]!="GET":continue
  if has_placeholder(op["path"]): probes.append({"method":"GET","path":op["path"],"status":"NOT_PROBED","reason":"parameterized path; no identifier guessed"});continue
  if op["path"] in seen_get:continue
  seen_get.add(op["path"]);u=build_url(op["path"]);s,body,e,er=fetch(u,headers=headers);item={"method":"GET","path":op["path"],"url":u,"http":s,"elapsed_s":e,"error":er}
  if s==200:
   try:
    d=json.loads(body);item["json_valid"]=True;item["json_type"]=type(d).__name__;item["top_level_keys"]=sorted(d.keys())[:50] if isinstance(d,dict) else None
   except json.JSONDecodeError:item["json_valid"]=False;item["error"]="successful HTTP response is not valid JSON"
  else:item["json_valid"]=None
  probes.append(item)
 report={"version":VERSION,"readonly":True,"method_policy":{"allowed":["GET"],"blocked":["POST","PUT","PATCH","DELETE"]},"write_requests_made":0,"ro_app_data_mutated":False,"sources":{"documentation_index":DOCS_INDEX,"api_base":BASE},"documentation":{"pages_discovered":len(links),"pages_fetched":sum(1 for p in pages if p["content_found"]),"pages_with_explicit_api_path_evidence":sum(1 for p in pages if p["path_evidence_count"]>0)},"operations":sorted(ops.values(),key=lambda x:(x["path"],x["method"])),"get_probes":probes,"summary":{"unique_confirmed_operations":len(ops),"get_operations":sum(1 for x in ops.values() if x["method"]=="GET"),"non_get_operations":sum(1 for x in ops.values() if x["method"]!="GET"),"get_probes_attempted":sum(1 for p in probes if p.get("status")!="NOT_PROBED"),"get_probes_http_200":sum(1 for p in probes if p.get("http")==200),"parameterized_not_probed":sum(1 for p in probes if p.get("status")=="NOT_PROBED"),"write_requests_made":0},"contract_state":{"completeness_claim":"NOT_ESTABLISHED","title_method_classification_is_not_url_evidence":True,"parameterized_identifiers_guessed":False},"safety":{"status":"PASS","write_requests_made":0,"ro_app_data_mutated":False},"reference_pages":[{"title":p["title"],"documentation_url":p["documentation_url"],"title_method":p["title_method"],"content_found":p["content_found"],"path_evidence_count":p["path_evidence_count"]} for p in pages],"generated_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
 with open(OUT,"w",encoding="utf-8") as f:json.dump(report,f,ensure_ascii=False,indent=2,sort_keys=True)
 report["report_sha256"]=sha(OUT)
 with open(OUT,"w",encoding="utf-8") as f:json.dump(report,f,ensure_ascii=False,indent=2,sort_keys=True)
 print(f"V{VERSION}_INVENTORY=PASS");print(f"REFERENCE_PAGES={len(links)}");print(f"CONFIRMED_OPERATIONS={len(ops)}");print(f"GET_PROBES_ATTEMPTED={report['summary']['get_probes_attempted']}");print("WRITE_REQUESTS_MADE=0");print("RO_APP_DATA_MUTATED=false");print(f"REPORT_SHA256={report['report_sha256']}")
 return 0
if __name__=="__main__":raise SystemExit(main())
