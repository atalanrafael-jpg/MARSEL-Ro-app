#!/usr/bin/env python3
"""MARSEL V20 — read-only verification of unresolved references.

Purpose: distinguish true unresolved references from pagination/coverage false positives.
RO App is accessed with GET requests only. No write method is called.
"""
import json, os, re, sys, time
from collections import defaultdict
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl
from urllib.request import Request, urlopen

API_BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = "marsel-reference-verification-v20.json"
if not KEY:
    sys.exit("ROAPP_API_KEY is not configured")

HEADERS = {"User-Agent": "MARSEL-REFERENCE-VERIFICATION/20.0", "Accept": "application/json,text/plain,*/*"}


def get(url, api=False):
    headers = dict(HEADERS)
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
    try:
        return json.loads(text(v))
    except (TypeError, json.JSONDecodeError):
        return None


def specs(v):
    out = []
    for m in re.finditer(r"```json\s*(\{.*?\})\s*```", text(v), re.S):
        try:
            x = json.loads(m.group(1))
            if isinstance(x, dict) and isinstance(x.get("paths"), dict):
                out.append(x)
        except (json.JSONDecodeError, TypeError):
            pass
    return out


def endpoints_from_page(page):
    out = []
    for spec in specs(page):
        servers = spec.get("servers") or [{}]
        server = ((servers[0].get("url") if isinstance(servers[0], dict) else None) or API_BASE).rstrip("/")
        for path, item in (spec.get("paths") or {}).items():
            if not isinstance(item, dict) or "get" not in item:
                continue
            op = item["get"] if isinstance(item["get"], dict) else {}
            params = []
            for p in (op.get("parameters") or item.get("parameters") or []):
                if isinstance(p, dict) and p.get("in") == "query":
                    name = p.get("name")
                    if not name:
                        continue
                    if "example" in p:
                        params.append((name, str(p["example"])))
                    elif "default" in (p.get("schema") or {}):
                        params.append((name, str(p["schema"]["default"])))
            base = server + ("/" if not path.startswith("/") else "") + path
            out.append({"url": base, "path": path, "operation_id": op.get("operationId"), "summary": op.get("summary"), "query": params})
    return list({(x["path"], x["operation_id"], x["url"]): x for x in out}.values())


def records(v):
    if isinstance(v, list):
        return v, None
    if isinstance(v, dict):
        for k in ("data", "items", "results", "records", "rows"):
            if isinstance(v.get(k), list):
                return v[k], v
    return None, v if isinstance(v, dict) else None


def rid(r):
    if not isinstance(r, dict):
        return None
    for k in ("id", "ID", "uuid", "uid"):
        if isinstance(r.get(k), (str, int)) and str(r[k]):
            return str(r[k])
    return None


def ref_keys(k):
    lk = str(k).lower()
    return lk.endswith("_id") or lk.endswith("_ids") or lk in {
        "customer", "customerid", "client", "clientid", "order", "orderid", "product", "productid",
        "service", "serviceid", "branch", "branchid", "employee", "employeeid", "category", "categoryid",
        "warehouse", "warehouseid", "invoice", "invoiceid", "payment", "paymentid", "author", "authorid",
        "assignee", "assigneeid", "manager", "managerid", "technician", "technicianid", "uom", "uom_id",
    }


def hint(field, source):
    x = (str(field) + " " + str(source)).lower()
    for key in ("customer", "client", "order", "product", "service", "branch", "employee", "category", "warehouse", "invoice", "payment", "author", "assignee", "manager", "technician", "uom"):
        if key in x:
            return key
    return "unknown"


def with_query(url, extra):
    p = urlsplit(url)
    q = dict(parse_qsl(p.query, keep_blank_values=True))
    q.update(extra)
    return urlunsplit((p.scheme, p.netloc, p.path, urlencode(q), p.fragment))


