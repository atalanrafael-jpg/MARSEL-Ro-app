# MARSEL ROAPP — Settings Baseline — 2026-09-04

## Purpose
Canonical, auditable baseline for repository/project settings that are verifiable from the repository and its CI configuration. This document does not claim account-level GitHub UI settings that are not exposed to the repository connector.

## Canonical configuration

- Repository: `atalanrafael-jpg/MARSEL-Ro-app`
- Canonical branch: `main`
- Canonical control plane: `.github/workflows/marsel-unified-control-plane.yml`
- Production gate: `.github/workflows/marsel-production-gate.yml`
- Default live mode: `READ_ONLY`
- Production WRITE: `DISABLED`
- Canonical RO App secret name: `ROAPP_API_KEY`
- RO App API base: `https://api.roapp.io/v2`

## Verified repository controls

- Unified control plane uses `contents: read`.
- Pull-request events do not receive `ROAPP_API_KEY`.
- Live RO App jobs run only outside pull-request events.
- Live audit jobs assert `write_requests_made == 0` and `ro_app_data_mutated == false`.
- Production gate sets `MARSEL_WRITE_APPROVED=false`.
- Production gate requires the unified evidence artifact and a fail-closed evidence inventory.
- Evidence is retained as GitHub Actions artifacts for 90 days.
- Canonical self-check rejects stale/forbidden live workflows, an empty canonical API registry, write methods in the read-only registry, missing canonical scripts, and missing production-safety markers.

## Current blockers — intentionally not auto-closed

1. Full backup/export evidence: `NOT VERIFIED`.
2. Independent restore/integrity evidence: `NOT VERIFIED`.
3. Warehouse-list official contract: `NOT VERIFIED` where documented `/v2/warehouse/` and live behavior disagree.
4. Full API/entity completeness: `REVIEW_REQUIRED` until authoritative coverage is directly evidenced.
5. Product-code collision findings require human review; no automatic delete/merge is authorized.
6. Gmail OAuth live user authorization: `NOT VERIFIED`.
7. Official RO App MCP authorization/tool discovery: `NOT VERIFIED`.
8. Credential-exposure remediation: `NOT VERIFIED` until direct rotation and history/log/artifact evidence exists.
9. Account-level GitHub ruleset, secret-scanning/push-protection and Copilot settings: require GitHub account UI/API verification not exposed by the repository connector.
10. ReadMe bi-directional sync: external setup remains pending.

## Change-control rule

A CI success is not equivalent to production readiness. A blocker may be closed only when its acceptance criteria have direct, fresh evidence. Historical reports are retained for traceability and never override newer evidence.

## Safety rule

No production write, deletion, mass mutation, credential reproduction, undocumented API promotion, or synthetic evidence is authorized by this baseline.
