#!/usr/bin/env python3
"""MARSEL release-readiness controller.

Fail-closed controller for the canonical release. It never writes to RO App and
never treats a placeholder or malformed evidence file as production evidence.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ".github/workflows/mcp-production.yml",
    "scripts/marsel_canonical_self_check.py",
    "scripts/marsel_production_gate_v1.py",
    "docs/MARSEL-PRODUCTION-GO-LIVE-GATES.md",
    "docs/MARSEL_ROAPP_TASK_REGISTRY.md",
    "SECURITY.md",
]
REQUIRED_EVIDENCE = [
    "backup_evidence.json",
    "restore_evidence.json",
    "wix_roapp_reconciliation.json",
    "marsel-unified-evidence.json",
    "duplicate_reference_evidence.json",
    "write_dry_run.json",
    "idempotency_evidence.json",
    "rollback_evidence.json",
]
MAX_EVIDENCE_AGE_HOURS = 24
SECRET_PATTERN = re.compile(r"(?i)(bearer\s+|sk-[a-z0-9]|api[_-]?key\s*[:=]|password\s*[:=]|secret\s*[:=])")


def fail(msg: str) -> None:
    raise SystemExit(f"RELEASE_READINESS_FAIL: {msg}")


def validate_evidence(path: Path) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as exc:
        fail(f"evidence_parse_error:{path.name}:{exc}")

    if not isinstance(data, dict):
        fail(f"evidence_document_is_not_object:{path.name}")
    if SECRET_PATTERN.search(raw):
        fail(f"credential_like_material_in_evidence:{path.name}")

    required = {"status", "observed_at", "source"}
    missing = sorted(required - data.keys())
    if missing:
        fail(f"evidence_schema_missing:{path.name}:{','.join(missing)}")
    if data["status"] != "PASS":
        fail(f"evidence_not_pass:{path.name}:{data['status']}")
    if not isinstance(data["source"], str) or not data["source"].strip():
        fail(f"evidence_source_invalid:{path.name}")

    try:
        observed = datetime.fromisoformat(str(data["observed_at"]).replace("Z", "+00:00"))
    except ValueError as exc:
        fail(f"evidence_timestamp_invalid:{path.name}:{exc}")
    if observed.tzinfo is None:
        fail(f"evidence_timestamp_not_timezone_aware:{path.name}")
    age_hours = (datetime.now(timezone.utc) - observed.astimezone(timezone.utc)).total_seconds() / 3600
    if age_hours < -0.05:
        fail(f"evidence_timestamp_in_future:{path.name}")
    if age_hours > MAX_EVIDENCE_AGE_HOURS:
        fail(f"evidence_stale:{path.name}:age_hours={age_hours:.2f}")
    return data


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        fail("missing_required_controls=" + ",".join(missing))

    gate = (ROOT / "scripts/marsel_production_gate_v1.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/mcp-production.yml").read_text(encoding="utf-8")
    if "MARSEL_WRITE_APPROVED" not in gate or "fail(\"write_approval_is_not_authorized_by_automated_gate\")" not in gate:
        fail("production_write_fail_closed_control_missing")
    if "pytest" not in workflow or "pip-audit" not in workflow:
        fail("production_ci_controls_missing")

    absent = [name for name in REQUIRED_EVIDENCE if not (EVIDENCE_DIR / name).exists()]
    print("MARSEL_RELEASE_READINESS=FAIL_CLOSED")
    print("PRODUCTION_WRITE_AUTHORIZED=false")
    print("REPOSITORY_CONTROLS=PASS")
    if absent:
        print("EXTERNAL_EVIDENCE=NOT_PRESENT")
        print("MISSING_EVIDENCE=" + ",".join(absent))
        print("RESULT=NOT_PRODUCTION_READY")
        return 2

    for name in REQUIRED_EVIDENCE:
        validate_evidence(EVIDENCE_DIR / name)

    print("EXTERNAL_EVIDENCE=PRESENT_AND_VALID")
    print("RESULT=RUN_PRODUCTION_GATE_FOR_FINAL_DECISION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
