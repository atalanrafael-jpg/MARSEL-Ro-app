#!/usr/bin/env python3
"""MARSEL V20.48 — documented RO App warehouse-list contract diagnostic.

READ-ONLY only. The warehouse-list endpoint is documented outside the /v2
namespace, while the current API reference uses /v2 for many other resources.
Undocumented compatibility routes are never promoted to PASS evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

KEY = os.getenv("ROAPP_API_KEY", "")
API_ROOT = os.getenv("ROAPP_API_ROOT", "https://api.roapp.io").rstrip("/")
TIMEOUT = float(os.getenv("ROAPP_TIMEOUT", "30"))
INTERVAL = max(float(os.getenv("ROAPP_MIN_REQUEST_INTERVAL", "0.34")), 0.34)
OUT = os.getenv("WAREHOUSE_DIAGNOSTIC_OUTPUT", "marsel-unified-warehouse-contract.json")
DOC = "https://roappua.readme.io/reference/get-warehouses"
DOCUMENTED_PATH = "/warehouse/"


def get(path: str, query: dict[str, str] | None = None):
    time.sleep(INTERVAL)
    url = f"{API_ROOT}{path}"
    if query:
        url += "?" + urlencode(query)
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Accept": "application/json",
            "User-Agent": "MARSEL-V20.48-READONLY",
        },
        method="GET",
    )
    started = time.time()
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {
                "url": url,
                "http": response.status,
                "elapsed_s": round(time.time() - started, 3),
                "body": body,
                "error": None,
            }
    except Exception as exc:
        body = ""
        status = getattr(exc, "code", None)
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        return {
            "url": url,
            "http": status,
            "elapsed_s": round(time.time() - started, 3),
            "body": body,
            "error": f"{type(exc).__name__}: {exc}",
        }


def summarize(result):
    body = result.get("body", "")
    summary = {k: result.get(k) for k in ("url", "http", "elapsed_s", "error")}
    try:
        payload = json.loads(body)
    except Exception:
        summary.update(
            {
                "json_valid": False,
                "top_level_type": None,
                "keys": None,
                "candidate_counts": {},
            }
        )
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


def main() -> int:
    if not KEY:
        raise SystemExit("ROAPP_API_KEY is required")

    probes = [
        summarize(get(DOCUMENTED_PATH, {"type": "product"})),
        summarize(get(DOCUMENTED_PATH, {"type": "product", "page": "1"})),
    ]
    list_ok = any(
        p.get("http") == 200
        and p.get("json_valid")
        and any(
            isinstance(v, int) and v > 0
            for v in (p.get("candidate_counts") or {}).values()
        )
        for p in probes
    )
    result = "PASS" if list_ok else "NOT_VERIFIED"
    report = {
        "version": "20.48",
        "mode": "READ_ONLY",
        "readonly": True,
        "result": result,
        "official_documentation": DOC,
        "documented_contract": "/warehouse/",
        "api_root": API_ROOT,
        "probed_path": "/warehouse/",
        "probes": probes,
        "warehouse_list_contract_verified": list_ok,
        "confirmed_live_gets": [
            p for p in probes if p.get("http") == 200 and p.get("json_valid")
        ],
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
    }
    raw = json.dumps(report, ensure_ascii=False, indent=2).encode()
    report["report_sha256"] = hashlib.sha256(raw).hexdigest()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    print(f"WAREHOUSE_CONTRACT_RESULT={result}")
    print(f"WAREHOUSE_LIST_CONTRACT_VERIFIED={str(list_ok).lower()}")
    print(f"WAREHOUSE_CONFIRMED_LIVE_GETS={len(report['confirmed_live_gets'])}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
