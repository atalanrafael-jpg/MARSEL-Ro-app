# MARSEL ROAPP — ACTIVE SCRIPT REGISTRY

**Authority:** `.github/workflows/marsel-unified-control-plane.yml` plus verified import/dependency graph.

## Canonical active entrypoints
- `scripts/marsel_canonical_self_check.py`
- `scripts/marsel_api_inventory_v20_32.py`
- `scripts/marsel_data_quality_v22_readonly.py`
- `scripts/marsel_entity_audit_v20_35.py`
- `scripts/marsel_product_code_collision_audit_v22_3.py`
- `scripts/marsel_warehouse_contract_v20_48.py`

## Rule
Version numbers do not create separate systems. A capability must have one active entrypoint; historical implementations are archived only after dependency and test verification.
