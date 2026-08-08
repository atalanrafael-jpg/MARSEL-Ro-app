#!/usr/bin/env python3
"""Run the verified V20.28 inventory against the current official RO App ReadMe index."""
from __future__ import annotations
import os
os.environ.setdefault("ROAPP_DOCS_INDEX", "https://roappua.readme.io/llms.txt")
from marsel_api_inventory_v20_28 import main
raise SystemExit(main())
