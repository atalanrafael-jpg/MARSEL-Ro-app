# MARSEL ROAPP MASTER AGENT CONTROL PLANE

## Status
PROPOSED IMPLEMENTATION / READ-ONLY DEFAULT

## Purpose
The Master Agent coordinates MARSEL business workflows and ROAPP technical workflows without granting unrestricted production access.

## Operating contract
`REQUEST → VALIDATE → READ → ANALYZE → PLAN → DRY-RUN → SAFETY GATE → WRITE (only when separately authorized) → VERIFY → LOG → CHECKPOINT`

## Internal roles
- Master/Orchestrator
- Audit
- Security
- API/MCP
- Data/ERP
- Repair
- Business/Finance
- Automation

## Permission model
Default: READ_ONLY.

The agent may:
- inspect repository state;
- inspect approved API evidence;
- analyze data and generate reports;
- prepare dry-runs and proposed changes.

The agent may not:
- mutate RO App production data by default;
- delete records automatically;
- guess endpoints, identifiers, schemas, or credentials;
- claim verification without evidence.

## Tool routing
Each tool call must declare:
- purpose;
- data scope;
- requested permission;
- expected evidence.

## Safety invariants
`write_requests_made == 0` and `ro_app_data_mutated == false` remain mandatory for READ-ONLY runs.

## Production gate
WRITE remains blocked until backup/export, restore, reconciliation, dry-run, idempotency, rollback and post-write verification are evidenced.

## Evidence statuses
- VERIFIED
- PARTIAL
- FAILED
- BLOCKED
- NOT_VERIFIED
- PROPOSED

## Integration boundary
RO App API, MCP and GitHub remain external tools. Their capabilities are not inferred from names; each contract must be verified.

## Current checkpoint
This document establishes the canonical control contract for the agent layer. It does not itself activate production automation.
