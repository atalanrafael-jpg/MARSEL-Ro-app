#!/usr/bin/env python3
"""Canonical RO APP API v2 registry scaffold.
READ-ONLY: this file only defines and validates endpoint metadata.
No network calls and no write methods are executed.
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

# Only explicitly documented GET collection routes may enter this registry.
# Unknown routes are intentionally excluded rather than guessed.
REGISTRY: tuple[Endpoint, ...] = ()


def validate_registry() -> None:
    for e in REGISTRY:
        if e.method != "GET":
            raise ValueError(f"Non-GET endpoint in READ-ONLY registry: {e}")
        if "{id}" in e.path or "{" in e.path:
            raise ValueError(f"Parameterized route requires a concrete documented ID: {e.path}")
        if e.status not in {"CONFIRMED", "UNRESOLVED", "NOT_ACCESSIBLE"}:
            raise ValueError(f"Invalid status: {e.status}")


if __name__ == "__main__":
    validate_registry()
    print(f"CANONICAL_V2_REGISTRY entries={len(REGISTRY)} write_methods=0")
