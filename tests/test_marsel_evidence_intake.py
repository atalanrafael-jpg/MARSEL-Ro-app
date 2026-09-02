import importlib.util
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "marsel_evidence_intake_v1.py"
SPEC = importlib.util.spec_from_file_location("marsel_evidence_intake_v1", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _evidence(filename="backup_evidence.json", timestamp_key="generated_at", timestamp=None):
    data = {
        "status": "PASS",
        "readonly": True,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "source_system": "controlled-staging",
        "environment": "staging",
        "producing_job_or_run": "run-123",
        "source_version": "abc123",
        "producer_identity": "github-actions",
        "scope": "controlled-test",
        timestamp_key: timestamp or datetime.now(timezone.utc).isoformat(),
        "sha256": "",
        "operation": "backup-test",
        "completion_result": "PASS",
        "integrity_reference": "checksum-ref",
    }
    if filename == "restore_evidence.json":
        data.update({"tested_backup": "backup-1", "target_environment": "staging", "restore_result": "PASS", "verification_result": "PASS"})
    elif filename == "wix_roapp_reconciliation.json":
        data.update({"systems": ["wix", "roapp"], "reconciliation_scope": "catalog", "comparison_result": "PASS", "unresolved_differences": []})
    elif filename == "duplicate_reference_evidence.json":
        data.update({"duplicate_check_scope": "catalog", "duplicate_check_result": "PASS"})
    elif filename == "write_dry_run.json":
        data.update({"operation_set": ["simulated-write"], "writes_executed": 0})
    elif filename == "idempotency_evidence.json":
        data.update({"operation": "simulated-write", "idempotency_tested": True, "idempotent": True})
    elif filename == "rollback_evidence.json":
        data.update({"tested": True, "reversible": True, "test_result": "PASS"})
    data["sha256"] = MODULE._canonical_sha256(data)
    return data


def test_accepts_contract_timestamp_fallback(tmp_path):
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(_evidence()), encoding="utf-8")
    assert MODULE.validate_file(path) == []


def test_rejects_stale_evidence(tmp_path, monkeypatch):
    monkeypatch.setenv("MARSEL_EVIDENCE_MAX_AGE_HOURS", "24")
    old = datetime.now(timezone.utc) - timedelta(hours=25)
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(_evidence(timestamp=old.isoformat())), encoding="utf-8")
    errors = MODULE.validate_file(path)
    assert "evidence.json: stale_evidence" in errors


def test_rejects_write_request(tmp_path):
    data = _evidence()
    data["write_requests_made"] = 1
    data["sha256"] = MODULE._canonical_sha256(data)
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    errors = MODULE.validate_file(path)
    assert "evidence.json: write_requests_made_must_be_zero" in errors


def test_enforces_evidence_specific_requirements(tmp_path):
    data = _evidence("rollback_evidence.json")
    data.pop("tested")
    data["sha256"] = MODULE._canonical_sha256(data)
    path = tmp_path / "rollback_evidence.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    errors = MODULE.validate_file(path)
    assert "rollback_evidence.json: missing_evidence_specific:tested" in errors


def test_rejects_non_idempotent_evidence(tmp_path):
    data = _evidence("idempotency_evidence.json")
    data["idempotent"] = False
    data["sha256"] = MODULE._canonical_sha256(data)
    path = tmp_path / "idempotency_evidence.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    errors = MODULE.validate_file(path)
    assert "idempotency_evidence.json: idempotent_must_be_true" in errors


def test_rejects_invalid_max_age_config_without_crashing(tmp_path, monkeypatch):
    monkeypatch.setenv("MARSEL_EVIDENCE_MAX_AGE_HOURS", "not-a-number")
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(_evidence()), encoding="utf-8")
    assert MODULE.validate_file(path) == []
