# MARSEL / ROAPP — CURRENT STATE — 2026-08-24

## Canonical system

- Repository: `atalanrafael-jpg/MARSEL-Ro-app`.
- `main` is the canonical production source branch.
- MARSEL and ROAPP are one system.
- `.github/workflows/marsel-unified-control-plane.yml` is the single live RO App audit control plane.

## Safety

- RO App production WRITE is disabled.
- Canonical live auditing is READ-ONLY.
- Parameterized identifiers are never guessed.
- Incomplete evidence must result in `REVIEW_REQUIRED`, never a false `PASS`.
- Historical snapshots do not override current evidence.

## Canonical audit components

The ACTIVE execution set is defined by `.github/workflows/marsel-unified-control-plane.yml` on `main`:

- API inventory: `scripts/marsel_api_inventory_v20_32.py`.
- Data quality: `scripts/marsel_data_quality_v22_readonly.py`.
- Entity audit: `scripts/marsel_entity_audit_v20_35.py`.
- Product-code review: `scripts/marsel_product_code_collision_audit_v22_3.py`.
- Warehouse contract: `scripts/marsel_warehouse_contract_v20_47.py`.
- Structural self-check: `scripts/marsel_canonical_self_check.py`.

Required internal API inventory dependencies remain `v20_31` and `v20_29` until their dependency chain is refactored and reverified.

## Current verification status

This document is a repository-state record. It does not claim that the latest live RO App audit has passed.

The following require fresh live evidence before being marked VERIFIED:

1. complete RO App entity/API coverage;
2. production backup plus successful restore test;
3. complete warehouse contract coverage;
4. live Gmail OAuth authorization and mailbox smoke test;
5. direct official RO App MCP authorization in the current ChatGPT environment;
6. current classification/reconciliation of product-code review groups.

These are blockers to production WRITE, not reasons to guess or force a PASS.

## Archive

Superseded dated snapshots, old control documents and historical changelogs are stored in `старые данные/` and are not active configuration.
