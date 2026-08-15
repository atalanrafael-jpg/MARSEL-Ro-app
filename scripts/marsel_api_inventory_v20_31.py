#!/usr/bin/env python3
"""MARSEL V20.31 — bounded, evidence-first, read-only API inventory.

The inventory is safety-strict: an HTTP method is accepted only when the
official documentation explicitly binds that method to the endpoint. No write
method is ever called and parameterized identifiers are never guessed.
"""
from __future__ import annotations

import html
import os
import time

from scripts import marsel_api_inventory_v20_29 as base

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
# The official llms indexes currently expose substantially more than 40
# reference pages. Do not truncate the evidence set before inventorying it.
base.MAX_DOCS = min(int(os.environ.get("MARSEL_MAX_DOCS", "200")), 200)
base.MAX_BUDGET = min(float(os.environ.get("MARSEL_INVENTORY_BUDGET_SECONDS", "300")), 300.0)
base.MIN_INTERVAL = max(float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34")), 0.34)


def strict_extract_paths(text, source, store):
    """Accept only method/path pairs explicitly evidenced in the same text."""
    t = html.unescape(text).replace("\\/", "/")

    for m in base.METHOD_PATH_RE.finditer(t):
        base.add(store, m.group(1), m.group(2), "DOCUMENTATION_CONFIRMED", source, "explicit method/path")

    for m in base.API_URL_RE.finditer(t):
        method = base.nearby_method(t, m.start(), m.end())
        if method:
            base.add(store, method, m.group(0), "DOCUMENTATION_CONFIRMED", source,
                     "explicit API URL with nearby documented method")

    for m in base.PATH_RE.finditer(t):
        path = base.normalize_path(m.group(0))
        if not path:
            continue
        method = base.nearby_method(t, m.start(), m.end())
        if method:
            base.add(store, method, path, "DOCUMENTATION_CONFIRMED", source,
                     "explicit path expression with nearby documented method")


base.extract_paths = strict_extract_paths

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
