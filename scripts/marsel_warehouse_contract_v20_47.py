#!/usr/bin/env python3
"""MARSEL warehouse contract audit — READ ONLY, canonical v20.47."""
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


def get(url):
    last = None
    for attempt in range(MAX_RETRIES + 1):
        if attempt:
            time.sleep(min(2 ** (attempt - 1), 4))
        time.sleep(MIN_INTERVAL)
        req = Request(url, headers={"Authorization": f"Bearer {KEY}", "Accept": "application/json", "User-Agent": "MARSEL-Warehouse-Contract-V20.47"}, method="GET")
        started = time.time()
        try:
            with urlopen(req, timeout=TIMEOUT) as r:
                body = r.read().decode("utf-8", errors="replace")
                return r.status, body, round(time.time() - started, 3), None
        except Exception as exc:
            status = getattr(exc, "code", None)
            body = ""
            try: body = exc.read().decode("utf-8", errors="replace")
            except Exception: pass
            last = f"{type(exc).__name__}: {exc}"
            if status in {408,429,500,502,503,504} and attempt < MAX_RETRIES: continue
            if status is None and attempt < MAX_RETRIES: continue
            return status, body, round(time.time() - started, 3), last
    return None, "", 0, last or "GET failed"


def parse(body):
    try: return json.loads(body), True
    except (json.JSONDecodeError, TypeError): return None, False


def rows(payload):
    if isinstance(payload, list): return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict): return []
    out = []
    for key in ("data", "warehouses", "warehouse", "items", "results", "records", "collection"):
        value = payload.get(key)
        if isinstance(value, list): out.extend(x for x in value if isinstance(x, dict))
    if not out:
        for value in payload.values():
            if isinstance(value, list): out.extend(x for x in value if isinstance(x, dict))
    seen, unique = set(), []
    for row in out:
        wid = row.get("id", row.get("warehouse_id"))
        if wid is not None and str(wid) not in seen:
            seen.add(str(wid)); unique.append(row)
    return unique


def warehouse_id(row):
    value = row.get("id", row.get("warehouse_id")) if isinstance(row, dict) else None
    return str(value).strip() if isinstance(value, (int, str)) and str(value).strip() else None


def probe(path, query, source, documented=True):
    url = path + (("?" + urlencode(query)) if query else "")
    status, body, elapsed, error = get(url)
    payload, valid = parse(body) if status == 200 else (None, False)
    found = rows(payload) if valid else []
    return {
        "method":"GET", "path":url.replace(API_ROOT, ""), "url":url,
        "source":source, "documented_contract":documented, "query":query or {},
        "http":status, "elapsed_s":elapsed, "json_valid":valid, "error":error,
        "response_top_level_type":type(payload).__name__ if valid else None,
        "response_keys":sorted(payload.keys()) if isinstance(payload, dict) else None,
        "rows_discovered":len(found)
    }, found


def discover_branch_ids():
    url = f"{API_ROOT}/branches/"
    status, body, elapsed, error = get(url)
    payload, valid = parse(body) if status == 200 else (None, False)
    ids = []
    if valid:
        value = payload if isinstance(payload, list) else payload.get("data", payload.get("branches", payload.get("items", []))) if isinstance(payload, dict) else []
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and item.get("id") is not None and str(item["id"]).strip() not in ids:
                    ids.append(str(item["id"]).strip())
    return {"method":"GET","path":"/branches/","url":url,"source":LOCATIONS_DOC,"documented_contract":True,"http":status,"elapsed_s":elapsed,"json_valid":valid,"error":error,"rows_discovered":len(ids),"real_branch_ids_used":ids}, ids


