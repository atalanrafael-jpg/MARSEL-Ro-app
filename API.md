# MARSEL ROAPP API

The API is part of the unified MARSEL ROAPP system. API inventory, entity verification and safety evidence are governed by the canonical unified control plane.

## Canonical sources

- API client: `app/roapp_client.py`
- Contract: `app/roapp_contract.py`
- API registry: `docs/MARSEL-API-REGISTRY.md`
- Verification ledger: `docs/MARSEL-ROAPP-API-VERIFICATION-LEDGER-V23.md`
- Unified CI: `.github/workflows/marsel-unified-control-plane.yml`

## Safety

Default audit mode is READ-ONLY. Production mutations require the production gate documented in `MARSEL_ROAPP_UNIFIED_SYSTEM.md`.
