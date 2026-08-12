#!/usr/bin/env python3
"""Offline integrity audit for MARSEL reference seed.

No network access. No Ro App writes. Validates IDs, normalized names,
category/group relations, and required top-level directories.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "docs" / "MARSEL-REFERENCE-DATA-SEED-V1.yaml"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


def audit_list(items: Any, label: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    names: set[str] = set()
    if not isinstance(items, list):
        errors.append(f"{label}: expected list")
        return ids
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}[{i}]: expected mapping")
            continue
        ident, name = item.get("id"), item.get("name")
        if not isinstance(ident, str) or not ID_RE.fullmatch(ident):
            errors.append(f"{label}[{i}]: invalid id")
        elif ident in ids:
            errors.append(f"{label}: duplicate id {ident}")
        else:
            ids.add(ident)
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{label}[{i}]: empty name")
        else:
            key = normalized(name)
            if key in names:
                errors.append(f"{label}: duplicate normalized name {name!r}")
            names.add(key)
    return ids


def main() -> int:
    errors: list[str] = []
    if not SEED.exists():
        print("MARSEL_REFERENCE_INTEGRITY=FAIL")
        print("seed_missing=true")
        return 2
    data = yaml.safe_load(SEED.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("MARSEL_REFERENCE_INTEGRITY=FAIL")
        print("root_not_mapping=true")
        return 2

    required = ["brands", "categories", "services", "warehouse_types", "material_types", "payment_methods", "asset_types"]
    for key in required:
        if key not in data:
            errors.append(f"missing top-level directory: {key}")

    audit_list(data.get("brands", []), "brands", errors)
    audit_list(data.get("services", []), "services", errors)
    audit_list(data.get("warehouse_types", []), "warehouse_types", errors)
    audit_list(data.get("material_types", []), "material_types", errors)
    audit_list(data.get("payment_methods", []), "payment_methods", errors)
    audit_list(data.get("asset_types", []), "asset_types", errors)

    categories = data.get("categories", [])
    category_ids = audit_list(categories, "categories", errors)
    for ci, category in enumerate(categories if isinstance(categories, list) else []):
        groups = category.get("groups", []) if isinstance(category, dict) else []
        group_ids = audit_list(groups, f"categories[{ci}].groups", errors)
        if len(group_ids) != len(groups):
            errors.append(f"categories[{ci}].groups: duplicate/invalid IDs detected")
        if isinstance(category, dict) and not category.get("id"):
            errors.append(f"categories[{ci}]: missing id")

    if data.get("status") != "PROPOSED_SEED_NOT_LIVE":
        errors.append("seed is not explicitly marked non-live")

    print(f"MARSEL_REFERENCE_INTEGRITY={'PASS' if not errors else 'FAIL'}")
    print("mode=OFFLINE_READ_ONLY")
    print(f"categories={len(category_ids)}")
    if errors:
        for e in errors:
            print(f"- {e}")
        return 1
    print("production_write=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
