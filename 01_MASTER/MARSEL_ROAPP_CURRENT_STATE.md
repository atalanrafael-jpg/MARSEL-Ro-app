# MARSEL ROAPP — CURRENT STATE

**Assessment date:** 2026-09-20
**State:** CANONICAL MAIN SYNCHRONIZED; PRODUCT GATE A AND EXTERNAL/SECURITY GATES REMAIN

## Verified
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`.
- Technical canonical branch: `main`.
- GitHub repository default branch: `main`.
- The current canonical HEAD is the live `main` HEAD; its SHA is intentionally not hardcoded here because this document is itself versioned on `main`.
- The compatibility branches `Main`, `main-MARSEL-ROAPP`, and `main-MARSEL-ROAPP-PROTECTION` were synchronized during the preceding verification; this must be rechecked after subsequent changes.
- The active ruleset ID `21230907` is enforced, but its ref condition currently targets `refs/heads/main-MARSEL-ROAPP`, not `refs/heads/main`. This is a governance mismatch that remains to be corrected through GitHub administration.
- Production WRITE remains disabled.

## Product Gate A
The repository contract states that the owner MVP is the priority. The implemented application path requires live deployment and direct end-to-end verification. Supabase application tables were documented as having zero application rows in the current productization contract.

Required vertical slice:
AUTH → OWNER DASHBOARD → CLIENT → REPAIR → ITEM → STATUS → ATTACHMENT → AUDIT → DEPLOY → VERIFY

## Remaining gates
1. Fresh Unified Control Plane run on the synchronized canonical state must be directly verified.
2. Gate A live deployment and end-to-end owner workflow must be directly verified.
3. Fresh authorized RO App API/entity coverage evidence remains required.
4. Fresh warehouse/stock contract evidence remains required.
5. Current duplicate/orphan/reference reconciliation remains required.
6. Credential rotation/remediation and absence-of-secret evidence remain required.
7. External Gmail OAuth / RO App MCP authorization and account-level GitHub administration remain external gates where applicable.
8. Production WRITE remains disabled until explicit staged evidence and authorization satisfy the production gates.

## Open GitHub work
The currently open issues include the owner MVP (#183), production/security/API evidence gates (#19, #23, #30, #83, #85, #77), Gmail OAuth (#27), GitHub account controls (#91), ReadMe sync (#106), and integration adapters (#135). Closed/superseded issues are not treated as active work.

## Canonical rule
Only `main` is the technical source of truth. Compatibility branches are synchronized aliases only. Historical material under `06_ARCHIVE` is evidence and does not override newer verified state. No archived document may override current verified state.
