#!/usr/bin/env python3
"""Validate the proposed MARSEL reference-data seed without contacting Ro App.

Safety: offline/read-only. No network calls and no production writes.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "docs" / "MARSEL-REFERENCE-DATA-SEED-V1.yaml"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


def walk_named(items: Any, path: str, errors: list[str], seen: dict[str, str]) -> None:
    if not isinstance(items, list):
        return
    for i, item in enumerate(items):
        where = f"{path}[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where}: expected object")
            continue
        ident = item.get("id")
        name = item.get("name")
        if ident is not None:
            if not isinstance(ident, str) or not ID_RE.fullmatch(ident):
                errors.append(f"{where}: invalid id={ident!r}")
            key = f"id:{ident}"
            if key in seen:
                errors.append(f"duplicate id {ident!r}: {seen[key]} and {where}")
            else:
                seen[key] = where
        if name is not None:
            if not isinstance(name, str) or not name.strip():
                errors.append(f"{where}: invalid/empty name")
            else:
                key = f"name:{norm(name)}"
                if key in seen:
                    errors.append(f"duplicate normalized name {name!r}: {seen[key]} and {where}")
                else:
                    seen[key] = where
        for key, value in item.items():
            if isinstance(value, list):
                walk_named(value, f"{where}.{key}", errors, seen)


def main() -> int:
    if not SEED.exists():
        print(f"FAIL: seed not found: {SEED}")
        return 2

    raw = SEED.read_bytes()
    data = yaml.safe_load(raw)
    errors: list[str] = []

    if not isinstance(data, dict):
        errors.append("root must be a mapping")
    else:
        if data.get("language") != "ru":
            errors.append("language must be 'ru'")
        if data.get("status") != "PROPOSED_SEED_NOT_LIVE":
            errors.append("seed must remain explicitly non-live")
        if data.get("source_of_truth") != "MARSEL_MASTER_REFERENCE_DATA":
            errors.append("unexpected source_of_truth")
        rules = data.get("rules")
        if not isinstance(rules, dict) or not all(rules.get(k) is True for k in ("normalized_names", "stable_ids", "no_silent_duplicates")):
            errors.append("required reference-data safety rules are missing")
        walk_named(data.get("categories", []), "categories", errors, {})
        walk_named(data.get("services", []), "services", errors, {})
        walk_named(data.get("warehouse_types", []), "warehouse_types", errors, {})
        walk_named(data.get("material_types", []), "material_types", errors, {})
        walk_named(data.get("payment_methods", []), "payment_methods", errors, {})
        walk_named(data.get("asset_types", []), "asset_types", errors, {})

    digest = hashlib.sha256(raw).hexdigest()
    if errors:
        print("MARSEL_REFERENCE_SEED_VALIDATION=FAIL")
        for error in errors:
            print(f"- {error}")
        print(f"sha256={digest}")
        return 1

    print("MARSEL_REFERENCE_SEED_VALIDATION=PASS")
    print(f"seed={SEED.relative_to(ROOT)}")
    print(f"sha256={digest}")
    print("mode=OFFLINE_READ_ONLY")
    print("production_write=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
