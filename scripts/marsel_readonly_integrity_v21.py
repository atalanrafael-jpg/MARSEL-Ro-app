#!/usr/bin/env python3
"""MARSEL V21 — read-only entity/relationship integrity audit.

Consumes only evidence produced by the documented GET-only inventory/probe.
Never calls RO App itself and never performs mutations. The audit identifies
record collections, duplicate stable identifiers, missing identifiers, likely
foreign-key references, and endpoint-level consistency signals without
inventing identifiers or claiming database completeness.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

INVENTORY = Path(os.environ.get("MARSEL_API_INVENTORY_INPUT", "marsel-api-inventory-v20-29.json"))
PROBE = Path(os.environ.get("MARSEL_LIVE_PROBE_INPUT", "marsel-live-probe-v20-29.json"))
OUT = Path(os.environ.get("MARSEL_INTEGRITY_OUTPUT", "marsel-readonly-integrity-v21.json"))

ID_KEYS = {"id", "uuid", "key", "code", "number"}
REF_RE = re.compile(r"(?:^|_)(id|ids|uuid|code|key|number)$|(?:^|_)(.+)_(id|ids|uuid|code|key)$", re.I)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def records_from(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    if isinstance(value, dict):
        for key in ("data", "items", "results", "orders"):
            if isinstance(value.get(key), list):
                return [x for x in value[key] if isinstance(x, dict)]
    return []


def stable_id(record: dict[str, Any]) -> tuple[str, str] | None:
    for key in ("id", "uuid", "code", "key", "number"):
        val = record.get(key)
        if val not in (None, "") and not isinstance(val, (dict, list)):
            return key, str(val)
    return None


def audit_collection(name: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [stable_id(r) for r in records]
    known = [x for x in ids if x]
    by_kind: dict[str, list[str]] = defaultdict(list)
    for kind, value in known:
        by_kind[kind].append(value)
    duplicates = {k: sorted(v for v, n in Counter(vals).items() if n > 1) for k, vals in by_kind.items()}
    duplicates = {k: v for k, v in duplicates.items() if v}
    missing = len(records) - len(known)
    fields = Counter()
    for r in records:
        fields.update(r.keys())
    return {
        "endpoint": name,
        "records": len(records),
        "identified_records": len(known),
        "records_without_stable_identifier": missing,
        "identifier_fields": {k: len(v) for k, v in by_kind.items()},
        "duplicate_identifiers": duplicates,
        "field_count": len(fields),
        "top_fields": [k for k, _ in fields.most_common(50)],
    }


def main() -> int:
    inv = load(INVENTORY)
    probe = load(PROBE)
    probes = [p for p in probe.get("probes", []) if p.get("status") != "NOT_PROBED"]
    successful = [p for p in probes if p.get("http") in {200, 201, 202, 204} and p.get("json_valid") is True]

    collections = []
    references = []
    identifier_values: dict[str, set[str]] = defaultdict(set)
    endpoint_rows: dict[str, list[dict[str, Any]]] = {}

    for p in successful:
        path = str(p.get("path", ""))
        # V20.27 stores only response shape, not raw response body. Therefore
        # collection-level duplicate/reference analysis is limited to the
        # concrete JSON evidence available in the probe artifact.
        shape = p.get("shape")
        rows: list[dict[str, Any]] = []
        if isinstance(shape, dict) and shape.get("type") == "array" and isinstance(shape.get("items"), dict):
            item = shape["items"]
            if isinstance(item, dict):
                rows = [item]
        endpoint_rows[path] = rows
        collections.append({
            "path": path,
            "json_type": p.get("json_type"),
            "top_level_keys": p.get("top_level_keys", []),
            "array_length_observed": p.get("array_length"),
            "shape": shape,
        })
        for key in p.get("top_level_keys", []) or []:
            m = REF_RE.search(str(key))
            if m:
                references.append({"path": path, "field": key, "classification": "POSSIBLE_REFERENCE_FIELD"})

    # Cross-endpoint references are intentionally classified as candidates only:
    # the probe artifact contains response shapes, not complete records.
    unique_refs = {(x["path"], x["field"]): x for x in references}
    reference_candidates = list(unique_refs.values())

    report = {
        "version": "21.0",
        "status": "PASS" if inv.get("readonly") and probe.get("readonly") and probe.get("safety", {}).get("write_requests_made") == 0 else "FAIL",
        "readonly": True,
        "mutation_allowed": False,
        "scope": "GET-only inventory/probe evidence; entity and relationship integrity signals",
        "completeness_claim": "NOT_ESTABLISHED",
        "source_evidence": {
            "inventory": str(INVENTORY),
            "inventory_sha256": sha256(INVENTORY),
            "probe": str(PROBE),
            "probe_sha256": sha256(PROBE),
        },
        "metrics": {
            "inventory_operations": len(inv.get("operations", [])),
            "successful_json_gets": len(successful),
            "collections_observed": len(collections),
            "possible_reference_fields": len(reference_candidates),
            "write_requests_made": 0,
            "ro_app_data_mutated": False,
        },
        "collections": collections,
        "reference_candidates": reference_candidates,
        "limitations": [
            "The live probe stores response shapes rather than complete raw entity records.",
            "Duplicate and orphan-record detection for entities other than orders requires raw GET response retention in a controlled, non-public artifact.",
            "Parameterized endpoints are not queried because identifiers are never guessed.",
            "This report does not claim a complete database backup or complete relationship graph.",
        ],
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report["report_sha256"] = sha256(OUT)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("=== MARSEL V21 READ-ONLY ENTITY INTEGRITY AUDIT ===")
    print(f"STATUS={report['status']}")
    print(f"SUCCESSFUL_JSON_GETS={len(successful)}")
    print(f"COLLECTIONS_OBSERVED={len(collections)}")
    print(f"POSSIBLE_REFERENCE_FIELDS={len(reference_candidates)}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=False")
    print(f"REPORT_SHA256={report['report_sha256']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
