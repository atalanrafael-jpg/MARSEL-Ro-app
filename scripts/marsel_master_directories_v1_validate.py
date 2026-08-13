#!/usr/bin/env python3
"""MARSEL offline master-directory quality gate.

This validator never calls RO App and never writes production data.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "config" / "marsel_master_directories_v1.json"
REQUIRED_KEYS = {"id", "name_ru"}
SUPPORTED_SCHEMA_VERSIONS = {"1.0", "1.1"}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []

    if not DATA.exists():
        print("ERROR|master_directories_missing")
        return 2

    try:
        payload = json.loads(DATA.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR|invalid_json|line={exc.lineno}|column={exc.colno}")
        return 2

    if payload.get("schema_version") not in SUPPORTED_SCHEMA_VERSIONS:
        fail(errors, f"invalid_schema_version|{payload.get('schema_version')}")
    if payload.get("status") != "OFFLINE_MASTER_DATA_ONLY":
        fail(errors, "invalid_status")
    if payload.get("production_import_allowed") is not False:
        fail(errors, "production_import_must_be_false")

    directories = payload.get("directories")
    if not isinstance(directories, dict) or not directories:
        fail(errors, "directories_missing")
        directories = {}

    all_ids: dict[str, str] = {}
    for directory, records in directories.items():
        if not isinstance(records, list) or not records:
            fail(errors, f"empty_directory|{directory}")
            continue
        local_ids: set[str] = set()
        for index, record in enumerate(records):
            prefix = f"{directory}[{index}]"
            if not isinstance(record, dict):
                fail(errors, f"record_not_object|{prefix}")
                continue
            for key in sorted(REQUIRED_KEYS - record.keys()):
                fail(errors, f"missing_key|{prefix}|{key}")
            record_id = record.get("id")
            name_ru = record.get("name_ru")
            if not isinstance(record_id, str) or not record_id.strip():
                fail(errors, f"invalid_id|{prefix}")
                continue
            if record_id in local_ids:
                fail(errors, f"duplicate_id_in_directory|{directory}|{record_id}")
            local_ids.add(record_id)
            if record_id in all_ids:
                fail(errors, f"duplicate_global_id|{record_id}|{all_ids[record_id]}|{directory}")
            else:
                all_ids[record_id] = directory
            if not isinstance(name_ru, str) or not name_ru.strip():
                fail(errors, f"invalid_name_ru|{prefix}")

    print(f"SCHEMA_VERSION={payload.get('schema_version')}")
    print(f"DIRECTORIES={len(directories)} RECORDS={sum(len(v) for v in directories.values() if isinstance(v, list))}")
    print(f"UNIQUE_IDS={len(all_ids)}")
    print(f"ERRORS={len(errors)}")
    for error in errors:
        print("ERROR|" + error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
