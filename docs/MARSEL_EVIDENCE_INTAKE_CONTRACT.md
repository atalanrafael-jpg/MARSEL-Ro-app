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

### Backup

Must identify the backup operation, source/environment, completion result, timestamp, and an integrity/checksum reference sufficient for an authorized reviewer to identify the produced backup.

### Restore

Must identify the tested backup, target controlled environment, restore result, and verification result. Production data must not be mutated by the evidence-generation test.

### Wix/ROAPP reconciliation

Must identify both systems/environment references, the reconciliation scope, comparison result, and any unresolved differences. No production write is permitted during reconciliation evidence generation.

### Unified read-only inventory

Must be the independently generated read-only MARSEL Unified Control Plane evidence and must demonstrate no writes and no ROAPP mutation.

### Duplicate-reference evidence

Must identify the duplicate/reference check scope and result, with no production mutation.

### Write dry-run

Must identify the simulated operation set and prove `writes_executed` is `0`, `false`, or `null`.

### Idempotency

Must prove the tested operation is idempotent and must demonstrate no ROAPP mutation while generating the pre-write evidence.

### Rollback

Must prove `tested=true` and `reversible=true`, with enough metadata to identify the controlled test and its result.

## Provenance requirements

The intake SHOULD additionally include, where available:

- source system/environment identifier;
- producing job/run identifier;
- source commit or version;
- evidence generation timestamp;
- SHA-256 of each evidence file;
- operator or automation identity (non-secret identifier);
- test scope and dataset/environment identifier.

These provenance fields identify evidence; they do not grant authorization.

## Intake rules

1. Missing evidence => `BLOCKED`.
2. Invalid JSON/schema => `BLOCKED`.
3. Unsafe write/mutation indicators => `BLOCKED`.
4. Credential-like material => `BLOCKED`.
5. Stale evidence => `BLOCKED`.
6. Evidence from an unlinked or untrusted source => `BLOCKED`.
7. Partial evidence MUST NOT be converted into placeholders.
8. Passing pre-write evidence still results in `PASS_PREWRITE_ONLY`; production WRITE remains separately controlled.

## Target handoff

```text
Authorized staging / controlled system
        ↓
Real evidence JSON files
        ↓
Trusted evidence intake
        ↓
MARSEL Evidence Orchestrator
        ↓
Evidence index + validation
        ↓
MARSEL Production Gate
        ↓
PASS_PREWRITE_ONLY (WRITE still disabled)
```

## Current implementation boundary

The repository currently consumes the unified control-plane artifact automatically. The other seven evidence files must be supplied by their authorized producing systems. Until that trusted intake path exists and all eight files are real, current behavior must remain fail-closed.
