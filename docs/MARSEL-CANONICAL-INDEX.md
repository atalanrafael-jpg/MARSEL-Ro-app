# MARSEL ROAPP — CANONICAL INDEX

**Status:** CANONICAL CONTROL INDEX  
**Repository:** `atalanrafael-jpg/MARSEL-Ro-app`  
**Branch:** `main`

## Rule
There is one MARSEL ROAPP project. This index defines which documents and controls are authoritative. Historical or superseded material is not a second source of truth.

## Source-of-truth map

| Area | Canonical source | Role |
|---|---|---|
| Project core | `MARSEL_ROAPP_MASTER_CORE.md` | Permanent governance and operating principles |
| Current unified state | `docs/MARSEL-UNIFIED-MASTER-2026-09-02.md` | Current project state, gates and priorities |
| Repository governance | `docs/MARSEL_ROAPP_CANONICAL_GOVERNANCE.md` | Canonical repository/control-plane rules |
| Task control | `docs/MARSEL_ROAPP_TASK_REGISTRY.md` | Active task registry |
| Workflow control | `docs/MARSEL_ROAPP_WORKFLOW_REGISTRY.md` | Active workflow responsibilities |
| Script control | `02_ROAPP/CONTROL/ACTIVE-SCRIPT-REGISTRY.md` | Active script registry |
| Integration control | `docs/MARSEL_EXTERNAL_INTEGRATION_REGISTRY.md` | External integration boundary |
| API control | `docs/MARSEL-API-REGISTRY.md` | API registry |
| MCP control | `docs/ROAPP_MCP_CONTRACT.md` | MCP contract |
| Data quality | `docs/MARSEL_DATA...` / current data-quality evidence | Data-quality controls; use newest verified evidence |
| Production gate | `docs/MARSEL-PRODUCTION-GO-LIVE-GATES.md` + `.github/workflows/marsel-production-gate.yml` | Release/write gate |
| Evidence | `evidence/` | Run-specific evidence only; never synthetic current truth |
| Historical | `старые данные/` | Archive/context only |

## Cleanup decisions

The following redundant active files were removed from the cleanup branch because they were superseded and had no repository references:

- root `CODEOWNERS` — ineffective duplicate; `.github/CODEOWNERS` is the active GitHub location;
- `docs/MARSEL-CURRENT-STATE-2026-08-21.md` — superseded current-state snapshot;
- `docs/MARSEL-MASTER-REGISTER-V2.md` — superseded master register.

Historical material remains preserved in `старые данные/` and is not deleted merely because it is old.

## Duplicate-control rule

Before creating a new document, script, workflow or registry:

1. search this index and the repository;
2. identify the existing owner of the responsibility;
3. extend the canonical artifact instead of creating a parallel implementation;
4. if replacement is necessary, mark the old artifact superseded and preserve traceability;
5. run CI and the relevant production/control gate before promotion.

## System shape

`MARSEL business` → `ROAPP technical layer` → `GitHub main` → `Actions / evidence / gates`.

Supporting components are allowed only when their responsibility is distinct, registered and non-duplicative.

## Safety

`READ_ONLY` remains the default. Production WRITE remains blocked until the current production gates contain fresh direct evidence.
