#!/usr/bin/env python3
"""MARSEL V20.22 — RO App API v2 READ-ONLY preflight.

Only verified GET /orders is exercised. No write methods are implemented or called.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "30"))
OUT = os.environ.get("MARSEL_PREFLIGHT_OUTPUT", "marsel-api-preflight-v20-22.json")


def get(path: str, params: dict[str, int] | None = None) -> dict:
    url = f"{BASE}{path}"
    if params:
        from urllib.parse import urlencode
        url += "?" + urlencode(params)
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Accept": "application/json",
            "User-Agent": "MARSEL-API-Preflight/20.22",
        },
        method="GET",
    )
    started = time.monotonic()
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            body = response.read().decode("utf-8")
            return {
                "http": response.status,
                "elapsed_s": round(time.monotonic() - started, 3),
                "json": json.loads(body),
                "error": None,
            }
    except HTTPError as exc:
        return {
            "http": exc.code,
            "elapsed_s": round(time.monotonic() - started, 3),
            "json": None,
            "error": exc.read().decode("utf-8", errors="replace")[:1000],
        }
    except (URLError, TimeoutError, ValueError) as exc:
        return {
            "http": None,
            "elapsed_s": round(time.monotonic() - started, 3),
            "json": None,
            "error": str(exc),
        }


def main() -> int:
    if not KEY:
        raise SystemExit("ROAPP_API_KEY is required")

    first = get("/orders", {"page": 1})
    payload = first.get("json")
    rows = []
    if isinstance(payload, dict):
        for key in ("data", "items", "orders"):
            if isinstance(payload.get(key), list):
                rows = payload[key]
                break
    elif isinstance(payload, list):
        rows = payload

    report = {
        "version": "20.22",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_url": BASE,
        "readonly": True,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "method_policy": {
            "allowed": ["GET"],
            "forbidden": ["POST", "PUT", "PATCH", "DELETE"],
        },
        "verified_scope": ["GET /orders?page=1"],
        "orders_probe": {
            "http": first["http"],
            "elapsed_s": first["elapsed_s"],
            "records": len(rows),
            "error": first["error"],
        },
    }
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("=== MARSEL API PREFLIGHT V20.22 / READ ONLY ===")
    print(f"BASE_URL={BASE}")
    print(f"GET_ORDERS_HTTP={first['http']}")
    print(f"ORDERS_PAGE_1_RECORDS={len(rows)}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=False")
    print(f"REPORT={OUT}")
    return 0 if first["http"] == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
