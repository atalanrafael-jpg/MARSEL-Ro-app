#!/usr/bin/env python3
"""MARSEL V18 — resilient documentation discovery + GET-only API audit, stdlib only."""
import html, json, os, re, sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urljoin, unquote
from urllib.request import Request, urlopen

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS_INDEX = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = os.environ.get("MARSEL_AUDIT_OUT", "marsel-live-api-readonly-v18.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "45"))
UA = "Mozilla/5.0 (compatible; MARSEL-LIVE-AUDIT/18.0; +https://github.com/atalanrafael-jpg/Ro-app)"

if not KEY:
    print("ERROR: ROAPP_API_KEY is not configured")
    sys.exit(2)


def fetch(url, api=False):
    headers = {"User-Agent": UA, "Accept": "text/plain, text/markdown, text/html, application/json, */*"}
    if api:
        headers["Authorization"] = f"Bearer {KEY}"
    req = Request(url, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=TIMEOUT) as r:
            return r.status, r.read(), None
    except HTTPError as e:
        return e.code, e.read(), None
    except (URLError, TimeoutError, OSError) as e:
        return None, b"", f"{type(e).__name__}: {e}"


def clean(raw):
    s = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else (raw or "")
    return html.unescape(s).replace("\\/", "/")


def refs(text):
    s = clean(text); out=[]; seen=set()
    for p in (r"\[[^\]]*\]\((https://roapp\.readme\.io/reference/[^)\s]+)", r"https://roapp\.readme\.io/reference/[A-Za-z0-9_./?=&%#:+~-]+"):
        for m in re.finditer(p, s, re.I):
            u = m.group(1) if m.lastindex else m.group(0)
            u = u.rstrip(".,;\"'`)]}")
            if u not in seen: seen.add(u); out.append(u)
    return out


def normalize(raw, page_url):
    raw = clean(raw).strip().strip("<>\"'`.,;)]}")
    if raw.startswith("//"): raw = "https:" + raw
    elif raw.startswith("/"): raw = urljoin(BASE + "/", raw)
    elif raw.startswith("api.roapp.io/"): raw = "https://" + raw
    if not re.match(r"^https://", raw, re.I): return None
    p = urlparse(raw)
    if p.netloc.lower() != "api.roapp.io" or not p.path.startswith("/v2/"): return None
    return raw


def safe(url):
    return not re.search(r"\{[^}]+\}|<[^>]+>|\[[^]]+\]|:[A-Za-z_][A-Za-z0-9_-]*", url)


def discover(page, ref):
    s=clean(page); out=[]; seen=set()
    patterns=[
        r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(https://api\.roapp\.io/v2[^\s<\"'`]+)",
        r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(/v2/[^\s<\"'`]+)",
        r"(?:curl\s+(?:-X\s+)?)(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)?\s*(?:[^\n]*?\s)?(https://api\.roapp\.io/v2[^\s\"'`]+)",
    ]
    for p in patterns:
        for m in re.finditer(p,s,re.I):
            method=(m.group(1) or "GET").upper(); u=normalize(m.group(2),ref)
            if u:
                k=(method,u)
                if k not in seen: seen.add(k); out.append({"method":method,"url":u,"source":"explicit"})
    for m in re.finditer(r"https://api\.roapp\.io/v2/[A-Za-z0-9_./?=&%#:+~-]+",s,re.I):
        u=normalize(m.group(0),ref)
        if not u: continue
        context=s[max(0,m.start()-100):m.start()]
        method="UNKNOWN" if re.search(r"\b(POST|PUT|PATCH|DELETE)\s*$",context,re.I) else "GET"
        k=(method,u)
        if k not in seen: seen.add(k); out.append({"method":method,"url":u,"source":"raw_url"})
    for m in re.finditer(r"[\"']?(?:path|url|endpoint)[\"']?\s*[:=]\s*[\"'](/v2/[A-Za-z0-9_./?=&%#:+~-]+)[\"']",s,re.I):
        u=normalize(m.group(1),ref)
        if u and safe(u) and ("GET",u) not in seen:
            seen.add(("GET",u)); out.append({"method":"GET","url":u,"source":"structured_path"})
    return out

print("=== MARSEL AUDIT V18 / RESILIENT DOC DISCOVERY / GET-ONLY / READ ONLY ===")
print(f"BASE={BASE}"); print(f"DOCS_INDEX={DOCS_INDEX}")
st, body, terr=fetch(DOCS_INDEX); print(f"DOCS_INDEX_HTTP={st}")
if st != 200:
    print("RESULT=READ_ONLY; DOCUMENTATION INDEX UNAVAILABLE; NO RO APP DATA CREATED, UPDATED OR DELETED"); sys.exit(4)
links=refs(body); print(f"REFERENCE_LINKS={len(links)}")
allc=[]; page_errors=[]
for ref in links:
    ps,pb,pe=fetch(ref)
    if ps is None: page_errors.append({"url":ref,"error":pe}); continue
    for ep in discover(pb,ref): ep.update(reference_url=ref, reference_http=ps); allc.append(ep)
uniq={}
for ep in allc:
    k=(ep["method"],ep["url"])
    if k not in uniq: uniq[k]={**ep,"sources":[ep["reference_url"]]}
    elif ep["reference_url"] not in uniq[k]["sources"]: uniq[k]["sources"].append(ep["reference_url"])
candidates=list(uniq.values())
getc=[x for x in candidates if x["method"]=="GET" and safe(x["url"])]
blocked=[x for x in candidates if x["method"]!="GET" or not safe(x["url"])]
print(f"ENDPOINT_CANDIDATES={len(candidates)}"); print(f"GET_CANDIDATES={len(getc)}"); print(f"BLOCKED_NON_GET_OR_UNSAFE={len(blocked)}"); print("WRITE_REQUESTS_PLANNED=0")
results=[]
for ep in getc:
    rs,payload,err=fetch(ep["url"],api=True)
    results.append({**ep,"http_status":rs,"response_bytes":len(payload or b""),"available":bool(rs and 200<=rs<300),"error_class":"none" if rs and 200<=rs<300 else ("http_error" if rs is not None else "transport_error"),"transport_error":err})
avail=sum(x["available"] for x in results); herr=sum(x["error_class"]=="http_error" for x in results); terrs=sum(x["error_class"]=="transport_error" for x in results)
print(f"GET_PROBES={len(results)}"); print(f"GET_AVAILABLE={avail}"); print(f"GET_HTTP_ERRORS={herr}"); print(f"GET_TRANSPORT_ERRORS={terrs}")
report={"audit":"MARSEL_AUDIT_V18","timestamp_utc":datetime.now(timezone.utc).isoformat(),"readonly":True,"documentation":{"index":DOCS_INDEX,"http_status":st,"reference_count":len(links),"page_errors":page_errors},"discovery":{"endpoint_candidates":len(candidates),"get_candidates":len(getc),"blocked_non_get_or_unsafe":len(blocked),"candidates":candidates},"get_results":results,"safety":{"api_requests_made":bool(results),"get_requests_made":bool(results),"write_requests_made":False,"post_requests_made":False,"put_requests_made":False,"patch_requests_made":False,"delete_requests_made":False,"updates_performed":False,"deletes_performed":False,"pii_persisted":False}}
with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(f"REPORT={OUT}"); print("RESULT=READ_ONLY; GET REQUESTS ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
