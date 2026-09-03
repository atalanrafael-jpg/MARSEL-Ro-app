# MARSEL ROAPP — Integration Registry

**Project:** MARSEL ROAPP  
**Mode:** Read-only health verification  
**Production write:** false  
**Credentials exposed:** false

## Repository topology

The canonical repository is `atalanrafael-jpg/MARSEL-Ro-app`. Supporting repositories are classified separately and are not treated as connected runtime systems unless direct evidence exists.

Canonical repository-link registry: [`docs/MARSEL-REPOSITORY-LINKS.md`](docs/MARSEL-REPOSITORY-LINKS.md).

## Integration declarations

| System | Registry status | Live verification |
|---|---|---|
| GitHub | CONNECTED | Repository access verified; account/ruleset controls still require account-level verification |
| Codex | CONFIGURED | Repository/tooling presence verified; live runtime not independently probed |
| GitHub Copilot | CONFIGURED | Repository instructions/workflow presence verified; account-level connection not independently probed |
| Cursor | CONFIGURED | Repository configuration presence verified; live connection not independently probed |
| VS Code Agent | CONFIGURED | Repository configuration presence verified; live connection not independently probed |
| MCP | CONFIGURED | Local MARSEL MCP/plugin configuration present; official RO App MCP authorization not verified |
| ROAPP API | NOT_VERIFIED | Requires direct live READ-ONLY verification |
| Supabase | AVAILABLE | Requires explicit MARSEL use case and live verification |
| Vercel | AVAILABLE | Requires explicit MARSEL use case and live verification |
| Linear | CONNECTED | Connector availability does not constitute repository/runtime integration evidence |
| Notion | CONNECTED | Connector availability does not constitute repository/runtime integration evidence |
| Airtable | CONNECTED | Connector availability does not constitute repository/runtime integration evidence |
| Microsoft Outlook | AVAILABLE | Not independently probed |
| Automations | AVAILABLE | Not independently probed |
| OpenAI Platform | NOT_VERIFIED | Requires direct account/runtime verification |
| Wix | NOT_VERIFIED | Requires direct live verification |
| WhatsApp | CANDIDATE | Current Cloud API integration must be explicitly implemented and verified |
| Zapier MCP | CANDIDATE | Requires explicit MARSEL workflow and authorized MCP connection |
| n8n | CANDIDATE | Requires explicit MARSEL workflow and deployment/runtime evidence |

## Evidence policy

This registry is a declaration/configuration inventory only. It is **not** production evidence and does not claim live connectivity for systems marked CONFIGURED, AVAILABLE, CONNECTED, or CANDIDATE. Live verification must come from the read-only health/probe jobs and their generated artifacts.

No credentials, tokens, secrets, or production write operations belong in this file.
