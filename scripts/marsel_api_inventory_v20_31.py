#!/usr/bin/env python3
"""MARSEL V20.31 — compatibility-safe API inventory.

Restores the richer V20.29 discovery engine (including OpenAPI/Swagger
candidate discovery) while fixing V20.30's regression that removed parameter
braces during path normalization. This wrapper never performs writes.
"""
from __future__ import annotations
import html
import os
import marsel_api_inventory_v20_29 as base

VERSION = "20.31"


def clean_preserve_parameters(value):
    """Normalize documentation text without stripping {id} path parameters."""
    return html.unescape(str(value)).strip().replace("\\/", "/").strip("`'\"<>[]();,.")


base.VERSION = VERSION
base.OUT = os.environ.get("MARSEL_API_INVENTORY_OUTPUT", "marsel-api-inventory-v20-31.json")
base.clean = clean_preserve_parameters

if __name__ == "__main__":
    raise SystemExit(base.main())
