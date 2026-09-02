---
title: Authentication
author: MARSEL ROAPP
category:
  uri: documentation
excerpt: Authentication rules for MARSEL ROAPP and separation of ReadMe documentation credentials.
hidden: false
---

# Authentication

MARSEL ROAPP uses a strict separation between documentation-publishing credentials and ROAPP API credentials.

## ReadMe publishing credential

The ReadMe project API key is used only by the GitHub Actions documentation workflow.

- Secret name: `README_API_KEY`
- Storage: GitHub Actions repository secret
- Scope: ReadMe documentation publication
- Never commit it to Git
- Never place it in Markdown examples
- Never expose it in workflow output

## ROAPP API credentials

ROAPP API credentials belong to the ROAPP integration/runtime security boundary. They must not be reused as the ReadMe project API key.

Use the authentication scheme specified by the current ROAPP API definition. If the API definition changes, update the API Reference and this guide together.

## Safe verification

Authentication should first be verified against a read-only endpoint.

Expected verification flow:

`CREDENTIAL → AUTHENTICATED GET → STATUS CHECK → RESPONSE VALIDATION`

Treat `401` and `403` as authentication/authorization failures. Do not retry blindly and do not downgrade security controls.

## Key rotation

Rotate credentials when exposure is suspected or when a credential is retired. Replace all dependent references, validate the replacement, and record evidence of the rotation without recording the secret value.

## Security rule

No secret values belong in the MARSEL ROAPP repository, documentation, issue comments, pull requests, examples, screenshots, or logs.
