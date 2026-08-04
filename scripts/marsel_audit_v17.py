#!/usr/bin/env python3
"""MARSEL V17 — live GET-only API audit, documentation-driven, stdlib only."""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS_INDEX = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = os.environ.get("MARSEL_AUDIT_OUT", "marsel-live-api-readonly-v17.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "45"))
UA = "Mozilla/5.0 (compatible; MARSEL-LIVE-AUDIT/17.0; +https://github.com/atalanrafael-jpg/Ro-app)"

if not KEY:
    print("ERROR: ROAPP_API_KEY is not configured")
    sys.exit(2)


def fetch(url, api=False):
    headers = {"User-Agent": UA, "Accept": "text/plain, text/markdown, text/html, application/json, */*"}
    if api:
        headers["Authorization"] = f"Bearer {KEY}"
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=TIMEOUT) as r:
            return r.status, r.read()
    except HTTPError as e:
        return e.code, e.read()
    except (URLError, TimeoutError, OSError) as e:
        return None, str(e).encode()


def links(text):
    out=[]; seen=set()
    for m in re.finditer(r"\[([^\]]+)\]\((https://roapp\.readme\.io/reference/[^)]+)\)", text or ""):
        title=m.group(1).strip(); url=m.group(2).strip()
        if url not in seen:
            seen.add(url); out.append({"title":title,"url":url})
    return out


def endpoint_candidates(html):
    s = html.decode("utf-8", "replace") if isinstance(html, bytes) else html
    found=[]; seen=set()
    # Covers common ReadMe-rendered forms: GET /v2/orders, curl examples, and full API URLs.
    patterns = [
        r"\b(GET|POST|PUT|PATCH|DELETE)\s+(https://api\.roapp\.io/v2[^\s<\"'`]+)",
        r"\b(GET|POST|PUT|PATCH|DELETE)\s+(/v2/[^\s<\"'`]+)",
        r"https://api\.roapp\.io/v2/[^\s<\"'`]+",
    ]
    for i,p in enumerate(patterns):
        for m in re.finditer(p,s,re.I):
            if i<2:
                method=m.group(1).upper(); raw=m.group(2)
            else:
                method="UNKNOWN"; raw=m.group(0)
            raw=raw.rstrip(".,;\"'`)]}")
            if raw.startswith("/v2/"): url="https://api.roapp.io"+raw
            else: url=raw
            key=(method,url)
            if key not in seen:
                seen.add(key); found.append({"method":method,"url":url})
    return found


def safe_url(url):
    # Never execute templated/parameterized URLs in V17.
    return not re.search(r"\{[^}]+\}|<[^>]+>|\[[^]]+\]", url)

print("=== MARSEL AUDIT V17 / LIVE GET-ONLY API AUDIT / READ ONLY ===")
print(f"BASE={BASE}")
print(f"DOCS_INDEX={DOCS_INDEX}")
status, body = fetch(DOCS_INDEX)
print(f"DOCS_INDEX_HTTP={status}")
if status != 200:
    print("RESULT=READ_ONLY; DOCUMENTATION INDEX UNAVAILABLE; NO RO APP DATA CREATED, UPDATED OR DELETED")
    sys.exit(4)
refs=links(body.decode("utf-8","replace"))
print(f"REFERENCE_LINKS={len(refs)}")

all_candidates=[]
for r in refs:
    st, page=fetch(r["url"])
    for ep in endpoint_candidates(page if st else b""):
        ep.update({"title":r["title"],"reference_url":r["url"],"reference_http":st})
        all_candidates.append(ep)

# Strict safety gate: only explicit GET candidates, no templated URLs.
get_candidates=[]; seen=set()
for ep in all_candidates:
    if ep["method"] != "GET" or not safe_url(ep["url"]):
        continue
    if ep["url"] not in seen:
        seen.add(ep["url"]); get_candidates.append(ep)

print(f"ENDPOINT_CANDIDATES={len(all_candidates)}")
print(f"GET_CANDIDATES={len(get_candidates)}")
print("WRITE_REQUESTS_PLANNED=0")

results=[]
for ep in get_candidates:
    st, payload=fetch(ep["url"], api=True)
    results.append({
        **ep,
        "http_status":st,
        "response_bytes":len(payload or b""),
        "available": st is not None and 200 <= st < 300,
        "error_class": "none" if st is not None and 200 <= st < 300 else ("http_error" if st is not None else "transport_error"),
    })

available=sum(1 for x in results if x["available"])
http_errors=sum(1 for x in results if x["error_class"]=="http_error")
transport_errors=sum(1 for x in results if x["error_class"]=="transport_error")
print(f"GET_PROBES={len(results)}")
print(f"GET_AVAILABLE={available}")
print(f"GET_HTTP_ERRORS={http_errors}")
print(f"GET_TRANSPORT_ERRORS={transport_errors}")

report={
 "audit":"MARSEL_AUDIT_V17",
 "timestamp_utc":datetime.now(timezone.utc).isoformat(),
 "readonly":True,
 "documentation":{"index":DOCS_INDEX,"http_status":status,"reference_count":len(refs)},
 "discovery":{"endpoint_candidates":len(all_candidates),"get_candidates":len(get_candidates)},
 "get_results":results,
 "safety":{"api_requests_made":bool(results),"get_requests_made":bool(results),"write_requests_made":False,"post_requests_made":False,"put_requests_made":False,"patch_requests_made":False,"delete_requests_made":False,"updates_performed":False,"deletes_performed":False,"pii_persisted":False}
}
with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; GET REQUESTS ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
