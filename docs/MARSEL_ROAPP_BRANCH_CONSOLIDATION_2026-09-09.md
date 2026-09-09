# MARSEL ROAPP — Branch Consolidation Register

Date: 2026-09-09
Canonical repository: `atalanrafael-jpg/MARSEL-Ro-app`
Canonical integration branch: `main`

## Rules

- This register covers only the MARSEL ROAPP repository.
- A branch is not classified for deletion solely by name.
- `DUPLICATE` requires identical tip SHA and/or proven equivalent history already integrated into `main`.
- `SUPERSEDED` means the branch contains no required change that should be promoted to `main`.
- `HISTORICAL` branches are retained unless their historical value is explicitly reviewed.
- `REVIEW_REQUIRED` blocks deletion.
- Open PRs and security/data branches are reviewed independently of branch-name similarity.
- No production RO App write is authorized by this register.

## Proven duplicate group

| Classification | Branches | Evidence |
|---|---|---|
| DUPLICATE | `audit-v6-readonly`, `audit-v6-readonly-final`, `audit-v6-readonly-final2`, `audit-v6-readonly-final3`, `audit-v6-readonly-final4`, `audit-v6-readonly-run`, `audit-v6-readonly-run-2` | All seven point to `cb67e29846b7d3ac0973b643e6b838d2f0600466`. The commit adds the obsolete `MARSEL audit v5` workflow. The same commit is an ancestor of current `main`; comparison confirms the branch tip is 0 commits ahead of `main`. |
| DUPLICATE | `feature/marsel-roapp-control-agent`, `feature/marsel-roapp-control-agent-v2` | Both point to `2ce18fc9461fcb22da630af20c8c23459e727980`, a completed ROAPP OpenAPI/ReadMe CI hardening commit already represented in repository history. |

## Verified fully integrated / historical branches

| Classification | Branch | Evidence |
|---|---|---|
| HISTORICAL / INTEGRATED | `chore/marsel-system-consolidation-2026-08-21` | Comparison against current `main`: 0 commits ahead; its tip `7c3ebed5f561bea726aec37107a476f72d780902` is fully behind current main. PR #40 is merged. |
| HISTORICAL / INTEGRATED | `audit-v6-readonly-final4` | Comparison against current `main`: 0 commits ahead; tip is the known `cb67e298...` duplicate group. |
| HISTORICAL / INTEGRATED | `fix/warehouse-contract-current` | Comparison against current `main`: 0 commits ahead; PR #114 is merged. The branch is retained as historical reference because it contains the prior warehouse-contract implementation. |

These branches are safe from a content perspective to archive/delete only after any historical/evidence retention requirement is satisfied. The connected interface does not expose physical branch deletion.

## Active / unique branches requiring review

- `feature/marsel-roapp-control-agent-v3`: distinct dependency change; PR #113 is closed without merge. Do not delete or promote merely because v1/v2 are duplicates.
- `audit/roapp-hardening-2026-09-07`: unique security hardening; PR #132 remains open Draft and must be preserved.
- `chore/integration-control-plane-v1`: unique integration registry/config changes; PR #146 remains open and must be preserved until reviewed/rebased.
- `chore/cursor-agent-governance`: unique `.cursor/rules/*` governance files; PR #131 remains open and must be preserved until reconciled.
- `feat/agent-runtime-v1-corrected`: unique Agent Runtime implementation/tests; PR #123 remains open and must be preserved.
- `erp-data-model-2026-09-06`: unique ERP entity ownership/API mapping plus dictionary work; PR #127 remains open and must be preserved.
- `feat/erp-data-dictionary-v1`: unique later dictionary revision sharing the same target filename as PR #127; PR #128 remains open. Treat as overlapping work requiring reconciliation, not automatic deletion.
- `test/codex-mcp-stdio-handshake`: PR #141 remains open; preserve until the handshake test is reconciled with the already merged MCP compatibility work.

## Important overlapping work

`feat/erp-data-dictionary-v1` and `erp-data-model-2026-09-06` both modify `docs/MARSEL_ERP_DATA_DICTIONARY_V1.md`, but they are not identical. The newer dictionary revision is 150 lines and the ERP model branch's version is 98 lines; the ERP model branch additionally carries ownership/API mapping documents. This is an overlap/reconciliation case, not a proven duplicate.

## Security / backup / historical retention

- Security branches are preserved until credential-exposure remediation and evidence are closed.
- Backup branches are preserved as recovery references.
- ERP/data-model branches are preserved until unique work is reconciled.
- Multi-agent/control-plane branches are preserved while related PRs/issues remain part of the active MARSEL ROAPP architecture.
- Historical branches may be retained even when their code is fully integrated if they are needed to preserve audit provenance.

## Administrative deletion status

The connected GitHub interface currently exposes no branch-delete operation. Therefore this register records safe deletion candidates but does not perform destructive ref deletion through an unrelated or unsafe operation.

## Current canonical state

`main` remains the only canonical integration branch. All reviewed work must be reconciled into current `main` through normal PR review and fresh CI/evidence verification. A stale branch is not a second source of truth.

## Production safety

`PRODUCTION_WRITE=DISABLED`.

Branch consolidation does not authorize RO App data mutation, production writes, credential rotation, or external authorization changes.
