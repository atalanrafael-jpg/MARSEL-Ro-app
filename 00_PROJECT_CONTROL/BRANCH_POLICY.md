# MARSEL ROAPP — Branch Policy

## Canonical

- `main` is the only canonical integration branch.

## Active work

Open PRs are the authoritative indicator of work that may still matter. Current open PRs must be evaluated before branch cleanup.

### Current open work identified during audit

- `chore/github-governance-hardening` → PR #64 — governance/security; overlaps this consolidation branch and should be reconciled rather than duplicated.
- `automation/continuous-verification` → PR #50 — automation; verify whether its checks are already covered by current workflows before merge.
- `ci/verify-unified-control-plane` → PR #49 — verification-only; close after current control-plane execution is independently evidenced.
- `fix/artifact-gates-sync-2026-08-21` → PR #46 — artifact/warehouse gate remediation; requires fresh CI/evidence.
- `fix/unified-issues-19-25-27-30-31-35-42` → PR #45 — broad remediation; requires comparison with current `main` before any merge.
- `fix/issue-42-warehouse-contract` → PR #43 — warehouse contract; requires fresh official-contract evidence.
- `chore/marsel-unified-structure-2026-08-21` → PR #41 — structural consolidation; overlaps this governance work and is stale relative to current `main`.
- `feat/rafael-ai-os-runtime-foundation` → PR #39 — AI runtime foundation; isolated feature, merge only after its own tests/gates.
- `feat/marsel-gmail-unified` → PR #38 — newer Gmail implementation; requires live OAuth/evidence gates.
- `feat/gmail-oauth-readonly` → PR #28 — older Gmail implementation; treat as superseded by #38 unless evidence proves otherwise.

## Lifecycle

- `ACTIVE` — current branch with an open, still-relevant PR.
- `CURRENT` — branch aligned with current architecture and still required.
- `SUPERSEDED` — replaced by a newer branch/PR; close PR and delete branch after evidence is preserved.
- `HISTORICAL` — retained only as reference/recovery evidence.
- `EXPERIMENTAL` — prototype with no production dependency.
- `BACKUP` — recovery reference; never merge as normal feature work.
- `REVIEW_REQUIRED` — cannot classify safely yet.

## Cleanup sequence

1. Compare branch head against current `main`.
2. Identify open PR and unique changes.
3. Preserve useful evidence/documentation.
4. Mark `SUPERSEDED` or `HISTORICAL`.
5. Close superseded PR.
6. Delete branch only after preservation and dependency checks.

No branch is deleted solely because it is old.
