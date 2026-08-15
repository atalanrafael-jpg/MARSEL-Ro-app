# MARSEL — Canonical Structure

Date: 2026-08-15

## Canonical automation

The single canonical MARSEL automation entry point is:

`.github/workflows/marsel-unified-control-plane.yml`

It runs, in order:

1. API inventory — READ ONLY
2. Data quality — READ ONLY
3. Entity audit — READ ONLY
4. Product-code collision review — READ ONLY
5. Unified safety/quality gate
6. Unified evidence artifact

## Safety invariants

The canonical pipeline must prove:

- `WRITE_REQUESTS_MADE=0`
- `RO_APP_DATA_MUTATED=false`
- no guessed identifiers
- no write HTTP methods
- incomplete live evidence is a failure/review state, never a false PASS

## Current repository cleanup

Superseded MARSEL workflows have been removed where safely confirmed redundant. Remaining legacy workflows are not treated as the canonical source and must not be used as evidence for project completion.

## Canonical source files

- `scripts/marsel_api_inventory_v20_31.py`
- `scripts/marsel_data_quality_v22_readonly.py`
- `scripts/marsel_entity_audit_v20_32.py`
- `scripts/marsel_product_code_collision_audit_v22_1.py`
- `scripts/marsel_api_v2_probe_v1.py`

Versioned historical scripts may remain for audit history, but new automation must reference the canonical files above.

## Completion rule

The MARSEL project is not considered complete until the canonical workflow finishes successfully on the current `main` revision and produces unified evidence with all safety and quality gates passing. A historical SUCCESS, an old report, or a partial run does not qualify.
