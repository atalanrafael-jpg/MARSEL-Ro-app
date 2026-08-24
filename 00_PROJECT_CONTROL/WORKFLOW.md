# MARSEL ROAPP — Automated Work Process

## Standard loop

1. **Capture** — issue or task is recorded with scope and risk.
2. **Classify** — `FEATURE`, `BUG`, `SECURITY`, `AUDIT`, `DATA`, `INTEGRATION`, `AI`, `CI`, or `OPS`.
3. **Plan** — identify affected domain, evidence required, rollback requirements, and production-write impact.
4. **Branch** — create `feat/`, `fix/`, `chore/`, `audit/`, `ci/`, `ops/`, or `backup/` branch from current `main`.
5. **Implement** — smallest reversible change.
6. **Validate** — unit tests, compile/lint, dependency checks, secret scan, and domain-specific checks.
7. **Audit** — for ROAPP/data work, run GET-only checks and produce evidence.
8. **Review** — PR review against the applicable gate checklist.
9. **Merge** — only after required checks are green and no unresolved blocking evidence remains.
10. **Verify main** — run canonical control-plane verification after merge.
11. **Release/readiness** — only a verified `main` state can be promoted.
12. **Record** — update current state, changelog, registry, and evidence references for material changes.

## Gate order

`Security → Correctness → Data integrity → API contract → Tests → Evidence → Operational readiness → Business feature`

A lower-priority feature does not override a blocking security/data-integrity gate.

## Production data gate

For any future production WRITE capability:

`backup → restore test → reconciliation → dry-run → explicit rollback plan → approval → controlled WRITE → post-write verification`

Until all gates are evidenced, production WRITE remains disabled.

## Automation map

Existing GitHub Actions are the execution layer. Their responsibilities should remain distinct:

- `test.yml` — code/tests/dependencies.
- `codeql.yml` — code security analysis.
- `marsel-secret-guard.yml` — credential-like material detection.
- `marsel-unified-control-plane.yml` — canonical ROAPP evidence/control gate.
- `marsel-production-gate.yml` — production-readiness gate; must remain fail-closed.
- `marsel-release-readiness.yml` — release readiness.
- `mcp-production.yml` — MCP production-readiness checks.
- `codex-plugin-validation.yml` — plugin validation.
- `language-quality.yml` — documentation/language quality.
- `dependabot.yml` — dependency update proposals.

Do not create a second control-plane workflow that duplicates the canonical one. Extend the canonical gate or add a narrowly scoped check with a unique responsibility.

## Evidence rule

A green unit test is not evidence of live ROAPP correctness. Live claims require live evidence. A missing artifact is `REVIEW_REQUIRED`, not `PASS`.
