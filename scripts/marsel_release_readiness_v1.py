#!/usr/bin/env python3
"""MARSEL release-readiness controller.

Static/read-only controller. It never contacts Ro App, never changes data, and
never authorizes production writes. It validates that the repository's canonical
controls are present and that unresolved external evidence cannot be silently
marked complete.
"""
from __future__ import annotations

import json
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
EVIDENCE_DIR = ROOT / "evidence"
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


def fail(msg: str) -> None:
    raise SystemExit(f"RELEASE_READINESS_FAIL: {msg}")


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        fail("missing_required_controls=" + ",".join(missing))

    gate = (ROOT / "scripts/marsel_production_gate_v1.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/mcp-production.yml").read_text(encoding="utf-8")
    if 'MARSEL_WRITE_APPROVED' not in gate or 'fail("write_approval_is_not_authorized_by_automated_gate")' not in gate:
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

    # Do not duplicate the production gate here. Its independent evidence checks
    # remain the authoritative pre-write control.
    try:
        docs = [json.loads((EVIDENCE_DIR / name).read_text(encoding="utf-8")) for name in REQUIRED_EVIDENCE]
    except Exception as exc:
        fail(f"evidence_parse_error={exc}")
    if not all(isinstance(d, dict) for d in docs):
        fail("evidence_document_is_not_object")
    print("EXTERNAL_EVIDENCE=PRESENT")
    print("RESULT=RUN_PRODUCTION_GATE_FOR_FINAL_DECISION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