def main():
    if not KEY: raise SystemExit("ROAPP_API_KEY is required")
    probes, all_rows = [], []

    # branch_id is optional in the documented warehouse contract. First verify
    # the canonical unfiltered GET so a branch filter cannot hide valid warehouses.
    p, found = probe(f"{API_BASE}/warehouse/", {"type":"product"}, WAREHOUSE_DOC, True)
    probes.append(p); all_rows.extend(found)

    branch_probe, branch_ids = discover_branch_ids()
    probes.append(branch_probe)
    for bid in branch_ids:
        p, found = probe(f"{API_BASE}/warehouse/", {"type":"product", "branch_id":bid}, WAREHOUSE_DOC, True)
        probes.append(p); all_rows.extend(found)

    ids = []
    for row in all_rows:
        wid = warehouse_id(row)
        if wid and wid not in ids: ids.append(wid)

    # Every discovered warehouse is verified through the documented stock GET.
    for wid in ids:
        url = f"{API_ROOT}/warehouse/goods/{wid}"
        status, body, elapsed, error = get(url)
        payload, valid = parse(body) if status == 200 else (None, False)
        probes.append({"method":"GET","path":"/warehouse/goods/{warehouse_id}","warehouse_id":wid,"url":url,"source":STOCK_DOC,"documented_contract":True,"http":status,"elapsed_s":elapsed,"json_valid":valid,"error":error,"response_top_level_type":type(payload).__name__ if valid else None,"response_keys":sorted(payload.keys()) if isinstance(payload,dict) else None})

    list_ok = any(p.get("documented_contract") and p.get("path") == "/v2/warehouse/" and p.get("http") == 200 and p.get("json_valid") and p.get("rows_discovered", 0) > 0 for p in probes)
    stock_probes = [p for p in probes if p.get("path") == "/warehouse/goods/{warehouse_id}"]
    stock_ok = bool(stock_probes) and all(p.get("http") == 200 and p.get("json_valid") for p in stock_probes)
    confirmed = [p for p in probes if p.get("documented_contract") and p.get("http") == 200 and p.get("json_valid") and (p.get("rows_discovered",0) > 0 or p.get("path") == "/warehouse/goods/{warehouse_id}")]
    result = "PASS" if ids and list_ok and stock_ok else "NOT_VERIFIED"

    report = {
        "version":"20.47", "mode":"READ_ONLY", "result":result, "readonly":True,
        "write_requests_made":0, "ro_app_data_mutated":False,
        "explicit_get_contracts":["/v2/warehouse/", "/warehouse/goods/{warehouse_id}"],
        "warehouse_reference_pages":[WAREHOUSE_DOC, STOCK_DOC, LOCATIONS_DOC],
        "official_documentation":{"warehouse_list":WAREHOUSE_DOC,"stock":STOCK_DOC,"locations":LOCATIONS_DOC},
        "warehouse_count":len(ids), "warehouse_ids_discovered":ids,
        "branch_ids_discovered":branch_ids, "probes":probes, "confirmed_live_gets":confirmed,
        "diagnostic_only_undocumented_probes":[],
        "retry_policy":{"max_retries":MAX_RETRIES,"timeout_seconds":TIMEOUT,"retryable_http":[408,429,500,502,503,504]}
    }
    raw = json.dumps(report, ensure_ascii=False, indent=2).encode()
    report["report_sha256"] = hashlib.sha256(raw).hexdigest()
    out = os.getenv("WAREHOUSE_CONTRACT_OUTPUT", "marsel-unified-warehouse-contract.json")
    with open(out, "w", encoding="utf-8") as fh: json.dump(report, fh, ensure_ascii=False, indent=2)
    print(f"WAREHOUSE_CONTRACT_RESULT={result}")
    print(f"WAREHOUSE_COUNT={len(ids)}")
    print(f"BRANCH_IDS_DISCOVERED={','.join(branch_ids) or 'NONE'}")
    print("WAREHOUSE_EXPLICIT_GET_CONTRACTS=2")
    print(f"WAREHOUSE_CONFIRMED_LIVE_GETS={len(confirmed)}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")


if __name__ == "__main__": raise SystemExit(main())
