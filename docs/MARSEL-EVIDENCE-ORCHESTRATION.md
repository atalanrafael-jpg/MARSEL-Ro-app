# MARSEL ROAPP — Evidence Orchestration

## Purpose

This document defines the boundary between informational local control tests and production evidence.

## Rules

1. `artifacts/marsel-safe-controls/` is informational only.
2. Local sandbox results MUST NOT be copied into `evidence/` automatically.
3. Production readiness requires fresh, real evidence for every required external control.
4. Missing external evidence keeps the release gate fail-closed.
5. No workflow in this repository may enable production writes as a side effect of evidence generation.

## Evidence classes

- `LOCAL_SANDBOX_CONTROL`: deterministic safety tests; not production evidence.
- `EXTERNAL_CONTROL`: evidence produced by a real connected system or authoritative environment.
- `PRODUCTION_EVIDENCE`: evidence accepted by the release-readiness controller after schema, freshness, source and secret checks.

## Required production evidence

- `backup_evidence.json`
- `restore_evidence.json`
- `wix_roapp_reconciliation.json`
- `marsel-unified-evidence.json`
- `duplicate_reference_evidence.json`
- `write_dry_run.json`
- `idempotency_evidence.json`
- `rollback_evidence.json`

The first three require real external-system verification. Local tests can validate safety mechanics for the last three, but cannot by themselves prove production behavior.
