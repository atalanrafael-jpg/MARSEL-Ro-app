#!/usr/bin/env python3
"""MARSEL V20.31 — bounded, evidence-first, read-only API inventory.

The inventory is safety-strict: an HTTP method is accepted only when the
official documentation explicitly binds that method to the endpoint. No write
method is ever called and parameterized identifiers are never guessed.
"""
from __future__ import annotations

import html
import os
import re
import time

try:
    # Normal package import (pytest / repository-root execution).
    from . import marsel_api_inventory_v20_29 as base
except ImportError:
    # Direct script execution from GitHub Actions' scripts/ directory.
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
base.MAX_DOCS = min(int(os.environ.get("MARSEL_MAX_DOCS", "200")), 200)
base.MAX_BUDGET = min(float(os.environ.get("MARSEL_INVENTORY_BUDGET_SECONDS", "300")), 300.0)
base.MIN_INTERVAL = max(float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34")), 0.34)


def _same_line_method(text, start, end):
    """Return a method only when it is explicitly tied to the path on its line."""
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end < 0:
        line_end = len(text)
    line = text[line_start:line_end]
    path_offset = start - line_start
    prefix = line[:path_offset]
    match = re.search(r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b\s*$", prefix, re.IGNORECASE)
    return match.group(1).upper() if match else None


def strict_extract_paths(text, source, store):
    """Accept only method/path pairs explicitly evidenced on the same line."""
    t = html.unescape(text).replace("\\/", "/")

    for m in base.METHOD_PATH_RE.finditer(t):
        base.add(store, m.group(1), m.group(2), "DOCUMENTATION_CONFIRMED", source, "explicit method/path")

    for m in base.API_URL_RE.finditer(t):
        method = _same_line_method(t, m.start(), m.end())
        if method:
            base.add(store, method, m.group(0), "DOCUMENTATION_CONFIRMED", source,
                     "explicit API URL with same-line documented method")

    for m in base.PATH_RE.finditer(t):
        path = base.normalize_path(m.group(0))
        if not path:
            continue
        method = _same_line_method(t, m.start(), m.end())
        if method:
            base.add(store, method, path, "DOCUMENTATION_CONFIRMED", source,
                     "explicit path expression with same-line documented method")


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
# Re-export the canonical runner so wrapper versions can delegate safely.
main = base.main

if __name__ == "__main__":
    raise SystemExit(main())
