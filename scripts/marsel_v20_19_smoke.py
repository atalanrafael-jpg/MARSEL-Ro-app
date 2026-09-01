#!/usr/bin/env python3
"""Read-only RO App authentication smoke test.

Canonical configuration uses ROAPP_BASE_URL, matching app/config.py.
ROAPP_API_BASE remains a compatibility fallback for legacy scripts.
"""

import os

import httpx

base = os.getenv("ROAPP_BASE_URL") or os.getenv("ROAPP_API_BASE", "https://api.roapp.io/v2")
base = base.rstrip("/")
key = os.getenv("ROAPP_API_KEY")
assert key, "ROAPP_API_KEY is required"

response = httpx.get(
    f"{base}/orders",
    headers={
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
    },
    timeout=30,
)

print(f"HTTP={response.status_code}")
print(f"CONTENT_TYPE={response.headers.get('content-type', '')}")
assert 200 <= response.status_code < 300, "RO App read request failed"
print("WRITE_REQUESTS=0")
print("RO_APP_DATA_MUTATED=False")
