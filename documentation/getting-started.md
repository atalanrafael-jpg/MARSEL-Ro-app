---
title: Getting Started
author: MARSEL ROAPP
category:
  uri: documentation
excerpt: Start integrating with the MARSEL ROAPP API safely and verify your first read-only request.
hidden: false
---

# Getting Started

This guide is the canonical onboarding path for **MARSEL ROAPP** integrations.

## 1. Choose your client

Use the language or HTTP client that best fits your integration. Keep credentials outside source code and CI logs.

## 2. Configure authentication

Use the authentication scheme defined by the current ROAPP API contract. Never place production credentials in this repository, documentation source files, browser code, or public examples.

For ReadMe CI publication, the credential is separate: `README_API_KEY` is stored only as a GitHub Actions repository secret.

## 3. Start with a read-only request

The first integration test should use a safe GET endpoint with the smallest required parameter set.

Recommended sequence:

`AUTHENTICATE → GET → VERIFY STATUS → VERIFY RESPONSE → RECORD EVIDENCE`

Do not use the first request to create, update, delete, post warehouse movements, or change production state.

## 4. Verify the response

Confirm:

- HTTP status is expected;
- response content type is expected;
- required fields are present;
- identifiers and relations are internally consistent;
- authentication failures are handled explicitly;
- no credentials or sensitive response data are written to logs.

## 5. Continue to the API Reference

After the first successful read-only request, use the generated ROAPP API Reference for endpoint-specific parameters, request bodies, responses, authentication, and examples.

## Production rule

`PASS` requires current direct evidence. A documented endpoint is not proof that the endpoint is currently available or that production credentials work.
