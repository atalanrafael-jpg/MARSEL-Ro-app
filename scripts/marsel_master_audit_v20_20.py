#!/usr/bin/env python3
"""MARSEL V20.20 — read-only master audit for RO App."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Support the existing CI command: `python scripts/marsel_master_audit_v20_20.py`.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.audit import audit_order_pages
from app.roapp_client import RoAppClient

OUTPUT_DIR = Path(os.environ.get("MARSEL_AUDIT_DIR", "artifacts/marsel-master-audit"))
MAX_PAGES = int(os.environ.get("MARSEL_MAX_ORDER_PAGES", "100"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def extract_records(pages: list[Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for page in pages:
        if isinstance(page, dict):
            rows = page.get("orders") or page.get("data") or page.get("items")
        elif isinstance(page, list):
            rows = page
        else:
            rows = None
        if isinstance(rows, list):
            records.extend(row for row in rows if isinstance(row, dict))
    return records


async def main() -> int:
    if not os.environ.get("ROAPP_API_KEY"):
        raise SystemExit("ROAPP_API_KEY is required")
    if MAX_PAGES < 1 or MAX_PAGES > 100:
        raise SystemExit("MARSEL_MAX_ORDER_PAGES must be between 1 and 100")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = await RoAppClient().get_orders_pages(MAX_PAGES)
    records = extract_records(pages)
    audit = audit_order_pages(pages)

    snapshot = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "RO App GET /orders",
        "readonly": True,
        "pages": pages,
    }
    snapshot_bytes = canonical_json(snapshot)
    snapshot_path = OUTPUT_DIR / "orders_snapshot.json"
    snapshot_path.write_bytes(snapshot_bytes)

    report = {
        "version": "20.20",
        "readonly": True,
        "mutation_allowed": False,
        "scope": "RO App orders endpoint only; not a full database backup",
        "pages_scanned": len(pages),
        "orders_scanned": len(records),
        "audit": audit,
        "snapshot_sha256": sha256_bytes(snapshot_bytes),
    }
    report_bytes = canonical_json(report)
    report_path = OUTPUT_DIR / "master_audit.json"
    report_path.write_bytes(report_bytes)

    manifest = {
        "version": "20.20",
        "readonly": True,
        "files": {
            snapshot_path.name: sha256_bytes(snapshot_bytes),
            report_path.name: sha256_bytes(report_bytes),
        },
    }
    (OUTPUT_DIR / "SHA256.json").write_bytes(canonical_json(manifest))

    print("=== MARSEL MASTER AUDIT V20.20 / READ ONLY ===")
    print(f"PAGES_SCANNED={len(pages)}")
    print(f"ORDERS_SCANNED={len(records)}")
    print(f"DUPLICATE_IDENTIFIERS={len(audit['duplicate_identifiers'])}")
    print(f"MISSING_ID={audit['missing_common_fields']['id']}")
    print(f"MISSING_STATUS={audit['missing_common_fields']['status']}")
    print(f"SNAPSHOT_SHA256={manifest['files'][snapshot_path.name]}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=False")
    print(f"ARTIFACT_DIR={OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
