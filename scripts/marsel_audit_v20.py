#!/usr/bin/env python3
"""MARSEL V20.1 — read-only paginated referential-integrity verification.

Only GET requests are made. Documentation is used to discover GET endpoints.
Endpoints requiring path parameters are resolved from observed reference IDs when
possible; endpoints that cannot be safely parameterized are skipped, not counted
as HTTP errors.
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

HEADERS = {
    "User-Agent": "MARSEL-REFERENCE-VERIFICATION/20.1",
    "Accept": "application/json,text/plain,*/*",
}


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
            for p in (item.get("parameters") or []) + (op.get("parameters") or []):
                if not isinstance(p, dict):
                    continue
                params.append(p)
            query = []
            path_params = []
            for p in params:
                name = p.get("name")
                if not name:
                    continue
                loc = p.get("in")
                schema = p.get("schema") or {}
                example = p.get("example")
                if example is None:
                    example = schema.get("example", schema.get("default"))
                if loc == "query" and example is not None:
                    query.append((name, str(example)))
                elif loc == "path":
                    path_params.append({
                        "name": name,
                        "required": bool(p.get("required", True)),
                        "example": None if example is None else str(example),
                    })
            base = server + ("/" if not path.startswith("/") else "") + path
            out.append({
                "url": base,
                "path": path,
                "operation_id": op.get("operationId"),
                "summary": op.get("summary"),
                "query": query,
                "path_params": path_params,
            })
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
        "customer", "customerid", "client", "clientid", "order", "orderid",
        "product", "productid", "service", "serviceid", "branch", "branchid",
        "employee", "employeeid", "category", "categoryid", "warehouse",
        "warehouseid", "invoice", "invoiceid", "payment", "paymentid",
        "author", "authorid", "assignee", "assigneeid", "manager", "managerid",
        "technician", "technicianid", "uom", "uom_id",
    }


def hint(field, source):
    x = (str(field) + " " + str(source)).lower()
    for key in ("customer", "client", "order", "product", "service", "branch",
                "employee", "category", "warehouse", "invoice", "payment",
                "author", "assignee", "manager", "technician", "uom"):
        if key in x:
            return key
    return "unknown"


def with_query(url, extra):
    p = urlsplit(url)
    q = dict(parse_qsl(p.query, keep_blank_values=True))
    q.update(extra)
    return urlunsplit((p.scheme, p.netloc, p.path, urlencode(q), p.fragment))


def entity_from_path(path):
    s = re.sub(r"\{[^}]+\}", "", path.lower())
    for key in ("customers", "clients", "orders", "products", "services",
                "branches", "employees", "categories", "warehouses",
                "invoices", "payments", "tasks", "uom", "units"):
        if key in s:
            return key.rstrip("s")
    return hint("id", path)


def extract_pagination(meta):
    """Return total, next-page value and pagination style from common RO App responses."""
    if not isinstance(meta, dict):
        return None, None, None
    candidates = [meta]
    for k in ("meta", "pagination"):
        if isinstance(meta.get(k), dict):
            candidates.append(meta[k])
    total = None
    next_page = None
    style = None
    for m in candidates:
        for k in ("count", "total", "total_count", "totalRecords", "total_records"):
            if isinstance(m.get(k), int):
                total = m[k]
                break
        for k in ("nextPageIndex", "next_page_index", "nextPage", "next_page"):
            if isinstance(m.get(k), int):
                next_page = m[k]
                style = "pageIndex"
                break
        if isinstance(m.get("nextPageToken"), str) and m.get("nextPageToken"):
            next_page = m["nextPageToken"]
            style = "pageToken"
        if isinstance(m.get("next"), str) and m.get("next"):
            next_page = m["next"]
            style = "url"
        if next_page is not None:
            break
    return total, next_page, style


def substitute_path(url, params):
    for name, value in params.items():
        url = url.replace("{" + name + "}", str(value))
    return url


def fetch_all(endpoint, path_values=None):
    url = substitute_path(endpoint["url"], path_values or {})
    if "{" in url or "}" in url:
        return [], [], 0, {"status": "SKIPPED_MISSING_PATH_PARAMETER"}
    first = with_query(url, dict(endpoint["query"]))
    status, body = get(first, True)
    if not (status and 200 <= status < 300):
        return [], [{"url": first, "status": status, "kind": "HTTP_ERROR"}], 1, {}
    payload = json_value(body)
    rows, meta = records(payload)
    if rows is None:
        return [], [], 1, {"non_list_response": True}
    all_rows = list(rows)
    total, next_page, style = extract_pagination(meta)
    pages = 1

    # RO App v2 documents pageSize for paginated list endpoints.
    page_size = 100
    base_q = dict(endpoint["query"])
    base_q.setdefault("pageSize", str(page_size))

    if style == "pageIndex":
        current = next_page
        while current is not None and pages < 1000:
            time.sleep(0.36)
            u = with_query(url, {**base_q, "pageIndex": str(current)})
            s, b = get(u, True)
            pages += 1
            if not (s and 200 <= s < 300):
                return all_rows, [{"url": u, "status": s, "kind": "HTTP_ERROR"}], pages, {}
            rr, mm = records(json_value(b))
            if not rr:
                break
            all_rows.extend(rr)
            _, current, _ = extract_pagination(mm)
    elif style == "pageToken":
        token = next_page
        while token and pages < 1000:
            time.sleep(0.36)
            u = with_query(url, {**base_q, "pageToken": str(token)})
            s, b = get(u, True)
            pages += 1
            if not (s and 200 <= s < 300):
                return all_rows, [{"url": u, "status": s, "kind": "HTTP_ERROR"}], pages, {}
            rr, mm = records(json_value(b))
            if not rr:
                break
            all_rows.extend(rr)
            _, token, _ = extract_pagination(mm)
    elif total is not None and total > len(all_rows):
        page = 2
        while len(all_rows) < total and page <= 1000:
            time.sleep(0.36)
            u = with_query(url, {**base_q, "page": str(page)})
            s, b = get(u, True)
            pages += 1
            if not (s and 200 <= s < 300):
                return all_rows, [{"url": u, "status": s, "kind": "HTTP_ERROR"}], pages, {}
            rr, _ = records(json_value(b))
            if not rr:
                break
            all_rows.extend(rr)
            page += 1
    return all_rows, [], pages, {"total": total, "pagination_style": style}


print("=== MARSEL AUDIT V20.1 / PAGINATED REFERENCE VERIFICATION / READ ONLY ===")
s, body = get(DOCS)
print(f"DOCS_INDEX_HTTP={s}")
if s != 200:
    sys.exit(4)
links = list(dict.fromkeys(re.findall(r"https://roapp\.readme\.io/reference/[^)\s]+", text(body))))
print(f"REFERENCE_LINKS={len(links)}")
endpoints = []
for ref in links:
    rs, rb = get(ref)
    if rs == 200:
        endpoints.extend(endpoints_from_page(rb))
endpoints = list({(e["path"], e["operation_id"], e["url"]): e for e in endpoints}.values())
print(f"GET_CANDIDATES={len(endpoints)}")

list_eps = [e for e in endpoints if not e["path_params"]]
detail_eps = [e for e in endpoints if e["path_params"]]
id_index = defaultdict(set)
records_seen = 0
http_errors = []
skipped = []
refs = []
endpoint_stats = []

# Phase 1: safely callable collection endpoints.
for ep in list_eps:
    rows, errs, pages, meta = fetch_all(ep)
    http_errors.extend(errs)
    endpoint_stats.append({
        "path": ep["path"], "operation_id": ep["operation_id"],
        "records": len(rows), "pages_attempted": pages, "meta": meta,
    })
    records_seen += len(rows)
    entity = entity_from_path(ep["path"])
    for r in rows:
        x = rid(r)
        if x:
            id_index[entity].add(x)
        if isinstance(r, dict):
            for k, v in r.items():
                if not ref_keys(k):
                    continue
                vals = v if isinstance(v, list) else [v]
                for val in vals:
                    if isinstance(val, (str, int)) and str(val):
                        refs.append({
                            "source_path": ep["path"], "field": str(k),
                            "value": str(val), "entity_hint": hint(k, ep["path"])
                        })

global_ids = set().union(*id_index.values()) if id_index else set()
unique_refs = {(r["source_path"], r["field"], r["value"]): r for r in refs}
results = []

# Phase 2: verify references against inferred collections.
for r in unique_refs.values():
    val = r["value"]
    entity = r["entity_hint"]
    if entity != "unknown" and val in id_index.get(entity, set()):
        results.append({**r, "classification": "RESOLVED_ENTITY_MATCH",
                        "severity": "INFO",
                        "reason": "Reference value matches a retrieved ID in the inferred target entity."})
    elif val in global_ids:
        results.append({**r, "classification": "RESOLVED_CROSS_ENTITY_ID",
                        "severity": "REVIEW",
                        "reason": "Reference value exists as an ID elsewhere but not in the inferred target entity."})
    else:
        results.append({**r, "classification": "UNRESOLVED_AFTER_COLLECTION_SCAN",
                        "severity": "REVIEW",
                        "reason": "Not found in retrieved collection IDs; detail verification may be attempted below."})

# Phase 3: probe detail endpoints only with observed reference values.
detail_checks = []
for ep in detail_eps:
    if len(ep["path_params"]) != 1:
        skipped.append({"path": ep["path"], "reason": "MULTIPLE_PATH_PARAMETERS"})
        continue
    p = ep["path_params"][0]
    target_hint = entity_from_path(ep["path"])
    candidates = []
    for r in unique_refs.values():
        if r["value"] in id_index.get(target_hint, set()) or target_hint in r["entity_hint"] or r["entity_hint"] in target_hint:
            candidates.append(r["value"])
    candidates = list(dict.fromkeys(candidates))[:5]
    if not candidates and p.get("example"):
        candidates = [p["example"]]
    if not candidates:
        skipped.append({"path": ep["path"], "reason": "NO_SAFE_REFERENCE_ID"})
        continue
    for value in candidates:
        u = substitute_path(ep["url"], {p["name"]: value})
        s2, _ = get(with_query(u, dict(ep["query"])), True)
        detail_checks.append({"path": ep["path"], "value": value, "status": s2})
        if s2 is not None and 200 <= s2 < 300:
            continue
        if s2 == 404:
            continue
        http_errors.append({"url": u, "status": s2, "kind": "HTTP_ERROR_DETAIL_PROBE"})
        time.sleep(0.36)

# Reclassify unresolved refs that can be verified through successful detail endpoints.
for r in results:
    if r["classification"] != "UNRESOLVED_AFTER_COLLECTION_SCAN":
        continue
    target = r["entity_hint"]
    matching = [x for x in detail_checks if x["value"] == r["value"] and target in x["path"].lower()]
    if any(x["status"] and 200 <= x["status"] < 300 for x in matching):
        r["classification"] = "RESOLVED_BY_DETAIL_GET"
        r["severity"] = "INFO"
        r["reason"] = "Reference value was verified by a successful read-only detail GET."
    else:
        r["classification"] = "UNRESOLVED_AFTER_READONLY_VERIFICATION"
        r["severity"] = "REVIEW"
        r["reason"] = "Reference value was not found in collections and no matching detail GET verified it."

summary = defaultdict(int)
for r in results:
    summary[r["classification"]] += 1

report = {
    "audit": "MARSEL_AUDIT_V20.1",
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
    "skipped_endpoints": skipped,
    "detail_checks": detail_checks,
    "http_errors": http_errors,
    "safety": {"write_requests_made": False, "data_mutated": False, "response_bodies_stored": False},
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"RECORDS_SEEN_AFTER_PAGINATION={records_seen}")
print(f"UNIQUE_REFERENCE_VALUES={len(results)}")
print(f"RESOLVED_ENTITY_MATCH={summary['RESOLVED_ENTITY_MATCH']}")
print(f"RESOLVED_CROSS_ENTITY_ID={summary['RESOLVED_CROSS_ENTITY_ID']}")
print(f"RESOLVED_BY_DETAIL_GET={summary['RESOLVED_BY_DETAIL_GET']}")
print(f"UNRESOLVED_AFTER_READONLY_VERIFICATION={summary['UNRESOLVED_AFTER_READONLY_VERIFICATION']}")
print(f"HTTP_ERRORS={len(http_errors)}")
print(f"SKIPPED_ENDPOINTS={len(skipped)}")
print("WRITE_REQUESTS_MADE=0")
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; PAGINATION-AWARE REFERENCE VERIFICATION; NO RO APP DATA CREATED, UPDATED OR DELETED")
