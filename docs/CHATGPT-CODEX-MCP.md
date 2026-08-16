# ChatGPT / Codex MCP Integration

The repository now exposes the MARSEL RO App connector through MCP. The integration has two modes:

- **Codex/local:** stdio via `python mcp_server.py`.
- **ChatGPT/remote:** Streamable HTTP at `/mcp`, protected by OAuth 2.1/OIDC JWT validation.

The current MCP tool surface is read-only.

## Why MCP instead of the legacy plugin format

The modern integration path for ChatGPT and Codex is MCP. A legacy `ai-plugin.json` is not added here because the production integration is implemented as an MCP server with optional UI rather than the retired plugin manifest model.

## Local Codex

Install dependencies and run the server from the repository root:

```bash
python -m pip install -r requirements.txt
python mcp_server.py
```

Register the stdio server with an MCP-compatible Codex configuration using the repository root as the working directory and:

```text
python mcp_server.py
```

Do not put RO App or OAuth secrets into a checked-in Codex configuration.

## Remote ChatGPT

Remote access must be deployed behind HTTPS and a real OAuth 2.1/OIDC authorization server. Set:

```text
MCP_HTTP_ENABLED=true
MCP_RESOURCE_SERVER_URL=https://your-domain.example.com/mcp
MCP_AUTH_ISSUER=https://your-issuer.example.com/
MCP_AUTH_JWKS_URL=https://your-issuer.example.com/.well-known/jwks.json
MCP_REQUIRED_SCOPES=["roapp:read"]
```

The MCP SDK publishes protected-resource metadata when authentication is configured. The authorization server must issue tokens whose audience is the configured MCP resource URL. The server validates the token signature, issuer, audience, expiry, and issued-at claims before tool execution.

## Production checks

1. Use HTTPS for the public MCP endpoint.
2. Use a real OAuth 2.1/OIDC provider; do not use a static bearer token or development verifier.
3. Restrict the OAuth scope to the minimum required read scope.
4. Keep RO App credentials server-side only.
5. Keep the MCP tool surface read-only until a separately reviewed write capability is required.
6. Run the full test suite and an MCP Inspector/compatible-client smoke test before release.

## Current tools

| Tool | Side effect | Purpose |
|---|---|---|
| `get_orders` | None | Fetch one bounded RO App orders page |
| `audit_orders` | None | Run the existing bounded order audit |
| `connector_readiness` | None | Report non-secret configuration readiness |

Tool annotations mark these tools as read-only. Authorization and side-effect controls remain enforced by the server implementation.
