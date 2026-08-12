# MARSEL — RO App API Verification Ledger V23

Status: **SAFE / READ-ONLY**

This ledger separates facts verified from the official RO App documentation from claims that still require a live authorized probe.

## Official documentation source

- https://roapp.readme.io/reference/getting-started-with-api
- https://roapp.readme.io/

## Confirmed project/API facts

| Item | Status | Evidence |
|---|---|---|
| API base URL | VERIFIED | Project configuration uses `https://api.roapp.io/v2`; official documentation is the governing source. |
| Authentication | VERIFIED | Project uses `Authorization: Bearer <token>` and `ROAPP_API_KEY`. |
| `GET /orders` | VERIFIED | Explicitly documented and used by the existing read-only client. |
| Rate limit: 3 req/s | VERIFIED | Recorded in project documentation from the official API documentation. |
| Pagination by `page` | VERIFIED | Recorded in project documentation from the official API documentation. |
| Up to 50 records/page | VERIFIED | Recorded in project documentation from the official API documentation. |
| `GET /company` response schema | NOT VERIFIED | The documentation page is not currently machine-readable through the available retrieval path; no response fields are inferred. |
| Write endpoints | NOT ENABLED | No write operation is enabled by the read-only audit policy. |
| Full production backup of every entity | NOT VERIFIED | A read-only audit is not proof of a complete backup. |

## Safety classification

### Allowed in the audit layer

- `GET` requests to explicitly verified endpoints.
- Pagination.
- Rate limiting.
- Retry on transient HTTP/network failures.
- Duplicate detection.
- Missing-ID detection.
- Count-vs-rows validation.
- Hashing of generated reports.

### Blocked

- `POST`
- `PUT`
- `PATCH`
- `DELETE`
- Automatic merge/delete of duplicates.
- Production synchronization.
- Any endpoint or response schema that has not been verified.

## Required promotion path

`OFFICIAL DOCS → READ-ONLY INVENTORY → LIVE GET PROBE → DATA QUALITY → BACKUP/RESTORE CHECK → CHANGESET → CONTROLLED APPLY → POST-AUDIT`

No step may be skipped for production writes.
