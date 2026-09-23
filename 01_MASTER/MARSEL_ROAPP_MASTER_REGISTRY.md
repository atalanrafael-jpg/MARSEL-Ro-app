# MARSEL ROAPP — MASTER REGISTRY

**Status:** CANONICAL

| Domain | Canonical location | Rule |
|---|---|---|
| Project control | `01_MASTER/` | Single authority |
| Business | `02_MARSEL/` | MARSEL business contour |
| Technical | `03_ROAPP/` | ROAPP technical/data contour |
| Development | `04_DEVELOPMENT/` | GitHub/code/CI/tests/AI/MCP |
| Control | `05_CONTROL/` | QA/security/backup/gates |
| History | `06_ARCHIVE/` | Non-active historical material |

## Canonical integration
- ROAPP API: READ-ONLY.
- ROAPP MCP: READ-ONLY boundary.
- Production WRITE: disabled.
- GitHub: canonical repository; current canonical branch is `main`.
- `main` is the technical canonical branch.
- Unified Control Plane: canonical control workflow.
- Release readiness: fail-closed.

## Registry rule
No document, script, workflow, project name, or versioned implementation outside this registry may become authoritative merely by existing in the repository.
