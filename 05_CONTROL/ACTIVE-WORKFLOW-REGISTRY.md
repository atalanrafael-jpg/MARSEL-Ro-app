# MARSEL ROAPP — ACTIVE WORKFLOW REGISTRY

## Canonical
- `marsel-unified-control-plane.yml` — one canonical READ-ONLY ROAPP audit/evidence path.
- `marsel-production-gate.yml` — fail-closed production gate.
- `marsel-release-readiness.yml` — release evidence gate.
- `marsel-backup-evidence-producer.yml` — backup evidence producer from verified read-only UCP evidence.
- `test.yml` — engineering tests.
- `codeql.yml` — security analysis.
- `marsel-secret-guard.yml` — secret boundary.
- `marsel-roapp-api-v2-guard.yml` — API safety guard.
- `mcp-production.yml` — MCP readiness.

## Consolidation rule
Supporting workflows may exist only when they have a distinct responsibility. No workflow may create a second canonical live ROAPP audit path.

## Safety
All ROAPP live access is READ-ONLY. Production WRITE remains disabled. Evidence must be real, complete and traceable; gates remain fail-closed.
