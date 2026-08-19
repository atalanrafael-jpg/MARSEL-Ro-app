# Security — MARSEL ROAPP

MARSEL ROAPP is one system. Security controls apply to MARSEL business logic, ROAPP API/integrations, AI/MCP and CI/CD.

- Never commit API keys, OAuth tokens, refresh tokens, client secrets or passwords.
- Keep production credentials in protected secret storage.
- Keep production mutations disabled until the unified production safety gate passes.
- Default live verification mode is READ-ONLY.
- Never claim backup, restore, reconciliation, OAuth, MCP authorization or WRITE readiness without direct evidence.
- Review history, Issues, PRs, Actions logs and artifacts when credential exposure is suspected.
- Minimize OAuth scopes and prefer read-only scopes.
- Use `.github/workflows/marsel-unified-control-plane.yml` as the canonical audit path.
