# MARSEL ROAPP MCP setup

## Verified repository configuration

The plugin declares the `marsel_roapp` MCP server in `.mcp.json`:

- command: `uv`
- args: `run --directory ./mcp_server server.py`
- environment: `ROAPP_API_KEY`, `ROAPP_BASE_URL`, `ROAPP_TIMEOUT_SECONDS`

The bundled MCP runtime is Python >= 3.11 and pins `mcp>=2.1.0,<3`.

## Local/Codex setup

1. Install `uv`.
2. Copy `.env.example` to a local environment file or configure the three variables through the Codex environment mechanism.
3. Set `ROAPP_API_KEY` locally. Never commit it.
4. Keep `ROAPP_BASE_URL` at the verified default unless the RO App integration documentation or repository configuration confirms another endpoint.
5. Start the plugin through the repository `.mcp.json` definition.

## Safety

The MCP surface is read-only. Do not add write tools without the MARSEL production safety gate in `AGENTS.md`.

Do not put credentials in GitHub files, source code, tests, logs, artifacts, PR comments, or documentation.

## Verification status

Repository configuration: VERIFIED.

Live RO App connectivity: NOT VERIFIED until a valid `ROAPP_API_KEY` is supplied in the local runtime and a read-only health/inspection call succeeds.
