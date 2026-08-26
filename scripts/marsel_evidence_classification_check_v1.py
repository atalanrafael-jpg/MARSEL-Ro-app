#!/usr/bin/env python3
"""Fail-closed check preventing local safety artifacts from becoming production evidence."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SAFE = ROOT / "artifacts" / "marsel-safe-controls"
PROD = ROOT / "evidence"


def main() -> int:
    if not SAFE.exists():
        print("SAFE_ARTIFACTS=NOT_PRESENT")
        return 0
    violations = []
    for path in SAFE.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("source") == "local_sandbox_control_test" and data.get("status") == "PASS":
            if path.name in {p.name for p in PROD.glob("*.json")}:
                violations.append(path.name)
    if violations:
        print("EVIDENCE_CLASSIFICATION=FAIL")
        print("LOCAL_ARTIFACTS_MUST_NOT_BE_PRODUCTION_EVIDENCE=" + ",".join(sorted(violations)))
        return 2
    print("EVIDENCE_CLASSIFICATION=PASS")
    print("LOCAL_SANDBOX_ARTIFACTS_NOT_PROMOTED=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
