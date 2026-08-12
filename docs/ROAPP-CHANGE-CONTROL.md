# RO App — Change Control Policy for MARSEL

## Purpose

Protect the live MARSEL RO App database while the API and data model are still being validated.

## Default mode

**READ-ONLY**.

Allowed HTTP method in audit workflows: `GET`.

Forbidden in audit workflows: `POST`, `PUT`, `PATCH`, `DELETE`.

## Required gates before any write

1. Confirm the exact official endpoint and method.
2. Confirm required payload fields and validation rules from official documentation.
3. Produce a read-only snapshot.
4. Produce a dry-run change set containing exact record IDs and before/after values.
5. Validate referential integrity.
6. Obtain explicit approval for the specific change set.
7. Execute the smallest possible batch.
8. Record request result, timestamp, record ID and response status.
9. Re-read changed records with GET.
10. Run a post-change audit.

## Scope rule

The current operational scope is **jewelry repair only**. Manufacturing and sales must remain inactive until separately approved.

## Secrets

`ROAPP_API_KEY` must remain in GitHub Secrets or an equivalent secret store. It must never be committed to source files, artifacts or logs.

## Evidence rule

A successful GitHub Actions run is not sufficient evidence of API connectivity. The audit must expose a factual API response/status in its artifact or log.

## Recovery rule

No mass update is permitted while a complete, verified backup/snapshot of the affected data is unavailable.
