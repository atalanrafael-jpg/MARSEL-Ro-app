#!/usr/bin/env python3
"""MARSEL V20.20 — automated gap analysis and repair-plan generator.

READ ONLY against RO App. It discovers deterministic data-quality gaps from the
already generated V20.14 API inventory and the live /orders collection.

It NEVER sends POST/PUT/PATCH/DELETE and NEVER changes RO App data.
It produces:
  - a machine-readable gap report;
  - deterministic repair candidates/requests for later controlled execution;
  - a compact summary suitable for CI.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

BASE = os.getenv("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.getenv("ROAPP_API_KEY", "")
TIMEOUT = float(os.getenv("ROAPP_TIMEOUT", "30"))
PAGE_SIZE = int(os.getenv("MARSEL_PAGE_SIZE", "100"))
INVENTORY = Path(os.getenv("MARSEL_API_INVENTORY_INPUT", "marsel-api-inventory-v20-14.json"))
OUT = Path(os.getenv("MARSEL_GAP_REPORT_OUTPUT", "marsel-gap-analysis-v20-20.json"))
PLAN = Path(os.getenv("MARSEL_REPAIR_PLAN_OUTPUT", "marsel-repair-plan-v20-20.json"))

# Fields whose absence is objectively suspicious for an order record.
REQUIRED_ORDER_FIELDS = {
    "id": "identity",
    "number": "identity",
    "client": "relationship",
    "status": "workflow",
    "branch_id": "relationship",
    "order_type": "classification",
    "created_at": "audit",
    "modified_at": "audit",
    "total": "finance",
}

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def die(message: str) -> None:
    print(f"ERROR={message}", file=sys.stderr)
    raise SystemExit(1)


def sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def extract_rows(payload: Any) -> list[dict[str, Any]] | None:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("orders", "data", "items", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
    return None


def norm_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip().casefold()


def client_fingerprint(client: Any) -> str | None:
    if not isinstance(client, dict):
        return None
    cid = client.get("id")
    if cid is not None:
        return f"id:{cid}"
    phone = client.get("phone")
    if isinstance(phone, list):
        phones = sorted(norm_text(x) for x in phone if norm_text(x))
    else:
        phones = [norm_text(phone)] if norm_text(phone) else []
    email = norm_text(client.get("email"))
    name = norm_text(client.get("name") or " ".join(filter(None, [client.get("first_name"), client.get("last_name")])))
    if phones:
        return "phone:" + "|".join(phones)
    if email:
        return "email:" + email
    if name:
        return "name:" + name
    return None


def inventory_stats() -> dict[str, Any]:
    if not INVENTORY.exists():
        return {"available": False, "reason": "inventory_file_missing"}
    try:
        data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"available": False, "reason": f"inventory_invalid:{type(exc).__name__}"}
    operations = data.get("operations", []) if isinstance(data, dict) else []
    methods = Counter()
    get_templates = []
    concrete_gets = []
    unresolved = []
    for op in operations:
        if not isinstance(op, dict):
            continue
        for method in op.get("methods", []):
            methods[str(method).upper()] += 1
        paths = op.get("paths", [])
        if "GET" in op.get("methods", []):
            for path in paths:
                path = str(path)
                if re.search(r"\{[^}]+\}|:[A-Za-z_][\w-]*|<[^>]+>", path):
                    get_templates.append(path)
                else:
                    concrete_gets.append(path)
        if op.get("method_source") == "unresolved" or not paths:
            unresolved.append({"title": op.get("title"), "documentation_url": op.get("documentation_url")})
    write_ops = [
        {"method": str(m).upper(), "title": op.get("title"), "paths": op.get("paths", []), "documentation_url": op.get("documentation_url")}
        for op in operations
        for m in op.get("methods", [])
        if str(m).upper() in WRITE_METHODS
    ]
    return {
        "available": True,
        "sha256": sha(data),
        "documented_operations": len(operations),
        "methods": dict(methods),
        "concrete_get_paths": sorted(set(concrete_gets)),
        "parameterized_get_templates": sorted(set(get_templates)),
        "unresolved_operations": unresolved,
        "write_operations_documented": write_ops,
    }


def read_all_orders(client: httpx.Client) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
    orders: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    page = 1
    complete = False
    while page <= 10000:
        started = time.monotonic()
        response = client.get("/orders", params={"page": page, "pageSize": PAGE_SIZE})
        elapsed = round((time.monotonic() - started) * 1000, 1)
        response.raise_for_status()
        payload = response.json()
        rows = extract_rows(payload)
        if rows is None:
            die(f"orders page {page}: response list not found")
        paging = payload.get("paging") if isinstance(payload, dict) else None
        pages.append({
            "page": page,
            "http": response.status_code,
            "rows": len(rows),
            "latency_ms": elapsed,
            "paging_keys": sorted(paging.keys()) if isinstance(paging, dict) else [],
        })
        orders.extend(rows)
        if len(rows) < PAGE_SIZE:
            complete = True
            break
        page += 1
        time.sleep(0.15)
    if page > 10000:
        die("pagination safety limit exceeded")
    return orders, pages, complete


def field_profile(orders: list[dict[str, Any]]) -> dict[str, Any]:
    profiles: dict[str, Any] = {}
    all_keys = sorted({k for row in orders for k in row.keys()})
    for key in all_keys:
        values = [row.get(key) for row in orders]
        non_null = [v for v in values if v is not None]
        types = Counter(type(v).__name__ for v in non_null)
        profiles[key] = {
            "present": sum(key in row for row in orders),
            "null": sum(v is None for v in values),
            "non_null": len(non_null),
            "types": dict(types),
            "type_drift": len(types) > 1,
        }
    return profiles


def main() -> None:
    if not KEY:
        die("ROAPP_API_KEY_missing")

    inv = inventory_stats()
    headers = {
        "Authorization": f"Bearer {KEY}",
        "Accept": "application/json",
        "User-Agent": "MARSEL-V20.20-Gap-Analyzer-Readonly",
    }
    with httpx.Client(base_url=BASE, headers=headers, timeout=TIMEOUT, follow_redirects=False) as client:
        orders, pages, pagination_complete = read_all_orders(client)

    ids = [row.get("id") for row in orders]
    numbers = [row.get("number") for row in orders]
    id_counts = Counter(x for x in ids if x is not None)
    number_counts = Counter(x for x in numbers if x not in (None, ""))

    duplicate_ids = {str(k): v for k, v in id_counts.items() if v > 1}
    duplicate_numbers = {str(k): v for k, v in number_counts.items() if v > 1}

    missing_required = {}
    for field in REQUIRED_ORDER_FIELDS:
        missing_required[field] = sum(field not in row or row.get(field) in (None, "") for row in orders)

    profiles = field_profile(orders)
    type_drift = {k: v["types"] for k, v in profiles.items() if v["type_drift"]}

    status_counts = Counter(
        str(row["status"].get("id"))
        for row in orders
        if isinstance(row.get("status"), dict) and row["status"].get("id") is not None
    )
    branch_counts = Counter(str(row.get("branch_id")) for row in orders if row.get("branch_id") is not None)
    order_type_counts = Counter(
        str(row["order_type"].get("id"))
        for row in orders
        if isinstance(row.get("order_type"), dict) and row["order_type"].get("id") is not None
    )

    client_missing = sum(not isinstance(row.get("client"), dict) or row["client"].get("id") is None for row in orders)
    client_fingerprints = Counter(client_fingerprint(row.get("client")) for row in orders)
    duplicate_client_fingerprints = {k: v for k, v in client_fingerprints.items() if k and v > 1 and not k.startswith("id:")}

    # Deterministic repair candidates only. No live write request is executed.
    candidates: list[dict[str, Any]] = []
    if duplicate_ids:
        candidates.append({"kind": "duplicate_order_ids", "action": "REVIEW_ONLY", "reason": "order IDs are immutable identifiers; duplicates require manual/API semantics verification", "groups": duplicate_ids})
    if duplicate_numbers:
        candidates.append({"kind": "duplicate_order_numbers", "action": "REVIEW_ONLY", "reason": "order numbers must be validated against RO App numbering semantics before any merge", "groups": duplicate_numbers})
    for field, count in missing_required.items():
        if count:
            candidates.append({"kind": "missing_required_field", "field": field, "count": count, "action": "PREPARE_UPDATE", "reason": REQUIRED_ORDER_FIELDS[field]})
    for field, types in type_drift.items():
        candidates.append({"kind": "field_type_drift", "field": field, "types": types, "action": "REVIEW_ONLY", "reason": "type normalization must follow official API schema"})
    if client_missing:
        candidates.append({"kind": "missing_client_relation", "count": client_missing, "action": "PREPARE_UPDATE", "reason": "orders without a valid client relation cannot be safely repaired without a source client ID"})
    if duplicate_client_fingerprints:
        candidates.append({"kind": "possible_duplicate_clients", "groups": duplicate_client_fingerprints, "action": "REVIEW_ONLY", "reason": "same phone/email/name fingerprint is not proof of duplicate identity"})

    # Prepare write requests only as inert records. They are intentionally NOT sent.
    write_request_queue = []
    for candidate in candidates:
        if candidate["action"] == "PREPARE_UPDATE":
            write_request_queue.append({
                "method": "PATCH",
                "endpoint": "/orders/{order_id}",
                "status": "NOT_EXECUTED",
                "requires": ["verified_order_id", "verified_field_value", "official_endpoint_schema"],
                "candidate": candidate,
            })

    report = {
        "version": "20.20",
        "mode": "READ_ONLY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "api_base": BASE,
        "orders": {
            "total": len(orders),
            "pages": len(pages),
            "pagination_complete": pagination_complete,
            "page_profile": pages,
            "duplicate_id_groups": duplicate_ids,
            "duplicate_number_groups": duplicate_numbers,
            "missing_required_fields": missing_required,
            "client_missing_relation": client_missing,
            "possible_duplicate_client_fingerprints": duplicate_client_fingerprints,
            "status_counts": dict(status_counts),
            "branch_counts": dict(branch_counts),
            "order_type_counts": dict(order_type_counts),
            "field_profile": profiles,
            "field_type_drift": type_drift,
        },
        "api_inventory": inv,
        "gaps": candidates,
        "repair_request_queue": write_request_queue,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
    }
    report["summary"] = {
        "orders_total": len(orders),
        "pagination_complete": pagination_complete,
        "duplicate_order_id_groups": len(duplicate_ids),
        "duplicate_order_number_groups": len(duplicate_numbers),
        "required_field_gap_count": sum(1 for x in missing_required.values() if x),
        "orders_missing_client": client_missing,
        "field_type_drift_count": len(type_drift),
        "possible_duplicate_client_groups": len(duplicate_client_fingerprints),
        "documented_write_operations": len(inv.get("write_operations_documented", [])) if inv.get("available") else None,
        "unresolved_inventory_operations": len(inv.get("unresolved_operations", [])) if inv.get("available") else None,
        "repair_candidates": len(candidates),
        "write_requests_prepared_but_not_executed": len(write_request_queue),
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
    }
    report["report_sha256"] = sha(report)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    plan = {
        "version": "20.20",
        "mode": "DRY_RUN_ONLY",
        "generated_at": report["generated_at"],
        "source_report": str(OUT),
        "source_report_sha256": report["report_sha256"],
        "requests": write_request_queue,
        "execution_policy": {
            "automatic_execution": False,
            "allowed_methods_now": ["GET"],
            "forbidden_methods_now": sorted(WRITE_METHODS),
            "require_verified_schema": True,
            "require_explicit_write_enablement": True,
        },
    }
    plan["plan_sha256"] = sha(plan)
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== MARSEL V20.20 / AUTOMATED GAP ANALYZER / READ ONLY ===")
    for key, value in report["summary"].items():
        print(f"{key.upper()}={value}")
    print(f"REPORT={OUT}")
    print(f"REPAIR_PLAN={PLAN}")
    print(f"REPORT_SHA256={report['report_sha256']}")
    print(f"PLAN_SHA256={plan['plan_sha256']}")
    print("WRITE_REQUESTS=0")
    print("RO_APP_DATA_MUTATED=False")
    print("RESULT=PASS" if pagination_complete and not duplicate_ids and not duplicate_numbers else "RESULT=REVIEW_REQUIRED")


if __name__ == "__main__":
    main()
