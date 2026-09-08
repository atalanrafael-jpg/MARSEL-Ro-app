# Codex MCP configuration

The plugin's MCP server is declared by `../.mcp.json` and is intentionally kept separate from project source code.

Required local environment:

- `ROAPP_API_KEY`
- `ROAPP_BASE_URL` (default: `https://api.roapp.io/v2`)
- `ROAPP_TIMEOUT_SECONDS` (default: `30`)

The MCP surface is read-only. Do not add credentials to repository files or enable production writes without the safety gate in the repository `AGENTS.md`.
