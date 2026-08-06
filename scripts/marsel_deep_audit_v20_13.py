#!/usr/bin/env python3
"""MARSEL V20.13 — deep audit of V20.12 inventory, READ ONLY."""
import hashlib
import json
import os
import re
from collections import Counter, defaultdict

INPUT = os.environ.get("MARSEL_INVENTORY_INPUT", "marsel-full-inventory-v20-12.json")
OUT = os.environ.get("MARSEL_DEEP_AUDIT_OUTPUT", "marsel-deep-audit-v20-13.json")

FIELDS = [
    "id", "name", "title", "code", "sku", "barcode", "cost", "price", "status",
    "client_id", "manager_id", "assignee_id", "branch_id", "category_id",
    "created_at", "updated_at", "due_date",
]


def norm(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip().casefold())


def ident(item):
    if not isinstance(item, dict):
        return None
    for key in ("id", "ID", "uuid"):
        if item.get(key) is not None:
            return item[key]
    return None


def rows_from_target(target):
    """Read the V20.12 record list, with compatibility for early page-level exports."""
    records = target.get("records")
    if isinstance(records, list):
        return records

    rows = []
    for page in target.get("pages", []):
        page_records = page.get("records_data")
        if isinstance(page_records, list):
            rows.extend(page_records)
    return rows


def main():
    with open(INPUT, encoding="utf-8") as handle:
        inventory = json.load(handle)

    assert inventory.get("version") == "20.12"
    assert inventory.get("readonly") is True
    assert inventory.get("write_requests_made") == 0
    assert inventory.get("ro_app_data_mutated") is False

    targets = inventory.get("targets", [])
    result = {
        "version": "20.13",
        "readonly": True,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "source_inventory_sha256": inventory.get("summary", {}).get("inventory_sha256"),
        "entities": {},
        "change_set": [],
        "summary": {},
    }

    total = 0
    for target in targets:
        entity = target.get("entity")
        rows = rows_from_target(target)
        total += len(rows)

        ids = [ident(item) for item in rows]
        id_counts = Counter(value for value in ids if value is not None)
        duplicate_ids = {key: value for key, value in id_counts.items() if value > 1}
        missing_id = sum(value is None for value in ids)

        field_presence = {
            field: sum(
                isinstance(item, dict) and item.get(field) not in (None, "")
                for item in rows
            )
            for field in FIELDS
        }

        exact_name = defaultdict(list)
        exact_title = defaultdict(list)
        exact_code = defaultdict(list)
        exact_sku = defaultdict(list)
        exact_barcode = defaultdict(list)

        buckets = {
            "name": exact_name,
            "title": exact_title,
            "code": exact_code,
            "sku": exact_sku,
            "barcode": exact_barcode,
        }
        for item in rows:
            if not isinstance(item, dict):
                continue
            item_id = ident(item)
            for field, bucket in buckets.items():
                value = norm(item.get(field))
                if value:
                    bucket[value].append(item_id)

        def dupmap(mapping):
            return {key: values for key, values in mapping.items() if len(values) > 1}

        costs = Counter(str(item.get("cost")) for item in rows if isinstance(item, dict))
        statuses = Counter(
            str(item.get("status"))
            for item in rows
            if isinstance(item, dict) and item.get("status") is not None
        )

        entity_out = {
            "records": len(rows),
            "missing_id": missing_id,
            "duplicate_ids": duplicate_ids,
            "field_presence": field_presence,
            "duplicate_name": dupmap(exact_name),
            "duplicate_title": dupmap(exact_title),
            "duplicate_code": dupmap(exact_code),
            "duplicate_sku": dupmap(exact_sku),
            "duplicate_barcode": dupmap(exact_barcode),
            "status_counts": dict(statuses),
            "cost_counts": dict(costs),
            "zero_cost": sum(
                isinstance(item, dict)
                and str(item.get("cost", "")) in ("0", "0.0", "0.00", "0.000")
                for item in rows
            ),
            "empty_code": sum(
                isinstance(item, dict) and not norm(item.get("code")) for item in rows
            ),
            "empty_sku": sum(
                isinstance(item, dict) and not norm(item.get("sku")) for item in rows
            ),
            "empty_barcode": sum(
                isinstance(item, dict) and not norm(item.get("barcode")) for item in rows
            ),
        }
        result["entities"][entity] = entity_out

        review_maps = [
            ("DUPLICATE_ID", "duplicate_ids"),
            ("DUPLICATE_NAME", "duplicate_name"),
            ("DUPLICATE_TITLE", "duplicate_title"),
            ("DUPLICATE_CODE", "duplicate_code"),
            ("DUPLICATE_SKU", "duplicate_sku"),
            ("DUPLICATE_BARCODE", "duplicate_barcode"),
        ]
        for reason, key in review_maps:
            for value, ids2 in entity_out[key].items():
                result["change_set"].append(
                    {
                        "action": "MANUAL_REVIEW",
                        "reason": reason,
                        "entity": entity,
                        "key": value,
                        "ids": ids2,
                    }
                )

    result["summary"] = {
        "entities": len(targets),
        "records": total,
        "change_set_items": len(result["change_set"]),
        "manual_review_items": len(result["change_set"]),
        "automatic_writes": 0,
    }

    payload = json.dumps(
        result, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    result["summary"]["deep_audit_sha256"] = hashlib.sha256(payload).hexdigest()

    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    print("=== MARSEL V20.13 / DEEP AUDIT / READ ONLY ===")
    print(f"ENTITIES={len(targets)}")
    print(f"RECORDS={total}")
    print(f"CHANGE_SET_ITEMS={len(result['change_set'])}")
    print("WRITE_REQUESTS_MADE=0")
    print(f"SOURCE_INVENTORY_SHA256={result['source_inventory_sha256']}")
    print(f"DEEP_AUDIT_SHA256={result['summary']['deep_audit_sha256']}")
    print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")


if __name__ == "__main__":
    main()
