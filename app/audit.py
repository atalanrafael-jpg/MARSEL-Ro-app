from collections import Counter
from typing import Any


COMMON_ID_FIELDS = ("id", "uuid", "number", "order_id", "order_number")
COMMON_REQUIRED_FIELDS = ("id", "status")


def _records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("data", "items", "orders", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _identifier(record: dict[str, Any]) -> str | None:
    for field in COMMON_ID_FIELDS:
        value = record.get(field)
        if value not in (None, ""):
            return str(value)
    return None


def audit_order_pages(pages: list[Any]) -> dict[str, Any]:
    records = [record for page in pages for record in _records(page)]
    identifiers = [_identifier(record) for record in records]
    known_identifiers = [value for value in identifiers if value is not None]
    duplicates = sorted(
        value for value, count in Counter(known_identifiers).items() if count > 1
    )

    missing_fields = {
        field: sum(1 for record in records if record.get(field) in (None, ""))
        for field in COMMON_REQUIRED_FIELDS
    }

    return {
        "pages_scanned": len(pages),
        "orders_scanned": len(records),
        "identifiers_found": len(known_identifiers),
        "duplicate_identifiers": duplicates,
        "missing_common_fields": missing_fields,
        "read_only": True,
    }
