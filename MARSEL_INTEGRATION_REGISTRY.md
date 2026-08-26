# MARSEL ROAPP — Integration Registry

## Purpose

Canonical registry for integrations around MARSEL ROAPP. This file records architectural roles and verification status without storing credentials, tokens, private keys, or secret values.

## Canonical system

**MARSEL ROAPP** is the canonical project context.

## Integration map

| System | Role | Status | Verification method | Write policy |
|---|---|---|---|---|
| GitHub | source control, PR, Actions, CI/CD, security | CONNECTED | GitHub connector + repository access | Controlled |
| Codex | coding agent / repository automation | CONFIGURED | repository agent instructions / CI integration | Controlled |
| GitHub Copilot | secondary coding assistant | CONFIGURED | repository instructions | Controlled |
| Cursor | development client / agent | CONFIGURED | repository-level agent configuration | Controlled |
| VS Code Agent | local development agent | CONFIGURED | `.vscode` configuration + agent instructions | Controlled |
| MCP | integration protocol layer | CONFIGURED | repository MCP configuration / readiness checks | Fail-closed |
| ROAPP API | operational ERP/source data | NOT_VERIFIED | API health/auth check required | Production writes disabled |
| Supabase | database/backend | AVAILABLE | connector present; project binding not verified here | Controlled |
| Vercel | deployment | AVAILABLE | connector present; project binding not verified here | Controlled |
| Linear | task/incident management | CONNECTED | ChatGPT connector access | Controlled |
| Notion | documentation/knowledge | CONNECTED | ChatGPT connector access | Controlled |
| Airtable | operational tables/data | CONNECTED | ChatGPT connector access | Controlled |
| Microsoft Outlook | email/notifications | AVAILABLE | connector present; mailbox operation not verified here | Controlled |
| Automations | scheduled checks | AVAILABLE | connector present | Controlled |
| OpenAI Platform | model/API project | NOT_VERIFIED | project URL supplied; API credential must remain secret | Controlled |
| Wix | commerce/site integration | NOT_VERIFIED | external connection/evidence required | Production writes disabled |

## Source-of-truth policy

1. GitHub is the technical source of truth for code and CI/CD.
2. MARSEL ROAPP is the canonical project identity and integration context.
3. ROAPP API is authoritative for operational ROAPP data when its connection is verified.
4. External systems must not be treated as connected solely because a connector exists.
5. Credentials are never stored in this registry.
6. Production writes remain disabled until the applicable production gate passes.

## Health states

- `CONNECTED` — an actual connector/action has been successfully used.
- `CONFIGURED` — repository configuration exists, but live external connectivity is not claimed.
- `AVAILABLE` — an integration capability exists in the current environment; live project/account binding is not verified.
- `NOT_VERIFIED` — required live connectivity or evidence is missing.
- `BLOCKED` — a gate explicitly prevents the action.

## Required automated checks

- GitHub repository and Actions health
- CI status and required checks
- MCP readiness
- ROAPP API authentication/health
- OpenAI project/API configuration without exposing secrets
- Vercel deployment health
- Supabase project health
- Linear/Notion/Airtable connector health
- Wix ↔ ROAPP reconciliation
- backup/restore evidence
- idempotency, rollback and write-dry-run evidence

## Security boundary

This registry is documentation only. It must never contain API keys, OAuth tokens, passwords, webhook secrets, private keys, or customer data.
