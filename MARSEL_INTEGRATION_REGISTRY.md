# MARSEL ROAPP — Integration Registry

**Project:** MARSEL ROAPP  
**Mode:** Read-only health verification  
**Production write:** false  
**Credentials exposed:** false

## Integration declarations

| System | Registry status | Live verification |
|---|---|---|
| GitHub | CONNECTED | Not independently probed by this checker |
| Codex | CONFIGURED | Not independently probed by this checker |
| GitHub Copilot | CONFIGURED | Not independently probed by this checker |
| Cursor | CONFIGURED | Not independently probed by this checker |
| VS Code Agent | CONFIGURED | Not independently probed by this checker |
| MCP | CONFIGURED | Not independently probed by this checker |
| ROAPP API | NOT_VERIFIED | Requires MARSEL_ROAPP_HEALTH_URL |
| Supabase | AVAILABLE | Requires MARSEL_SUPABASE_HEALTH_URL |
| Vercel | AVAILABLE | Requires MARSEL_VERCEL_HEALTH_URL |
| Linear | CONNECTED | Not independently probed by this checker |
| Notion | CONNECTED | Not independently probed by this checker |
| Airtable | CONNECTED | Not independently probed by this checker |
| Microsoft Outlook | AVAILABLE | Not independently probed by this checker |
| Automations | AVAILABLE | Not independently probed by this checker |
| OpenAI Platform | NOT_VERIFIED | Requires MARSEL_OPENAI_HEALTH_URL |
| Wix | NOT_VERIFIED | Requires MARSEL_WIX_HEALTH_URL |

## Evidence policy

This registry is a declaration/configuration inventory only. It is **not** production evidence and does not claim live connectivity for systems marked CONFIGURED, AVAILABLE, or CONNECTED. Live verification must come from the read-only health/probe jobs and their generated artifacts.

No credentials, tokens, secrets, or production write operations belong in this file.
