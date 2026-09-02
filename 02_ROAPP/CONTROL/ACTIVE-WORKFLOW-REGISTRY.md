# MARSEL ROAPP — ACTIVE WORKFLOW REGISTRY

## Canonical identity

- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Branch: `main`
- Canonical live RO App audit: `.github/workflows/marsel-unified-control-plane.yml`

## Rule

GitHub Actions are components of the MARSEL ROAPP control plane, not separate projects. Every workflow must have one distinct responsibility and be registered here. No supporting workflow may silently become a second live RO App audit path.

## Core

**`marsel-unified-control-plane.yml`** — canonical READ-ONLY RO App audit/evidence path: structure, API inventory, data quality, entity audit, product-code review, warehouse contract, safety/quality gate and evidence.

**`marsel-production-gate.yml`** — fail-closed production gate; it does not authorize WRITE merely because CI is green.

**`test.yml`** — general engineering/unit tests; not the canonical live RO App audit.

**`mcp-production.yml`** — MCP-specific engineering/readiness checks.

## Supporting / security / auxiliary workflows

- `marsel-evidence-orchestrator.yml` — evidence orchestration.
- `marsel-integration-health.yml` — integration health.
- `marsel-live-probes.yml` — supporting live probes.
- `marsel-roapp-api-v2-guard.yml` — API guard.
- `marsel-secret-guard.yml` — security/secret checks.
- `marsel-warehouse-contract-v20-48.yml` — warehouse contract diagnostic; review-only unless authoritative contract evidence exists.
- `codeql.yml` — code security.
- `codex-plugin-validation.yml` — Codex/plugin validation.
- `ai-os-runtime-tests.yml` — AI runtime tests.
- `language-quality.yml` — language/code quality.
- `github-account-health.yml` — GitHub health.
- `generate-drafts.yml` — AI draft generation; has write permission to issues and is not part of the live audit control plane.

## Canonical production chain

`Issue → PR → CI/Actions → Evidence → Gate → Result`

## Consolidation policy

Do not delete workflows solely because their names overlap. Before removal or merge, inspect triggers, jobs, artifacts, dependencies, checks and historical evidence. A workflow becomes a deletion candidate only after its responsibility is proven redundant and its dependencies are removed.

## Safety

Production WRITE remains disabled. Live RO App audit invariant:

- READ-ONLY;
- `WRITE_REQUESTS_MADE=0`;
- `RO_APP_DATA_MUTATED=false`;
- no guessed identifiers;
- no undocumented endpoint promoted to PASS;
- skipped, stale, synthetic or incomplete evidence cannot produce production PASS.

## Current blockers — 2026-09-02

- Backup/export: NOT VERIFIED
- Restore/integrity: NOT VERIFIED
- Warehouse official contract: NOT VERIFIED
- Full current API/entity coverage: NOT VERIFIED
- Credential-exposure remediation: NOT VERIFIED
- Gmail OAuth live authorization: NOT VERIFIED
- Official RO App MCP authorization: NOT VERIFIED
- Current GitHub account/ruleset security controls: PARTIAL / external verification required

## Current status

`REVIEW_REQUIRED / NO-GO FOR PRODUCTION WRITE`

Current priority source: `docs/MARSEL-UNIFIED-MASTER-2026-09-02.md`.
