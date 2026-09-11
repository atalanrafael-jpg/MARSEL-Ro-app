# MARSEL ROAPP — ACTIVE SCRIPT REGISTRY

**Authority:** `.github/workflows/marsel-unified-control-plane.yml` plus verified import/dependency graph.

## Canonical active entrypoints
- `scripts/marsel_canonical_self_check.py`
- `scripts/marsel_api_inventory_v20_32.py`
- `scripts/marsel_data_quality_v22_readonly.py`
- `scripts/marsel_entity_audit_v20_35.py`
- `scripts/marsel_product_code_collision_audit_v22_3.py`
- `scripts/marsel_warehouse_contract_v20_48.py`

## Required internal dependencies
- `scripts/marsel_api_inventory_v20_31.py`
- `scripts/marsel_api_inventory_v20_29.py`

These versioned files are currently retained because the active inventory implementation imports them. They are not independent canonical entrypoints. The next refactor should collapse this dependency chain into one canonical inventory module before removal.

## Supporting active controls
- `scripts/marsel_api_v2_canonical_registry_v1.py`
- `scripts/marsel_api_v2_probe_v1.py`
- `scripts/marsel_backup_evidence_v1.py`
- `scripts/marsel_full_readonly_backup_v1.py`
- `scripts/marsel_release_readiness_v1.py`
- `scripts/marsel_production_gate_v1.py`
- `scripts/marsel_roapp_api_v2_guard.py`
- `scripts/marsel_evidence_builder_v1.py`
- `scripts/marsel_evidence_intake_v1.py`
- `scripts/marsel_integration_health_v1.py`
- `scripts/marsel_live_probe_v1.py`

## Rule
Version numbers do not create separate systems. A capability must have one active entrypoint; historical implementations are archived only after dependency and test verification.
