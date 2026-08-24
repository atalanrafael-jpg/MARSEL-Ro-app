# MARSEL ROAPP — Branch Inventory 2026-08-24

This is a point-in-time inventory of branches returned by GitHub. Classification based on branch name and open PR mapping is provisional until branch diffs are compared with current `main`.

## Canonical

- `main` — CANONICAL

## Open-PR / active candidates

- `chore/github-governance-hardening` — REVIEW_REQUIRED; PR #64
- `automation/continuous-verification` — REVIEW_REQUIRED; PR #50
- `ci/verify-unified-control-plane` — REVIEW_REQUIRED; PR #49
- `fix/artifact-gates-sync-2026-08-21` — REVIEW_REQUIRED; PR #46
- `fix/unified-issues-19-25-27-30-31-35-42` — REVIEW_REQUIRED; PR #45
- `fix/issue-42-warehouse-contract` — REVIEW_REQUIRED; PR #43
- `chore/marsel-unified-structure-2026-08-21` — REVIEW_REQUIRED; PR #41
- `feat/rafael-ai-os-runtime-foundation` — ACTIVE candidate; PR #39
- `feat/marsel-gmail-unified` — ACTIVE candidate; PR #38
- `feat/gmail-oauth-readonly` — likely SUPERSEDED by #38; verify before deletion; PR #28
- `chore/marsel-github-governance-v1` — CURRENT governance work; PR #65

## Automation / audit / security branches

- `audit/marsel-v20-35-followup`
- `audit/raw-read-integrity`
- `audit/v21-readonly-integrity`
- `audit-v6-readonly`
- `audit-v6-readonly-final`
- `audit-v6-readonly-final2`
- `audit-v6-readonly-final3`
- `audit-v6-readonly-final4`
- `audit-v6-readonly-run`
- `audit-v6-readonly-run-2`
- `automation/continuous-verification`
- `ci/gpt-integration-smoke-tests`
- `ci/verify-unified-control-plane`
- `codex/marsel-api-v2-readonly-preflight`
- `codex/marsel-control-hardening-2026-08-15`
- `codex/openai-ads-conversions`
- `codex/chatgpt-plugin-production`
- `codex-plugin-cleanup`
- `feat/marsel-audit-v15`
- `feat/marsel-gmail-unified`
- `feat/marsel-roapp-api-hardening-v23`
- `feat/openai-ads-conversions`
- `feat/roapp-readonly-audit`
- `feature/gpt-integration`
- `fix/artifact-gates-sync-2026-08-21`

These require branch-to-main comparison before deletion. Several are known historical or merged-PR branches.

## Structural / consolidation branches

- `act/marsel-unified-system-2026-08-22`
- `chore/marsel-system-consolidation-2026-08-21`
- `chore/marsel-unified-structure-2026-08-21`
- `backup/pr40-before-sync-2026-08-22`
- `backup/pr40-conflict-fix-2026-08-22`
- `cloudflare/container-deployment`
- `Secret`
- `1-security-exposed-ro-app-credential-rotate-required`
- `35-ro-app-data-review-11-duplicate-product-code-groups`
- `4-marsel-v13-fix-api-catalog-extraction-v12-discovers-148-docs-but-only-1-operation`

Classify individually as CURRENT, SUPERSEDED, HISTORICAL, BACKUP, or REVIEW_REQUIRED.

## Dependency automation branches

- `dependabot/github_actions/actions/checkout-7`
- `dependabot/github_actions/actions/setup-python-7`
- `dependabot/github_actions/actions/upload-artifact-7`
- `dependabot/pip/httpx-gte-0.28.1`
- `dependabot/pip/mcp-gte-2.0.0-and-lt-3`
- `dependabot/pip/openai-gte-3.3.1-and-lt-4`
- `dependabot/pip/pyjwt-gte-2.13.0-and-lt-3`
- `dependabot/pip/pyspellchecker-gte-0.9.0`
- `dependabot/pip/pytest-asyncio-gte-1.4.0`
- `dependabot/pip/pytest-gte-9.1.1`
- `dependabot/pip/python-dotenv-gte-1.2.3`

Dependabot branches are transient and should be merged or closed according to their PR state, not manually converted into permanent development branches.

## Cleanup policy

No deletion is performed from this snapshot alone. Branch cleanup requires: current-PR comparison → diff against `main` → evidence preservation → classification → close PR if superseded → delete branch only after confirmation.
