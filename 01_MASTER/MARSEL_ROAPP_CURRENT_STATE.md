# MARSEL ROAPP — CURRENT STATE

**Assessment date:** 2026-09-18
**State:** CANONICAL STRUCTURE ESTABLISHED; FINAL CI/EXTERNAL GATES REMAIN

## Verified
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`.
- Technical canonical branch: `main`.
- `main` is the current execution source.
- Six canonical zones `01_MASTER` through `06_ARCHIVE` exist.
- Historical `старые данные/` content was migrated into `06_ARCHIVE/legacy-old-data/` and the legacy tree removed.
- Superseded root master documents were migrated into `06_ARCHIVE/legacy-root/` and removed from the active root.
- Canonical governance, agent instructions and static self-check were aligned to the technical canonical branch.
- Production WRITE remains disabled.
- GitHub currently reports `main-MARSEL-ROAPP` as the repository default branch; this is an administrative/default-branch state and does not override the project technical canonical rule.

## Remaining gates
- Fresh GitHub Actions/control-plane run after the final cleanup corrections must be directly verified.
- Fresh authorized RO App evidence for complete applicable API/entity coverage remains required.
- Fresh warehouse/stock contract evidence remains required.
- Current duplicate/orphan/reference reconciliation remains required.
- Credential remediation/security evidence remains required.
- External OAuth/MCP and account-level GitHub administration remain external gates where applicable.
- Historical snapshots and temporary branches require dependency/evidence review before retirement; they are not to be deleted blindly.

## Canonical rule
Only `main` is the technical source of truth. Historical material under `06_ARCHIVE` is evidence only. No archived document may override newer verified state.
