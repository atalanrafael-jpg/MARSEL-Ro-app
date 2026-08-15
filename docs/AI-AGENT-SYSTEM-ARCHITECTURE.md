# MARSEL — AI Agent System Architecture

Date: 2026-08-15
Status: DESIGN + READ-ONLY IMPLEMENTATION PLAN

## Objective

Create a coordinated multi-agent system for MARSEL, Ro App and GitHub/Codex that can inspect, plan, execute permitted actions, verify results, and stop safely when a required capability or authorization is missing.

## Agent roles

1. **Orchestrator** — receives the task, resolves dependencies, delegates work, tracks state and completion criteria.
2. **Ro App Auditor** — inventories API capabilities, audits data quality, detects duplicates/missing references and maintains the verification ledger.
3. **MARSEL Operations Agent** — models workshop workflows, services, products, clients, warehouses, costing and operational KPIs without changing production unless the write gate is unlocked.
4. **GitHub/Codex Agent** — inspects code, proposes changes, runs tests and prepares pull requests.
5. **Security Agent** — checks secrets, authentication boundaries, dependency risks, prompt-injection risks and excessive permissions.
6. **Data Agent** — validates schemas, IDs, referential integrity, backup/hash requirements and before/after datasets.
7. **QA Agent** — runs regression tests and independently verifies claimed fixes.
8. **Research Agent** — verifies external facts against current authoritative documentation before they are used in implementation decisions.
9. **Automation Agent** — schedules repeatable audits and reports only verified state.
10. **Reporting Agent** — produces a concise status: DONE / VERIFIED / BLOCKED / ACTION REQUIRED.

## Control loop

`INTAKE → CONTEXT → PLAN → READ/RESEARCH → CHANGESET → APPROVAL GATE → APPLY (only when authorized) → RE-READ → QA → AUDIT → REPORT`

Every mutation must have an explicit allow-list, exact target IDs, before/after values, rollback path and post-change verification.

## Current Ro App restriction

The existing project documentation states that live Ro App access is currently blocked by `403 subscription expired`. Therefore the agent system must remain read-only/offline for production Ro App mutations until access is restored and all write-gate requirements are independently verified.

## Safety gates

- No invented API fields, IDs, permissions or production state.
- No automatic deletion, merging or bulk mutation.
- Secrets must remain outside source files and artifacts.
- High-impact actions require explicit human approval.
- Failed verification stops the workflow rather than being treated as success.

## Verification standard

A task is not marked complete merely because code was changed. Completion requires an observable test, re-read or independent verification appropriate to the task.

## Initial automation backlog

- Unified agent task registry.
- Daily read-only Ro App/API health audit.
- GitHub repository/CI health audit.
- Secret exposure scan.
- API verification ledger synchronization.
- Regression-test execution and failure classification.
- MASTER status report aggregating Ro App + MARSEL + GitHub.
- Escalation when a gate changes from BLOCKED to actionable.
