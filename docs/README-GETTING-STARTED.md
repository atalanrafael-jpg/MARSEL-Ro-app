# ReadMe Getting Started — MARSEL ROAPP

Status: configuration runbook; no credentials are stored in this repository.

Official ReadMe reference: https://docs.readme.com/main/reference/getting-started

## Objective

Configure ReadMe's API Reference **Getting Started** page so a developer can select a language, authenticate, and make a minimal first API request through ReadMe's interactive Try It flow.

## Required ReadMe setup

1. In the ReadMe project dashboard, open the **Getting Started** page in the API Reference section.
2. Complete the setup flow.
3. Ensure an API definition has been imported into the project. ReadMe supports OpenAPI 3.0, OpenAPI 3.1, and Swagger 2.0.
4. Select one minimal `GET` endpoint with no required parameters for the first-call experience. ReadMe recommends a simple ping/Hello World-style endpoint where available.
5. Configure the authentication scheme represented by the API definition so the Credentials section matches the real API authentication.
6. Save the configuration and verify the interactive Try It request.

## MARSEL ROAPP contract gate

The MARSEL ROAPP repository currently treats the RO App API as a protected, read-only integration surface. The canonical workflow uses `https://api.roapp.io/v2` and keeps `ROAPP_API_KEY` in GitHub protected secrets rather than source code.

The existing unified control-plane workflow explicitly verifies the secret and runs read-only API inventory, data-quality, entity, collision, and warehouse audits. It does not expose the secret in pull-request events.

Do not put the RO App API key into ReadMe documentation, GitHub files, examples, or committed configuration.

## Authentication

ReadMe's current API documentation supports API-key authentication in the Getting Started experience. The exact credential type and header must be derived from the imported MARSEL/ROAPP OpenAPI contract; do not invent an authentication scheme or endpoint.

If ReadMe's generated page currently shows `Basic` authentication while the intended ROAPP contract is Bearer/API-key authentication, correct the OpenAPI security scheme before relying on the page. The displayed authentication method must match the actual API contract.

## Validation

A production-ready Getting Started configuration requires all of the following:

- API definition imported and accepted by ReadMe.
- Selected first endpoint is a real `GET` endpoint documented by the API contract.
- No required parameters are needed for the first request, unless intentionally documented.
- Authentication shown by ReadMe matches the API's actual security scheme.
- Try It request succeeds with valid credentials in a controlled test.
- `401`/`403` behavior is documented and understandable.
- No real API credentials are committed to Git.
- MARSEL ROAPP remains read-only unless a separately approved write gate is introduced.

## ReadMe API automation

ReadMe provides an API for programmatic documentation management and an official CLI/GitHub Action path. This can be used later to automate publication from MARSEL ROAPP after the API specification and authentication contract are verified.

Reference: https://docs.readme.com/main/reference/intro-to-the-readme-api

## Security gate

Never commit ReadMe API keys, ROAPP API keys, Auth0 secrets, private keys, session tokens, or other credentials. Use protected GitHub Secrets/Environments or the appropriate external secret store.
