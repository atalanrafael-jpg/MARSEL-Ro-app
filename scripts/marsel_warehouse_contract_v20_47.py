#!/usr/bin/env python3
"""MARSEL warehouse contract audit — READ ONLY.

Canonical version 20.47. The script verifies the documented RO App warehouse
GET contracts. It never invents warehouse or branch IDs and never performs
writes.

Important: the RO App documentation currently exposes warehouse listing under
/v2/warehouse/ and locations under /branches/. The locations endpoint is not
/v2/company/locations, so branch discovery must use the documented /branches/
contract before passing real branch IDs to the warehouse query.
"""
from __future__ import annotations
import hashlib, json, os, time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

KEY = os.getenv("ROAPP_API_KEY", "")
API_BASE = os.getenv("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
API_ROOT = API_BASE.removesuffix("/v2")
TIMEOUT = float(os.getenv("ROAPP_WAREHOUSE_TIMEOUT", os.getenv("ROAPP_TIMEOUT", "15")))
MAX_RETRIES = max(int(os.getenv("ROAPP_MAX_RETRIES", "2")), 0)
MIN_INTERVAL = max(float(os.getenv("ROAPP_MIN_REQUEST_INTERVAL", "0.34")), 0.34)
WAREHOUSE_DOC = "https://roappua.readme.io/reference/get-warehouses"
STOCK_DOC = "https://roappua.readme.io/reference/get-stock"
LOCATIONS_DOC = "https://roappua.readme.io/reference/get-locations"
EXPLICIT_GET_CONTRACTS = ["/v2/warehouse/", "/warehouse/goods/{warehouse_id}"]
EXPLICIT_GET_CONTRACTS = [
    "/v2/warehouse/",
    "/warehouse/goods/{warehouse_id}",
]
REFERENCE_PAGES = [WAREHOUSE_DOC, STOCK_DOC, LOCATIONS_DOC]


def get(url: str):
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        if attempt:
            time.sleep(min(2 ** (attempt - 1), 4))
        time.sleep(MIN_INTERVAL)
        req = Request(url, headers={"Authorization": f"Bearer {KEY}", "Accept": "application/json", "User-Agent": "MARSEL-Warehouse-Contract-V20.47"}, method="GET")
        started = time.time()
        try:
            with urlopen(req, timeout=TIMEOUT) as r:
                body = r.read().decode("utf-8", errors="replace")
                if r.status in {408, 429, 500, 502, 503, 504} and attempt < MAX_RETRIES:
                    continue
                return r.status, body, round(time.time() - started, 3), None
        except Exception as exc:
            status = getattr(exc, "code", None)
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            last_error = f"{type(exc).__name__}: {exc}"
            if status in {408, 429, 500, 502, 503, 504} and attempt < MAX_RETRIES:
                continue
            if status is None and attempt < MAX_RETRIES:
                continue
            return status, body, round(time.time() - started, 3), last_error
    return None, "", 0, last_error or "GET request failed"


def parse_json(body: str):
    try:
        return json.loads(body), True
    except (json.JSONDecodeError, TypeError):
        return None, False


def extract_rows(payload):
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []
    rows = []
    for key in ("data", "warehouses", "warehouse", "items", "results", "records", "collection"):
        value = payload.get(key)
        if isinstance(value, list):
            rows.extend(x for x in value if isinstance(x, dict))
        elif isinstance(value, dict):
            rows.extend(x for x in value.get("items", []) if isinstance(x, dict))
    unique, seen = [], set()
    for row in rows:
        sig = json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)
        if sig not in seen:
            seen.add(sig)
    preferred = ("data", "warehouses", "warehouse", "items", "results", "records", "collection")
    seen, found = set(), []
    def walk(value, depth=0):
        if depth > 5 or id(value) in seen:
            return
        if isinstance(value, (dict, list)):
            seen.add(id(value))
        if isinstance(value, list):
            rows = [x for x in value if isinstance(x, dict)]
            if rows and any(row.get("id") or row.get("warehouse_id") for row in rows):
                found.extend(rows)
                return
            for item in value:
                walk(item, depth + 1)
            return
        if not isinstance(value, dict):
            return
        for key in preferred:
            if key in value:
                walk(value[key], depth + 1)
        for key, child in value.items():
            if key not in preferred and isinstance(child, (dict, list)):
                walk(child, depth + 1)
    walk(payload)
    unique, signatures = [], set()
    for row in found:
        sig = json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)
        if sig not in signatures:
            signatures.add(sig)
            unique.append(row)
    return unique


def extract_location_ids(payload):
    rows = payload if isinstance(payload, list) else payload.get("data", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list): rows = []
    return list(dict.fromkeys(str(row["id"]).strip() for row in rows if isinstance(row, dict) and row.get("id") is not None and str(row["id"]).strip()))
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = payload.get("data")
        if not isinstance(rows, list): rows = payload.get("branches")
        if not isinstance(rows, list): rows = payload.get("items")
        if not isinstance(rows, list): rows = []
    else:
        rows = []
    ids = []
    for row in rows:
        if isinstance(row, dict) and row.get("id") is not None:
            value = str(row["id"]).strip()
            if value and value not in ids: ids.append(value)
    return ids


