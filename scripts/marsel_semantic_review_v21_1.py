#!/usr/bin/env python3
"""MARSEL V21.1 — offline semantic review of V20.36 read-only evidence.

Consumes only the V20.36 entity-inventory artifact. It never calls RO App and
never performs mutations. Duplicate candidates are classified for manual
review; no candidate is treated as a confirmed duplicate merely because its
normalized title matches.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

INPUT = Path(os.environ.get("MARSEL_ENTITY_INVENTORY_INPUT", "marsel-entity-inventory-v20-19.json"))
OUTPUT = Path(os.environ.get("MARSEL_SEMANTIC_REVIEW_OUTPUT", "marsel-semantic-review-v21-1.json"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load() -> dict[str, Any]:
    return json.loads(INPUT.read_text(encoding="utf-8"))


def classify_endpoint(endpoint: str) -> str:
    if endpoint == "/catalog/products":
        return "PRODUCT"
    if endpoint == "/catalog/services":
        return "SERVICE"
    if endpoint.endswith("/categories"):
        return "CATEGORY"
    if "employee" in endpoint.lower() or "staff" in endpoint.lower():
        return "EMPLOYEE"
    return "OTHER"


def main() -> int:
    d = load()
    assert d.get("version") == "20.36", "unexpected V20.36 evidence version"
    assert d.get("mode") == "READ_ONLY"
    assert d.get("write_requests") == 0
    assert d.get("ro_app_data_mutated") is False
    assert d.get("parameterized_identifiers_guessed") is False
    assert d.get("audit_status") == "PASS"

    candidates = d.get("duplicate_candidates") or {}
    review = []
    for endpoint, groups in candidates.items():
        for group in groups or []:
            key = group.get("key") or []
            ids = [str(x) for x in (group.get("ids") or [])]
            title = None
            for pair in key:
                if isinstance(pair, list) and len(pair) == 2 and pair[0] == "title":
                    title = str(pair[1])
            review.append({
                "endpoint": endpoint,
                "entity_type": classify_endpoint(endpoint),
                "candidate_key": key,
                "title": title,
                "ids": ids,
                "id_count": len(ids),
                "classification": "MANUAL_REVIEW_REQUIRED",
                "reason": "same normalized title is evidence of a duplicate candidate, not proof of duplicate business records",
                "safe_next_check": "compare SKU/article, price, unit, category, archived/active state, stock, cost and other documented fields before any merge/delete decision",
            })

    by_type: dict[str, int] = {}
    for item in review:
        by_type[item["entity_type"]] = by_type.get(item["entity_type"], 0) + 1

    report = {
        "version": "21.1",
        "status": "PASS",
        "mode": "READ_ONLY_OFFLINE",
        "source": str(INPUT),
        "source_sha256": sha256(INPUT),
        "source_audit_status": d.get("audit_status"),
        "source_metrics": {
            "collection_paths_considered": d.get("collection_paths_considered"),
            "collection_pages_fetched": sum(x.get("pages_fetched", 0) for x in (d.get("collection_stats") or {}).values()),
            "collection_records_fetched": sum(x.get("records_fetched", 0) for x in (d.get("collection_stats") or {}).values()),
            "real_identifiers_extracted": d.get("real_identifiers_extracted"),
            "detail_probes": len(d.get("detail_results") or []),
        },
        "duplicate_candidate_groups": len(review),
        "candidate_groups_by_entity_type": by_type,
        "duplicate_candidates": review,
        "confirmed_duplicates": 0,
        "writes_performed": 0,
        "ro_app_data_mutated": False,
        "next_gate": "controlled field-level comparison and backup before any production write",
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report["report_sha256"] = sha256(OUTPUT)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("=== MARSEL V21.1 SEMANTIC REVIEW / READ ONLY ===")
    print("STATUS=PASS")
    print(f"DUPLICATE_CANDIDATE_GROUPS={len(review)}")
    print(f"BY_ENTITY_TYPE={json.dumps(by_type, sort_keys=True)}")
    print("CONFIRMED_DUPLICATES=0")
    print("WRITES_PERFORMED=0")
    print("RO_APP_DATA_MUTATED=False")
    print(f"REPORT_SHA256={report['report_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
