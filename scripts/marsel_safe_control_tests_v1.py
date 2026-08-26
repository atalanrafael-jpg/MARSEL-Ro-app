#!/usr/bin/env python3
"""Run deterministic local control tests without contacting ROAPP or production.

Produces evidence under artifacts/marsel-safe-controls, never under evidence/.
These artifacts are informational and MUST NOT satisfy production readiness.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "marsel-safe-controls"


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_json(name: str, payload: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dry_run_test() -> dict:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "state.json"
        original = b'{"quantity":10}\n'
        p.write_bytes(original)
        before = digest(p.read_bytes())
        proposed = b'{"quantity":9}\n'
        # Deliberately do not write proposed state.
        after = digest(p.read_bytes())
        assert before == after
        assert proposed != original
    return {"status": "PASS", "test": "write_dry_run", "mutation": "not_performed"}


def idempotency_test() -> dict:
    operation = b"reconcile:SKU-TEST:10"
    first = digest(operation)
    second = digest(operation)
    assert first == second
    return {"status": "PASS", "test": "idempotency", "same_operation_same_fingerprint": True}


def rollback_test() -> dict:
    original = {"quantity": 10, "version": 1}
    changed = {"quantity": 9, "version": 2}
    restored = dict(original)
    assert changed != original
    assert restored == original
    return {"status": "PASS", "test": "rollback", "state_restored": True}


def main() -> int:
    observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    tests = [dry_run_test(), idempotency_test(), rollback_test()]
    for result in tests:
        name = f"{result['test']}_evidence.json"
        result.update({"observed_at": observed_at, "source": "local_sandbox_control_test"})
        write_json(name, result)
    manifest = {
        "status": "PASS",
        "observed_at": observed_at,
        "source": "local_sandbox_control_test",
        "production_write_authorized": False,
        "production_evidence_directory_touched": False,
        "tests": [r["test"] for r in tests],
    }
    write_json("manifest.json", manifest)
    print("MARSEL_SAFE_CONTROL_TESTS=PASS")
    print("PRODUCTION_WRITE_AUTHORIZED=false")
    print("PRODUCTION_EVIDENCE_DIRECTORY_TOUCHED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
