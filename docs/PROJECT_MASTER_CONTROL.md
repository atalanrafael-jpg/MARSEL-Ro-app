# MARSEL ROAPP — MASTER PROJECT CONTROL

## Purpose
Единая контрольная точка проекта: техническое состояние RO App integration, качество данных, безопасность, бизнес-автоматизация, deployment и коммерческий контур MARSEL.

## Canonical state — 2026-09-17
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Canonical branch: `main-MARSEL-ROAPP`
- Current canonical HEAD: **the current HEAD of `main-MARSEL-ROAPP`; do not hardcode a SHA in this self-updating control file.**
- Previous canonical checkpoint: `7aa02f2e6d33219240973b9157f9117aa1a073ba`
- Canonical control plane: `.github/workflows/marsel-unified-control-plane.yml`
- Canonical control contract: `01_MASTER/MARSEL_ROAPP_CONTROL_PLANE_V2.md`
- Repository validator: `scripts/marsel_control_plane_validate.py`
- Current integration mode: READ-ONLY.
- Production WRITE: DISABLED.

## Implemented in this checkpoint
- Added a fail-closed repository-local control-plane validator.
- Added the V2 control contract covering lifecycle, statuses, evidence, safety, multi-agent orchestration and drift control.
- Added the validator as a mandatory step in the unified GitHub Actions control plane.
- Preserved the existing live RO App audits as READ-ONLY and secret-protected.
- Aligned `python/requirements.txt` to `openai>=3.14.1,<4`.
- Aligned `requirements.lock` to `openai==3.14.1` and restored the complete locked dependency set.
- Removed the self-referential hardcoded HEAD pin so future documentation commits cannot make the registry one checkpoint behind the repository.

## Verified current repository state
- `main-MARSEL-ROAPP` is the repository default branch and is protected at the branch level; GitHub reports required status-check enforcement as off, so CI completion must still be verified from actual workflow evidence.
- The repository's canonical structure separates `01_MASTER`, `02_MARSEL`, `03_ROAPP`, `04_DEVELOPMENT`, `05_CONTROL` and `06_ARCHIVE`; historical control documents are archived and explicitly marked superseded.
- The unified workflow is scoped to the canonical branch, uses read-only repository permissions, keeps production WRITE disabled, and obtains `ROAPP_API_KEY` only from GitHub Actions Secrets.
- Backup/export and isolated restore/integrity are recorded as already verified in the project control issues; they are not repeated merely because other gates remain open.
- Observability/correlation is recorded as verified under Issue #134.
- The current canonical branch commit status must be checked from live GitHub evidence before CI is marked PASS.

## Hard blockers for 100% production readiness
1. Fresh authorized RO App GET evidence must prove complete applicable API/entity coverage.
2. Warehouse/stock live contract must be proven with fresh authoritative evidence.
3. Current duplicate/reference reconciliation must be closed.
4. Credential-exposure remediation remains open under Issue #23 until rotation/revocation and exposure verification are directly evidenced.
5. Official RO App MCP authorization is not independently verified.
6. Gmail OAuth requires actual user authorization if this integration remains in scope.
7. A production deployment target is not verified as configured in Vercel or Railway.
8. Current Wix ↔ RO App reconciliation, mutation dry-run, idempotency and rollback evidence remain open under the production-gate issues.
9. GitHub account-level security controls and branch hygiene requiring administration remain open under Issue #91.
10. Production WRITE remains disabled until every applicable safety gate passes and explicit authorization exists.

## Safety
Never claim backup, restore, reconciliation, security rotation, OAuth, MCP authorization, deployment, synchronization or WRITE readiness without direct evidence. Never guess an API endpoint or identifier. Never execute a production mutation merely to make a test green. Never expose or commit `ROAPP_API_KEY`.

## Continuation rule
Every execution starts from this file and the current `main-MARSEL-ROAPP` checkpoint. Verify current CI/live evidence, fix the highest-priority safe defect, verify the result, document the checkpoint, and continue. If an external authorization or secret is required and unavailable to the connected tools, mark the gate `BLOCKED` rather than simulating completion.
