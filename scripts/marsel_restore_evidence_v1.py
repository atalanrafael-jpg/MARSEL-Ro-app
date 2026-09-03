#!/usr/bin/env python3
"""Validate independently produced restore evidence.

This program NEVER performs a restore and NEVER mutates RO App data. It only
validates a JSON report produced by an external, controlled non-production
restore procedure. Missing input, unsafe target, failed verification, writes
or missing provenance are hard failures; no PASS is fabricated.
"""
from __future__ import annotations
import hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

INPUT = Path(os.environ.get("MARSEL_RESTORE_EVIDENCE_INPUT", "restore_evidence.input.json"))
OUTPUT = Path(os.environ.get("MARSEL_RESTORE_EVIDENCE_OUTPUT", "restore_evidence.json"))

REQUIRED = {
    "status", "readonly", "write_requests_made", "ro_app_data_mutated",
    "source_system", "environment", "producing_job_or_run", "source_version",
    "producer_identity", "scope", "generated_at", "sha256", "operation",
    "tested_backup", "target_environment", "restore_result", "verification_result",
    "integrity_reference",
}

if not INPUT.exists():
    raise SystemExit(f"restore evidence input missing: {INPUT}")

try:
    data = json.loads(INPUT.read_text(encoding="utf-8"))
except Exception as exc:
    raise SystemExit(f"invalid restore evidence JSON: {exc}")

if not isinstance(data, dict):
    raise SystemExit("restore evidence must be a JSON object")

missing = sorted(REQUIRED - set(data))
if missing:
    raise SystemExit("missing required fields: " + ", ".join(missing))

status = str(data["status"]).upper()
target = str(data["target_environment"]).lower()
restore_result = str(data["restore_result"]).upper()
verification = str(data["verification_result"]).upper()
unsafe_targets = {"production", "prod", "live"}

checks = {
    "status_pass": status in {"PASS", "PASSED", "VERIFIED"},
    "target_non_production": target not in unsafe_targets,
    "restore_pass": restore_result in {"PASS", "PASSED", "VERIFIED"},
    "verification_pass": verification in {"PASS", "PASSED", "VERIFIED"},
    "readonly": data["readonly"] is True,
    "zero_write_requests": data["write_requests_made"] == 0,
    "no_ro_app_mutation": data["ro_app_data_mutated"] is False,
    "tested_backup_present": bool(data["tested_backup"]),
    "integrity_reference_present": bool(data["integrity_reference"]),
    "provenance_complete": all(bool(data.get(k)) for k in (
        "source_system", "environment", "producing_job_or_run", "source_version",
        "producer_identity", "scope", "generated_at", "sha256", "operation")),
}

try:
    ts = datetime.fromisoformat(str(data["generated_at"]).replace("Z", "+00:00"))
    checks["timestamp_timezone_aware"] = ts.tzinfo is not None and ts.utcoffset() is not None
    checks["timestamp_not_future"] = ts <= datetime.now(timezone.utc)
except Exception:
    checks["timestamp_timezone_aware"] = False
    checks["timestamp_not_future"] = False

passed = all(checks.values())
result = dict(data)
result["schema"] = "marsel-restore-evidence/v1"
result["validated_by"] = "marsel_restore_evidence_v1.py"
result["validation_result"] = "PASS" if passed else "BLOCKED"
result["fabricated_evidence"] = False
result["production_write_enabled"] = False
result["validation_checks"] = checks
canonical = json.dumps({k: result[k] for k in sorted(result) if k != "validation_sha256"}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
result["validation_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"RESULT={result['validation_result']}")
print("PRODUCTION_WRITE_ENABLED=False")
if not passed:
    raise SystemExit(2)
