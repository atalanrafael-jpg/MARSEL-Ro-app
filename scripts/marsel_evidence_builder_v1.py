#!/usr/bin/env python3
"""MARSEL ROAPP evidence collector boundary.

This command NEVER fabricates production evidence and NEVER performs writes.
It validates externally supplied evidence files and emits a deterministic
inventory for the production gate. Real backup/restore/reconciliation tests
must be executed by their authorized staging systems and supplied as files.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = (
    "backup_evidence.json",
    "restore_evidence.json",
    "wix_roapp_reconciliation.json",
    "marsel-unified-evidence.json",
    "duplicate_reference_evidence.json",
    "write_dry_run.json",
    "idempotency_evidence.json",
    "rollback_evidence.json",
)


def main() -> int:
    root = Path(os.getenv("MARSEL_EVIDENCE_DIR", "artifacts/evidence"))
    out = Path(os.getenv("MARSEL_EVIDENCE_INDEX", "artifacts/marsel-evidence-index.json"))
    out.parent.mkdir(parents=True, exist_ok=True)

    present, missing, invalid = [], [], []
    for filename in REQUIRED:
        path = root / filename
        if not path.exists():
            missing.append(filename)
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(doc, dict):
                invalid.append(filename)
            else:
                present.append(filename)
        except Exception:
            invalid.append(filename)

    payload = {
        "schema": "marsel-evidence-index/v1",
        "project": "MARSEL ROAPP",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "READ_ONLY",
        "production_write": False,
        "fabricated_evidence": False,
        "status": "READY_FOR_GATE" if not missing and not invalid else "BLOCKED",
        "present": present,
        "missing": missing,
        "invalid": invalid,
        "required_count": len(REQUIRED),
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"MARSEL_EVIDENCE_BUILDER={payload['status']}")
    print(f"PRESENT={len(present)}/{len(REQUIRED)}")
    if missing:
        print("MISSING=" + ",".join(missing))
    if invalid:
        print("INVALID=" + ",".join(invalid))
    return 0 if payload["status"] == "READY_FOR_GATE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
