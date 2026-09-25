"""Deterministic, read-only exception classification for MARSEL ROAPP.

This module does not call external services and never performs production writes.
It converts observed evidence into reviewable exceptions for later automation/AI layers.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


SEVERITIES = ("INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL")
CATEGORIES = (
    "FACTUAL",
    "DUPLICATE",
    "MISSING_DATA",
    "INVALID_RELATION",
    "CLASSIFICATION",
    "CONFIGURATION",
    "API",
    "SECURITY",
    "INTEGRATION",
    "PERFORMANCE",
    "LEGAL_TAX",
    "UNVERIFIED",
)


@dataclass(frozen=True)
class ExceptionRecord:
    category: str
    severity: str
    code: str
    message: str
    evidence_class: str
    action: str = "REVIEW_REQUIRED"


def classify(*, code: str, message: str, evidence_class: str = "UNVERIFIED", severity: str = "MEDIUM", category: str = "UNVERIFIED") -> ExceptionRecord:
    """Create a normalized exception; invalid inputs fail closed."""
    if category not in CATEGORIES:
        raise ValueError(f"Unsupported category: {category}")
    if severity not in SEVERITIES:
        raise ValueError(f"Unsupported severity: {severity}")
    if not code or not message:
        raise ValueError("code and message are required")
    return ExceptionRecord(category, severity, code, message, evidence_class)


def summarize(records: list[ExceptionRecord]) -> dict[str, Any]:
    """Return deterministic counts without changing source data."""
    counts = {severity: 0 for severity in SEVERITIES}
    categories: dict[str, int] = {}
    for record in records:
        counts[record.severity] += 1
        categories[record.category] = categories.get(record.category, 0) + 1
    return {
        "mode": "READ_ONLY",
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "total": len(records),
        "severity_counts": counts,
        "category_counts": categories,
        "records": [asdict(record) for record in records],
    }


if __name__ == "__main__":
    print(summarize([]))
