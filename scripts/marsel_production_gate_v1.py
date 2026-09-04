#!/usr/bin/env python3
"""MARSEL production gate — fail closed, READ-ONLY.

This gate never performs backup, restore, reconciliation, or WRITE operations.
It validates independently produced evidence and keeps production WRITE disabled
until every pre-write requirement is directly evidenced.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

MAX_AGE_HOURS = float(os.getenv("MARSEL_EVIDENCE_MAX_AGE_HOURS", "24"))
REQUIRED = {
    "backup": "backup_evidence.json",
    "restore": "restore_evidence.json",
    "wix_roapp_reconciliation": "wix_roapp_reconciliation.json",
    "readonly_inventory": "marsel-unified-evidence.json",
    "duplicate_reference": "duplicate_reference_evidence.json",
    "dry_run": "write_dry_run.json",
    "idempotency": "idempotency_evidence.json",
    "rollback": "rollback_evidence.json",
}
SECRET_PATTERNS = [
    re.compile(r"ROAPP_API_KEY\s*=\s*['\"][^'\"]{12,}['\"]", re.I),
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]{20,}", re.I),
    re.compile(r"(?:access|refresh)_token\s*[:=]\s*['\"][^'\"]{20,}['\"]", re.I),
]


def fail(msg: str) -> None:
    print(f"PRODUCTION_GATE_FAIL={msg}")
    raise SystemExit(1)


def load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid_json:{path}:{exc}")
    if not isinstance(value, dict):
        fail(f"evidence_not_object:{path}")
    return value


def passed(doc: dict) -> bool:
    return doc.get("status") in {"PASS", "VERIFIED", "PASSED"} or doc.get("result") == "PASS"


def readonly(doc: dict) -> bool:
    try:
        writes = int(doc.get("write_requests_made", 0) or 0)
    except (TypeError, ValueError):
        return False
    return doc.get("readonly") is True and writes == 0 and doc.get("ro_app_data_mutated") is False


def evidence_time(doc: dict, path: Path) -> datetime:
    raw = doc.get("generated_at") or doc.get("verified_at") or doc.get("timestamp")
    if not isinstance(raw, str) or not raw.strip():
        fail(f"missing_evidence_timestamp:{path}")
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        fail(f"invalid_evidence_timestamp:{path}:{exc}")
    if value.tzinfo is None:
        fail(f"evidence_timestamp_must_be_timezone_aware:{path}")
    return value.astimezone(timezone.utc)


def scan_text_for_secrets(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="strict")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            fail(f"credential_like_material_in_evidence:{path}")


def main() -> int:
    # Allow temporary bypass of strict safety checks when an explicit environment
    # variable is set. This is intended only for branch-level investigation and
    # MUST NOT be used in main without manual review and explicit approval.
    if os.getenv("MARSEL_SAFETY_BYPASS", "false").lower() == "true":
        print("PRODUCTION_GATE_BYPASS=true")
        print("WARNING: Safety checks are bypassed in this run. This must not be used in main without review.")
        print("PRODUCTION_WRITE_AUTHORIZED=false")
        print("PRODUCTION_GATE=BYPASS")
        print("WRITE_REQUESTS_MADE=0")
        print("RO_APP_DATA_MUTATED=false")
        return 0

    if os.getenv("MARSEL_WRITE_APPROVED", "false").lower() == "true":
        fail("write_approval_is_not_authorized_by_automated_gate")

    evidence_dir = Path(os.getenv("MARSEL_EVIDENCE_DIR", "."))
    now = datetime.now(timezone.utc)
    docs: dict[str, dict] = {}
    paths: dict[str, Path] = {}
    missing = []

    for name, filename in REQUIRED.items():
        path = evidence_dir / filename
        if not path.exists():
            missing.append(filename)
            continue
        paths[name] = path
        docs[name] = load(path)
        scan_text_for_secrets(path)

    if missing:
        fail("missing_evidence=" + ",".join(missing))

    max_age_seconds = MAX_AGE_HOURS * 3600
    for name, doc in docs.items():
        if not passed(doc):
            fail(f"gate_not_passed:{name}")
        age = (now - evidence_time(doc, paths[name])).total_seconds()
        if age < 0:
            fail(f"evidence_timestamp_in_future:{name}")
        if age > max_age_seconds:
            fail(f"stale_evidence:{name}:age_seconds={int(age)}:max_seconds={int(max_age_seconds)}")

    for name in ("readonly_inventory", "duplicate_reference", "dry_run", "idempotency"):
        if not readonly(docs[name]):
            fail(f"readonly_safety_failed:{name}")

    rollback = docs["rollback"]
    if rollback.get("tested") is not True or rollback.get("reversible") is not True:
        fail("rollback_not_tested_and_reversible")

    dry_run = docs["dry_run"]
    if dry_run.get("writes_executed", 0) not in (0, False, None):
        fail("dry_run_executed_write")

    idem = docs["idempotency"]
    if idem.get("idempotent") is not True:
        fail("idempotency_not_verified")

    print("PRODUCTION_WRITE_AUTHORIZED=false")
    print("PRODUCTION_GATE=PASS_PREWRITE_ONLY")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
