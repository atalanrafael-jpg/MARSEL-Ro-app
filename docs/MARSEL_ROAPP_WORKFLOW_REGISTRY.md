# MARSEL ROAPP — GitHub Actions Workflow Registry

## Canonical repository

`atalanrafael-jpg/MARSEL-Ro-app`

Canonical branch: `main`

## Rule

GitHub Actions are control-plane components of MARSEL ROAPP. A workflow is not a separate project. New workflows must have a defined MARSEL ROAPP responsibility and must not duplicate an existing control-plane responsibility.

## Current workflow inventory

| Workflow | Role | Classification |
|---|---|---|
| `marsel-unified-control-plane.yml` | Canonical read-only audit/evidence control plane | CANONICAL |
| `marsel-production-gate.yml` | Fail-closed production gate | CANONICAL GATE |
| `marsel-evidence-orchestrator.yml` | Evidence orchestration | SUPPORTING |
| `marsel-integration-health.yml` | Integration health | SUPPORTING |
| `marsel-live-probes.yml` | Live probes | SUPPORTING |
| `marsel-roapp-api-v2-guard.yml` | RO App API guard | SUPPORTING |
| `marsel-secret-guard.yml` | Secret/source safety | SECURITY |
| `marsel-warehouse-contract-v20-48.yml` | Warehouse contract diagnostic | CONTRACT / REVIEW |
| `mcp-production.yml` | MCP application tests and dependency audit | ENGINEERING |
| `codeql.yml` | Code security analysis | SECURITY |
| `codex-plugin-validation.yml` | Codex/plugin validation | ENGINEERING |
| `ai-os-runtime-tests.yml` | AI runtime tests | ENGINEERING |
| `language-quality.yml` | Language/code quality | ENGINEERING |
| `github-account-health.yml` | GitHub account/repository health | SUPPORTING |
| `generate-drafts.yml` | Draft generation | AUXILIARY |
| `test.yml` | General test workflow | ENGINEERING / REVIEW |

## Consolidation policy

Do not delete a workflow solely because its name overlaps another workflow. Before removal or merge, verify its triggers, jobs, artifacts, checks, and historical evidence.

The canonical production chain is:

`Issue → PR → CI/Actions → Evidence → Gate → Result`

## Production safety

Production WRITE remains disabled until all mandatory gates have direct evidence. No workflow may treat synthetic, skipped, stale, or incomplete evidence as a production PASS.

## Current blockers

- Backup/export evidence: NOT VERIFIED
- Restore/integrity evidence: NOT VERIFIED
- Warehouse contract: NOT VERIFIED unless direct live contract evidence exists
- Product-code collision review: unresolved items require review

These blockers must remain visible to the production gate.
