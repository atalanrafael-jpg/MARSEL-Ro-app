# RO APP — MASTER API REGISTRY

## Evidence policy
Only official RO App documentation may establish an endpoint contract. Names inferred from entity names are not endpoint evidence.

## Required record
For every operation record:

- Entity
- HTTP method
- Exact path
- Official documentation URL
- Evidence type
- Parameters
- Response shape
- Live verification result
- Safety classification
- Last verification timestamp

## Safety policy
- Allowed inventory/probe method: `GET` only.
- `POST`, `PUT`, `PATCH`, `DELETE`: blocked until their official contracts, validation, backup, dry-run, idempotency, rollback and post-write verification are proven.
- Parameterized paths must never be probed with guessed IDs.

## Status vocabulary
- `CONFIRMED`: official evidence + verification.
- `DOCUMENTED_NOT_TESTED`: official evidence, not yet live-tested.
- `NOT_DOCUMENTED`: no official evidence.
- `BLOCKED`: intentionally prevented by safety policy.
- `FAILED`: live verification failed and requires investigation.

## Current principle
The registry is the source of truth for the integration. Application code must consume the registry rather than inventing endpoint paths.
