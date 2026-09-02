#!/usr/bin/env python3
"""Validate externally produced MARSEL production evidence.

This module is intentionally validation-only: it never creates evidence,
performs ROAPP writes, or changes production state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
PASS_STATUSES = {"PASS", "PASSED", "VERIFIED"}
PROVENANCE = (
    "source_system",
    "environment",
    "producing_job_or_run",
    "source_version",
    "generated_at",
    "sha256",
    "producer_identity",
    "scope",
)


def _is_iso_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"{path.name}: invalid_json_or_read_error:{exc}"]

    if not isinstance(data, dict):
        return [f"{path.name}: root_must_be_object"]
    if str(data.get("status", "")).upper() not in PASS_STATUSES:
        errors.append(f"{path.name}: status_not_verified")
    if data.get("readonly") is not True:
        errors.append(f"{path.name}: readonly_must_be_true")
    if data.get("write_requests_made") != 0:
        errors.append(f"{path.name}: write_requests_made_must_be_zero")
    if data.get("ro_app_data_mutated") is not False:
        errors.append(f"{path.name}: ro_app_data_mutated_must_be_false")
    if not _is_iso_timestamp(data.get("generated_at")):
        errors.append(f"{path.name}: generated_at_invalid")
    for key in PROVENANCE:
        if not data.get(key):
            errors.append(f"{path.name}: missing_provenance:{key}")
    if data.get("sha256") != _sha256(path):
        errors.append(f"{path.name}: sha256_mismatch")
    serialized = json.dumps(data, ensure_ascii=False).lower()
    for marker in ("api_key", "authorization", "bearer ", "secret", "password", "token"):
        if marker in serialized:
            errors.append(f"{path.name}: credential_like_material_detected:{marker}")
            break
    return errors


def validate_directory(root: Path) -> dict[str, object]:
    errors: list[str] = []
    present: list[str] = []
    missing: list[str] = []
    for name in REQUIRED:
        path = root / name
        if not path.is_file():
            missing.append(name)
            continue
        present.append(name)
        errors.extend(validate_file(path))
    return {
        "status": "PASS" if not missing and not errors else "BLOCKED",
        "readonly": True,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "required": list(REQUIRED),
        "present": present,
        "missing": missing,
        "errors": errors,
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }


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
