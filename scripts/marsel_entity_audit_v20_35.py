#!/usr/bin/env python3
"""MARSEL V20.35 — read-only entity audit from canonical API evidence.

Identifiers are never guessed. Parameterized nested routes are probed only after
real parent IDs have been obtained from a confirmed live collection endpoint.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from urllib.request import Request, urlopen

BASE = os.getenv("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.getenv("ROAPP_API_KEY", "")
INV = os.getenv("MARSEL_API_INVENTORY_OUTPUT", "marsel-unified-api-inventory.json")
OUT = os.getenv("MARSEL_ENTITY_AUDIT_OUTPUT", "marsel-entity-audit-v20-35.json")
TIMEOUT = min(int(os.getenv("ROAPP_TIMEOUT", "8")), 8)
PARAM = re.compile(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>")

CLASSIFIERS = {
    "people": lambda p: "/contacts/people" in p,
    "employees": lambda p: "/company/employees" in p,
    "locations": lambda p: "/company/locations" in p,
    "legal_entities": lambda p: "/company/legal-entities" in p,
    "warehouse": lambda p: "warehouse" in p.lower() or "warehouses" in p.lower(),
    "custom_directories": lambda p: "/company/directories" in p,
    "resources": lambda p: "/resources" in p.lower(),
}


def norm(path: str) -> str:
    return "/" + path.lstrip("/")[3:] if path.startswith("/v2/") else "/" + path.lstrip("/")


def get(path: str):
    request = Request(
        BASE + norm(path),
        headers={
            "Authorization": f"Bearer {KEY}",
            "Accept": "application/json",
            "User-Agent": "MARSEL-Audit-V20.35",
        },
        method="GET",
    )
    started = time.time()
    with urlopen(request, timeout=TIMEOUT) as response:
        return response.status, response.read().decode("utf-8", errors="replace"), round(time.time() - started, 3)


def extract_rows(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"]
    return []


def real_ids(payload):
    return [row.get("id") for row in extract_rows(payload) if isinstance(row, dict) and row.get("id") is not None]


def main():
    if not KEY:
        print("ROAPP_API_KEY is required", file=sys.stderr)
        return 2

    inv = json.load(open(INV, encoding="utf-8"))
    ops = inv.get("operations", [])
    confirmed = [
        o.get("path")
        for o in ops
        if str(o.get("method")).upper() == "GET"
        and o.get("evidence") in {"DOCUMENTATION_CONFIRMED", "OPENAPI_CONFIRMED"}
        and o.get("path")
    ]
    confirmed_collection = [p for p in confirmed if not PARAM.search(p)]

    results = []
    resolved = []

    # Standard non-parameterized collection audits.
    for entity, match in CLASSIFIERS.items():
        if entity == "resources":
            continue
        candidates = [p for p in confirmed_collection if match(norm(p))]
        if not candidates:
            results.append({
                "entity": entity,
                "status": "BLOCKED",
                "reason": "No non-parameterized contract-confirmed GET collection route; endpoint will not be guessed.",
            })
            continue
        path = candidates[0]
        try:
            status, body, elapsed = get(path)
            payload = json.loads(body)
            data = payload.get("data") if isinstance(payload, dict) else None
            issues = []
            if isinstance(data, list) and any(not isinstance(x, dict) or x.get("id") is None for x in data):
                issues.append("missing_id")
            row = {
                "entity": entity,
                "path": path,
                "http": status,
                "elapsed_s": elapsed,
                "json_valid": True,
                "quality_issues": issues,
                "contract_claim": "DOCUMENTATION_OR_OPENAPI_CONFIRMED",
            }
            if status == 200 and not issues:
                resolved.append(entity)
            results.append(row)
        except Exception as exc:
            results.append({
                "entity": entity,
                "path": path,
                "http": None,
                "error": f"{type(exc).__name__}: {exc}",
                "quality_issues": ["request_failed"],
            })

    # Resources are documented only as a nested route under a real location ID.
    resource_templates = [
        p for p in confirmed
        if "/resources" in norm(p).lower() and PARAM.search(p)
    ]
    if not resource_templates:
        results.append({
            "entity": "resources",
            "status": "BLOCKED",
            "reason": "No contract-confirmed parameterized GET resource route found; endpoint will not be guessed.",
        })
    else:
        location_paths = [p for p in confirmed_collection if "/company/locations" in norm(p)]
        if not location_paths:
            results.append({
                "entity": "resources",
                "status": "BLOCKED",
                "reason": "Resource route exists, but no confirmed live locations collection is available to supply real IDs.",
            })
        else:
            location_path = location_paths[0]
            template = resource_templates[0]
            try:
                location_status, location_body, location_elapsed = get(location_path)
                location_payload = json.loads(location_body)
                ids = real_ids(location_payload)
                if location_status != 200 or not ids:
                    results.append({
                        "entity": "resources",
                        "path_template": template,
                        "parent_path": location_path,
                        "http": location_status,
                        "parent_elapsed_s": location_elapsed,
                        "status": "BLOCKED",
                        "reason": "Confirmed locations collection returned no usable real IDs; no identifier was guessed.",
                    })
                else:
                    probe_results = []
                    for location_id in ids:
                        path = template.replace("{id}", str(location_id)).replace("{location_id}", str(location_id))
                        try:
                            status, body, elapsed = get(path)
                            json.loads(body)
                            probe_results.append({
                                "location_id": location_id,
                                "path": path,
                                "http": status,
                                "elapsed_s": elapsed,
                                "json_valid": True,
                            })
                        except Exception as exc:
                            probe_results.append({
                                "location_id": location_id,
                                "path": path,
                                "http": None,
                                "error": f"{type(exc).__name__}: {exc}",
                            })
                    failures = [r for r in probe_results if r.get("http") != 200]
                    row = {
                        "entity": "resources",
                        "path_template": template,
                        "parent_path": location_path,
                        "parent_http": location_status,
                        "real_parent_ids_used": ids,
                        "probes": probe_results,
                        "quality_issues": ["request_failed"] if failures else [],
                        "contract_claim": "DOCUMENTATION_OR_OPENAPI_CONFIRMED",
                        "identifiers_guessed": False,
                    }
                    if not failures:
                        resolved.append("resources")
                    results.append(row)
            except Exception as exc:
                results.append({
                    "entity": "resources",
                    "path_template": template,
                    "http": None,
                    "error": f"{type(exc).__name__}: {exc}",
                    "quality_issues": ["request_failed"],
                })

    blocked = [r for r in results if r.get("status") == "BLOCKED"]
    failed = [
        r for r in results
        if r.get("http") not in (None, 200) or r.get("quality_issues")
        or any(p.get("http") != 200 for p in r.get("probes", []))
    ]
    report = {
        "version": "20.35",
        "readonly": True,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "confirmed_collection_audits": results,
        "verified_live_collection_audits": [
            r for r in results
            if r.get("http") == 200 and not r.get("quality_issues")
            and all(p.get("http") == 200 for p in r.get("probes", []))
        ],
        "blocked_entities": blocked,
        "failed_entities": failed,
        "resolved_entities": sorted(set(resolved)),
        "completeness": "ESTABLISHED_FOR_AUDITED_COLLECTIONS" if not blocked and not failed else "NOT_ESTABLISHED",
        "safe_fix_status": "PREPARED_NOT_APPLIED",
        "safety": {"write_methods_used": [], "identifiers_guessed": False},
    }
    json.dump(report, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"VERIFIED_LIVE_COLLECTIONS_AUDITED={len(report['verified_live_collection_audits'])}")
    print(f"BLOCKED_ENTITIES={len(blocked)}")
    print(f"FAILED_ENTITIES={len(failed)}")
    print(f"RESOLVED_ENTITIES={','.join(sorted(set(resolved))) or 'NONE'}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    print(f"COMPLETENESS={report['completeness']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
