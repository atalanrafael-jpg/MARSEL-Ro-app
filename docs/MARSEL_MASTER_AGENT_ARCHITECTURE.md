# MARSEL ROAPP MASTER AGENT — ARCHITECTURE

**Status:** IMPLEMENTATION IN PROGRESS  
**Mode:** READ-ONLY by default  
**Production WRITE:** BLOCKED

## 1. Canonical identity

- Project: **MARSEL ROAPP**
- MARSEL: business contour
- ROAPP: technology contour
- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Canonical branch: `main`

## 2. Agent topology

```text
                         MARSEL ROAPP MASTER AGENT
                                  |
                         MASTER ORCHESTRATOR
                                  |
        +-------------------------+-------------------------+
        |                         |                         |
      AUDIT                    SECURITY                 API / MCP
        |                         |                         |
      DATA / ERP              REPAIR                  AUTOMATION
        |                         |                         |
 BUSINESS / FINANCE       EVIDENCE / LOGGING       CI / CD / GATES
```

The modules are logical capabilities under one control plane, not independent project sources of truth.

## 3. Mandatory execution pipeline

```text
REQUEST
  -> VALIDATE
  -> READ
  -> ANALYZE
  -> BACKUP/RESTORE CHECK
  -> DRY-RUN
  -> SAFETY GATE
  -> WRITE (only when explicitly permitted)
  -> VERIFY
  -> LOG
  -> CHECKPOINT
```

A step may stop the pipeline. Fail-closed behavior is required for missing evidence, conflicting state, unsafe scope, or unavailable rollback.

## 4. Operating modes

| Mode | Default | Production mutation |
|---|---|---|
| READ_ONLY | YES | No |
| DRY_RUN | No | No |
| PROPOSE | No | No |
| WRITE | No | Blocked until gates pass |
| EMERGENCY | No | Not implemented by this architecture |

## 5. Module responsibilities

### MASTER / ORCHESTRATOR
Routes requests, selects modules, enforces ordering, maintains checkpoint and task state.

### AUDIT
Performs read-only inspections, anomaly detection, duplicate detection and evidence collection.

### SECURITY
Checks credentials handling, authorization boundaries, secrets exposure, destructive-operation restrictions and fail-closed conditions.

### API / MCP
Uses only verified contracts. Never invents endpoints, schemas, permissions or tool capabilities.

### DATA / ERP
Analyzes products, materials, inventory, orders, references, consistency and reconciliation requirements.

### REPAIR
Handles jewelry and watch-repair workflow requirements without changing production data unless the production gate explicitly permits it.

### BUSINESS / FINANCE
Analyzes business workflows, costs, revenue and operational data while preserving the rule that AI is not the accounting source of truth.

### AUTOMATION
Coordinates GitHub Actions and other approved automation while preserving the production gate.

## 6. Evidence model

Every material action must produce or reference evidence sufficient to determine:

- what was requested;
- what was actually executed;
- against which version/commit;
- which source/API was used;
- what changed;
- what verification succeeded or failed;
- what remains `NOT_VERIFIED`.

`DONE` is prohibited without direct evidence.

## 7. Safety invariants

1. No mass write without an approved production gate.
2. No deletion through the agent by default.
3. No secret values in source code, logs or evidence.
4. READ-only evidence cannot be presented as WRITE evidence.
5. Historical documents cannot override newer verified state.
6. A successful CI run is not proof of production synchronization.
7. Unknown or conflicting state causes a safe stop.

## 8. Current boundary

This architecture defines the Master Agent control plane. It does not claim that a Custom GPT has been physically created, nor that production write access is active.
