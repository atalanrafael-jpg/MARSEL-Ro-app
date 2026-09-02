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
import re
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
    "source_system", "environment", "producing_job_or_run", "source_version",
    "generated_at", "sha256", "producer_identity", "scope",
)
CREDENTIAL_KEYS = {
    "api_key", "apikey", "authorization", "access_token", "refresh_token",
    "client_secret", "password", "passwd", "private_key", "secret",
}
TOKEN_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]+ PRIVATE KEY-----"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}\b", re.IGNORECASE),
)


def _is_iso_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _canonical_sha256(data: dict[str, object]) -> str:
    canonical = dict(data)
    canonical["sha256"] = ""
    payload = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _credential_like_material(value: object, key: str = "") -> str | None:
    normalized_key = key.strip().lower().replace("-", "_")
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


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"{path.name}: invalid_json_or_read_error:{exc}"]
    if not isinstance(data, dict):
        return [f"{path.name}: root_must_be_object"]

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
    if not _is_iso_timestamp(data.get("generated_at")):
        errors.append(f"{path.name}: generated_at_invalid")
    for key in PROVENANCE:
        if not data.get(key):
            errors.append(f"{path.name}: missing_provenance:{key}")
    if data.get("sha256") != _canonical_sha256(data):
        errors.append(f"{path.name}: sha256_mismatch")
    marker = _credential_like_material(data)
    if marker:
        errors.append(f"{path.name}: credential_like_material_detected:{marker}")
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
