# MARSEL ROAPP — CANONICAL INDEX

**Status:** CANONICAL CONTROL INDEX
**Repository:** `atalanrafael-jpg/MARSEL-Ro-app`
**Canonical branch:** `main`

## 1. One system

There is exactly one MARSEL ROAPP project/control plane. `MARSEL` is the business contour; `ROAPP` is the technology contour of the same system. No parallel project, repository, production audit path or duplicate source of truth is permitted.

## 2. Source-of-truth hierarchy

1. Current `main` repository state.
2. Current GitHub Actions evidence tied to that state.
3. Direct live RO App evidence with timestamps/artifacts.
4. Current authoritative RO App documentation.
5. Historical documents/chats/evidence only as context.

## 3. Canonical ownership map

| Responsibility | Canonical source |
|---|---|
| Permanent project principles | `MARSEL_ROAPP_MASTER_CORE.md` |
| Current project control, gates and blockers | `docs/PROJECT_MASTER_CONTROL.md` |
| Canonical architecture | `MARSEL_ROAPP_UNIFIED_SYSTEM.md` |
| Repository governance | `docs/MARSEL_ROAPP_CANONICAL_GOVERNANCE.md` |
| Task control | `docs/MARSEL_ROAPP_TASK_REGISTRY.md` |
| Workflow control | `docs/MARSEL_ROAPP_WORKFLOW_REGISTRY.md` |
| Script control | `02_ROAPP/CONTROL/ACTIVE-SCRIPT-REGISTRY.md` |
| External integrations | `docs/MARSEL_EXTERNAL_INTEGRATION_REGISTRY.md` |
| API registry | `docs/MARSEL-API-REGISTRY.md` |
| MCP contract | `docs/ROAPP_MCP_CONTRACT.md` |
| Data-quality controls | Current data-quality registry/evidence; newest verified evidence wins |
| Production gate | `docs/MARSEL-PRODUCTION-GO-LIVE-GATES.md` + `.github/workflows/marsel-production-gate.yml` |
| Live audit control plane | `.github/workflows/marsel-unified-control-plane.yml` |
| Run-specific evidence | `evidence/` |
| Historical material | `старые данные/` |

## 4. Canonical continuation rule

`PROJECT_MASTER_CONTROL.md` is the current operational checkpoint. It must be consulted before continuation. It contains the current gates, blockers and evidence precedence. The permanent Core and architecture documents define rules; they do not replace the current checkpoint.

## 5. Duplicate-control rule

Before creating or retaining a document, script, workflow, registry or integration:

1. search the repository for an existing responsibility owner;
2. identify whether the candidate duplicates an active artifact;
3. extend the canonical artifact instead of creating a parallel implementation;
4. if superseded, archive it and remove it from the active path only after dependency checks;
5. preserve Git history and traceability;
6. run the relevant CI/control gate before promotion.

Version numbers alone are not a deletion criterion. Dependencies, imports, workflow references, tests and documentation references must be checked first.

## 6. Active workflow rule

`docs/MARSEL_ROAPP_WORKFLOW_REGISTRY.md` is the single workflow registry. `.github/workflows/marsel-unified-control-plane.yml` is the single canonical live RO App audit path. Supporting workflows may exist only for distinct registered responsibilities and may not silently become a second live audit path.

## 7. Archive rule

`старые данные/` is historical context, not active configuration. Superseded files are archived only after dependency checks. Historical evidence and Git history are preserved.

## 8. Safety invariant

`READ_ONLY` is the default. Production WRITE remains disabled until current direct evidence closes all applicable safety gates:

`backup/export → restore → reconciliation → full READ-ONLY inventory → duplicate/reference analysis → dry-run → idempotency → rollback → safety gate → controlled write → post-write verification`

No guessed identifier, undocumented endpoint, synthetic evidence, mass deletion or production mutation may be promoted to PASS.

## 9. Current project status

Use `docs/PROJECT_MASTER_CONTROL.md` for the current verified blockers and gate status. Never infer current readiness from an older dated document.
