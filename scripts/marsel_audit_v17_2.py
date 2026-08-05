#!/usr/bin/env python3
"""MARSEL V17.2.2 — metadata-only inspection of live GET responses."""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = "marsel-live-api-metadata-v17-2-2.json"
if not KEY:
    sys.exit("ROAPP_API_KEY is not configured")


def get(url, api=False):
    headers = {
        "User-Agent": "MARSEL-LIVE-AUDIT/17.2.2",
        "Accept": "application/json,text/plain,*/*",
    }
    if api:
        headers["Authorization"] = f"Bearer {KEY}"
    try:
        with urlopen(Request(url, headers=headers), timeout=45) as response:
            return response.status, response.read()
    except HTTPError as exc:
        return exc.code, exc.read()
    except (URLError, TimeoutError, OSError) as exc:
        return None, str(exc).encode()


def text_of(value):
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return str(value)


def refs(text):
    pattern = r"https://roapp\.readme\.io/reference/[^)\s]+"
    return list(dict.fromkeys(re.findall(pattern, text_of(text))))


def specs(text):
    text = text_of(text)
    out = []
    for match in re.finditer(r"```json\s*(\{.*?\})\s*```", text, re.S):
        try:
            spec = json.loads(match.group(1))
            if isinstance(spec, dict) and isinstance(spec.get("paths"), dict):
                out.append(spec)
        except (json.JSONDecodeError, TypeError):
            continue
    return out


def candidate_urls(page):
    out = []
    for spec in specs(page):
        servers = spec.get("servers") or [{}]
        server = ((servers[0].get("url") if isinstance(servers[0], dict) else None) or API_BASE).rstrip("/")
        for path, item in (spec.get("paths") or {}).items():
            if not isinstance(item, dict) or "get" not in item:
                continue
            if re.search(r"\{[^}]+\}", path):
                continue
            operation = item["get"] if isinstance(item["get"], dict) else {}
            url = server + ("/" if not path.startswith("/") else "") + path
            params = operation.get("parameters") or item.get("parameters") or []
            query = []
            for param in params:
                if not isinstance(param, dict) or param.get("in") != "query":
                    continue
                if "example" in param:
                    query.append((param.get("name"), str(param["example"])))
                elif "default" in (param.get("schema") or {}):
                    query.append((param.get("name"), str(param["schema"]["default"])))
            query = [(k, v) for k, v in query if k]
            if query:
                url += "?" + urlencode(query)
            out.append((url, path, operation.get("operationId"), operation.get("summary")))
    return list(dict.fromkeys(out))


def shape(payload):
    payload = payload if isinstance(payload, bytes) else str(payload).encode()
    try:
        value = json.loads(payload.decode("utf-8", "replace"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"json": False, "top_type": None, "keys": [], "list_length": None}
    if isinstance(value, dict):
        return {"json": True, "top_type": "object", "keys": sorted(map(str, value.keys()))[:100], "list_length": None}
    if isinstance(value, list):
        return {"json": True, "top_type": "array", "keys": [], "list_length": len(value)}
    return {"json": True, "top_type": type(value).__name__, "keys": [], "list_length": None}


print("=== MARSEL AUDIT V17.2.2 / LIVE GET RESPONSE METADATA / READ ONLY ===")
status, body = get(DOCS)
print(f"DOCS_INDEX_HTTP={status}")
if status != 200:
    sys.exit(4)

reference_links = refs(body)
print(f"REFERENCE_LINKS={len(reference_links)}")

endpoints = []
for reference_url in reference_links:
    page_status, page_body = get(reference_url)
    if page_status == 200:
        endpoints.extend(candidate_urls(page_body))

endpoints = list(dict.fromkeys(endpoints))
print(f"GET_PROBES={len(endpoints)}")

rows = []
for url, path, operation_id, summary in endpoints:
    status, payload = get(url, True)
    rows.append({
        "method": "GET",
        "path": path,
        "operation_id": operation_id,
        "summary": summary,
        "http_status": status,
        "response_bytes": len(payload),
        "available": bool(status and 200 <= status < 300),
        "metadata": shape(payload),
    })

available = sum(row["available"] for row in rows)
http_errors = sum(row["http_status"] is not None and not 200 <= row["http_status"] < 300 for row in rows)
print(f"GET_AVAILABLE={available}")
print(f"GET_HTTP_ERRORS={http_errors}")
print("WRITE_REQUESTS_MADE=0")

report = {
    "audit": "MARSEL_AUDIT_V17.2.2",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "reference_links": len(reference_links),
    "get_probes": len(endpoints),
    "get_available": available,
    "get_http_errors": http_errors,
    "endpoints": rows,
    "safety": {"write_requests_made": False, "response_bodies_stored": False, "data_mutated": False},
}
with open(OUT, "w", encoding="utf-8") as report_file:
    json.dump(report, report_file, ensure_ascii=False, indent=2)
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; GET REQUESTS ONLY; RESPONSE BODIES NOT STORED; NO RO APP DATA CREATED, UPDATED OR DELETED")
