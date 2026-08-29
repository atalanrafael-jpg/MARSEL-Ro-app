#!/usr/bin/env python3
"""MARSEL warehouse contract audit — READ ONLY.

Canonical version 20.47. Verifies documented RO App warehouse GET contracts.
Never invents warehouse or branch IDs and never performs writes.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
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
REFERENCE_PAGES = [WAREHOUSE_DOC, STOCK_DOC, LOCATIONS_DOC]


def get(url: str):
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        if attempt:
            time.sleep(min(2 ** (attempt - 1), 4))
        time.sleep(MIN_INTERVAL)
        req = Request(
            url,
            headers={
                "Authorization": f"Bearer {KEY}",
                "Accept": "application/json",
                "User-Agent": "MARSEL-Warehouse-Contract-V20.47",
            },
            method="GET",
        )
        started = time.time()
        try:
            with urlopen(req, timeout=TIMEOUT) as response:
                body = response.read().decode("utf-8", errors="replace")
                status = response.status
                if status in {408, 429, 500, 502, 503, 504} and attempt < MAX_RETRIES:
                    continue
                return status, body, round(time.time() - started, 3), None
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
    preferred = ("data", "warehouses", "warehouse", "items", "results", "records", "collection")
    found = []
    seen_objects = set()

    def walk(value, depth=0):
        if depth > 6 or id(value) in seen_objects:
            return
        if isinstance(value, (dict, list)):
            seen_objects.add(id(value))
        if isinstance(value, list):
            rows = [item for item in value if isinstance(item, dict)]
            if rows and any(item.get("id") or item.get("warehouse_id") for item in rows):
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
        signature = json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)
        if signature not in signatures:
            signatures.add(signature)
            unique.append(row)
    return unique


def extract_location_ids(payload):
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = payload.get("data")
        if not isinstance(rows, list):
            rows = payload.get("branches")
        if not isinstance(rows, list):
            rows = payload.get("items")
        if not isinstance(rows, list):
            rows = []
    else:
        rows = []

    ids = []
    for row in rows:
        if isinstance(row, dict) and row.get("id") is not None:
            value = str(row["id"]).strip()
            if value and value not in ids:
                ids.append(value)
    return ids


def warehouse_id(row):
    if not isinstance(row, dict):
        return None
    for key in ("id", "warehouse_id"):
        value = row.get(key)
        if isinstance(value, (int, str)) and str(value).strip():
            return str(value).strip()
    return None


def probe(path: str, query: dict | None, source: str, documented: bool):
    url = path + (f"?{urlencode(query)}" if query else "")
    status, body, elapsed, error = get(url)
    payload, valid_json = parse_json(body) if status == 200 else (None, False)
    rows = extract_rows(payload) if valid_json else []
    return {
        "method": "GET",
        "path": url.replace(API_ROOT, ""),
        "url": url,
        "source": source,
        "documented_contract": documented,
        "query": query or {},
        "http": status,
        "elapsed_s": elapsed,
        "json_valid": valid_json,
        "error": error,
        "response_top_level_type": type(payload).__name__ if valid_json else None,
        "response_keys": sorted(payload.keys()) if isinstance(payload, dict) else None,
        "rows_discovered": len(rows),
    }, rows


def main():
    if not KEY:
        raise SystemExit("ROAPP_API_KEY is required")

    branch_id = os.getenv("ROAPP_BRANCH_ID", "").strip()
    probes = []
    branch_ids = [branch_id] if branch_id else []

    if not branch_ids:
        location_url = f"{API_ROOT}/branches/"
        status, body, elapsed, error = get(location_url)
        payload, valid = parse_json(body) if status == 200 else (None, False)
        branch_ids = extract_location_ids(payload) if valid else []
        probes.append({
            "method": "GET",
            "path": "/branches/",
            "url": location_url,
            "source": LOCATIONS_DOC,
            "documented_contract": True,
            "http": status,
            "elapsed_s": elapsed,
            "json_valid": valid,
            "error": error,
            "rows_discovered": len(branch_ids),
            "real_branch_ids_used": branch_ids,
        })

    query_variants = [{"type": "product", "branch_id": bid} for bid in branch_ids] or [{"type": "product"}]
    rows = []
    for query in query_variants:
        list_probe, candidate_rows = probe(f"{API_BASE}/warehouse/", query, WAREHOUSE_DOC, True)
        probes.append(list_probe)
        rows.extend(candidate_rows)

    if not rows and not branch_ids:
        fallback_probe, fallback_rows = probe(
            f"{API_BASE}/warehouse/", {"type": "product"}, WAREHOUSE_DOC, True
        )
        fallback_probe["reason"] = "documented type parameter defaults to product"
        probes.append(fallback_probe)
        rows.extend(fallback_rows)

    if not rows:
        for candidate in (f"{API_ROOT}/warehouse/", f"{API_BASE}/warehouses"):
            candidate_probe, candidate_rows = probe(candidate, {"type": "product"}, WAREHOUSE_DOC, False)
            candidate_probe["reason"] = "undocumented compatibility probe"
            probes.append(candidate_probe)
            rows.extend(candidate_rows)

    ids = []
    for row in rows:
        wid = warehouse_id(row)
        if wid and wid not in ids:
            ids.append(wid)

    for wid in ids:
        url = f"{API_ROOT}/warehouse/goods/{wid}"
        status, body, elapsed, error = get(url)
        payload, valid_json = parse_json(body) if status == 200 else (None, False)
        probes.append({
            "method": "GET",
            "path": "/warehouse/goods/{warehouse_id}",
            "warehouse_id": wid,
            "url": url,
            "source": STOCK_DOC,
            "documented_contract": True,
            "http": status,
            "elapsed_s": elapsed,
            "json_valid": valid_json,
            "error": error,
            "response_top_level_type": type(payload).__name__ if valid_json else None,
            "response_keys": sorted(payload.keys()) if isinstance(payload, dict) else None,
        })

    confirmed_live_gets = [
        probe_result
        for probe_result in probes
        if probe_result.get("documented_contract")
        and probe_result.get("http") == 200
        and probe_result.get("json_valid")
        and (
            probe_result.get("rows_discovered", 0) > 0
            or probe_result.get("path") == "/warehouse/goods/{warehouse_id}"
        )
    ]
    list_ok = any(
        p.get("documented_contract")
        and p.get("path") == "/v2/warehouse/"
        and p.get("http") == 200
        and p.get("json_valid")
        and p.get("rows_discovered", 0) > 0
        for p in probes
    )
    stock_ok = any(
        p.get("documented_contract")
        and p.get("path") == "/warehouse/goods/{warehouse_id}"
        and p.get("http") == 200
        and p.get("json_valid")
        for p in probes
    )

    # Issue #42 defines the warehouse blocker narrowly as the documented list
    # contract. Stock detail is reported separately and must not invalidate a
    # successful list-contract verification. This avoids converting a separate
    # stock-detail diagnostic into a false warehouse-list failure.
    result = "PASS" if ids and list_ok else "NOT_VERIFIED"

    report = {
        "version": "20.47",
        "mode": "READ_ONLY",
        "result": result,
        "readonly": True,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "explicit_get_contracts": EXPLICIT_GET_CONTRACTS,
        "warehouse_reference_pages": REFERENCE_PAGES,
        "official_documentation": {
            "warehouse_list": WAREHOUSE_DOC,
            "stock": STOCK_DOC,
            "locations": LOCATIONS_DOC,
        },
        "warehouse_count": len(ids),
        "warehouse_ids_discovered": ids,
        "branch_ids_discovered": branch_ids,
        "probes": probes,
        "confirmed_live_gets": confirmed_live_gets,
        "warehouse_list_contract_verified": list_ok,
        "stock_detail_contract_verified": stock_ok,
        "diagnostic_only_undocumented_probes": [
            p for p in probes if not p.get("documented_contract")
        ],
        "retry_policy": {
            "max_retries": MAX_RETRIES,
            "timeout_seconds": TIMEOUT,
            "retryable_http": [408, 429, 500, 502, 503, 504],
        },
    }
    raw = json.dumps(report, ensure_ascii=False, indent=2).encode()
    report["report_sha256"] = hashlib.sha256(raw).hexdigest()
    output = os.getenv("WAREHOUSE_CONTRACT_OUTPUT", "marsel-unified-warehouse-contract.json")
    with open(output, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    print(f"WAREHOUSE_CONTRACT_RESULT={result}")
    print(f"WAREHOUSE_COUNT={len(ids)}")
    print(f"BRANCH_IDS_DISCOVERED={','.join(branch_ids) or 'NONE'}")
    print("WAREHOUSE_EXPLICIT_GET_CONTRACTS=2")
    print(f"WAREHOUSE_LIST_CONTRACT_VERIFIED={str(list_ok).lower()}")
    print(f"WAREHOUSE_STOCK_DETAIL_CONTRACT_VERIFIED={str(stock_ok).lower()}")
    print(f"WAREHOUSE_CONFIRMED_LIVE_GETS={len(confirmed_live_gets)}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
