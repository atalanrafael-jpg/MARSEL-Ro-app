# MARSEL / ROAPP — CANONICAL STRUCTURE

> Historical document normalized on 2026-09-02. Current truth is the latest `main` state and `docs/MARSEL-UNIFIED-MASTER-2026-09-02.md`.

## 1. Unified system

`MARSEL` and `ROAPP` are one system and one source-of-truth chain.

- MARSEL — business contour.
- ROAPP — technical contour: API, data, integrations, automation, MCP and CI/CD.
- Canonical repository: `atalanrafael-jpg/MARSEL-Ro-app`.
- Canonical branch: `main`.
- Historical material: `старые данные/`.

## 2. Canonical live audit

`.github/workflows/marsel-unified-control-plane.yml` is the single canonical live RO App audit path.

Order:

1. canonical structure self-check;
2. secret/configuration checks;
3. API inventory — READ ONLY;
4. data quality — READ ONLY;
5. entity audit — READ ONLY;
6. product-code collision review — READ ONLY/advisory;
7. warehouse contract audit — READ ONLY;
8. unified safety/quality gate;
9. evidence artifact.

Other workflows may perform distinct engineering, security, MCP, evidence or production-gate responsibilities, but must not create a second independent live RO App audit path.

## 3. Active runtime components

The active set is determined by the current workflow on `main`, not by historical filenames. Current documented components include:

- `scripts/marsel_canonical_self_check.py`
- `scripts/marsel_api_inventory_v20_32.py`
- `scripts/marsel_data_quality_v22_readonly.py`
- `scripts/marsel_entity_audit_v20_35.py`
- `scripts/marsel_product_code_collision_audit_v22_3.py`
- `scripts/marsel_warehouse_contract_v20_47.py`
- `scripts/marsel_api_v2_probe_v1.py`
- `scripts/marsel_api_v2_canonical_registry_v1.py`

Internal dependencies with older version numbers remain active until their dependency chain is refactored and verified. Version number alone is not grounds for deletion.

## 4. Repository structure

```text
MARSEL-Ro-app/
├── app/
├── ai_service/
├── config/
├── data/
├── docs/
├── scripts/
├── tests/
├── javascript/
├── typescript/
├── python/
├── 02_ROAPP/CONTROL/
├── .agents/
├── .github/workflows/
├── plugins/
├── старые данные/
└── requirements.txt
```

## 5. CI/CD classification

- `marsel-unified-control-plane.yml` — canonical live RO App audit.
- `marsel-production-gate.yml` — fail-closed production gate.
- `marsel-evidence-orchestrator.yml` — evidence orchestration.
- `marsel-integration-health.yml` — integration health.
- `marsel-live-probes.yml` — supporting live probes.
- `marsel-secret-guard.yml` — security/secret checks.
- `mcp-production.yml` — MCP-specific engineering checks.
- `codeql.yml` — code security.
- `language-quality.yml` — quality checks.
- `test.yml` — general engineering tests; not the canonical live audit.

Every workflow must have one documented responsibility in `02_ROAPP/CONTROL/ACTIVE-WORKFLOW-REGISTRY.md`.

## 6. Safety invariants

The canonical live audit must preserve:

- `WRITE_REQUESTS_MADE=0`;
- `RO_APP_DATA_MUTATED=false`;
- `identifiers_guessed=false`;
- no POST/PUT/PATCH/DELETE in live audit paths;
- incomplete/conflicting evidence = `REVIEW_REQUIRED`;
- secrets absent from source, documentation, logs and artifacts;
- current `main` evidence takes precedence over historical runs.

## 7. Archive policy

`старые данные/` contains historical snapshots and superseded implementations. They are not active configuration.

A file is moved to archive only after dependency checks across workflows, tests, runtime imports, scripts and documentation. Historical Git history and evidence are preserved.

## 8. Production readiness

Production WRITE is disabled until direct evidence exists for:

`backup/export → restore integrity → schema reconciliation → full READ-ONLY inventory → duplicate/orphan/reference analysis → dry-run → idempotency → rollback → controlled write → post-write verification`.

A green CI run or existing code is not sufficient evidence of production readiness.

## 9. Current verdict

`REVIEW_REQUIRED / NO-GO FOR PRODUCTION WRITE`

Use `docs/MARSEL-UNIFIED-MASTER-2026-09-02.md` for the current priority order and remaining gates.
