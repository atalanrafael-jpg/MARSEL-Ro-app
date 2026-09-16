#!/usr/bin/env python3
"""Restore verification for MARSEL read-only backup evidence.

Restores the exported RO App JSON into an isolated local SQLite staging
 database. It never contacts RO App and never performs a production write.
The test proves that the backup is structurally complete, hash-valid and
reconstructable into a queryable staging database.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BACKUP = Path(os.environ.get("MARSEL_FULL_BACKUP_INPUT", "marsel-full-readonly-backup-v1.json"))
EVIDENCE = Path(os.environ.get("MARSEL_BACKUP_EVIDENCE_INPUT", "backup_evidence.json"))
DB = Path(os.environ.get("MARSEL_RESTORE_DB", "marsel-restore-staging.sqlite"))
OUT = Path(os.environ.get("MARSEL_RESTORE_EVIDENCE_OUTPUT", "restore_evidence.json"))
SOURCE_VERSION = os.environ.get("GITHUB_SHA", "unknown")
RUN_ID = os.environ.get("GITHUB_RUN_ID", "unknown")
ENVIRONMENT = os.environ.get("MARSEL_EVIDENCE_ENVIRONMENT", "staging")

if not BACKUP.exists():
    raise SystemExit(f"backup missing: {BACKUP}")
if not EVIDENCE.exists():
    raise SystemExit(f"backup evidence missing: {EVIDENCE}")

evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
if evidence.get("status") != "PASS":
    raise SystemExit("backup evidence is not PASS")
if evidence.get("readonly") is not True or evidence.get("write_requests_made") != 0 or evidence.get("ro_app_data_mutated") is not False:
    raise SystemExit("backup safety contract failed")

backup = json.loads(BACKUP.read_text(encoding="utf-8"))
if backup.get("complete") is not True:
    raise SystemExit("backup complete flag is not true")
if backup.get("readonly") is not True or backup.get("write_requests_made") != 0 or backup.get("ro_app_data_mutated") is not False:
    raise SystemExit("backup mutation-safety contract failed")

stored_sha = backup.get("sha256")
without_sha = dict(backup)
without_sha.pop("sha256", None)
canonical = json.dumps(without_sha, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
computed_sha = hashlib.sha256(canonical.encode()).hexdigest()
if stored_sha != computed_sha:
    raise SystemExit(f"backup hash mismatch: stored={stored_sha} computed={computed_sha}")

DB.unlink(missing_ok=True)
con = sqlite3.connect(DB)
try:
    con.execute("CREATE TABLE restore_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    con.execute("CREATE TABLE restored_records (endpoint TEXT NOT NULL, ordinal INTEGER NOT NULL, record_json TEXT NOT NULL, PRIMARY KEY(endpoint, ordinal))")
    con.execute("INSERT INTO restore_metadata(key,value) VALUES(?,?)", ("backup_sha256", stored_sha))
    con.execute("INSERT INTO restore_metadata(key,value) VALUES(?,?)", ("source_system", str(evidence.get("source_system", "roapp"))))

    endpoint_count = 0
    record_count = 0
    for endpoint in backup.get("results", []):
        if endpoint.get("ok") is not True:
            raise SystemExit(f"backup contains failed endpoint: {endpoint.get('path')}")
        path = str(endpoint.get("path"))
        endpoint_count += 1
        for ordinal, record in enumerate(endpoint.get("data", [])):
            con.execute(
                "INSERT INTO restored_records(endpoint,ordinal,record_json) VALUES(?,?,?)",
                (path, ordinal, json.dumps(record, ensure_ascii=False, sort_keys=True)),
            )
            record_count += 1
    con.commit()

    restored_endpoints = con.execute("SELECT COUNT(DISTINCT endpoint) FROM restored_records").fetchone()[0]
    restored_records = con.execute("SELECT COUNT(*) FROM restored_records").fetchone()[0]
    if restored_records != record_count:
        raise SystemExit("restored record count mismatch")
    if record_count != int(backup.get("total_records", -1)):
        raise SystemExit("restored record count does not match backup total_records")
    if endpoint_count and restored_endpoints > endpoint_count:
        raise SystemExit("restored endpoint count is inconsistent")
finally:
    con.close()

result = {
    "schema": "marsel-restore-evidence/v1",
    "status": "PASS",
    "readonly": True,
    "write_requests_made": 0,
    "ro_app_data_mutated": False,
    "source_system": "roapp",
    "environment": ENVIRONMENT,
    "producing_job_or_run": f"github-actions:{RUN_ID}",
    "source_version": SOURCE_VERSION,
    "producer_identity": "github-actions:marsel-backup-evidence-producer",
    "scope": "isolated local staging reconstruction from canonical read-only RO App backup",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "operation": "restore/verification",
    "tested_backup": str(BACKUP),
    "target_environment": "isolated-local-staging",
    "restore_result": "PASS",
    "verification_result": "PASS",
    "production_write_attempted": False,
    "backup_sha256": stored_sha,
    "restored_endpoint_entries": endpoint_count,
    "restored_records": record_count,
    "staging_database": str(DB),
}
canonical_result = dict(result)
canonical_result["sha256"] = ""
canonical = json.dumps(canonical_result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
result["sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("RESTORE_EVIDENCE=PASS")
print("MODE=ISOLATED_LOCAL_STAGING_RESTORE")
print(f"RESTORED_RECORDS={record_count}")
print("PRODUCTION_WRITE_ATTEMPTED=False")
print("RO_APP_DATA_MUTATED=False")
