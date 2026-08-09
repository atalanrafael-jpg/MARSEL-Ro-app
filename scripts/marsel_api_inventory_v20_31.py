#!/usr/bin/env python3
"""MARSEL V20.31 — bounded compatibility-safe API inventory.

Restores the richer V20.29 discovery engine while adding a hard runtime guard
for CI. The inventory is READ ONLY: no write methods are called and
parameterized identifiers are never guessed.
"""
from __future__ import annotations

import html
import os
import time
import marsel_api_inventory_v20_29 as base

VERSION = "20.31"


def clean_preserve_parameters(value):
    """Normalize documentation text without stripping {id} path parameters."""
    return html.unescape(str(value)).strip().replace("\\/", "/").strip("`'\"<>[]();,.")


# V20.29's discovery is intentionally retained, but its unbounded request
# behavior is unsafe for a 15-minute GitHub Actions job. Bound every source of
# latency before delegating to the proven read-only implementation.
base.VERSION = VERSION
base.OUT = os.environ.get("MARSEL_API_INVENTORY_OUTPUT", "marsel-api-inventory-v20-31.json")
base.clean = clean_preserve_parameters
base.TIMEOUT = min(int(os.environ.get("ROAPP_TIMEOUT", "8")), 8)
base.MAX_RETRIES = 0
base.RETRY_BASE = 0.0
base.MAX_DOCS = min(int(os.environ.get("MARSEL_MAX_DOCS", "40")), 40)
base.MAX_BUDGET = min(float(os.environ.get("MARSEL_INVENTORY_BUDGET_SECONDS", "240")), 150.0)

# Keep the API's documented request pacing; do not increase request rate.
base.MIN_INTERVAL = max(float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34")), 0.34)

# The wrapper itself also stops before the CI job timeout. This does not
# cancel an individual in-flight request; that request is bounded by TIMEOUT.
_deadline = time.monotonic() + base.MAX_BUDGET
_original_fetch = base.fetch


def bounded_fetch(url, headers=None):
    remaining = _deadline - time.monotonic()
    if remaining <= 0:
        return None, "", 0.0, "inventory budget exhausted"
    # base.fetch uses base.TIMEOUT; temporarily cap it to remaining time.
    old_timeout = base.TIMEOUT
    base.TIMEOUT = max(1, min(old_timeout, int(remaining)))
    try:
        return _original_fetch(url, headers)
    finally:
        base.TIMEOUT = old_timeout


base.fetch = bounded_fetch

if __name__ == "__main__":
    raise SystemExit(base.main())
