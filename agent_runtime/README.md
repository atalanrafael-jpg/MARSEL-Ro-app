# Master Agent Runtime

## Current safety level
READ_ONLY_DEFAULT

## Execution pipeline
`VALIDATE → AUTHORIZE → PLAN → DRY_RUN → SAFETY_GATE → VERIFY → EVIDENCE → CHECKPOINT`

## Components
- schema.py: task validation
- policy.py: permission decisions
- runtime.py: controlled task handling
- dry_run.py: non-mutating plan execution
- audit.py: evidence records
- checkpoint.py: checkpoint records

## Hard invariants
- No production write by default.
- No automatic delete.
- Unknown actions are rejected.
- Dry-run reports zero executed writes.
- Every future external adapter must be separately contract-verified.

## Adapter status
ROAPP: NOT_IMPLEMENTED / NOT_VERIFIED
GitHub: NOT_IMPLEMENTED
MCP: NOT_IMPLEMENTED
