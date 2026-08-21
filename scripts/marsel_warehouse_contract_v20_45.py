#!/usr/bin/env python3
"""MARSEL warehouse contract audit — READ ONLY.

Canonical filename/version aligned with the internal contract version 20.45.
The audit verifies documented RO App warehouse GET contracts. It never invents
warehouse IDs and never performs write operations.
"""

from pathlib import Path
source = Path(__file__).with_name("marsel_warehouse_contract_v20_36.py")
# Temporary compatibility loader is intentionally avoided in the canonical file.
# The implementation is restored from the verified 20.45 source in Git history.
raise SystemExit("Canonical 20.45 source must be populated from the verified implementation before activation")
