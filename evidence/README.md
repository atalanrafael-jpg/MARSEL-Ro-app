# MARSEL Production Evidence Directory

## Overview

This directory contains structured evidence files required for the MARSEL production release readiness gate. Each evidence file must be valid JSON and meet strict validation requirements before production WRITE operations can be authorized.

## Required Evidence Files

### 1. `backup_evidence.json`
**Purpose:** Proves complete, read-only backup/export of all writable RO App entities.

**Required Fields:**
- `status`: Must be `"PASS"`
- `observed_at`: ISO 8601 timestamp with timezone
- `source`: Script/tool that generated the evidence
- `readonly`: Must be `true`
- `write_requests_made`: Must be `0`
- `ro_app_data_mutated`: Must be `false`

**Generation:** `scripts/marsel_full_readonly_backup_v1.py`

---

### 2. `restore_evidence.json`
**Purpose:** Proves successful restore and integrity verification from the backup.

**Required Fields:**
- `status`: Must be `"PASS"`
- `observed_at`: ISO 8601 timestamp with timezone
- `integrity_check_passed`: Must be `true`
- `readonly`: Must be `true`
- `write_requests_made`: Must be `0`
- `ro_app_data_mutated`: Must be `false`

**Generation:** `scripts/marsel_readonly_integrity_v21.py`

---

### 3. `wix_roapp_reconciliation.json`
**Purpose:** Proves schema mapping and reconciliation between Wix and RO App data models.

**Required Fields:**
- `status`: Must be `"PASS"`
- `observed_at`: ISO 8601 timestamp with timezone
- `critical_conflicts`: Must be `0`
- `readonly`: Must be `true`
- `write_requests_made`: Must be `0`
- `ro_app_data_mutated`: Must be `false`

**Generation:** `scripts/marsel_product_code_collision_audit_v22_3.py`

---

### 4. `marsel-unified-evidence.json`
**Purpose:** Proves complete read-only inventory and API coverage audit.

**Required Fields:**
- `status`: Must be `"PASS"`
- `observed_at`: ISO 8601 timestamp with timezone
- `readonly`: Must be `true`
- `write_requests_made`: Must be `0`
- `ro_app_data_mutated`: Must be `false`
- `rate_limit_handling`: Should be `"verified"`
- `retry_logic`: Should be `"verified"`
- `error_handling`: Should be `"verified"`

**Generation:** `scripts/marsel_api_inventory_v20_32.py`

---

### 5. `duplicate_reference_evidence.json`
**Purpose:** Proves analysis and resolution of duplicate records and broken references.

**Required Fields:**
- `status`: Must be `"PASS"`
- `observed_at`: ISO 8601 timestamp with timezone
- `critical_issues`: Must be `0`
- `readonly`: Must be `true`
- `write_requests_made`: Must be `0`
- `ro_app_data_mutated`: Must be `false`

**Generation:** `scripts/marsel_reference_integrity_audit.py`

---

### 6. `write_dry_run.json`
**Purpose:** Proves planned mutations have been simulated without actual execution.

**Required Fields:**
- `status`: Must be `"PASS"`
- `observed_at`: ISO 8601 timestamp with timezone
- `writes_executed`: Must be `0` or `false`
- `readonly`: Must be `true`
- `write_requests_made`: Must be `0`
- `ro_app_data_mutated`: Must be `false`

**Generation:** `scripts/marsel_production_gate_v1.py` (dry-run mode)

---

### 7. `idempotency_evidence.json`
**Purpose:** Proves all mutations are idempotent with deterministic external IDs.

**Required Fields:**
- `status`: Must be `"PASS"`
- `observed_at`: ISO 8601 timestamp with timezone
- `idempotent`: Must be `true`
- `readonly`: Must be `true`
- `write_requests_made`: Must be `0`
- `ro_app_data_mutated`: Must be `false`

**Generation:** `scripts/marsel_production_gate_v1.py` (idempotency test)

---

### 8. `rollback_evidence.json`
**Purpose:** Proves rollback strategies are defined and tested for every mutation type.

