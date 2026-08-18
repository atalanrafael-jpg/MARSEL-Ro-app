#!/usr/bin/env python3
"""MARSEL warehouse contract audit — READ ONLY.

Uses only explicitly documented RO App GET contracts. The warehouse list endpoint
supports the documented `type` query parameter; we request `type=product` explicitly
because the contract being verified is the product-stock contract. Warehouse IDs are
never invented: they are extracted only from the live warehouse-list response.
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
        "User-Agent": "MARSEL-Warehouse-Contract-V20.38",
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
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    # Known/common collection envelopes; no endpoint-specific identifier is invented.
    for key in ("data", "warehouses", "warehouse", "items", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            for nested_key in ("data", "items", "results", "warehouses"):
                nested = value.get(nested_key)
                if isinstance(nested, list):
                    return nested
    return []


def warehouse_id(row):
    if not isinstance(row, dict):
        return None
    for key in ("id", "warehouse_id"):
        value = row.get(key)
        if isinstance(value, (int, str)) and str(value).strip():
            return str(value).strip()
    return None


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

    query = {"type": "product"}
    branch_id = os.getenv("ROAPP_BRANCH_ID", "").strip()
    if branch_id:
        query["branch_id"] = branch_id
    list_url = f"{API_BASE}/warehouse/?{urlencode(query)}"
    status, body, elapsed, error = get(list_url)
    warehouses_payload, valid_json = parse_json(body) if status == 200 else (None, False)
    rows = extract_rows(warehouses_payload) if valid_json else []
    ids = []
    for row in rows:
        wid = warehouse_id(row)
        if wid and wid not in ids:
            ids.append(wid)

    probe = {
        "method": "GET", "path": "/v2/warehouse/", "url": list_url,
        "source": WAREHOUSE_DOC, "query": query, "http": status,
        "elapsed_s": elapsed, "json_valid": valid_json, "error": error,
        "response_top_level_type": type(warehouses_payload).__name__ if valid_json else None,
        "response_keys": sorted(warehouses_payload.keys()) if isinstance(warehouses_payload, dict) else None,
        "rows_discovered": len(rows),
    }
    probes = [probe]
    confirmed_live_gets = []
    if status == 200 and valid_json and len(rows) > 0:
        confirmed_live_gets.append(probe)

    for wid in ids:
        url = f"{API_ROOT}/warehouse/goods/{wid}"
        s, b, e, er = get(url)
        parsed, ok = parse_json(b) if s == 200 else (None, False)
        row = {
            "method": "GET", "path": "/warehouse/goods/{warehouse_id}",
            "warehouse_id": wid, "url": url, "source": STOCK_DOC,
            "http": s, "elapsed_s": e, "json_valid": ok, "error": er,
            "response_top_level_type": type(parsed).__name__ if ok else None,
            "response_keys": sorted(parsed.keys()) if isinstance(parsed, dict) else None,
        }
        probes.append(row)
        if s == 200 and ok:
            confirmed_live_gets.append(row)

    result = "PASS" if status == 200 and valid_json and len(ids) > 0 and len(confirmed_live_gets) >= 2 else "NOT_VERIFIED"
    report = {
        "version": "20.38",
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
    print(f"WAREHOUSE_LIST_HTTP={status}")
    print(f"WAREHOUSE_LIST_JSON_VALID={str(valid_json).lower()}")
    print(f"WAREHOUSE_LIST_ROWS={len(rows)}")
    print(f"WAREHOUSE_LIST_KEYS={probe['response_keys']}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