def warehouse_id(row):
    if not isinstance(row, dict): return None
    for key in ("id", "warehouse_id"):
        value = row.get(key)
        if isinstance(value, (int, str)) and str(value).strip(): return str(value).strip()
    return None


def probe(path: str, query: dict | None, source: str, documented: bool):
    url = path + (f"?{urlencode(query)}" if query else "")
    status, body, elapsed, error = get(url)
    payload, valid_json = parse_json(body) if status == 200 else (None, False)
    rows = extract_rows(payload) if valid_json else []
    return {"method":"GET","path":url.replace(API_ROOT,""),"url":url,"source":source,"documented_contract":documented,"query":query or {},"http":status,"elapsed_s":elapsed,"json_valid":valid_json,"error":error,"rows_discovered":len(rows)}, rows
    url = f"{path}" + (f"?{urlencode(query)}" if query else "")
    status, body, elapsed, error = get(url)
    payload, valid_json = parse_json(body) if status == 200 else (None, False)
    rows = extract_rows(payload) if valid_json else []
    return {"method":"GET","path":url.replace(API_ROOT,""),"url":url,"source":source,"documented_contract":documented,"query":query or {},"http":status,"elapsed_s":elapsed,"json_valid":valid_json,"error":error,"response_top_level_type":type(payload).__name__ if valid_json else None,"response_keys":sorted(payload.keys()) if isinstance(payload,dict) else None,"rows_discovered":len(rows)}, rows


