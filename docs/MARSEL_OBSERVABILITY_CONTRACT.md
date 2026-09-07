# MARSEL ROAPP — Observability & Correlation Contract

**Status:** v1.0

## Required fields

Every integration operation should emit structured telemetry containing:

- `request_id`
- `correlation_id`
- `integration`
- `endpoint`
- `latency_ms`
- `http_status` or normalized `result_status`
- `retry_count`
- `rate_limit_state`
- `error_class` when applicable
- `actor`
- `evidence_id` when the operation contributes to gate evidence

## Security rules

- Never log API keys, OAuth tokens, cookies, authorization headers, or credential-like values.
- Do not log full customer/payment payloads unless an approved data-minimization policy explicitly requires a field.
- Correlation IDs are metadata, not credentials.

## Health semantics

`/health` answers whether the process is alive.

`/ready` answers whether the process is configured and able to serve its intended readiness contract. It must not disclose secret values or sensitive configuration.

Dependency-specific readiness must be explicit; a process being alive does not imply RO App, Gmail, marketplace, payment or database availability.

## Integration trace

A business operation should be traceable as:

`request_id → correlation_id → integration → endpoint → result → evidence_id`

Retries retain the correlation ID and increment `retry_count`.

## Failure classification

Use stable error classes rather than free-form-only messages:

- `AUTHENTICATION`
- `AUTHORIZATION`
- `VALIDATION`
- `UPSTREAM_4XX`
- `UPSTREAM_5XX`
- `TIMEOUT`
- `RATE_LIMIT`
- `NETWORK`
- `IDEMPOTENCY_CONFLICT`
- `RECONCILIATION_DRIFT`
- `INTERNAL`

## Production safety

Observability is diagnostic evidence, not authorization. Green telemetry does not authorize production WRITE. Gate decisions remain evidence-driven and independently reviewable.
