#!/usr/bin/env python3
"""MARSEL V20.31 — bounded, evidence-first, read-only API inventory.

The underlying V20.29 discovery engine is retained, but endpoint extraction is
made safety-strict: an HTTP method is accepted only when the documentation
explicitly binds that method to the same endpoint expression. An endpoint URL
or path without an explicit method is unresolved and is never silently treated
as GET. No write method is ever called.
"""
from __future__ import annotations

import html
import os
import re
import time
import marsel_api_inventory_v20_29 as base

VERSION = "20.31"


def clean_preserve_parameters(value):
    """Normalize documentation text without stripping {id} path parameters."""
    return html.unescape(str(value)).strip().replace("\\/", "/").strip("`'\"<>[]();,.")


base.VERSION = VERSION
base.OUT = os.environ.get("MARSEL_API_INVENTORY_OUTPUT", "marsel-api-inventory-v20-31.json")
base.clean = clean_preserve_parameters
base.TIMEOUT = min(int(os.environ.get("ROAPP_TIMEOUT", "8")), 8)
base.MAX_RETRIES = 0
base.RETRY_BASE = 0.0
base.MAX_DOCS = min(int(os.environ.get("MARSEL_MAX_DOCS", "40")), 40)
base.MAX_BUDGET = min(float(os.environ.get("MARSEL_INVENTORY_BUDGET_SECONDS", "240")), 150.0)
base.MIN_INTERVAL = max(float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34")), 0.34)


# V20.29 previously promoted an endpoint with no explicit HTTP method to GET.
# That violates the V13 evidence rule. Keep only method/path pairs explicitly
# documented in the same local evidence window. Undeclared methods remain
# unresolved and therefore cannot be probed.
def strict_extract_paths(text, source, store):
    t = html.unescape(text).replace("\\/", "/")

    for m in base.METHOD_PATH_RE.finditer(t):
        base.add(
            store,
            m.group(1),
            m.group(2),
            "DOCUMENTATION_CONFIRMED",
            source,
            "explicit method/path",
        )

    for m in base.API_URL_RE.finditer(t):
        method = base.nearby_method(t, m.start(), m.end())
        if method:
            base.add(
                store,
                method,
                m.group(0),
                "DOCUMENTATION_CONFIRMED",
                source,
                "explicit API URL with nearby documented method",
            )

    for m in base.PATH_RE.finditer(t):
        path = base.normalize_path(m.group(0))
        if not path:
            continue
        method = base.nearby_method(t, m.start(), m.end())
        if method:
            base.add(
                store,
                method,
                path,
                "DOCUMENTATION_CONFIRMED",
                source,
                "explicit path expression with nearby documented method",
            )


base.extract_paths = strict_extract_paths

# Bound every source of latency before delegating to the read-only engine.
_deadline = time.monotonic() + base.MAX_BUDGET
_original_fetch = base.fetch


def bounded_fetch(url, headers=None):
    remaining = _deadline - time.monotonic()
    if remaining <= 0:
        return None, "", 0.0, "inventory budget exhausted"
    old_timeout = base.TIMEOUT
    base.TIMEOUT = max(1, min(old_timeout, int(remaining)))
    try:
        return _original_fetch(url, headers)
    finally:
        base.TIMEOUT = old_timeout


base.fetch = bounded_fetch

if __name__ == "__main__":
    raise SystemExit(base.main())
