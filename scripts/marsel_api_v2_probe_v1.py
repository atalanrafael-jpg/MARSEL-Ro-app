#!/usr/bin/env python3
"""RO APP V2 read-only probe.
Only registry entries with method GET and status CONFIRMED are callable.
No write method is accepted. Parameterized routes are rejected.
"""
from __future__ import annotations
import os, sys, json
from urllib.parse import urljoin
import httpx

BASE = os.getenv("ROAPP_API_BASE", "https://api.roapp.io/v2/")
KEY = os.getenv("ROAPP_API_KEY")
if not KEY:
    raise SystemExit("FAIL: ROAPP_API_KEY is not configured")

# Populate only from explicitly verified official API Reference entries.
# Empty registry is a deliberate fail-closed state.
REGISTRY = []

for e in REGISTRY:
    if e.get("method") != "GET":
        raise SystemExit(f"FAIL: non-GET registry entry: {e}")
    if "{" in e.get("path", "") or "}" in e.get("path", ""):
        raise SystemExit(f"FAIL: parameterized path requires concrete ID: {e['path']}")
    if e.get("status") != "CONFIRMED":
        raise SystemExit(f"FAIL: unconfirmed endpoint: {e}")

results=[]
with httpx.Client(base_url=BASE, headers={"Authorization": f"Bearer {KEY}", "Accept":"application/json"}, timeout=30) as c:
    for e in REGISTRY:
        r=c.get(e["path"])
        results.append({"name":e["name"],"path":e["path"],"status_code":r.status_code,"ok":r.is_success})

failed=[x for x in results if not x["ok"]]
summary={"registry_count":len(REGISTRY),"success":len(results)-len(failed),"failed":len(failed),"write_requests_made":0,"ro_app_data_mutated":False,"result":"PASS" if REGISTRY and not failed else "INCOMPLETE"}
print(json.dumps({"summary":summary,"results":results},ensure_ascii=False,indent=2))
sys.exit(0 if summary["result"]=="PASS" else 2)
