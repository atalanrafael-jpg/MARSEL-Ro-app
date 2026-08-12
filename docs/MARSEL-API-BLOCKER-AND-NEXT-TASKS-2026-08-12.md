# MARSEL / Ro App — API blocker and parallel work plan

Date: 2026-08-12

## Verified blocker

The latest read-only API quality run reached the Ro App API but received HTTP 403 for the audited collections. The API response reported an expired subscription/licence. No write operation was performed.

Status: `BLOCKED_BY_API_ACCESS`

This document does not infer the state of production data while API access is blocked.

## Work that can continue safely without production API access

1. Maintain read-only enforcement in all existing audit workflows.
2. Consolidate duplicate/legacy workflow generations into a documented migration plan before deleting or disabling anything.
3. Keep endpoint capabilities classified as `CONFIRMED`, `UNVERIFIED`, `BLOCKED`, or `FAILED`.
4. Keep data-changing operations disabled until endpoint contracts and backup coverage are verified.
5. Maintain deterministic audit artifacts and SHA-256 integrity metadata where already implemented.
6. Prepare the post-access verification sequence:
   - API access probe
   - company identity verification
   - pagination verification
   - products/services/orders read audit
   - duplicate and referential-integrity checks
   - backup validation
   - dry-run write tests only if write endpoints are explicitly confirmed

## Workflow governance

The repository currently contains multiple generations of MARSEL API inventory/diagnostic/read-only workflows. Examples visible in the repository include:

- `marsel-api-inventory-v20-14.yml`
- `marsel-api-inventory-v20-19.yml`
- `marsel-api-inventory-v20-22.yml`
- `marsel-api-inventory-v20-23.yml`
- `marsel-api-endpoint-diagnostics-v20-18.yml`
- `marsel-api-endpoint-diagnostics-v20-22.yml`
- `marsel-api-v20-28-readonly.yml`
- `marsel-api-v20-29-readonly.yml`
- `marsel-api-v20-30-readonly.yml`
- `marsel-live-probe-v20-27.yml`
- `marsel-contract-v20-26.yml`
- `marsel-coverage-v20-25.yml`
- `marsel-entity-mapping-v21-3.yml`

No workflow should be deleted solely because it appears older. Before cleanup, compare its implementation and recent run history against the newest workflow and record the replacement relationship.

## Release gate

A future production write release must not proceed unless all of the following are true:

- API access is no longer blocked.
- Company identity matches the intended MARSEL company.
- Read-only audit completes successfully.
- Backup completeness is verified.
- Endpoint write capability is directly confirmed from the current API contract or successful controlled test.
- Dry-run produces the expected diff.
- No unexpected destructive operation is present.
- Post-write verification is defined before enabling writes.

## Current decision

Keep production writes disabled. Continue repository-level quality, documentation, workflow-governance, and offline validation work while Ro App API access is unavailable.
