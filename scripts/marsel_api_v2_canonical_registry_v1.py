#!/usr/bin/env python3
"""Canonical RO App API v2 registry, READ-ONLY.

Only routes with explicit documentary evidence are marked CONFIRMED.
Unknown routes are deliberately not guessed or promoted to the contract.
No network calls and no write methods are executed here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Status = Literal["CONFIRMED", "UNRESOLVED", "NOT_ACCESSIBLE"]


@dataclass(frozen=True)
class Endpoint:
    name: str
    method: Literal["GET"]
    path: str
    source: str
    status: Status


REGISTRY: tuple[Endpoint, ...] = (
    Endpoint(
        name="orders_collection",
        method="GET",
        path="/orders",
        source="RO App API documentation / Getting Started",
        status="CONFIRMED",
    ),
)


def validate_registry() -> None:
    seen: set[tuple[str, str]] = set()
    for endpoint in REGISTRY:
        if endpoint.method != "GET":
            raise ValueError(f"Non-GET endpoint in READ-ONLY registry: {endpoint}")
        if "{" in endpoint.path or "}" in endpoint.path:
            raise ValueError(f"Parameterized route is not allowed in collection registry: {endpoint.path}")
        if not endpoint.path.startswith("/"):
            raise ValueError(f"Endpoint path must start with '/': {endpoint.path}")
        if endpoint.status not in {"CONFIRMED", "UNRESOLVED", "NOT_ACCESSIBLE"}:
            raise ValueError(f"Invalid status: {endpoint.status}")
        key = (endpoint.method, endpoint.path)
        if key in seen:
            raise ValueError(f"Duplicate canonical endpoint: {key}")
        seen.add(key)


if __name__ == "__main__":
    validate_registry()
    confirmed = sum(item.status == "CONFIRMED" for item in REGISTRY)
    print(f"CANONICAL_V2_REGISTRY entries={len(REGISTRY)} confirmed={confirmed} write_methods=0")
