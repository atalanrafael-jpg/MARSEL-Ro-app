#!/usr/bin/env python3
"""MARSEL V20.3 — read-only Access/Reference Matrix.

Runs the existing V20.2 read-only verifier, then turns its raw observations
into an explicit machine-readable matrix for access restrictions, skipped
endpoints and unresolved references. No POST/PATCH/PUT/DELETE requests are
made by this script; V20.2 is itself GET-only.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V20_2 = os.path.join(ROOT, "scripts", "marsel_audit_v20_2.py")
SOURCE_REPORT = os.path.join(ROOT, "marsel-reference-verification-v20-2.json")
OUT = os.path.join(ROOT, "marsel-access-reference-matrix-v20-3.json")

if not os.path.exists(V20_2):
    raise SystemExit("V20.2 verifier is missing")

print("=== MARSEL AUDIT V20.3 / ACCESS + REFERENCE MATRIX / READ ONLY ===")
result = subprocess.run([sys.executable, V20_2, "--readonly"], cwd=ROOT, env=os.environ.copy())
if result.returncode != 0:
    raise SystemExit(result.returncode)

with open(SOURCE_REPORT, "r", encoding="utf-8") as fh:
    source = json.load(fh)

access = source.get("detail_checks", [])
skipped = source.get("skipped_endpoints_detail", [])
unresolved = [
    item for item in source.get("reference_results", [])
    if item.get("classification") == "UNRESOLVED_AFTER_COLLECTION_SCAN"
]

access_by_status = {}
for item in access:
    status = str(item.get("status"))
    access_by_status[status] = access_by_status.get(status, 0) + 1

matrix = {
    "version": "20.3",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "write_requests_made": False,
    "ro_app_data_mutated": False,
    "source_audit": "marsel-reference-verification-v20-2.json",
    "summary": {
        "reference_links": source.get("reference_links", 0),
        "get_candidates": source.get("get_candidates", 0),
        "records_seen_after_pagination": source.get("records_seen_after_pagination", 0),
        "unique_reference_values": source.get("unique_reference_values", 0),
        "resolved_entity_match": source.get("resolved_entity_match", 0),
        "resolved_cross_entity_id": source.get("resolved_cross_entity_id", 0),
        "external_references": source.get("external_references", 0),
        "unresolved_references": len(unresolved),
        "access_restrictions": len(access),
        "access_by_status": access_by_status,
        "skipped_endpoints": len(skipped),
        "http_errors": source.get("http_errors", 0),
    },
    "access_restrictions": access,
    "skipped_endpoints": skipped,
    "unresolved_references": unresolved,
    "endpoint_stats": source.get("endpoint_stats", []),
}

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(matrix, fh, ensure_ascii=False, indent=2)

print(f"REFERENCE_LINKS={matrix['summary']['reference_links']}")
print(f"GET_CANDIDATES={matrix['summary']['get_candidates']}")
print(f"RECORDS_SEEN_AFTER_PAGINATION={matrix['summary']['records_seen_after_pagination']}")
print(f"ACCESS_RESTRICTIONS={len(access)}")
print("ACCESS_BY_STATUS=" + ",".join(f"{k}:{v}" for k, v in sorted(access_by_status.items())))
print(f"SKIPPED_ENDPOINTS={len(skipped)}")
print(f"UNRESOLVED_REFERENCES={len(unresolved)}")
print(f"HTTP_ERRORS={matrix['summary']['http_errors']}")
print("WRITE_REQUESTS_MADE=0")
print(f"REPORT={os.path.basename(OUT)}")
print("RESULT=READ_ONLY; V20.3; NO RO APP DATA CREATED, UPDATED OR DELETED")
