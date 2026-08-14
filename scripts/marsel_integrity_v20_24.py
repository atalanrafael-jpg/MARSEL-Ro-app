#!/usr/bin/env python3
"""MARSEL V20.24 — consolidation/integrity gate for the read-only API inventory."""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "marsel-api-inventory-v20-23.json"
WORKFLOWS = ROOT / ".github" / "workflows"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if not INVENTORY.exists():
        fail(f"missing inventory: {INVENTORY}")

    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    required = {"version", "readonly", "method_policy", "operations", "summary", "safety"}
    missing = required - set(data)
    if missing:
        fail(f"inventory missing keys: {sorted(missing)}")

    if data["version"] != "20.23":
        fail(f"unexpected inventory version: {data['version']}")
    if data["readonly"] is not True:
        fail("readonly flag is not true")
    if data.get("write_requests_made") != 0 or data.get("ro_app_data_mutated") is not False:
        fail("mutation safety invariant failed")
    if data["method_policy"] != {"allowed": ["GET"], "blocked": ["POST", "PUT", "PATCH", "DELETE"]}:
        fail("method policy changed unexpectedly")
    if data["safety"].get("status") != "PASS":
        fail("safety status is not PASS")

    completeness = data.get("completeness", {})
    if completeness and completeness.get("never_guess_identifiers") is not True:
        fail("identifier safety invariant failed")

    operations = data["operations"]
    keys = [(x.get("method"), x.get("path")) for x in operations]
    if any(method not in {"GET", "POST", "PUT", "PATCH", "DELETE"} for method, _ in keys):
        fail("unknown HTTP method in inventory")
    if len(keys) != len(set(keys)):
        fail("duplicate method/path operations found")
    if any(not isinstance(path, str) or not re.match(r"^/(?:v2|1\.1)/", path) for _, path in keys):
        fail("operation path is outside supported API prefixes")

    summary = data["summary"]
    if summary.get("unique_operations") != len(operations):
        fail("summary.unique_operations does not match operations length")
    if summary.get("non_get_operations") != sum(1 for m, _ in keys if m != "GET"):
        fail("summary.non_get_operations mismatch")
    if summary.get("write_requests_made") != 0:
        fail("summary reports write requests")

    v23 = sorted(p.name for p in WORKFLOWS.glob("*v20-23*.yml")) if WORKFLOWS.exists() else []
    if len(v23) > 1:
        fail(f"multiple V20.23 workflows detected: {v23}")

    print("V20.24_INTEGRITY=PASS")
    print(f"INVENTORY_OPERATIONS={len(operations)}")
    print(f"GET_OPERATIONS={summary.get('get_operations', 0)}")
    print(f"NON_GET_OPERATIONS={summary.get('non_get_operations', 0)}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    print(f"V20.23_WORKFLOW_FILES={len(v23)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
