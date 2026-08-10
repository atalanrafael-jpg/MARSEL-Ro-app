#!/usr/bin/env python3
"""MARSEL V20.26 — API/Data Contract Verification, strictly READ ONLY.

Validates the structure and provenance of documented API operations without
issuing write requests. Documentation may describe POST/PUT/PATCH/DELETE
operations; that is not itself a write request and must not fail a read-only
inventory gate. Actual mutation remains prohibited.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

VERSION = "20.26"
INVENTORY = Path(os.environ.get("MARSEL_API_INVENTORY_INPUT", "marsel-api-inventory-v20-23.json"))
OUT = Path(os.environ.get("MARSEL_CONTRACT_OUTPUT", "marsel-api-contract-v20-26.json"))
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
PARAM_RE = re.compile(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(msg: str) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return 1


def write_report(result: dict) -> str:
    payload = dict(result)
    payload.pop("report_sha256", None)
    canonical = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    payload["report_sha256"] = digest
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return digest


def main() -> int:
    if not INVENTORY.exists():
        return fail(f"inventory not found: {INVENTORY}")
    try:
        data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    except Exception as exc:
        return fail(f"invalid inventory JSON: {exc}")

    ops = data.get("operations", [])
    errors: list[str] = []
    warnings: list[str] = []

    if data.get("readonly") is not True:
        errors.append("inventory readonly flag is not true")
    if data.get("write_requests_made") != 0:
        errors.append("inventory write_requests_made is not zero")
    if data.get("ro_app_data_mutated") is not False:
        errors.append("inventory ro_app_data_mutated is not false")

    methods = {str(x.get("method", "")).upper() for x in ops}
    documented_write_methods = sorted(methods & WRITE_METHODS)
    # These are documentation facts, not performed HTTP writes.
    if documented_write_methods:
        warnings.append(f"DOCUMENTED_WRITE_METHODS_PRESENT={documented_write_methods}; NO_WRITE_REQUESTS_PERFORMED")

    missing_paths = sum(1 for x in ops if not str(x.get("path", "")).strip())
    missing_evidence = sum(1 for x in ops if not x.get("source"))
    parameterized_gets = sum(
        1 for x in ops
        if str(x.get("method", "")).upper() == "GET" and PARAM_RE.search(str(x.get("path", "")))
    )
    get_count = sum(1 for x in ops if str(x.get("method", "")).upper() == "GET")

    if missing_paths:
        errors.append(f"operations without path: {missing_paths}")
    if missing_evidence:
        errors.append(f"operations without evidence source: {missing_evidence}")
    if not ops:
        errors.append("no documented API operations available for contract verification")

    summary = data.get("summary", {})
    inventory_get_count = summary.get("get_operations")
    if inventory_get_count != get_count:
        errors.append(f"summary.get_operations does not match inventory: {inventory_get_count!r}!={get_count}")

    pagination_fields = {"page", "page_size", "pagesize", "limit", "offset", "cursor", "next", "next_page", "next_cursor"}
    pagination_mentions = []
    for op in ops:
        text = json.dumps(op, ensure_ascii=False).lower()
        hits = sorted(x for x in pagination_fields if x in text)
        if hits:
            pagination_mentions.append({"method": op.get("method"), "path": op.get("path"), "fields": hits})

    warnings.extend([
        "LIVE_RESPONSE_SCHEMA=NOT_VERIFIED",
        "HTTP_ERROR_CONTRACT=NOT_VERIFIED",
        "PAGINATION_BEHAVIOR=DOCUMENTATION_ONLY",
        "REQUIRED_FIELD_CONTRACT=NOT_VERIFIED",
    ])

    result = {
        "version": VERSION,
        "readonly": True,
        "status": "PASS" if not errors else "FAIL",
        "inventory_sha256": sha256(INVENTORY),
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "operations": len(ops),
            "get_operations": get_count,
            "documented_write_operations": sum(1 for x in ops if str(x.get("method", "")).upper() in WRITE_METHODS),
            "parameterized_gets": parameterized_gets,
            "missing_paths": missing_paths,
            "missing_evidence_sources": missing_evidence,
            "pagination_mentions": len(pagination_mentions),
        },
        "pagination_mentions": pagination_mentions,
        "contract_state": {
            "documented_endpoint_structure": "CHECKED",
            "live_response_schema": "NOT_VERIFIED",
            "required_fields": "NOT_VERIFIED",
            "field_types": "NOT_VERIFIED",
            "pagination_behavior": "NOT_VERIFIED",
            "http_error_shapes": "NOT_VERIFIED",
            "completeness_claim": "NOT_ESTABLISHED",
        },
        "safety": {
            "write_requests_made": 0,
            "ro_app_data_mutated": False,
            "documented_write_methods_are_not_executed": True,
        },
    }
    report_sha = write_report(result)

    print(f"V{VERSION}_CONTRACT_AUDIT={result['status']}")
    print(f"OPERATIONS={len(ops)}")
    print(f"GET_OPERATIONS={get_count}")
    print(f"DOCUMENTED_WRITE_OPERATIONS={result['metrics']['documented_write_operations']}")
    print(f"PARAMETERIZED_GETS={parameterized_gets}")
    print("LIVE_RESPONSE_SCHEMA=NOT_VERIFIED")
    print("COMPLETENESS_CLAIM=NOT_ESTABLISHED")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    print(f"REPORT_SHA256={report_sha}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
