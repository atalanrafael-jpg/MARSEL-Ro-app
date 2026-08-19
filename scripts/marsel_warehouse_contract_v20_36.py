#!/usr/bin/env python3
"""MARSEL warehouse contract audit — READ ONLY.

The script verifies documented RO App warehouse GET contracts. It never invents
warehouse IDs and never performs write operations. A missing/404 contract is an
external API compatibility finding, not a reason to fabricate a PASS result.
Transient transport failures are retried within a bounded budget and remain
NOT_VERIFIED unless the documented GET contract is actually confirmed live.
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


def get(url: str):
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        if attempt:
            time.sleep(min(2 ** (attempt - 1), 4))
        time.sleep(MIN_INTERVAL)
        req = Request(url, headers={
            "Authorization": f"Bearer {KEY}",
            "Accept": "application/json",
            "User-Agent": "MARSEL-Warehouse-Contract-V20.45",
        }, method="GET")
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


def warehouse_id(row):
    if not isinstance(row, dict):
        return None
    for key in ("id", "warehouse_id"):
        value = row.get(key)
        if isinstance(value, (int, str)) and str(value).strip():
            return str(value).strip()
    return None


def probe(path: str, query: dict | None, source: str, documented: bool):
    url = f"{path}" + (f"?{urlencode(query)}" if query else "")
    status, body, elapsed, error = get(url)
    payload, valid_json = parse_json(body) if status == 200 else (None, False)
    rows = extract_rows(payload) if valid_json else []
    return {
        "method": "GET", "path": url.replace(API_ROOT, ""), "url": url,
        "source": source, "documented_contract": documented,
        "query": query or {}, "http": status, "elapsed_s": elapsed,
        "json_valid": valid_json, "error": error,
        "response_top_level_type": type(payload).__name__ if valid_json else None,
        "response_keys": sorted(payload.keys()) if isinstance(payload, dict) else None,
        "rows_discovered": len(rows),
    }, rows


def main():
    if not KEY:
        raise SystemExit("ROAPP_API_KEY is required")

    branch_id = os.getenv("ROAPP_BRANCH_ID", "").strip()
    query = {"type": "product"}
    if branch_id:
        query["branch_id"] = branch_id

    probes = []
    list_probe, rows = probe(f"{API_BASE}/warehouse/", query, WAREHOUSE_DOC, True)
    probes.append(list_probe)

    if list_probe["http"] == 200 and list_probe["json_valid"] and not rows and not branch_id:
        fallback_probe, fallback_rows = probe(f"{API_BASE}/warehouse/", {}, WAREHOUSE_DOC, True)
        fallback_probe["reason"] = "documented type parameter defaults to product"
        probes.append(fallback_probe)
        if fallback_rows:
            rows = fallback_rows

    if not rows:
        for candidate in (f"{API_ROOT}/warehouse/", f"{API_BASE}/warehouses"):
            candidate_probe, candidate_rows = probe(candidate, query, WAREHOUSE_DOC, False)
            candidate_probe["reason"] = "undocumented compatibility probe"
            probes.append(candidate_probe)
            if candidate_rows:
                rows = candidate_rows

    ids = []
    for row in rows:
        wid = warehouse_id(row)
        if wid and wid not in ids:
            ids.append(wid)

    stock_probes = []
    for wid in ids:
        url = f"{API_ROOT}/warehouse/goods/{wid}"
        status, body, elapsed, error = get(url)
        parsed, valid_json = parse_json(body) if status == 200 else (None, False)
        stock_probes.append({
            "method": "GET", "path": "/warehouse/goods/{warehouse_id}",
            "warehouse_id": wid, "url": url, "source": STOCK_DOC,
            "documented_contract": True, "http": status,
            "elapsed_s": elapsed, "json_valid": valid_json, "error": error,
            "response_top_level_type": type(parsed).__name__ if valid_json else None,
            "response_keys": sorted(parsed.keys()) if isinstance(parsed, dict) else None,
        })

    probes.extend(stock_probes)
    confirmed_live_gets = [
        p for p in probes
        if p.get("documented_contract") and p.get("http") == 200 and p.get("json_valid")
        and (p.get("rows_discovered", 0) > 0 or p.get("path") == "/warehouse/goods/{warehouse_id}")
    ]

    list_ok = any(
        p.get("documented_contract") and p.get("path") == "/v2/warehouse/"
        and p.get("http") == 200 and p.get("json_valid") and p.get("rows_discovered", 0) > 0
        for p in probes
    )
    stock_ok = any(
        p.get("documented_contract") and p.get("path") == "/warehouse/goods/{warehouse_id}"
        and p.get("http") == 200 and p.get("json_valid")
        for p in probes
    )
    result = "PASS" if ids and list_ok and stock_ok else "NOT_VERIFIED"

    report = {
        "version": "20.45", "mode": "READ_ONLY", "result": result, "readonly": True,
        "write_requests_made": 0, "ro_app_data_mutated": False,
        "official_documentation": {"warehouse_list": WAREHOUSE_DOC, "stock": STOCK_DOC},
        "warehouse_count": len(ids), "warehouse_ids_discovered": ids,
        "probes": probes, "confirmed_live_gets": confirmed_live_gets,
        "diagnostic_only_undocumented_probes": [p for p in probes if not p.get("documented_contract")],
        "retry_policy": {"max_retries": MAX_RETRIES, "timeout_seconds": TIMEOUT,
                         "retryable_http": [408, 429, 500, 502, 503, 504]},
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
    print(f"WAREHOUSE_LIST_HTTP={list_probe['http']}")
    print(f"WAREHOUSE_LIST_JSON_VALID={str(list_probe['json_valid']).lower()}")
    print(f"WAREHOUSE_LIST_ROWS={list_probe['rows_discovered']}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
