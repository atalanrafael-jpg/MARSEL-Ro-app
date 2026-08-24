# MARSEL ROAPP

**Единая система ювелирной студии MARSEL.** MARSEL — бизнес-контур; ROAPP — технологический контур той же системы.

## Canonical source

- Repository: `atalanrafael-jpg/Ro-app`
- Branch: `main`
- Canonical control plane: `.github/workflows/marsel-unified-control-plane.yml`
- Canonical governance: `00_PROJECT_CONTROL/GITHUB_GOVERNANCE.md`
- Repository registry: `00_PROJECT_CONTROL/REPOSITORY_REGISTRY.md`
- Project structure: `00_PROJECT_CONTROL/PROJECT_DATA_STRUCTURE.md`
- Automated work process: `00_PROJECT_CONTROL/WORKFLOW.md`
- Canonical documentation: `MARSEL_ROAPP_UNIFIED_SYSTEM.md` and `docs/PROJECT_MASTER_CONTROL.md`
- Historical material: `старые данные/`

## Operating model

`CAPTURE → CLASSIFY → PLAN → BRANCH → IMPLEMENT → VALIDATE → AUDIT → REVIEW → MERGE → VERIFY MAIN → RELEASE/READINESS → RECORD`

For RO App live auditing:

`INVENTORY → DATA QUALITY → ENTITY AUDIT → COLLISION REVIEW → WAREHOUSE CONTRACT → SAFETY GATE → EVIDENCE`

All RO App live auditing is READ-ONLY. Parameterized identifiers are never guessed. Missing or incomplete evidence produces `REVIEW_REQUIRED`, not `PASS`.

## Production safety

Production mutations remain disabled until direct evidence exists for:

`backup/export → restore → reconciliation → full READ-ONLY inventory → duplicate/orphan/reference analysis → dry-run → idempotency → rollback → controlled write → post-write verification`.

A successful CI run alone is not proof of a successful production synchronization.

## Current known external gates

Live Gmail OAuth, official RO App MCP authorization, complete warehouse/API coverage, production backup/restore, and credential rotation after the previously exposed ROAPP key are external verification gates. They must not be reported as completed without fresh evidence.

## GitHub operating rule

`main` is the only canonical integration branch. Work is performed in scoped branches and merged through PRs after the applicable CI/security/evidence gates pass. Historical branches are classified before deletion; they are not treated as a second source of truth.
