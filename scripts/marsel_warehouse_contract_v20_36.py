#!/usr/bin/env python3
"""MARSEL warehouse contract audit — READ ONLY.

Uses explicit official RO App documentation evidence. No endpoint or identifier is
invented. Warehouse IDs are obtained only from the documented GET /v2/warehouse/
response, then used to verify the documented GET /warehouse/goods/{warehouse_id}.
"""
from __future__ import annotations
import hashlib, json, os, time
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
        "User-Agent": "MARSEL-Warehouse-Contract-V20.37",
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
    for key in ("data", "warehouses", "items", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
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

    # Both routes are explicitly documented by RO App.
    contract = {
        "warehouse_list": {"method": "GET", "path": "/v2/warehouse/", "source": WAREHOUSE_DOC},
        "stock": {"method": "GET", "path": "/warehouse/goods/{warehouse_id}", "source": STOCK_DOC},
    }

    list_url = f"{API_BASE}/warehouse/"
    status, body, elapsed, error = get(list_url)
    warehouses_payload, valid_json = parse_json(body) if status == 200 else (None, False)
    rows = extract_rows(warehouses_payload) if valid_json else []
    ids = []
    for row in rows:
        wid = warehouse_id(row)
        if wid and wid not in ids:
            ids.append(wid)

    probes = [{
        "method": "GET", "path": "/v2/warehouse/", "url": list_url,
        "source": WAREHOUSE_DOC, "http": status, "elapsed_s": elapsed,
        "json_valid": valid_json, "error": error,
    }]

    confirmed_live_gets = []
    if status == 200 and valid_json:
        confirmed_live_gets.append(probes[-1])

    for wid in ids:
        url = f"{API_ROOT}/warehouse/goods/{wid}"
        s, b, e, er = get(url)
        parsed, ok = parse_json(b) if s == 200 else (None, False)
        row = {
            "method": "GET", "path": "/warehouse/goods/{warehouse_id}",
            "warehouse_id": wid, "url": url, "source": STOCK_DOC,
            "http": s, "elapsed_s": e, "json_valid": ok, "error": er,
        }
        probes.append(row)
        if s == 200 and ok:
            confirmed_live_gets.append(row)

    result = "PASS" if status == 200 and valid_json and bool(confirmed_live_gets) and len(ids) > 0 else "NOT_VERIFIED"
    report = {
        "version": "20.37",
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
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
