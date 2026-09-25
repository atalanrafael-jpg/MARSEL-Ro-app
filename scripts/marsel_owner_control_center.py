"""Read-only owner control center for MARSEL ROAPP.

Aggregates evidence into a deterministic operational snapshot. This module does
not call external services, mutate ROAPP data, or authorize production writes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


STATUSES = ("VERIFIED", "PARTIAL", "FAILED", "BLOCKED", "NOT VERIFIED", "PROPOSED")


@dataclass(frozen=True)
class ControlItem:
    area: str
    status: str
    evidence_class: str
    message: str
    next_step: str


def item(*, area: str, status: str, evidence_class: str, message: str, next_step: str) -> ControlItem:
    """Normalize one owner-control item; invalid status fails closed."""
    if status not in STATUSES:
        raise ValueError(f"Unsupported status: {status}")
    if not area or not evidence_class or not message or not next_step:
        raise ValueError("area, evidence_class, message and next_step are required")
    return ControlItem(area, status, evidence_class, message, next_step)


def snapshot(items: list[ControlItem]) -> dict[str, Any]:
    """Build a read-only dashboard snapshot from supplied evidence."""
    counts = {status: 0 for status in STATUSES}
    for control_item in items:
        counts[control_item.status] += 1
    return {
        "mode": "READ_ONLY",
        "production_write_authorized": False,
        "ro_app_data_mutated": False,
        "total": len(items),
        "status_counts": counts,
        "items": [asdict(control_item) for control_item in items],
    }


if __name__ == "__main__":
    print(snapshot([]))
