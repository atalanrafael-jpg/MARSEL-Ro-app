#!/usr/bin/env python3
"""MARSEL V21.6 naming/manufacturer static Quality Gate.

Read-only: validates naming governance rules and the reference seed taxonomy.
Placeholder rows for unverified manufacturers/brands/models/references are allowed
when they are explicitly marked as unknown and contain no canonical value.
"""
from pathlib import Path
import csv
import sys

DOC = Path("docs/MARSEL_V21_6_NAMING_MANUFACTURER_DIRECTORY.md")
SEED = Path("data/marsel_v21_6_reference_seed.csv")
REQUIRED_RULES = [
    "производител",
    "бренд",
    "модел",
    "Reference",
    "серийный номер",
    "синоним",
    "каноничес",
    "орфограф",
    "пунктуац",
]


def main() -> int:
    errors = []
    warnings = []

    if not DOC.exists():
        errors.append("missing_naming_directory")
    if not SEED.exists():
        errors.append("missing_reference_seed")

    if DOC.exists():
        text = DOC.read_text(encoding="utf-8").lower()
        for rule in REQUIRED_RULES:
            if rule.lower() not in text:
                errors.append(f"missing_rule:{rule}")
        if "автоматическ" in text and "объедин" in text and "запрещ" not in text:
            warnings.append("auto_merge_rule_should_be_explicit")

    if SEED.exists():
        with SEED.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))

        if not rows:
            errors.append("empty_reference_seed")
        else:
            # The repository seed uses the explicit entity_type field.
            required_cols = {"entity_type", "canonical_name", "status"}
            if not required_cols.issubset(rows[0]):
                errors.append("seed_schema_missing_columns")
            else:
                seen = set()
                for i, row in enumerate(rows, 2):
                    entity_type = row.get("entity_type", "").strip().lower()
                    canonical = row.get("canonical_name", "").strip()
                    status = row.get("status", "").strip().lower()
                    source = row.get("source", "").strip()
                    key = (entity_type, canonical.lower())

                    # Empty canonical names are valid only for explicit, unverified
                    # placeholders. Multiple placeholder rows of the same type are
                    # represented by one row, so they are not treated as duplicates.
                    placeholder = (
                        not canonical
                        and status == "unknown"
                        and not source
                    )
                    if placeholder:
                        continue

                    if key in seen:
                        errors.append(f"duplicate_seed_row:{i}")
                    seen.add(key)

                    if not entity_type:
                        errors.append(f"empty_entity_type:{i}")
                    if not canonical:
                        errors.append(f"empty_canonical_name:{i}")
                    if not status:
                        errors.append(f"empty_status:{i}")

    print("MARSEL_V21_6_NAMING_QUALITY_GATE")
    print(f"ERRORS={len(errors)}")
    for error in errors:
        print(f"ERROR={error}")
    print(f"WARNINGS={len(warnings)}")
    for warning in warnings:
        print(f"WARNING={warning}")
    print("RO_APP_DATA_MUTATED=False")
    print("WRITE_REQUESTS_MADE=0")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
