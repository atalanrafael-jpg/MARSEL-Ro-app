#!/usr/bin/env python3
"""MARSEL V20.48 — documented warehouse-list contract diagnostic, READ ONLY.

Purpose: determine why the documented GET /warehouse/ contract is not being
recognized by the current parser. No fallback endpoint is treated as official.
No write request is made.
"""
from __future__ import annotations

import json
import os
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

KEY = os.getenv("ROAPP_API_KEY", "")
BASE = os.getenv("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
TIMEOUT = float(os.getenv("ROAPP_TIMEOUT", "30"))
INTERVAL = max(float(os.getenv("ROAPP_MIN_REQUEST_INTERVAL", "0.34")), 0.34)
OUT = os.getenv("WAREHOUSE_DIAGNOSTIC_OUTPUT", "marsel-warehouse-contract-v20-48.json")
DOC = "https://roapp.readme.io/reference/get-warehouses"

if not KEY:
    raise SystemExit("ROAPP_API_KEY is required")


def get(path: str, query: dict[str, str] | None = None):
    time.sleep(INTERVAL)
    url = f"{BASE}{path}"
    if query:
        url += "?" + urlencode(query)
    req = Request(url, headers={"Authorization": f"Bearer {KEY}", "Accept": "application/json", "User-Agent": "MARSEL-V20.48-READONLY"}, method="GET")
    started = time.time()
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {"url": url, "http": response.status, "elapsed_s": round(time.time() - started, 3), "body": body}
    except Exception as exc:
        body = ""
        status = getattr(exc, "code", None)
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        return {"url": url, "http": status, "elapsed_s": round(time.time() - started, 3), "error": f"{type(exc).__name__}: {exc}", "body": body}


def summarize(result):
    body = result.get("body", "")
    summary = {k: result.get(k) for k in ("url", "http", "elapsed_s", "error")}
    try:
        payload = json.loads(body)
    except Exception:
        summary.update({"json_valid": False, "top_level_type": None, "keys": None, "candidate_counts": {}})
        return summary
    summary.update({"json_valid": True, "top_level_type": type(payload).__name__})
    if isinstance(payload, dict):
        summary["keys"] = sorted(payload.keys())
        counts = {}
        for key, value in payload.items():
            if isinstance(value, list):
                counts[key] = len(value)
            elif isinstance(value, dict):
                counts[key] = {"type": "dict", "keys": sorted(value.keys())[:30]}
        summary["candidate_counts"] = counts
        summary["page"] = payload.get("page")
        summary["count"] = payload.get("count")
        summary["success"] = payload.get("success")
    elif isinstance(payload, list):
        summary["keys"] = None
        summary["candidate_counts"] = {"root_list": len(payload)}
    return summary


def main():
    probes = []
    for query in ({"type": "product"}, {"type": "product", "page": "1"}):
        result = get("/warehouse/", query)
        probes.append(summarize(result))

    report = {
        "version": "20.48",
        "mode": "READ_ONLY",
        "official_documentation": DOC,
        "documented_contract": "/v2/warehouse/",
        "probes": probes,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    for index, probe in enumerate(probes, 1):
        print(f"WAREHOUSE_LIST_PROBE_{index}_HTTP={probe.get('http')}")
        print(f"WAREHOUSE_LIST_PROBE_{index}_JSON={probe.get('json_valid')}")
        print(f"WAREHOUSE_LIST_PROBE_{index}_TYPE={probe.get('top_level_type')}")
        print(f"WAREHOUSE_LIST_PROBE_{index}_KEYS={','.join(probe.get('keys') or [])}")
        print(f"WAREHOUSE_LIST_PROBE_{index}_COUNTS={json.dumps(probe.get('candidate_counts', {}), ensure_ascii=False, sort_keys=True)}")
        print(f"WAREHOUSE_LIST_PROBE_{index}_PAGE={probe.get('page')}")
        print(f"WAREHOUSE_LIST_PROBE_{index}_COUNT={probe.get('count')}")
        print(f"WAREHOUSE_LIST_PROBE_{index}_SUCCESS={probe.get('success')}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=False")
    print(f"REPORT={OUT}")


if __name__ == "__main__":
    main()
