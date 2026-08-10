"""Deterministic anomaly checks for MARSEL.

The engine flags suspicious values; it does not mutate business data and does
not use AI as the source of truth for financial or inventory fields.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable


@dataclass(frozen=True)
class Anomaly:
    severity: str
    code: str
    field: str
    message: str
    value: Any = None


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def inspect_record(record: dict[str, Any], *, required_fields: Iterable[str] = ()) -> list[Anomaly]:
    findings: list[Anomaly] = []
    for field in required_fields:
        if field not in record or record[field] in (None, "", []):
            findings.append(Anomaly("HIGH", "MISSING_REQUIRED", field, f"Required field is missing: {field}"))

    for field in ("price", "cost", "amount", "total", "quantity", "stock"):
        if field in record:
            value = _number(record[field])
            if value is not None and value < 0:
                findings.append(Anomaly("HIGH", "NEGATIVE_VALUE", field, f"Negative value detected in {field}", value))

    for field in ("price", "cost", "amount", "total"):
        if field in record:
            value = _number(record[field])
            if value is not None and value > 10_000_000:
                findings.append(Anomaly("MEDIUM", "LARGE_VALUE", field, f"Unusually large value in {field}", value))

    return findings


def inspect_records(records: Iterable[dict[str, Any]], *, required_fields: Iterable[str] = ()) -> list[dict[str, Any]]:
    return [asdict(item) for record in records for item in inspect_record(record, required_fields=required_fields)]
