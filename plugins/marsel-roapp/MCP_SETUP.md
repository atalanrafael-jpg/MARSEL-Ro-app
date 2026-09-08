# MARSEL ROAPP MCP setup

## MCP Python SDK baseline

MARSEL ROAPP uses the official **MCP Python SDK v2**, the current stable SDK line. The SDK requires Python 3.10+, while the bundled MARSEL runtime intentionally requires Python >= 3.11. The runtime dependency is pinned to `mcp>=2.1.0,<3` to stay on the v2 major line.

Official getting-started flow: install the SDK, run the server locally, connect it to a real host over stdio, and test it before enabling live integration. See the official MCP Python SDK documentation: https://py.sdk.modelcontextprotocol.io/get-started/

## Verified repository configuration

The plugin declares the `marsel_roapp` MCP server in `.mcp.json`:

- command: `uv`
- args: `run --directory ./mcp_server server.py`
- environment: `ROAPP_API_KEY`, `ROAPP_BASE_URL`, `ROAPP_TIMEOUT_SECONDS`
- transport: stdio, provided by `mcp.run()` when `server.py` is launched without an explicit transport

The server implementation uses `MCPServer` from the v2 SDK and exposes only read-only tools. It does not write to RO App.

## Local/Codex setup

1. Install `uv`.
2. From the `plugins/marsel-roapp` directory, install/resolve the bundled runtime with:

   `uv sync`

3. For an interactive local smoke test, use the official SDK CLI pattern:

   `uv run mcp dev mcp_server/server.py`

   This opens the MCP Inspector and starts the server locally over stdio.

4. For a host-style launch test, use an absolute server path when launching outside the plugin working directory, following the official MCP host guidance:

   `uv run --with "mcp[cli]" mcp run /absolute/path/to/plugins/marsel-roapp/mcp_server/server.py`

   A stdio server normally prints nothing and waits for the host to send requests. An immediate traceback/exit is a startup failure.

5. Configure the plugin through the repository `.mcp.json` definition.
6. Configure `ROAPP_API_KEY`, `ROAPP_BASE_URL`, and `ROAPP_TIMEOUT_SECONDS` through the local Codex/plugin environment. Never commit the API key.
7. Keep `ROAPP_BASE_URL` at the verified default unless RO App integration documentation or repository configuration confirms another endpoint.

## MARSEL safety gate

The MCP surface is read-only. Do not add write tools without the MARSEL production safety gate in `AGENTS.md`.

Before any future production write capability, the required sequence remains:

`READ -> ANALYZE -> BACKUP -> VERIFY RESTORE PATH -> DRY-RUN -> AUTHORIZED WRITE -> VERIFY -> QA/EVIDENCE`

Credentials must not be placed in GitHub files, source code, tests, logs, artifacts, PR comments, or documentation.

## Verification status

- Repository MCP v2 configuration: VERIFIED.
- stdio server startup/handshake tests: VERIFIED in CI.
- MCP SDK v2 tool registration compatibility: VERIFIED in CI.
- Live RO App connectivity: **NOT VERIFIED** until a valid `ROAPP_API_KEY` is supplied to the local runtime and a read-only inspection call succeeds.

This distinction is intentional: repository configuration and MCP protocol readiness must not be reported as proof of live RO App access.
