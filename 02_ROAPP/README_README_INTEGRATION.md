# ROAPP ↔ ReadMe integration

## Purpose

ReadMe is the publication and AI-discovery layer for the official RO App API documentation. The repository remains the canonical engineering control plane for MARSEL ROAPP.

## Source of truth

The RO App OpenAPI contract is discovered from the official RO App ReadMe publication endpoints:

- `https://roapp.readme.io/openapi.json`
- `https://roapp.readme.io/openapi.yaml`
- `https://roapp.readme.io/llms.txt`

The existing `scripts/marsel_official_roapp_discovery_v1.py` records availability, HTTP status, content type, byte count and SHA-256 evidence without making write requests to RO App.

## CI controls

`.github/workflows/readme-roapp-sync.yml` performs these gates:

1. Discover the official RO App documentation endpoints.
2. Download the official OpenAPI JSON.
3. Reject the pipeline if the document is not valid OpenAPI JSON.
4. Validate the specification with ReadMe's official `rdme@v10` CLI.
5. Upload the validated specification to ReadMe only when both required repository secrets are configured.

The sync job is deliberately disabled until the exact existing ReadMe API definition slug is known. This prevents creating a duplicate API definition.

## Required GitHub secrets

Add these repository secrets in GitHub → Settings → Secrets and variables → Actions:

- `README_API_KEY` — the ReadMe project API key. Never commit this value.
- `README_API_DEFINITION_SLUG` — the existing ReadMe API definition slug for the ROAPP specification.

ReadMe recommends storing the API key as a GitHub Actions secret. The official `rdme@v10` action is used for validation and synchronization.

## MCP

ReadMe can expose the published ROAPP OpenAPI specification and documentation through its MCP server. After enabling MCP in the ROAPP ReadMe project, AI coding tools can discover endpoints, inspect schemas and use the documented API surface.

Expected server URL:

`https://roapp.readme.io/mcp`

MCP exposure must be reviewed before enabling write-capable routes. Only documented and intentionally enabled routes should be exposed.

## Duplicate-control rule

Do not create a new ReadMe API definition from CI. The workflow always requires an explicit `README_API_DEFINITION_SLUG` and updates that definition only.

## Security rule

No RO App credentials, ReadMe API keys, access tokens, cookies or private customer data may be committed to the repository. CI must use GitHub Secrets.

## Verification rule

A successful GitHub workflow proves only that the fetched OpenAPI document passed local/CI validation and, when configured, that ReadMe accepted the upload. It does not prove that every documented RO App operation is semantically correct or that production data was accessed.
