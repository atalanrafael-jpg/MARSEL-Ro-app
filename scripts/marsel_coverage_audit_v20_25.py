#!/usr/bin/env python3
"""MARSEL V20.25 — API inventory coverage audit, strictly READ ONLY.

Audits the V20.23 inventory itself for false completeness signals, duplicate
operations, evidence consistency, unsafe probe declarations, and documentation
coverage. It does not call the Ro App API and never mutates Ro App data.
"""
from __future__ import annotations

import json
import os
import re
import sys
import hashlib
from pathlib import Path

VERSION = "20.25"
INVENTORY = Path(os.environ.get("MARSEL_API_INVENTORY_INPUT", "marsel-api-inventory-v20-23.json"))
OUT = Path(os.environ.get("MARSEL_COVERAGE_OUTPUT", "marsel-api-coverage-v20-25.json"))
ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
BLOCKED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
EVIDENCE_RANK = {"OPENAPI_CONFIRMED": 4, "DOCUMENTATION_CONFIRMED": 3, "URL_CONFIRMED": 2, "HEURISTIC": 1}
PARAM_RE = re.compile(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>")


def fail(msg: str):
    print(f"ERROR: {msg}", file=sys.stderr)
    return 1


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not INVENTORY.exists():
        return fail(f"inventory not found: {INVENTORY}")
    try:
        data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    except Exception as exc:
        return fail(f"invalid inventory JSON: {exc}")

    errors = []
    warnings = []
    ops = data.get("operations", [])
    summary = data.get("summary", {})
    safety = data.get("safety", {})
    policy = data.get("method_policy", {})

    if data.get("readonly") is not True:
        errors.append("readonly flag is not true")
    if data.get("write_requests_made") != 0:
        errors.append("write_requests_made is not zero")
    if data.get("ro_app_data_mutated") is not False:
        errors.append("ro_app_data_mutated is not false")
    if policy.get("allowed") != ["GET"]:
        errors.append("method policy allowed list is not exactly ['GET']")
    if set(policy.get("blocked", [])) != BLOCKED_METHODS:
        errors.append("method policy blocked set is incorrect")
    if safety.get("status") != "PASS":
        errors.append("safety status is not PASS")

    seen = set()
    duplicate_count = 0
    invalid_methods = 0
    bad_evidence = 0
    missing_sources = 0
    parameterized_gets = 0
    non_gets = 0
    evidence_counts = {k: 0 for k in EVIDENCE_RANK}

    for op in ops:
        method = str(op.get("method", "")).upper()
        path = str(op.get("path", ""))
        evidence = str(op.get("evidence", ""))
        key = (method, path)
        if key in seen:
            duplicate_count += 1
        seen.add(key)
        if method not in ALLOWED_METHODS:
            invalid_methods += 1
        if evidence not in EVIDENCE_RANK:
            bad_evidence += 1
        else:
            evidence_counts[evidence] += 1
        if not op.get("sources"):
            missing_sources += 1
        if method != "GET":
            non_gets += 1
        if method == "GET" and PARAM_RE.search(path):
            parameterized_gets += 1

    if duplicate_count:
        errors.append(f"duplicate method/path operations: {duplicate_count}")
    if invalid_methods:
        errors.append(f"invalid HTTP methods: {invalid_methods}")
    if bad_evidence:
        errors.append(f"unknown evidence levels: {bad_evidence}")
    if missing_sources:
        errors.append(f"operations without source evidence: {missing_sources}")

    if summary.get("unique_operations") != len(ops):
        errors.append("summary.unique_operations does not match operations length")
    if summary.get("get_operations") != sum(1 for x in ops if x.get("method") == "GET"):
        errors.append("summary.get_operations mismatch")
    if summary.get("non_get_operations") != non_gets:
        errors.append("summary.non_get_operations mismatch")

    # The old V20.23 completeness status is intentionally not trusted: its
    # uniqueness condition is tautological after dictionary de-duplication.
    old_status = data.get("completeness", {}).get("status")
    if old_status == "PASS":
        warnings.append("V20.23 completeness=PASS is not accepted as proof of API completeness")

    docs = data.get("documentation", {})
    openapi = data.get("openapi_discovery", {})
    pages_discovered = int(docs.get("pages_discovered", 0) or 0)
    pages_fetched = int(docs.get("pages_fetched", 0) or 0)
    spec_candidates = int(openapi.get("candidate_urls", 0) or 0)
    specs_checked = int(openapi.get("documents_checked", 0) or 0)
    specs_with_ops = int(openapi.get("documents_with_operations", 0) or 0)

    if pages_fetched > pages_discovered:
        errors.append("pages_fetched exceeds pages_discovered")
    if specs_checked > spec_candidates:
        errors.append("documents_checked exceeds candidate_urls")
    if specs_with_ops > specs_checked:
        errors.append("documents_with_operations exceeds documents_checked")
    if not ops:
        errors.append("no operations discovered")

    # A coverage score is descriptive only; it is not a claim that undocumented
    # endpoints do not exist.
    source_score = 0.0 if pages_discovered == 0 else min(1.0, pages_fetched / pages_discovered)
    openapi_score = 0.0 if specs_checked == 0 else min(1.0, specs_with_ops / specs_checked)
    evidence_score = 0.0 if not ops else min(1.0, (evidence_counts["OPENAPI_CONFIRMED"] + evidence_counts["DOCUMENTATION_CONFIRMED"]) / len(ops))
    safety_score = 1.0 if not errors and data.get("readonly") is True and data.get("write_requests_made") == 0 else 0.0
    coverage_score = round((source_score + openapi_score + evidence_score) / 3.0, 4)

    result = {
        "version": VERSION,
        "readonly": True,
        "inventory_sha256": sha256(INVENTORY),
        "inventory_source": str(INVENTORY),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "operations": len(ops),
            "unique_operations": len(seen),
            "duplicate_operations": duplicate_count,
            "get_operations": sum(1 for x in ops if x.get("method") == "GET"),
            "non_get_operations": non_gets,
            "parameterized_gets_not_probed": parameterized_gets,
            "invalid_methods": invalid_methods,
            "missing_source_evidence": missing_sources,
            "evidence_counts": evidence_counts,
            "documentation_pages_discovered": pages_discovered,
            "documentation_pages_fetched": pages_fetched,
            "openapi_candidates": spec_candidates,
            "openapi_documents_checked": specs_checked,
            "openapi_documents_with_operations": specs_with_ops,
        },
        "scores": {
            "documentation_fetch_coverage": round(source_score, 4),
            "openapi_operation_document_coverage": round(openapi_score, 4),
            "operation_evidence_coverage": round(evidence_score, 4),
            "descriptive_coverage_score": coverage_score,
            "safety_score": safety_score,
        },
        "interpretation": {
            "completeness_claim": "NOT_ESTABLISHED",
            "reason": "A documentation-derived inventory cannot prove that undocumented/private endpoints do not exist. V20.25 audits evidence integrity and coverage signals rather than asserting complete API discovery.",
            "writes_performed": 0,
            "ro_app_data_mutated": False,
        },
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["report_sha256"] = sha256(OUT)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"V{VERSION}_COVERAGE_AUDIT={result['status']}")
    print(f"OPERATIONS={len(ops)}")
    print(f"DUPLICATES={duplicate_count}")
    print(f"PARAMETERIZED_GETS_NOT_PROBED={parameterized_gets}")
    print(f"DESCRIPTIVE_COVERAGE_SCORE={coverage_score}")
    print("COMPLETENESS_CLAIM=NOT_ESTABLISHED")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    print(f"REPORT_SHA256={result['report_sha256']}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
