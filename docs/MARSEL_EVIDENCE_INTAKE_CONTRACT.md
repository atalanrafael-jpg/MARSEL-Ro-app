# MARSEL ROAPP — Evidence Intake Contract

## Purpose

Define the minimum trusted handoff contract for externally produced pre-write evidence. This document does **not** create evidence, authorize production WRITE, or replace staging/controlled-system execution.

## Security boundary

Evidence MUST originate from an authorized staging or otherwise explicitly controlled system. GitHub Actions may validate and index supplied evidence, but must not fabricate it or execute production mutations.

The production gate remains fail-closed. `MARSEL_WRITE_APPROVED=true` is not an authorization path for automated workflows.

## Required evidence

The intake must provide all eight files:

1. `backup_evidence.json`
2. `restore_evidence.json`
3. `wix_roapp_reconciliation.json`
4. `marsel-unified-evidence.json`
5. `duplicate_reference_evidence.json`
6. `write_dry_run.json`
7. `idempotency_evidence.json`
8. `rollback_evidence.json`

## Common evidence contract

Each JSON file MUST be a JSON object and MUST contain:

- `status`: `PASS`, `VERIFIED`, or `PASSED` (or `result: PASS` where already supported by the gate)
- `generated_at` (preferred) or `verified_at` / `timestamp`: timezone-aware ISO-8601 timestamp
- `readonly`: `true`
- `write_requests_made`: `0`
- `ro_app_data_mutated`: `false`

Evidence MUST NOT contain API keys, bearer tokens, access/refresh tokens, passwords, or other credential material.

## Evidence-specific requirements

The validator enforces minimum fields so producers cannot pass the gate with an unstructured narrative alone.

### Backup

`operation`, `completion_result`, and `integrity_reference` are required.

### Restore

`tested_backup`, `target_environment`, `restore_result`, and `verification_result` are required.

### Wix/ROAPP reconciliation

`systems`, `reconciliation_scope`, `comparison_result`, and `unresolved_differences` are required.

### Unified read-only inventory

The unified control-plane artifact is validated by its own control-plane schema and gate. It must be independently generated, read-only, and demonstrate no writes or ROAPP mutation.

### Duplicate-reference evidence

`duplicate_check_scope` and `duplicate_check_result` are required.

### Write dry-run

`operation_set` and `writes_executed` are required. `writes_executed` must be `0`, `false`, or `null`.

### Idempotency

`operation`, `idempotency_tested`, and `idempotent` are required. Both boolean fields must be `true` for a passing artifact.

### Rollback

`tested`, `reversible`, and `test_result` are required. Both `tested` and `reversible` must be `true` for a passing artifact.

## Provenance requirements

Each evidence object MUST provide source system/environment, producing job/run, source version, generation timestamp, `sha256`, producer identity, and scope. Provenance identifies evidence; it does not grant authorization.

### Canonical SHA-256 convention

The `sha256` value MUST be the SHA-256 digest of the evidence JSON after replacing its own `sha256` field with the empty string, serialized as UTF-8 JSON with `ensure_ascii=false`, lexicographically sorted object keys (`sort_keys=true`), and compact separators `(',', ':')`.

## Intake rules

1. Missing evidence => `BLOCKED`.
2. Invalid JSON/schema => `BLOCKED`.
3. Unsafe write/mutation indicators => `BLOCKED`.
4. Credential-like material => `BLOCKED`.
5. Stale evidence => `BLOCKED`.
6. Evidence from an unlinked or untrusted source => `BLOCKED`.
7. Partial evidence MUST NOT be converted into placeholders.
8. Passing pre-write evidence results in `PASS_PREWRITE_ONLY`; production WRITE remains separately controlled.

## Current implementation boundary

The repository consumes the unified control-plane artifact automatically. The other seven evidence files must be supplied by their authorized producing systems. Until that trusted intake path exists and all eight files are real, behavior must remain fail-closed.
