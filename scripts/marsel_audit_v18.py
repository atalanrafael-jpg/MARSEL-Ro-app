#!/usr/bin/env python3
"""MARSEL V18 — read-only structural audit of live RO App GET responses."""
import hashlib, json, os, re, sys
from collections import Counter
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
DOCS = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
OUT = "marsel-structural-data-audit-v18.json"
if not KEY:
    sys.exit("ROAPP_API_KEY is not configured")


def get(url, api=False):
    headers = {"User-Agent": "MARSEL-STRUCTURAL-AUDIT/18", "Accept": "application/json,text/plain,*/*"}
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
    return value.decode("utf-8", "replace") if isinstance(value, bytes) else str(value)


def refs(text):
    return list(dict.fromkeys(re.findall(r"https://roapp\.readme\.io/reference/[^)\s]+", text_of(text))))


def specs(text):
    text = text_of(text)
    out = []
    for match in re.finditer(r"```json\s*(\{.*?\})\s*```", text, re.S):
        try:
            spec = json.loads(match.group(1))
            if isinstance(spec, dict) and isinstance(spec.get("paths"), dict):
                out.append(spec)
        except (json.JSONDecodeError, TypeError):
            pass
    return out


def candidate_urls(page):
    out = []
    for spec in specs(page):
        servers = spec.get("servers") or [{}]
        server = ((servers[0].get("url") if isinstance(servers[0], dict) else None) or API_BASE).rstrip("/")
        for path, item in (spec.get("paths") or {}).items():
            if not isinstance(item, dict) or "get" not in item or re.search(r"\{[^}]+\}", path):
                continue
            operation = item["get"] if isinstance(item["get"], dict) else {}
            url = server + ("/" if not path.startswith("/") else "") + path
            query = []
            for param in operation.get("parameters") or item.get("parameters") or []:
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


def json_value(payload):
    try:
        return json.loads(text_of(payload))
    except (TypeError, json.JSONDecodeError):
        return None


def record_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("data", "items", "results", "records", "rows", "customers", "orders", "products", "services", "invoices", "payments"):
            if isinstance(value.get(key), list):
                return value[key]
    return None


def scalar_id(record):
    if not isinstance(record, dict):
        return None
    for key in ("id", "ID", "uuid", "uid"):
        if key in record and isinstance(record[key], (str, int)):
            return str(record[key])
    return None


def fingerprint(record):
    if not isinstance(record, dict):
        return None
    cleaned = {}
    for k, v in sorted(record.items(), key=lambda x: str(x[0])):
        if str(k).lower() in {"updated_at", "created_at", "timestamp", "modified_at"}:
            continue
        cleaned[str(k)] = v
    raw = json.dumps(cleaned, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def key_profile(value):
    records = record_list(value)
    if records is None:
        return {"records": None, "empty_records": 0, "duplicate_ids": [], "duplicate_fingerprints": [], "common_keys": []}
    ids = [scalar_id(r) for r in records]
    ids = [x for x in ids if x is not None]
    fps = [fingerprint(r) for r in records if fingerprint(r)]
    id_counts = Counter(ids)
    fp_counts = Counter(fps)
    key_counts = Counter()
    for r in records:
        if isinstance(r, dict):
            key_counts.update(map(str, r.keys()))
    n = len(records)
    common = [k for k, c in key_counts.most_common(50) if c >= max(1, n // 2)]
    return {
        "records": n,
        "empty_records": sum(1 for r in records if not isinstance(r, dict) or not r),
        "records_without_id": sum(1 for r in records if scalar_id(r) is None),
        "duplicate_ids": sorted([k for k, c in id_counts.items() if c > 1])[:100],
        "duplicate_fingerprints": sorted([k for k, c in fp_counts.items() if c > 1])[:100],
        "common_keys": common,
    }


def relationship_hints(value):
    records = record_list(value)
    hints = Counter()
    if records:
        for r in records:
            if not isinstance(r, dict):
                continue
            for k, v in r.items():
                lk = str(k).lower()
                if lk.endswith("_id") or lk in {"customer", "customerid", "client", "clientid", "order", "orderid", "product", "productid", "service", "serviceid", "branch", "branchid", "employee", "employeeid", "category", "categoryid", "warehouse", "warehouseid", "invoice", "invoiceid", "payment", "paymentid"}:
                    if isinstance(v, (str, int)) and str(v):
                        hints[str(k)] += 1
    return dict(hints.most_common(50))


print("=== MARSEL AUDIT V18 / LIVE STRUCTURAL DATA AUDIT / READ ONLY ===")
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
    value = json_value(payload) if status and 200 <= status < 300 else None
    profile = key_profile(value)
    rows.append({
        "method": "GET", "path": path, "operation_id": operation_id, "summary": summary,
        "http_status": status, "available": bool(status and 200 <= status < 300),
        "metadata": profile, "relationship_hints": relationship_hints(value),
        "response_body_stored": False,
    })

available = sum(r["available"] for r in rows)
errors = sum(r["http_status"] is not None and not 200 <= r["http_status"] < 300 for r in rows)
record_counts = [r["metadata"]["records"] for r in rows if isinstance(r["metadata"].get("records"), int)]
empty_total = sum(r["metadata"].get("empty_records", 0) for r in rows)
dup_id_endpoints = sum(bool(r["metadata"].get("duplicate_ids")) for r in rows)
dup_fp_endpoints = sum(bool(r["metadata"].get("duplicate_fingerprints")) for r in rows)
print(f"GET_AVAILABLE={available}")
print(f"GET_HTTP_ERRORS={errors}")
print(f"ENDPOINTS_WITH_RECORD_LISTS={len(record_counts)}")
print(f"TOTAL_RECORDS_ACROSS_RESPONSES={sum(record_counts)}")
print(f"ENDPOINTS_WITH_EMPTY_RECORDS={empty_total}")
print(f"ENDPOINTS_WITH_DUPLICATE_IDS={dup_id_endpoints}")
print(f"ENDPOINTS_WITH_DUPLICATE_FINGERPRINTS={dup_fp_endpoints}")
print("WRITE_REQUESTS_MADE=0")

report = {
    "audit": "MARSEL_AUDIT_V18",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "reference_links": len(reference_links), "get_probes": len(endpoints),
    "get_available": available, "get_http_errors": errors,
    "summary": {"endpoints_with_record_lists": len(record_counts), "total_records_across_responses": sum(record_counts), "empty_records": empty_total, "endpoints_with_duplicate_ids": dup_id_endpoints, "endpoints_with_duplicate_fingerprints": dup_fp_endpoints},
    "endpoints": rows,
    "safety": {"write_requests_made": False, "response_bodies_stored": False, "data_mutated": False},
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f"REPORT={OUT}")
print("RESULT=READ_ONLY; GET REQUESTS ONLY; DERIVED STRUCTURAL METADATA ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
