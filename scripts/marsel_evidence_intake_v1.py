#!/usr/bin/env python3
"""Validate externally produced MARSEL production evidence.

Validation-only: never creates evidence, performs ROAPP writes, or changes
production state. The declared sha256 is the SHA-256 of canonical JSON with
its own sha256 field replaced by an empty string.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = ("backup_evidence.json", "restore_evidence.json", "wix_roapp_reconciliation.json", "marsel-unified-evidence.json", "duplicate_reference_evidence.json", "write_dry_run.json", "idempotency_evidence.json", "rollback_evidence.json")
PASS_STATUSES = {"PASS", "PASSED", "VERIFIED"}
PROVENANCE = ("source_system", "environment", "producing_job_or_run", "source_version", "sha256", "producer_identity", "scope")
TIMESTAMP_KEYS = ("generated_at", "verified_at", "timestamp")
CREDENTIAL_KEYS = {"api_key", "apikey", "authorization", "access_token", "accesstoken", "refresh_token", "refreshtoken", "client_secret", "clientsecret", "password", "passwd", "private_key", "privatekey", "secret"}
TOKEN_PATTERNS = (re.compile(r"-----BEGIN [A-Z0-9 ]+ PRIVATE KEY-----"), re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}\b", re.IGNORECASE))
EVIDENCE_REQUIREMENTS = {
    "backup_evidence.json": ("operation", "completion_result", "integrity_reference"),
    "restore_evidence.json": ("tested_backup", "target_environment", "restore_result", "verification_result"),
    "wix_roapp_reconciliation.json": ("systems", "reconciliation_scope", "comparison_result", "unresolved_differences"),
    "duplicate_reference_evidence.json": ("duplicate_check_scope", "duplicate_check_result"),
    "write_dry_run.json": ("operation_set", "writes_executed"),
    "idempotency_evidence.json": ("operation", "idempotency_tested", "idempotent"),
    "rollback_evidence.json": ("tested", "reversible", "test_result"),
}


def _evidence_timestamp(data: dict[str, object]) -> object:
    return data.get("generated_at") or data.get("verified_at") or data.get("timestamp")


def _parse_iso_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else None


def _max_age_hours() -> float:
    try:
        value = float(os.getenv("MARSEL_EVIDENCE_MAX_AGE_HOURS", "24"))
    except ValueError:
        return 24.0
    return value if value >= 0 else 24.0


def _canonical_sha256(data: dict[str, object]) -> str:
    canonical = dict(data)
    canonical["sha256"] = ""
    payload = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _credential_like_material(value: object, key: str = "") -> str | None:
    normalized_key = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key.strip()).lower().replace("-", "_")
    if normalized_key in CREDENTIAL_KEYS:
        return normalized_key
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            marker = _credential_like_material(child_value, str(child_key))
            if marker:
                return marker
    elif isinstance(value, list):
        for child in value:
            marker = _credential_like_material(child)
            if marker:
                return marker
    elif isinstance(value, str):
        for pattern in TOKEN_PATTERNS:
            if pattern.search(value):
                return pattern.pattern
    return None


def _validate_evidence_specifics(filename: str, data: dict[str, object]) -> list[str]:
    errors = []
    for key in EVIDENCE_REQUIREMENTS.get(filename, ()):
        if key not in data or data[key] in (None, "", []):
            errors.append(f"{filename}: missing_evidence_specific:{key}")
    if filename == "write_dry_run.json" and "writes_executed" in data and data["writes_executed"] not in (0, False, None):
        errors.append(f"{filename}: writes_executed_must_be_zero_false_or_null")
    if filename == "idempotency_evidence.json":
        if data.get("idempotency_tested") is not True:
            errors.append(f"{filename}: idempotency_tested_must_be_true")
        if data.get("idempotent") is not True:
            errors.append(f"{filename}: idempotent_must_be_true")
    if filename == "rollback_evidence.json":
        if data.get("tested") is not True:
            errors.append(f"{filename}: tested_must_be_true")
        if data.get("reversible") is not True:
            errors.append(f"{filename}: reversible_must_be_true")
    return errors


def validate_file(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"{path.name}: invalid_json_or_read_error:{exc}"]
    if not isinstance(data, dict):
        return [f"{path.name}: root_must_be_object"]
    errors = []
    status = str(data.get("status", "")).upper()
    result = str(data.get("result", "")).upper()
    if status not in PASS_STATUSES and result != "PASS":
        errors.append(f"{path.name}: status_not_verified")
    if data.get("readonly") is not True:
        errors.append(f"{path.name}: readonly_must_be_true")
    if data.get("write_requests_made") != 0:
        errors.append(f"{path.name}: write_requests_made_must_be_zero")
    if data.get("ro_app_data_mutated") is not False:
        errors.append(f"{path.name}: ro_app_data_mutated_must_be_false")
    parsed_timestamp = _parse_iso_timestamp(_evidence_timestamp(data))
    if parsed_timestamp is None:
        errors.append(f"{path.name}: evidence_timestamp_invalid_or_timezone_missing")
    else:
        age_seconds = (datetime.now(timezone.utc) - parsed_timestamp).total_seconds()
        if age_seconds < 0:
            errors.append(f"{path.name}: evidence_timestamp_in_future")
        elif age_seconds > _max_age_hours() * 3600:
            errors.append(f"{path.name}: stale_evidence")
    for key in PROVENANCE:
        if not data.get(key):
            errors.append(f"{path.name}: missing_provenance:{key}")
    if data.get("sha256") != _canonical_sha256(data):
        errors.append(f"{path.name}: sha256_mismatch")
    errors.extend(_validate_evidence_specifics(path.name, data))
    marker = _credential_like_material(data)
    if marker:
        errors.append(f"{path.name}: credential_like_material_detected:{marker}")
    return errors


def validate_directory(root: Path) -> dict[str, object]:
    errors, present, missing = [], [], []
    for name in REQUIRED:
        path = root / name
        if not path.is_file():
            missing.append(name)
        else:
            present.append(name)
            errors.extend(validate_file(path))
    return {"status": "PASS" if not missing and not errors else "BLOCKED", "readonly": True, "write_requests_made": 0, "ro_app_data_mutated": False, "required": list(REQUIRED), "present": present, "missing": missing, "errors": errors, "validated_at": datetime.now(timezone.utc).isoformat()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed MARSEL evidence intake validator")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate_directory(args.directory)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
