# OpenAI Ads Conversions

## Current implementation

This repository is a FastAPI/server-side connector. It has no browser JavaScript/TypeScript application surface, so the repository integration uses the OpenAI Ads Conversions API (CAPI) rather than installing the browser Measurement Pixel.

OpenAI documents CAPI as server-to-server and requires the Pixel ID plus a Conversions API key. Requests are sent to `POST https://bzr.openai.com/v1/events?pid=<PIXEL-ID>` with a Bearer token. Events may be batched up to 1,000 per request. `validate_only=true` validates without saving; production sending uses `false`.

## Environment

Set these runtime secrets/configuration values outside source control:

- `OPENAI_ADS_PIXEL_ID` — Pixel ID from Ads Manager > Conversions.
- `OPENAI_ADS_CONVERSIONS_API_KEY` — Conversions API key from Ads Manager > Conversions. Server-side only; never expose it to browser code.
- `OPENAI_ADS_BASE_URL` — normally `https://bzr.openai.com`.
- `OPENAI_ADS_VALIDATE_ONLY` — `false` for production sending; `true` only for validation tests.
- `OPENAI_ADS_DEFAULT_CURRENCY` — `RUB` for the current MARSEL configuration.
- `OPENAI_ADS_SOURCE_URL` — canonical HTTP(S) conversion URL when a request-specific source URL is not available.
- `OPENAI_ADS_TIMEOUT_SECONDS` — bounded HTTP timeout; default `15`.

## Conversion event

The reusable client currently supports the confirmed purchase boundary as `order_created`.

- `id` is the stable order identifier and is suitable for deduplication with a browser Pixel event if the same order is later instrumented in a web application.
- `timestamp_ms` is validated against OpenAI's documented seven-day ingestion window and ten-minute future limit.
- `data.amount` uses the currency's standard minor unit. For RUB this means kopecks.
- `action_source` is `web`, so `source_url` is required.
- `source_url` is normalized to HTTP(S) origin plus pathname; query strings and fragments are removed.
- `oppref` is accepted as opaque attribution context and passed through unchanged when available.
- `user` may contain only approved/documented event-scoped fields; raw email and raw external IDs must never be supplied.

## Attribution and hybrid Pixel/CAPI use

OpenAI's current CAPI documentation states that the API does not capture `oppref` automatically. Capture it in the browser/landing flow and forward the raw value to the server when available.

If a browser Measurement Pixel is added later, use the same Pixel ID and the same logical conversion identifier: Pixel `event_id` must match CAPI event `id` for the same conversion.

## Important repository limitation

The repository currently exposes the CAPI client but does not contain a confirmed customer-facing order-success handler that can call `send_order_created()` without inventing a business event boundary. Therefore this change deliberately does **not** attach conversion reporting to an arbitrary endpoint or to order reads/audits.

The next integration point should be the actual successful order/payment completion path once that path exists in the application. The call must be non-blocking for the core business transaction and must preserve the repository's consent/privacy rules.

## Verification

Run:

```bash
pytest -q tests/test_openai_ads.py
```

Before production deployment, provision the Pixel ID and CAPI key in Ads Manager and run a validation-only event first. Then switch `OPENAI_ADS_VALIDATE_ONLY=false` and verify that the production conversion is visible in Ads Manager.

Review the implementation against applicable privacy, consent, security, and data-handling requirements before deployment.
