# MARSEL ROAPP — CONTROL PLANE V2

Status: IMPLEMENTED — 2026-09-16
Canonical branch: `main-MARSEL-ROAPP`
Production WRITE: DISABLED

## 1. Single authority

`docs/PROJECT_MASTER_CONTROL.md` is the entry point. `01_MASTER/` is the canonical control domain. Historical control documents remain in `06_ARCHIVE/` and are not authoritative.

## 2. Execution lifecycle

`INTAKE → ROUTE → PLAN → ACT → VERIFY → EVIDENCE → CLOSE`

Any failed verification follows:

`STOP → CORRECT → REVERIFY`

A task cannot be marked DONE without verifiable evidence.

## 3. Control domains

| Domain | Responsibility |
|---|---|
| Master Registry | canonical project identity, branches, integrations, environments |
| Task Register | one task identity, status, dependency and acceptance criteria |
| Decision Log | durable decisions and superseded decisions |
| Change History | commits, PRs, workflow evidence and control changes |
| Data Governance | entity coverage, duplicates, orphan/reference integrity |
| Security | secrets, exposure, permissions, production gates |
| Production Gate | independent evidence before any mutation |
| Observability | correlation IDs, run markers, failure provenance |
| Recovery | backup/restore evidence and rollback controls |

## 4. Status contract

- `OPEN`: identified and not started.
- `IN_PROGRESS`: active execution.
- `VERIFIED`: evidence satisfies the acceptance criteria but the task remains part of a larger gate.
- `DONE`: acceptance criteria are satisfied and evidence is recorded.
- `BLOCKED`: required external authorization, secret or administration is unavailable.
- `FAILED`: execution produced an error and requires correction.

Never convert `BLOCKED` or `FAILED` to `DONE` without new evidence.

## 5. Evidence contract

Evidence must identify:

- canonical branch and commit SHA;
- execution/run identifier when applicable;
- timestamp/freshness;
- operation mode (`READ_ONLY` or explicitly authorized controlled mutation);
- write count and mutation flag;
- source/provenance;
- result (`PASS`, `REVIEW_REQUIRED`, `BLOCKED`, or `FAILED`);
- failure details where applicable.

Repository documentation is not a substitute for fresh external evidence.

## 6. Safety invariants

1. `PRODUCTION_WRITE=DISABLED` until all production gates pass and explicit authorization exists.
2. `ROAPP_API_KEY` is never committed, printed, copied into issues, or placed in artifacts.
3. Pull requests must not receive production secrets through untrusted execution paths.
4. No undocumented API endpoint or guessed identifier becomes a contract.
5. No production mutation is performed merely to make CI green.
6. Existing verified backup/restore evidence is not repeatedly reopened unless a change invalidates it.

## 7. Multi-agent execution model

Multi-agent work is subordinate to the control plane, not a second control plane:

- **Planner:** decomposes the task and dependencies.
- **Executor:** makes the smallest safe change.
- **Verifier:** checks implementation and evidence independently.
- **Security gate:** checks secrets, permissions and mutation boundaries.
- **Controller:** decides `DONE`, `BLOCKED` or `FAILED` from evidence.

Agents must not override safety invariants or invent missing evidence.

## 8. Drift control

The canonical branch is `main-MARSEL-ROAPP`. Feature, audit, backup and historical branches are non-canonical. Work may be developed elsewhere, but only verified changes become canonical. Branch deletion is an administration operation and must not be simulated by the connector.

## 9. Current unresolved external gates

The current project control record remains authoritative for unresolved external gates, including credential remediation, fresh RO App evidence, Wix reconciliation, official MCP authorization, Gmail authorization, production deployment configuration and GitHub account-level administration. These are not closed by this document.
