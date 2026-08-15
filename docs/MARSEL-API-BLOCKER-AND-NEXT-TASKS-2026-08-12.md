# MARSEL / Ro App — API blocker and next tasks

> Historical filename retained for continuity; content is maintained as the current status record.

## Current verified state

The previous HTTP 403/subscription blocker is no longer the current state. The canonical MARSEL Unified Control Plane has successfully reached the Ro App API and completed the READ-ONLY inventory, data-quality, entity-audit and product-code review stages on the latest completed run.

The latest completed live run remains `REVIEW_REQUIRED`, not because the API is inaccessible, but because API/entity completeness is not yet established and product-code duplicates remain advisory review findings.

## What is verified

- `ROAPP_API_KEY` is configured for the canonical workflow.
- The API inventory executes against `https://api.roapp.io/v2`.
- READ-ONLY inventory completes against live data.
- Data-quality audit completes.
- Entity audit completes without guessing identifiers.
- Product-code collision review completes.
- Unified evidence is generated and uploaded.
- Production write invariants remain zero-write.

## Remaining blockers

1. **API completeness — NOT_ESTABLISHED**
   - The canonical registry must be expanded only from explicit official documentation evidence.
   - Unknown routes must remain unresolved rather than guessed.
2. **Entity completeness — NOT_ESTABLISHED**
   - Collection endpoints for currently blocked/unconfirmed entities require documentary evidence before live probing.
3. **Production readiness — NOT_READY**
   - Backup/restore verification, reconciliation, dry-run write validation and rollback evidence remain prerequisites.

## Canonical workflow governance

The active MARSEL live audit is:

`.github/workflows/marsel-unified-control-plane.yml`

Historical workflow generations are not active and must not be reintroduced as parallel live pipelines.

## Safety rules

1. Production audit remains READ-ONLY.
2. No endpoint is guessed from naming conventions.
3. `WRITE_REQUESTS_MADE=0` is mandatory for the audit pipeline.
4. `RO_APP_DATA_MUTATED=false` is mandatory.
5. Product-code duplicate findings are advisory unless the API contract establishes a uniqueness invariant.
6. Production WRITE remains disabled until endpoint contracts, backup coverage, dry-run and rollback verification are complete.

## Next verification sequence

1. Complete the official-documentation API registry.
2. Re-run live inventory and entity coverage.
3. Reconcile API registry vs implementation vs live evidence.
4. Verify backup completeness and restore procedure.
5. Verify production-readiness gates.
6. Perform a final independent self-check before any release decision.
