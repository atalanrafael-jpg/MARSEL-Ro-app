"""Provider-agnostic integration adapter foundation for MARSEL ROAPP.

Adapters are READ/sandbox-first. Production writes require both a provider gate
and the global production gate; this module never enables writes by itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence
import time


@dataclass(frozen=True)
class AdapterCapabilities:
    provider: str
    version: str
    entities: tuple[str, ...]
    read: bool = True
    write: bool = False
    sandbox: bool = True
    rate_limit_per_minute: int | None = None
    idempotency: bool = True
    credential_ref: str | None = None


@dataclass(frozen=True)
class ReconciliationResult:
    status: str
    conflicts: tuple[str, ...] = ()
    planned_operations: tuple[str, ...] = ()


class Adapter(Protocol):
    capabilities: AdapterCapabilities

    def read(self, **params: Any) -> Sequence[Mapping[str, Any]]: ...
    def normalize(self, payload: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def validate(self, payload: Mapping[str, Any]) -> None: ...
    def map_identity(self, payload: Mapping[str, Any]) -> Mapping[str, str]: ...
    def reconcile(self, provider: Sequence[Mapping[str, Any]], operational: Sequence[Mapping[str, Any]]) -> ReconciliationResult: ...
    def write(self, *, operation: str, payload: Mapping[str, Any], idempotency_key: str) -> Mapping[str, Any]: ...


class ProductionWriteBlocked(RuntimeError):
    """Raised when an adapter attempts a write without explicit gates."""


def retry_with_backoff(fn, *, attempts: int = 3, base_delay: float = 0.25,
                       retryable: tuple[type[Exception], ...] = (TimeoutError,)):
    """Retry only declared transient failures with bounded exponential backoff."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    for attempt in range(attempts):
        try:
            return fn()
        except retryable:
            if attempt == attempts - 1:
                raise
            time.sleep(base_delay * (2 ** attempt))


def deterministic_idempotency_key(*, provider: str, entity: str,
                                   external_id: str, operation: str) -> str:
    """Create a stable key for the same provider/entity/mutation tuple."""
    import hashlib
    raw = f"{provider}:{entity}:{external_id}:{operation}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def assert_write_gate(*, provider_gate: bool, production_gate: bool) -> None:
    """Require both gates; no implicit or fallback authorization is allowed."""
    if not (provider_gate and production_gate):
        raise ProductionWriteBlocked("MARSEL ROAPP production WRITE is disabled")
