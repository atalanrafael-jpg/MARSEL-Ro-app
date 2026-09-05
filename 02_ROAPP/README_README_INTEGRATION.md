# ROAPP ↔ ReadMe integration

## Purpose

ReadMe is the publication and AI-discovery layer for the official RO App API documentation. The repository remains the canonical engineering control plane for MARSEL ROAPP.

## Source of truth

The RO App OpenAPI contract is discovered from the official RO App ReadMe publication endpoints:

- `https://roapp.readme.io/openapi.json`
- `https://roapp.readme.io/openapi.yaml`
- `https://roapp.readme.io/llms.txt`

The existing `scripts/marsel_official_roapp_discovery_v1.py` records availability, HTTP status, content type, byte count and SHA-256 evidence without making write requests to RO App.

## RO App API authentication

The current official RO App Public API authentication model is **Bearer Token**. Every authenticated request must send the employee API key from RO App **Settings → API** in the `Authorization` header:

`Authorization: Bearer YOUR_API_KEY`

RO App states that the API key is tied to the employee profile and that access is constrained by that employee's permissions, including location/warehouse access. Invalid or missing authentication returns `401 Unauthorized`. The current official guidance also states a rate limit of 3 requests per second.

This credential is an **RO App credential** and is distinct from the **ReadMe project API key** used only to publish documentation.

### ReadMe API Reference configuration

The published OpenAPI definition should represent the RO App authentication scheme as an HTTP Bearer security scheme and apply it globally or to every protected operation. No real token may be stored in the OpenAPI file, repository, examples, generated artifacts, or documentation source.

Recommended OpenAPI shape:

```yaml
components:
  securitySchemes:
    roappBearerAuth:
      type: http
      scheme: bearer
security:
  - roappBearerAuth: []
```

The repository does not guess or overwrite the official RO App OpenAPI source. The CI pipeline fetches the current official specification and validates it with ReadMe before any publication step.

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

- `README_API_KEY` — the ReadMe project API key used by `rdme`. Never commit this value.
- `README_API_DEFINITION_SLUG` — the existing ReadMe API definition slug for the ROAPP specification.

The ReadMe API key is **not** the same credential as the RO App employee API key. ReadMe recommends storing its API key as a GitHub Actions secret, and the official `rdme@v10` action is used for validation and synchronization.

## MCP

ReadMe can expose the published ROAPP OpenAPI specification and documentation through its MCP server. After enabling MCP in the ROAPP ReadMe project, AI coding tools can discover endpoints, inspect schemas and use the documented API surface.

Expected server URL:

`https://roapp.readme.io/mcp`

MCP exposure must be reviewed before enabling write-capable routes. Only documented and intentionally enabled routes should be exposed.

## Duplicate-control rule

Do not create a new ReadMe API definition from CI. The workflow always requires an explicit `README_API_DEFINITION_SLUG` and updates that definition only.

## Security rule

No RO App credentials, ReadMe API keys, access tokens, cookies or private customer data may be committed to the repository. CI must use GitHub Secrets or equivalent secret storage.

## Verification rule

A successful GitHub workflow proves only that the fetched OpenAPI document passed local/CI validation and, when configured, that ReadMe accepted the upload. It does not prove that every documented RO App operation is semantically correct or that production data was accessed.

## Evidence status

- **VERIFIED:** RO App Public API uses Bearer Token authentication according to current official RO App documentation.
- **VERIFIED:** ReadMe supports OpenAPI security schemes and authenticated API requests in its API Reference.
- **VERIFIED:** ReadMe `rdme@v10` can validate and upload an OpenAPI definition using a GitHub secret.
- **REVIEW_REQUIRED:** the exact current ROAPP ReadMe OpenAPI `securitySchemes` object must be checked against the freshly fetched official `openapi.json`; repository documentation must not be treated as proof of the live published schema.