def main():
    if not KEY: raise SystemExit("ROAPP_API_KEY is required")
    branch_id = os.getenv("ROAPP_BRANCH_ID", "").strip()
    probes, branch_ids = [], [branch_id] if branch_id else []
    if not branch_ids:
        status, body, elapsed, error = get(f"{API_ROOT}/branches/")
        payload, valid = parse_json(body) if status == 200 else (None, False)
        branch_ids = extract_location_ids(payload) if valid else []
        probes.append({"method":"GET","path":"/branches/","source":LOCATIONS_DOC,"documented_contract":True,"http":status,"elapsed_s":elapsed,"json_valid":valid,"error":error,"rows_discovered":len(branch_ids),"real_branch_ids_used":branch_ids})
    query_variants = [{"type":"product", "branch_id": bid} for bid in branch_ids] or [{"type":"product"}]
    rows = []
    for query in query_variants:
        p, candidate_rows = probe(f"{API_BASE}/warehouse/", query, WAREHOUSE_DOC, True)
        probes.append(p); rows.extend(candidate_rows)
    ids = list(dict.fromkeys(wid for wid in (warehouse_id(row) for row in rows) if wid))
    for wid in ids:
        url = f"{API_ROOT}/warehouse/goods/{wid}"
        status, body, elapsed, error = get(url)
        payload, valid = parse_json(body) if status == 200 else (None, False)
        probes.append({"method":"GET","path":"/warehouse/goods/{warehouse_id}","warehouse_id":wid,"url":url,"source":STOCK_DOC,"documented_contract":True,"http":status,"elapsed_s":elapsed,"json_valid":valid,"error":error,"response_top_level_type":type(payload).__name__ if valid else None})
    confirmed = [p for p in probes if p.get("documented_contract") and p.get("http") == 200 and p.get("json_valid") and (p.get("rows_discovered", 0) > 0 or p.get("path") == "/warehouse/goods/{warehouse_id}")]
    result = "PASS" if ids and any(p.get("path") == "/v2/warehouse/" and p.get("http") == 200 for p in probes) and any(p.get("path") == "/warehouse/goods/{warehouse_id}" and p.get("http") == 200 for p in probes) else "NOT_VERIFIED"
    report = {"version":"20.47","mode":"READ_ONLY","result":result,"readonly":True,"write_requests_made":0,"ro_app_data_mutated":False,"explicit_get_contracts":EXPLICIT_GET_CONTRACTS,"warehouse_reference_pages":REFERENCE_PAGES,"warehouse_ids_discovered":ids,"branch_ids_discovered":branch_ids,"probes":probes,"confirmed_live_gets":confirmed}
    raw = json.dumps(report, ensure_ascii=False, indent=2).encode(); report["report_sha256"] = hashlib.sha256(raw).hexdigest()
    with open(os.getenv("WAREHOUSE_CONTRACT_OUTPUT", "marsel-unified-warehouse-contract.json"), "w", encoding="utf-8") as fh: json.dump(report, fh, ensure_ascii=False, indent=2)
    print(f"WAREHOUSE_CONTRACT_RESULT={result}")
    print(f"WAREHOUSE_COUNT={len(ids)}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
        location_url = f"{API_ROOT}/branches/"
        location_status, location_body, location_elapsed, location_error = get(location_url)
        location_payload, location_json = parse_json(location_body) if location_status == 200 else (None, False)
        branch_ids = extract_location_ids(location_payload) if location_json else []
        probes.append({"method":"GET","path":"/branches/","url":location_url,"source":LOCATIONS_DOC,"documented_contract":True,"http":location_status,"elapsed_s":location_elapsed,"json_valid":location_json,"error":location_error,"rows_discovered":len(branch_ids),"real_branch_ids_used":branch_ids})
    query_variants = [{"type":"product","branch_id":bid} for bid in branch_ids] or [{"type":"product"}]
    rows = []
    for query in query_variants:
        list_probe, candidate_rows = probe(f"{API_BASE}/warehouse/", query, WAREHOUSE_DOC, True)
        probes.append(list_probe)
        if candidate_rows: rows.extend(candidate_rows)
    if not rows and not branch_ids:
        fallback_probe, fallback_rows = probe(f"{API_BASE}/warehouse/", {"type":"product"}, WAREHOUSE_DOC, True)
        fallback_probe["reason"] = "documented type parameter defaults to product"
        probes.append(fallback_probe)
        if fallback_rows: rows = fallback_rows
    if not rows:
        for candidate in (f"{API_ROOT}/warehouse/", f"{API_BASE}/warehouses"):
            candidate_probe, candidate_rows = probe(candidate, {"type":"product"}, WAREHOUSE_DOC, False)
            candidate_probe["reason"] = "undocumented compatibility probe"
            probes.append(candidate_probe)
            if candidate_rows: rows.extend(candidate_rows)
    ids = []
    for row in rows:
        wid = warehouse_id(row)
        if wid and wid not in ids: ids.append(wid)
    for wid in ids:
        url = f"{API_ROOT}/warehouse/goods/{wid}"
        status, body, elapsed, error = get(url)
        parsed, valid_json = parse_json(body) if status == 200 else (None, False)
        probes.append({"method":"GET","path":"/warehouse/goods/{warehouse_id}","warehouse_id":wid,"url":url,"source":STOCK_DOC,"documented_contract":True,"http":status,"elapsed_s":elapsed,"json_valid":valid_json,"error":error,"response_top_level_type":type(parsed).__name__ if valid_json else None,"response_keys":sorted(parsed.keys()) if isinstance(parsed,dict) else None})
    confirmed_live_gets = [p for p in probes if p.get("documented_contract") and p.get("http")==200 and p.get("json_valid") and (p.get("rows_discovered",0)>0 or p.get("path")=="/warehouse/goods/{warehouse_id}")]
    list_ok = any(p.get("documented_contract") and p.get("path")=="/v2/warehouse/" and p.get("http")==200 and p.get("json_valid") and p.get("rows_discovered",0)>0 for p in probes)
    stock_ok = any(p.get("documented_contract") and p.get("path")=="/warehouse/goods/{warehouse_id}" and p.get("http")==200 and p.get("json_valid") for p in probes)
    result = "PASS" if ids and list_ok and stock_ok else "NOT_VERIFIED"
    report = {"version":"20.47","mode":"READ_ONLY","result":result,"readonly":True,"write_requests_made":0,"ro_app_data_mutated":False,"explicit_get_contracts":EXPLICIT_GET_CONTRACTS,"warehouse_reference_pages":REFERENCE_PAGES,"official_documentation":{"warehouse_list":WAREHOUSE_DOC,"stock":STOCK_DOC,"locations":LOCATIONS_DOC},"warehouse_count":len(ids),"warehouse_ids_discovered":ids,"branch_ids_discovered":branch_ids,"probes":probes,"confirmed_live_gets":confirmed_live_gets,"diagnostic_only_undocumented_probes":[p for p in probes if not p.get("documented_contract")],"retry_policy":{"max_retries":MAX_RETRIES,"timeout_seconds":TIMEOUT,"retryable_http":[408,429,500,502,503,504]}}
    raw = json.dumps(report, ensure_ascii=False, indent=2).encode()
    report["report_sha256"] = hashlib.sha256(raw).hexdigest()
    out = os.getenv("WAREHOUSE_CONTRACT_OUTPUT", "marsel-unified-warehouse-contract.json")
    with open(out, "w", encoding="utf-8") as fh: json.dump(report, fh, ensure_ascii=False, indent=2)
    print(f"WAREHOUSE_CONTRACT_RESULT={result}")
    print(f"WAREHOUSE_COUNT={len(ids)}")
    print(f"BRANCH_IDS_DISCOVERED={','.join(branch_ids) or 'NONE'}")
    print("WAREHOUSE_EXPLICIT_GET_CONTRACTS=2")
    print(f"WAREHOUSE_CONFIRMED_LIVE_GETS={len(confirmed_live_gets)}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    return 0


if __name__ == "__main__": raise SystemExit(main())
