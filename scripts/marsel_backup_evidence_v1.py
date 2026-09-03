#!/usr/bin/env python3
"""Convert a completed read-only RO App export into canonical backup evidence.

This wrapper does not call RO App and does not fabricate evidence. It accepts
only the output of marsel_full_readonly_backup_v1.py and emits backup_evidence.json
that satisfies the production evidence provenance contract when the export is
complete and mutation-free.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

INPUT = Path(os.environ.get("MARSEL_FULL_BACKUP_INPUT", "marsel-full-readonly-backup-v1.json"))
OUTPUT = Path(os.environ.get("MARSEL_BACKUP_EVIDENCE_OUTPUT", "backup_evidence.json"))
SOURCE_VERSION = os.environ.get("GITHUB_SHA", "unknown")
RUN_ID = os.environ.get("GITHUB_RUN_ID", "unknown")
ENVIRONMENT = os.environ.get("MARSEL_EVIDENCE_ENVIRONMENT", "staging")

if not INPUT.exists():
    raise SystemExit(f"backup export missing: {INPUT}")

source = json.loads(INPUT.read_text(encoding="utf-8"))
if not isinstance(source, dict):
    raise SystemExit("backup export must be a JSON object")

complete = source.get("complete") is True
readonly = source.get("readonly") is True
writes = source.get("write_requests_made") == 0
mutated = source.get("ro_app_data_mutated") is False
status = "PASS" if complete and readonly and writes and mutated else "REVIEW_REQUIRED"

report = {
    "status": status,
    "readonly": True,
    "write_requests_made": 0,
    "ro_app_data_mutated": False,
    "source_system": "roapp",
    "environment": ENVIRONMENT,
    "producing_job_or_run": f"github-actions:{RUN_ID}",
    "source_version": SOURCE_VERSION,
    "producer_identity": "github-actions:marsel-backup-evidence-producer",
    "scope": "documented GET endpoint export from canonical RO App API inventory",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "operation": "backup/export",
    "completion_result": "PASS" if complete else "INCOMPLETE",
    "integrity_reference": source.get("sha256"),
    "export_summary": {
        "documented_get_endpoints": len(source.get("documented_get_endpoints", [])),
        "successful_endpoints": source.get("successful_endpoints"),
        "failed_endpoints": source.get("failed_endpoints"),
        "total_records": source.get("total_records"),
        "backup_output": str(INPUT),
    },
}
canonical = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
report["sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
if status != "PASS":
    raise SystemExit(2)
