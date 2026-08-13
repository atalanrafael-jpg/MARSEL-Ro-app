# MARSEL Ro App — Write Gate

Status: **LOCKED**

## Purpose

Prevent any accidental mutation of the production Ro App database until a write endpoint, request schema, authentication requirements, and rollback procedure are independently verified.

## Current verified contract

- Base API: `https://api.roapp.io/v2`
- Verified read endpoint: `GET /orders`
- Blocked methods: `POST`, `PUT`, `PATCH`, `DELETE`
- Official API documentation: `https://roapp.readme.io/reference/getting-started-with-api`

## Unlock requirements

All requirements below must be satisfied before enabling any write operation:

1. Official Ro App documentation explicitly identifies the endpoint and HTTP method.
2. Request payload/schema is documented or independently confirmed from an official source.
3. Authentication and required headers are confirmed.
4. A production backup/snapshot is completed and its integrity hash is recorded.
5. A dry-run changeset contains exact object IDs and before/after values.
6. Referential dependencies are validated.
7. The write operation is implemented behind an explicit allow-list; all other write methods remain denied.
8. A minimal test batch is applied only after explicit release approval.
9. Each changed object is re-read with GET and compared against the intended state.
10. A post-write data-quality audit passes.

## Safety rules

- Never probe an unverified write endpoint against production.
- Never invent IDs, payload fields, or HTTP methods.
- Never enable writes merely because an endpoint appears in an API inventory.
- Never perform bulk mutation without a verified backup and rollback path.
- If official documentation cannot be independently verified, keep the gate locked.

## Current conclusion

The repository currently does **not** contain sufficient independently verified evidence to unlock production writes. Read-only auditing remains the permitted mode.
