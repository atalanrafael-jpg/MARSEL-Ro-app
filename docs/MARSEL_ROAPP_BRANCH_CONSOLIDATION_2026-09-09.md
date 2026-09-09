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
- No production RO App write is authorized by this register.

## Proven duplicate group

| Classification | Branches | Evidence |
|---|---|---|
| DUPLICATE | `audit-v6-readonly`, `audit-v6-readonly-final`, `audit-v6-readonly-final2`, `audit-v6-readonly-final3`, `audit-v6-readonly-final4`, `audit-v6-readonly-run`, `audit-v6-readonly-run-2` | All seven point to `cb67e29846b7d3ac0973b643e6b838d2f0600466`. The commit adds the obsolete `MARSEL audit v5` workflow. The same commit is an ancestor of current `main`, so the branch tips contain no unintegrated change. |
| DUPLICATE | `feature/marsel-roapp-control-agent`, `feature/marsel-roapp-control-agent-v2` | Both point to `2ce18fc9461fcb22da630af20c8c23459e727980`, a completed ROAPP OpenAPI/ReadMe CI hardening commit already represented in the repository history. |

## Do not delete automatically

- `feature/marsel-roapp-control-agent-v3`: contains a distinct dependency change and must not be promoted merely because related branches are duplicates.
- `audit/roapp-hardening-2026-09-07`: has unique commits and remains `REVIEW_REQUIRED`.
- security branches: preserve until security remediation/evidence is closed.
- backup branches: preserve as historical recovery references.
- ERP/data-model branches: preserve until unique work is reconciled.
- multi-agent/control-plane branches: preserve while related PRs/issues remain part of the active MARSEL ROAPP control architecture.

## Administrative deletion status

The connected GitHub interface currently exposes no branch-delete operation. Therefore this register records safe deletion candidates but does not perform destructive ref deletion through an unrelated or unsafe operation.

## Production safety

`PRODUCTION_WRITE=DISABLED`.

Branch consolidation does not authorize RO App data mutation, production writes, credential rotation, or external authorization changes.
