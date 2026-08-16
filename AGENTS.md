# MARSEL RO App — Codex Agent Contract

## Scope

This repository is the MARSEL RO App connector and its ChatGPT/Codex integration.

## Safety boundary

- RO App operations exposed through MCP are **read-only** unless a future change explicitly adds and tests a write tool.
- Never expose `ROAPP_API_KEY`, Ads conversion keys, OAuth client secrets, or bearer tokens in tool output, logs, tests, or documentation.
- Treat MCP tool annotations as UX hints, not authorization controls. Enforce authorization server-side.
- Remote MCP HTTP mode must use a real OAuth 2.1/OIDC issuer and HTTPS.
- Do not add a development token verifier to production code.

## Required verification

Before declaring a change production-ready:

1. Run the full pytest suite.
2. Run an import/startup smoke test with MCP HTTP disabled.
3. If MCP HTTP is enabled in a test environment, verify unauthorized requests fail and valid JWTs pass issuer, audience, expiry, signature, and scope checks.
4. Inspect the final diff for secrets, unintended writes, and changes outside the requested scope.

## MCP design

- Prefer focused, bounded tools over a large generic tool surface.
- Use `readOnlyHint=true` for read-only tools.
- Keep tool descriptions explicit about side effects and limits.
- Use Streamable HTTP for remote deployments; do not introduce new SSE transport.
- Keep local Codex access on stdio.
