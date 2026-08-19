# Security — MARSEL ROAPP

MARSEL ROAPP is one system. Security controls apply to the complete repository, including MARSEL business logic, ROAPP API/integrations, AI/MCP and CI/CD.

## Mandatory rules

- Never commit API keys, OAuth tokens, refresh tokens, client secrets or passwords.
- Keep production credentials in protected secret storage.
- Keep RO App production mutations disabled until the unified production safety gate passes.
- Treat READ-ONLY evidence as the default verification mode.
- Do not claim backup, restore, reconciliation, OAuth, MCP authorization or WRITE readiness without direct evidence.
- Review repository history, Issues, PRs, Actions logs and artifacts when credential exposure is suspected.
- Minimize OAuth scopes and use read-only scopes unless a documented business requirement requires more.

## Canonical control

Use `.github/workflows/marsel-unified-control-plane.yml` as the canonical MARSEL ROAPP audit workflow. Avoid parallel security/audit implementations that duplicate the same responsibility.
