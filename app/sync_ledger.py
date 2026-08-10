"""Persistent synchronization ledger primitives for MARSEL.

This module is intentionally storage-agnostic: production adapters can persist
entries in a database without coupling the audit layer to a specific vendor.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Literal
import hashlib
import json

Operation = Literal["CREATE", "UPDATE", "DELETE", "SKIP", "ERROR", "DRY_RUN"]


@dataclass(frozen=True)
class LedgerEntry:
    source_system: str
    source_id: str
    target_system: str
    target_id: str
    operation: Operation
    correlation_id: str
    timestamp_utc: str
    result: str
    payload_hash: str | None = None
    error_code: str | None = None


def payload_hash(payload: Any) -> str:
    """Return deterministic SHA-256 for an auditable payload."""
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def new_entry(*, source_system: str, source_id: str, target_system: str,
              target_id: str, operation: Operation, correlation_id: str,
              result: str, payload: Any = None, error_code: str | None = None) -> LedgerEntry:
    return LedgerEntry(
        source_system=source_system,
        source_id=source_id,
        target_system=target_system,
        target_id=target_id,
        operation=operation,
        correlation_id=correlation_id,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        result=result,
        payload_hash=payload_hash(payload) if payload is not None else None,
        error_code=error_code,
    )


def to_dict(entry: LedgerEntry) -> dict[str, Any]:
    return asdict(entry)
