# MARSEL ROAPP — Integration Registry

This registry separates integrations that already exist in the repository from integrations that still require external configuration or live verification.

| Integration | Role | Repository state | Production rule |
|---|---|---|---|
| GitHub Actions | CI/CD, audits, evidence | ACTIVE | Canonical automation layer |
| CodeQL | Security analysis | ACTIVE | Required for security-sensitive changes |
| Dependabot | Dependency updates | ACTIVE | Merge only after CI/security gates |
| MARSEL Unified Control Plane | ROAPP live audit | ACTIVE | GET/read-only; evidence required |
| Secret Guard | Credential detection | ACTIVE | Fail closed on high-confidence findings |
| MCP / MARSEL ROAPP plugin | ChatGPT/Codex integration | ACTIVE | Read-only tools only |
| Codex plugin | Developer workflow | ACTIVE | No implicit production writes |
| OpenAI Ads CAPI | Conversion measurement | IMPLEMENTED / VERIFY | Wire only to confirmed order-success boundary; secrets server-side |
| Gmail OAuth | Read-only business email | IMPLEMENTED / VERIFY | Read-only scope, encrypted storage, live smoke test required |
| Outlook/Microsoft 365 | Email context | EXTERNAL / VERIFY | Add only after explicit account/permission setup |
| n8n | Workflow automation | EXTERNAL / REVIEW_REQUIRED | Use as orchestration only; production actions require approval gates |
| Cloudflare | Deployment/edge | EXTERNAL / REVIEW_REQUIRED | Add only when actual deployment topology is confirmed |
| Supabase/Postgres | Structured data layer | EXTERNAL / REVIEW_REQUIRED | Do not introduce a second system of record without architecture approval |
| Linear/Jira | Work management | OPTIONAL / REVIEW_REQUIRED | One project tracker only; GitHub Issues can remain canonical until migration is justified |

## Required integration order

1. GitHub repository governance and Actions.
2. ROAPP read-only API + evidence.
3. Secret management and credential rotation.
4. Codex/MCP read-only surface.
5. Gmail read-only OAuth if required by operations.
6. OpenAI Ads CAPI at a confirmed order-success boundary.
7. Automation/orchestration (n8n/Cloudflare/etc.) only after the core gates are stable.
8. Optional project-management connectors only if they reduce duplication.

## Anti-duplication rule

Do not add an integration merely because a connector/plugin exists. Every integration must have one documented purpose, one owner, one credential boundary, one test, and one failure/rollback behavior.
