#!/usr/bin/env python3
"""MARSEL V20.32 — expanded documentation inventory, READ ONLY.

Extends the canonical V20.31 inventory without changing its safety model.
The only change is a larger documentation window so the canonical registry
can discover more of the current RO App v2 reference surface. No write
methods are executed and parameterized identifiers are never probed.
"""
from __future__ import annotations

import os

try:
    from . import marsel_api_inventory_v20_31 as base
except ImportError:
    import marsel_api_inventory_v20_31 as base

VERSION = "20.32"
base.VERSION = VERSION
base.OUT = os.environ.get("MARSEL_API_INVENTORY_OUTPUT", "marsel-api-inventory-v20-32.json")
base.MAX_DOCS = min(int(os.environ.get("MARSEL_MAX_DOCS", "300")), 300)
base.MAX_BUDGET = min(float(os.environ.get("MARSEL_INVENTORY_BUDGET_SECONDS", "300")), 300.0)
base.TIMEOUT = min(int(os.environ.get("ROAPP_TIMEOUT", "8")), 8)
base.MAX_RETRIES = 0
base.RETRY_BASE = 0.0
base.MIN_INTERVAL = max(float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34")), 0.34)

if __name__ == "__main__":
    raise SystemExit(base.main())
