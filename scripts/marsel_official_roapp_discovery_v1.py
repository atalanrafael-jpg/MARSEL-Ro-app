#!/usr/bin/env python3
"""Discover the official RO App API index/OpenAPI metadata, read-only."""
from __future__ import annotations
import hashlib, json, sys, time
from datetime import datetime, timezone
from urllib.request import Request, urlopen

URLS = [
    "https://roapp.readme.io/llms.txt",
    "https://roapp.readme.io/openapi.json",
    "https://roapp.readme.io/openapi.yaml",
]

out = {"version": 1, "generated_at_utc": datetime.now(timezone.utc).isoformat(), "sources": []}
for url in URLS:
    item = {"url": url}
    try:
        req = Request(url, headers={"User-Agent": "MARSEL-ROApp-Discovery/1.0", "Accept": "text/plain,application/json,text/yaml,*/*"})
        with urlopen(req, timeout=20) as r:
            body = r.read()
            item.update({"http_status": getattr(r, "status", None), "content_type": r.headers.get("content-type"), "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(), "preview": body[:2000].decode("utf-8", "replace")})
    except Exception as e:
        item.update({"error": f"{type(e).__name__}: {e}"})
    out["sources"].append(item)
    time.sleep(0.34)

out["official_llms_available"] = any(x.get("url", "").endswith("/llms.txt") and x.get("http_status") == 200 for x in out["sources"])
out["openapi_available"] = any("openapi" in x.get("url", "") and x.get("http_status") == 200 for x in out["sources"])
out["readonly"] = True
out["write_requests_made"] = 0
out["ro_app_data_mutated"] = False
print(json.dumps(out, ensure_ascii=False, indent=2))
with open("marsel-official-roapp-discovery-v1.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"OFFICIAL_LLMS_AVAILABLE={out['official_llms_available']}")
print(f"OPENAPI_AVAILABLE={out['openapi_available']}")
print("WRITE_REQUESTS_MADE=0")
print("RO_APP_DATA_MUTATED=False")
