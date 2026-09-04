# ROAPP API Contract Evidence

## Source
Official RO App Public API documentation: https://roapp.readme.io/reference/getting-started-with-api

## Verified documentation facts
- Base URL: https://api.roapp.io/v2
- Authentication: Bearer Token
- Rate limit: up to 3 requests/second
- Exceeding the limit: HTTP 429
- Pagination: page parameter where supported
- Maximum page response size: 50 entries
- Invalid/missing token: HTTP 401

## Runtime status
DOCUMENTED_NOT_LIVE_VERIFIED

No credential is stored in this repository.
No live request is made by this contract layer.
No RO App production data is mutated.

## Live verification gate
Before any live call:
1. retrieve credential only from approved secret storage;
2. confirm endpoint from official reference;
3. confirm method and schema;
4. perform a single bounded READ request;
5. capture status and non-sensitive evidence;
6. verify pagination before full-range audit.

