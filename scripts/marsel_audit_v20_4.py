#!/usr/bin/env python3
"""MARSEL V20.4 read-only audit.

V20.4 keeps the existing GET-only verifier but fixes the V20.3 classification
problem: HTTP 404 is NOT treated as an access restriction. The report separates
access denied, not found, authentication, rate-limit, server and unexpected
responses. No write request is made by this script.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "scripts", "marsel_audit_v20_2.py")
RAW = os.path.join(ROOT, "marsel-reference-verification-v20-4.json")
OUT = os.path.join(ROOT, "marsel-access-reference-matrix-v20-4.json")

if not os.path.exists(ENGINE):
    raise SystemExit("V20.2 verifier is missing")

env = os.environ.copy()
env["MARSEL_AUDIT_VERSION"] = "20.4"
env["MARSEL_AUDIT_OUTPUT"] = os.path.basename(RAW)

print("=== MARSEL AUDIT V20.4 / CLASSIFIED ACCESS + REFERENCE MATRIX / READ ONLY ===")
result = subprocess.run([sys.executable, ENGINE, "--readonly"], cwd=ROOT, env=env)
if result.returncode != 0:
    raise SystemExit(result.returncode)

with open(RAW, "r", encoding="utf-8") as fh:
    source = json.load(fh)

http_errors = source.get("http_error_detail", [])
detail_checks = source.get("detail_checks", [])
skipped = source.get("skipped_endpoints_detail", [])
unresolved = [
    item for item in source.get("reference_results", [])
    if item.get("classification") == "UNRESOLVED_AFTER_COLLECTION_SCAN"
]

classification = {
    "401": "AUTH_FAILURE",
    "403": "ACCESS_DENIED",
    "404": "NOT_FOUND",
    "408": "TIMEOUT",
    "409": "CONFLICT",
    "429": "RATE_LIMIT",
}

classified = []
for item in detail_checks + http_errors:
    status = item.get("status")
    key = str(status)
    if key in classification:
        kind = classification[key]
    elif isinstance(status, int) and 500 <= status <= 599:
        kind = "SERVER_ERROR"
    elif isinstance(status, int) and 400 <= status <= 499:
        kind = "CLIENT_ERROR"
    elif status is None:
        kind = "NETWORK_OR_TIMEOUT"
    else:
        kind = "UNEXPECTED_HTTP"
    classified.append({**item, "classification": kind})

counts = {}
for item in classified:
    key = item["classification"]
    counts[key] = counts.get(key, 0) + 1

matrix = {
    "version": "20.4",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "readonly": True,
    "write_requests_made": False,
    "ro_app_data_mutated": False,
    "source_audit": os.path.basename(RAW),
    "summary": {
        "reference_links": source.get("reference_links", 0),
        "get_candidates": source.get("get_candidates", 0),
        "records_seen_after_pagination": source.get("records_seen_after_pagination", 0),
        "unique_reference_values": source.get("unique_reference_values", 0),
        "resolved_entity_match": source.get("resolved_entity_match", 0),
        "resolved_cross_entity_id": source.get("resolved_cross_entity_id", 0),
        "external_references": source.get("external_references", 0),
        "unresolved_references": len(unresolved),
        "classified_http_observations": len(classified),
        "http_by_classification": counts,
        "skipped_endpoints": len(skipped),
        "raw_http_errors": source.get("http_errors", 0),
    },
    "http_observations": classified,
    "skipped_endpoints": skipped,
    "unresolved_references": unresolved,
    "endpoint_stats": source.get("endpoint_stats", []),
}

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(matrix, fh, ensure_ascii=False, indent=2)

print(f"REFERENCE_LINKS={matrix['summary']['reference_links']}")
print(f"GET_CANDIDATES={matrix['summary']['get_candidates']}")
print(f"RECORDS_SEEN_AFTER_PAGINATION={matrix['summary']['records_seen_after_pagination']}")
print("HTTP_BY_CLASSIFICATION=" + ",".join(f"{k}:{v}" for k, v in sorted(counts.items())))
print(f"SKIPPED_ENDPOINTS={len(skipped)}")
print(f"UNRESOLVED_REFERENCES={len(unresolved)}")
print(f"RAW_HTTP_ERRORS={source.get('http_errors', 0)}")
print("WRITE_REQUESTS_MADE=0")
print(f"REPORT={os.path.basename(OUT)}")
print("RESULT=READ_ONLY; V20.4; NO RO APP DATA CREATED, UPDATED OR DELETED")
