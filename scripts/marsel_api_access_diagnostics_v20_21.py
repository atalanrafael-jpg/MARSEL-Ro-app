#!/usr/bin/env python3
"""MARSEL V20.21 — RO App access diagnostics, READ ONLY.

Purpose: distinguish authentication (401), permission/scope (403), missing endpoint
(404), rate limiting (429), server failures (5xx), and successful access.
Only GET requests are issued. No RO App data is written or deleted.
"""
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path
import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "30"))
OUT = Path(os.environ.get("MARSEL_DIAGNOSTIC_OUTPUT", "marsel-api-access-diagnostics-v20-21.json"))
if not KEY:
    raise SystemExit("ROAPP_API_KEY is required")

headers = {"Authorization": f"Bearer {KEY}", "Accept": "application/json", "User-Agent": "MARSEL-V20.21-Readonly-Diagnostics"}
endpoints = ["/company", "/orders"]
results = []

with httpx.Client(timeout=TIMEOUT, follow_redirects=True) as client:
    for endpoint in endpoints:
        try:
            r = client.get(f"{BASE}{endpoint}", headers=headers)
            body = r.text[:1000]
            try:
                parsed = r.json()
                if isinstance(parsed, dict):
                    safe_body = {k: parsed[k] for k in parsed.keys() if k.lower() in {"error", "message", "detail", "code", "status"}}
                    body = json.dumps(safe_body, ensure_ascii=False)[:1000] if safe_body else "JSON response received"
            except Exception:
                pass
            results.append({"endpoint": endpoint, "http_status": r.status_code, "classification": {
                200: "PASS",
                401: "AUTHENTICATION_FAILURE",
                403: "PERMISSION_OR_SCOPE_FAILURE",
                404: "ENDPOINT_NOT_FOUND",
                405: "METHOD_NOT_ALLOWED",
                429: "RATE_LIMIT",
            }.get(r.status_code, "SERVER_ERROR" if r.status_code >= 500 else "HTTP_ERROR"), "response_excerpt": body})
        except Exception as exc:
            results.append({"endpoint": endpoint, "http_status": None, "classification": "NETWORK_OR_TIMEOUT", "error_type": type(exc).__name__, "response_excerpt": str(exc)[:500]})

report = {
    "version": "20.21",
    "readonly": True,
    "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
    "api_base": BASE,
    "endpoints": results,
    "write_requests_made": 0,
    "ro_app_data_mutated": False,
}
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
for item in results:
    print(f"{item['endpoint']} HTTP={item['http_status']} CLASSIFICATION={item['classification']}")
    if item.get("response_excerpt"):
        print(f"RESPONSE={item['response_excerpt']}")
print("WRITE_REQUESTS_MADE=0")
print("RO_APP_DATA_MUTATED=False")
print(f"REPORT={OUT}")
# Diagnostic job itself must complete so the evidence can be reviewed; it never treats 401/403/404 as success.
if any(item.get("classification") in {"PASS"} for item in results):
    print("DIAGNOSTIC_RESULT=PARTIAL_OR_PASS")
else:
    print("DIAGNOSTIC_RESULT=ACCESS_BLOCKED_OR_UNAVAILABLE")
