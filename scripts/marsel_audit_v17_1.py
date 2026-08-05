#!/usr/bin/env python3
"""MARSEL V17.1 — OpenAPI-driven live GET-only audit, stdlib only."""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS_INDEX = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = os.environ.get("MARSEL_AUDIT_OUT", "marsel-live-api-readonly-v17-1.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "45"))
UA = "Mozilla/5.0 (compatible; MARSEL-LIVE-AUDIT/17.1; +https://github.com/atalanrafael-jpg/Ro-app)"

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


def reference_links(text):
    out, seen = [], set()
    for m in re.finditer(r"\[([^\]]+)\]\((https://roapp\.readme\.io/reference/[^)]+)\)", text or ""):
        title, url = m.group(1).strip(), m.group(2).strip()
        if url not in seen:
            seen.add(url)
            out.append({"title": title, "url": url})
    return out


def openapi_specs(page):
    text = page.decode("utf-8", "replace") if isinstance(page, bytes) else page
    specs = []
    for m in re.finditer(r"```json\s*(\{.*?\})\s*```", text, re.S):
        try:
            obj = json.loads(m.group(1))
            if isinstance(obj, dict) and isinstance(obj.get("paths"), dict):
                specs.append(obj)
        except json.JSONDecodeError:
            continue
    return specs


def sample_query(parameters):
    q = {}
    for p in parameters or []:
        if p.get("in") != "query":
            continue
        name = p.get("name")
        schema = p.get("schema") or {}
        if not name or "default" not in schema:
            continue
        value = schema["default"]
        if isinstance(value, list):
            for v in value:
                q.setdefault(name, []).append(str(v))
        else:
            q[name] = str(value)
    return q


def build_get_candidates(ref, spec):
    server = ((spec.get("servers") or [{}])[0].get("url") or API_BASE).rstrip("/")
    paths = spec.get("paths") or {}
    out = []
    for path, item in paths.items():
        if not isinstance(item, dict) or "get" not in item:
            continue
        # Never probe parameterized resources in V17.1.
        if re.search(r"\{[^}]+\}", path):
            continue
        op = item.get("get") or {}
        query = sample_query(op.get("parameters") or item.get("parameters") or [])
        url = server + (path if path.startswith("/") else "/" + path)
        if query:
            flat = []
            for k, v in query.items():
                if isinstance(v, list):
                    flat.extend((k, x) for x in v)
                else:
                    flat.append((k, v))
            url += "?" + urlencode(flat)
        out.append({
            "method": "GET",
            "url": url,
            "server": server,
            "path": path,
            "operation_id": op.get("operationId"),
            "summary": op.get("summary"),
            "reference_url": ref["url"],
            "title": ref["title"],
        })
    return out

print("=== MARSEL AUDIT V17.1 / OPENAPI-DRIVEN LIVE GET-ONLY AUDIT / READ ONLY ===")
print(f"API_BASE_ENV={API_BASE}")
print(f"DOCS_INDEX={DOCS_INDEX}")
status, body = fetch(DOCS_INDEX)
print(f"DOCS_INDEX_HTTP={status}")
if status != 200:
    print("RESULT=READ_ONLY; DOCUMENTATION INDEX UNAVAILABLE; NO RO APP DATA CREATED, UPDATED OR DELETED")
    sys.exit(4)

refs = reference_links(body.decode("utf-8", "replace"))
print(f"REFERENCE_LINKS={len(refs)}")

candidates, unresolved = [], []
for ref in refs:
    st, page = fetch(ref["url"])
    specs = openapi_specs(page) if st == 200 else []
    if not specs:
        unresolved.append({"title": ref["title"], "reference_url": ref["url"], "reference_http": st})
        continue
    for spec in specs:
        candidates.extend(build_get_candidates(ref, spec))

seen = set(); unique = []
for ep in candidates:
    key = ep["url"]
    if key not in seen:
        seen.add(key); unique.append(ep)

print(f"OPENAPI_GET_CANDIDATES={len(unique)}")
print(f"UNRESOLVED_REFERENCE_PAGES={len(unresolved)}")
print("WRITE_REQUESTS_PLANNED=0")

results = []
for ep in unique:
    st, payload = fetch(ep["url"], api=True)
    results.append({
        **ep,
        "http_status": st,
        "response_bytes": len(payload or b""),
        "available": st is not None and 200 <= st < 300,
        "error_class": "none" if st is not None and 200 <= st < 300 else ("http_error" if st is not None else "transport_error"),
    })

available = sum(x["available"] for x in results)
http_errors = sum(x["error_class"] == "http_error" for x in results)
transport_errors = sum(x["error_class"] == "transport_error" for x in results)
print(f"GET_PROBES={len(results)}")
print(f"GET_AVAILABLE={available}")
print(f"GET_HTTP_ERRORS={http_errors}")
print(f"GET_TRANSPORT_ERRORS={transport_errors}")

report = {
    "audit": "MARSEL_AUDIT_V17.1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "documentation": {"index": DOCS_INDEX, "http_status": status, "reference_count": len(refs)},
    "discovery": {"openapi_get_candidates": len(unique), "unresolved_reference_pages": len(unresolved)},
    "get_results": results,
    "unresolved": unresolved,
    "safety": {
        "get_requests_made": bool(results),
        "write_requests_made": False,
        "post_requests_made": False,
        "put_requests_made": False,
        "patch_requests_made": False,
        "delete_requests_made": False,
        "updates_performed": False,
        "deletes_performed": False,
        "pii_persisted": False,
    },
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; GET REQUESTS ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
