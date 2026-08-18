#!/usr/bin/env python3
"""MARSEL warehouse contract audit — READ ONLY.

Uses only explicitly documented RO App GET contracts. The warehouse list endpoint
supports the documented `branch_id` and `type` query parameters. Warehouse IDs are
never invented: they are extracted only from live warehouse-list responses.
"""
from __future__ import annotations
import hashlib, json, os, time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

KEY = os.getenv("ROAPP_API_KEY", "")
API_BASE = os.getenv("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
API_ROOT = API_BASE.removesuffix("/v2")
TIMEOUT = 8
MIN_INTERVAL = 0.34
WAREHOUSE_DOC = "https://roappua.readme.io/reference/get-warehouses"
STOCK_DOC = "https://roappua.readme.io/reference/get-stock"


def get(url: str):
    time.sleep(MIN_INTERVAL)
    req = Request(url, headers={
        "Authorization": f"Bearer {KEY}",
        "Accept": "application/json",
        "User-Agent": "MARSEL-Warehouse-Contract-V20.39",
    }, method="GET")
    started = time.time()
    try:
        with urlopen(req, timeout=TIMEOUT) as r:
            body = r.read().decode("utf-8", errors="replace")
            return r.status, body, round(time.time() - started, 3), None
    except Exception as exc:
        return None, "", round(time.time() - started, 3), f"{type(exc).__name__}: {exc}"


def parse_json(body: str):
    try:
        return json.loads(body), True
    except json.JSONDecodeError:
        return None, False


def extract_rows(payload):
    """Find collection rows without assuming one undocumented response envelope."""
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []

    preferred = ("data", "warehouses", "warehouse", "items", "results", "records", "collection")
    seen = set()
    found = []

    def walk(value, depth=0):
        if depth > 5 or id(value) in seen:
            return
        if isinstance(value, (dict, list)):
            seen.add(id(value))
        if isinstance(value, list):
            dict_rows = [x for x in value if isinstance(x, dict)]
            if dict_rows and any(row.get("id") or row.get("warehouse_id") for row in dict_rows):
                found.extend(dict_rows)
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
    unique = []
    signatures = set()
    for row in found:
        sig = json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)
        if sig not in signatures:
            signatures.add(sig)
            unique.append(row)
    return unique


def warehouse_id(row):
    if not isinstance(row, dict):
        return None
    for key in ("id", "warehouse_id"):
        value = row.get(key)
        if isinstance(value, (int, str)) and str(value).strip():
            return str(value).strip()
    return None


def probe_warehouse_list(query):
    url = f"{API_BASE}/warehouse/" + (f"?{urlencode(query)}" if query else "")
    status, body, elapsed, error = get(url)
    payload, valid_json = parse_json(body) if status == 200 else (None, False)
    rows = extract_rows(payload) if valid_json else []
    probe = {
        "method": "GET", "path": "/v2/warehouse/", "url": url,
        "source": WAREHOUSE_DOC, "query": query,
        "http": status, "elapsed_s": elapsed, "json_valid": valid_json,
        "error": error,
        "response_top_level_type": type(payload).__name__ if valid_json else None,
        "response_keys": sorted(payload.keys()) if isinstance(payload, dict) else None,
        "rows_discovered": len(rows),
    }
    return probe, rows


def main():
    if not KEY:
        raise SystemExit("ROAPP_API_KEY is required")

    contract = {
        "warehouse_list": {
            "method": "GET", "path": "/v2/warehouse/", "source": WAREHOUSE_DOC,
            "query": {"type": "product"},
        },
        "stock": {"method": "GET", "path": "/warehouse/goods/{warehouse_id}", "source": STOCK_DOC},
    }

    branch_id = os.getenv("ROAPP_BRANCH_ID", "").strip()
    query = {"type": "product"}
    if branch_id:
        query["branch_id"] = branch_id

    probe, rows = probe_warehouse_list(query)
    probes = [probe]

    # `type=product` is explicitly documented, but it also defaults to product.
    # If a valid 200 response contains no rows, retry the same documented GET
    # without optional query parameters rather than inventing another endpoint.
    if probe["http"] == 200 and probe["json_valid"] and not rows and not branch_id:
        fallback_probe, fallback_rows = probe_warehouse_list({})
        fallback_probe["reason"] = "documented type parameter defaults to product; first valid response contained no discoverable rows"
        probes.append(fallback_probe)
        if fallback_rows:
            rows = fallback_rows
            query = {}

    ids = []
    for row in rows:
        wid = warehouse_id(row)
        if wid and wid not in ids:
            ids.append(wid)

    confirmed_live_gets = [p for p in probes if p.get("http") == 200 and p.get("json_valid") and p.get("rows_discovered", 0) > 0]

    for wid in ids:
        url = f"{API_ROOT}/warehouse/goods/{wid}"
        status, body, elapsed, error = get(url)
        parsed, valid_json = parse_json(body) if status == 200 else (None, False)
        row = {
            "method": "GET", "path": "/warehouse/goods/{warehouse_id}",
            "warehouse_id": wid, "url": url, "source": STOCK_DOC,
            "http": status, "elapsed_s": elapsed, "json_valid": valid_json,
            "error": error,
            "response_top_level_type": type(parsed).__name__ if valid_json else None,
            "response_keys": sorted(parsed.keys()) if isinstance(parsed, dict) else None,
        }
        probes.append(row)
        if status == 200 and valid_json:
            confirmed_live_gets.append(row)

    result = "PASS" if ids and len(confirmed_live_gets) >= 2 else "NOT_VERIFIED"
    report = {
        "version": "20.39",
        "mode": "READ_ONLY",
        "result": result,
        "readonly": True,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "official_documentation": {
            "warehouse_list": WAREHOUSE_DOC,
            "stock": STOCK_DOC,
            "explicit_contracts": list(contract.values()),
        },
        "warehouse_count": len(ids),
        "warehouse_ids_discovered": ids,
        "probes": probes,
        "confirmed_live_gets": confirmed_live_gets,
    }
    raw = json.dumps(report, ensure_ascii=False, indent=2).encode()
    report["report_sha256"] = hashlib.sha256(raw).hexdigest()
    out = os.getenv("WAREHOUSE_CONTRACT_OUTPUT", "marsel-unified-warehouse-contract.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    print(f"WAREHOUSE_CONTRACT_RESULT={result}")
    print(f"WAREHOUSE_COUNT={len(ids)}")
    print("WAREHOUSE_EXPLICIT_GET_CONTRACTS=2")
    print(f"WAREHOUSE_CONFIRMED_LIVE_GETS={len(confirmed_live_gets)}")
    print(f"WAREHOUSE_LIST_HTTP={probe['http']}")
    print(f"WAREHOUSE_LIST_JSON_VALID={str(probe['json_valid']).lower()}")
    print(f"WAREHOUSE_LIST_ROWS={probe['rows_discovered']}")
    print(f"WAREHOUSE_LIST_KEYS={probe['response_keys']}")
    if len(probes) > 1:
        print(f"WAREHOUSE_FALLBACK_HTTP={probes[1]['http']}")
        print(f"WAREHOUSE_FALLBACK_ROWS={probes[1]['rows_discovered']}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