def fetch_all(endpoint):
    """Fetch all available pages for a list endpoint, respecting the documented 3 req/s limit."""
    first = with_query(endpoint["url"], dict(endpoint["query"]))
    status, body = get(first, True)
    if not (status and 200 <= status < 300):
        return [], [{"url": first, "status": status}], None
    payload = json_value(body)
    rows, meta = records(payload)
    if rows is None:
        return [], [], payload
    all_rows = list(rows)
    count = None
    if isinstance(meta, dict):
        for k in ("count", "total", "total_count"):
            if isinstance(meta.get(k), int):
                count = meta[k]
                break
        if isinstance(meta.get("meta"), dict):
            for k in ("count", "total", "total_count"):
                if isinstance(meta["meta"].get(k), int):
                    count = meta["meta"][k]
                    break
    if "page" not in endpoint["url"] and count is not None and count > len(all_rows):
        page = 2
        while len(all_rows) < count and page <= 1000:
            time.sleep(0.36)
            u = with_query(first, {"page": str(page)})
            s, b = get(u, True)
            if not (s and 200 <= s < 300):
                return all_rows, [{"url": u, "status": s}], payload
            rr, _ = records(json_value(b))
            if not rr:
                break
            all_rows.extend(rr)
            page += 1
    return all_rows, [], payload


print("=== MARSEL AUDIT V20 / PAGINATED REFERENCE VERIFICATION / READ ONLY ===")
s, body = get(DOCS)
print(f"DOCS_INDEX_HTTP={s}")
if s != 200:
    sys.exit(4)
links = list(dict.fromkeys(re.findall(r"https://roapp\\.readme\\.io/reference/[^)\\s]+", text(body))))
print(f"REFERENCE_LINKS={len(links)}")
endpoints = []
for ref in links:
    rs, rb = get(ref)
    if rs == 200:
        endpoints.extend(endpoints_from_page(rb))
endpoints = list({(e["path"], e["operation_id"], e["url"]): e for e in endpoints}.values())
print(f"GET_CANDIDATES={len(endpoints)}")

id_index = defaultdict(set)
records_seen = 0
http_errors = []
refs = []
endpoint_stats = []

for ep in endpoints:
    rows, errs, _ = fetch_all(ep)
    http_errors.extend(errs)
    endpoint_stats.append({"path": ep["path"], "operation_id": ep["operation_id"], "records": len(rows), "pages_attempted": 1 + sum(1 for e in errs if "page=" in e.get("url", ""))})
    records_seen += len(rows)
    for r in rows:
        x = rid(r)
        if x:
            id_index[hint("id", ep["path"])].add(x)
        if isinstance(r, dict):
            for k, v in r.items():
                if not ref_keys(k):
                    continue
                vals = v if isinstance(v, list) else [v]
                for val in vals:
                    if isinstance(val, (str, int)) and str(val):
                        refs.append({"source_path": ep["path"], "field": str(k), "value": str(val), "entity_hint": hint(k, ep["path"])})

# Build a global ID index as a second pass because some entity types are not obvious from endpoint names.
global_ids = set().union(*id_index.values()) if id_index else set()
unique_refs = {(r["source_path"], r["field"], r["value"]): r for r in refs}
results = []
for r in unique_refs.values():
    val = r["value"]
    if val in global_ids:
        cls = "RESOLVED_BY_ID"
        reason = "Reference value exists as an ID in at least one successfully retrieved GET record after pagination."
    else:
        cls = "UNRESOLVED_AFTER_PAGINATION"
        reason = "Reference value was not found in any successfully retrieved GET list after pagination; this is evidence for review, not proof of corruption."
    results.append({**r, "classification": cls, "severity": "INFO" if cls == "RESOLVED_BY_ID" else "REVIEW", "reason": reason})

summary = defaultdict(int)
for r in results:
    summary[r["classification"]] += 1

report = {
    "audit": "MARSEL_AUDIT_V20",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "docs_index_http": s,
    "reference_links": len(links),
    "get_candidates": len(endpoints),
    "records_seen_after_pagination": records_seen,
    "unique_reference_values": len(results),
    "classification_summary": dict(summary),
    "references": results,
    "endpoint_stats": endpoint_stats,
    "http_errors": http_errors,
    "safety": {"write_requests_made": False, "data_mutated": False, "response_bodies_stored": False},
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f"RECORDS_SEEN_AFTER_PAGINATION={records_seen}")
print(f"UNIQUE_REFERENCE_VALUES={len(results)}")
print(f"RESOLVED_BY_ID={summary['RESOLVED_BY_ID']}")
print(f"UNRESOLVED_AFTER_PAGINATION={summary['UNRESOLVED_AFTER_PAGINATION']}")
print(f"HTTP_ERRORS={len(http_errors)}")
print("WRITE_REQUESTS_MADE=0")
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; PAGINATION-AWARE REFERENCE VERIFICATION; NO RO APP DATA CREATED, UPDATED OR DELETED")