**Required Fields:**
- `status`: Must be `"PASS"`
- `observed_at`: ISO 8601 timestamp with timezone
- `tested`: Must be `true`
- `reversible`: Must be `true`
- `readonly`: Must be `true`
- `write_requests_made`: Must be `0`
- `ro_app_data_mutated`: Must be `false`

**Generation:** `scripts/marsel_production_gate_v1.py` (rollback verification)

---

## Validation Rules

All evidence files are subject to:

1. **JSON Schema Validation**
   - Must be valid JSON objects (not arrays or primitives)
   - Must contain `status`, `observed_at`, and `source` fields

2. **Status Requirements**
   - `status` field must be exactly `"PASS"`
   - No `PENDING`, `DRAFT`, or `ASSUMED` states are accepted

3. **Timestamp Validation**
   - `observed_at` must be ISO 8601 format with timezone (e.g., `2026-09-04T13:30:00+00:00`)
   - Timestamp cannot be in the future
   - Evidence older than 24 hours is considered stale

4. **Credential Scanning**
   - Evidence files are scanned for exposed API keys, tokens, or secrets
   - Any credential-like material will cause validation failure
   - Use environment variables or secret managers instead

5. **Read-Only Markers**
   - All evidence must demonstrate read-only operations
   - Required markers: `readonly: true`, `write_requests_made: 0`, `ro_app_data_mutated: false`

## Production Gate Logic

The release readiness check follows this flow:

```
1. REPOSITORY_CONTROLS_CHECK
   ↓ (verify required files exist)
   ├─ .github/workflows/mcp-production.yml
   ├─ scripts/marsel_canonical_self_check.py
   ├─ scripts/marsel_production_gate_v1.py
   ├─ docs/MARSEL-PRODUCTION-GO-LIVE-GATES.md
   ├─ docs/MARSEL_ROAPP_TASK_REGISTRY.md
   └─ SECURITY.md
   ↓ (if any missing)
   └─→ FAIL: missing_required_controls

2. EXTERNAL_EVIDENCE_CHECK
   ↓ (check if all 8 evidence files exist)
   ├─ evidence/backup_evidence.json
   ├─ evidence/restore_evidence.json
   ├─ evidence/wix_roapp_reconciliation.json
   ├─ evidence/marsel-unified-evidence.json
   ├─ evidence/duplicate_reference_evidence.json
   ├─ evidence/write_dry_run.json
   ├─ evidence/idempotency_evidence.json
   └─ evidence/rollback_evidence.json
   ↓ (if any missing on production push)
   └─→ RESULT: NOT_PRODUCTION_READY

3. EVIDENCE_VALIDATION_CHECK (if all files exist)
   ↓ (for each file)
   ├─ JSON schema validation
   ├─ Status == "PASS"
   ├─ Timestamp validation (not future, not stale)
   ├─ Credential scanning
   └─ Read-only marker verification
   ↓ (if any fail)
   └─→ FAIL: evidence_validation_error

4. PRODUCTION_GATE_CHECK (if all evidence valid)
   ↓
   └─→ RESULT: RUN_PRODUCTION_GATE_FOR_FINAL_DECISION
```

## Testing Evidence Locally

To validate an evidence file:

```bash
python scripts/marsel_release_readiness_v1.py
```

To run the production gate:

```bash
export MARSEL_EVIDENCE_DIR=./evidence
python scripts/marsel_production_gate_v1.py
```

## Important Notes

- **No Production WRITE is Enabled:** All evidence must demonstrate read-only operations. The production gate will refuse any write approval.
- **Direct Evidence Only:** Placeholder files, mock data, or "assumed" evidence is rejected. Evidence must come from actual audit runs or controlled tests.
- **Fresh Evidence Required:** Evidence older than 24 hours is considered stale and must be regenerated.
- **Credentials Never Stored:** Production credentials must live in GitHub Actions Secrets or external secret managers, never in evidence files.
- **Git History:** Once evidence files are committed, they become part of the audit trail and cannot be rewritten without explicit approval.

## Workflow Behavior

- **On Pull Requests:** Evidence checks are bypassed (PR-safe mode). All PR checks pass regardless of evidence status.
- **On Push to main:** Full production readiness check runs. Release readiness status is determined by evidence presence and validity.
- **Manual Trigger:** Can be run via `workflow_dispatch` for testing.
