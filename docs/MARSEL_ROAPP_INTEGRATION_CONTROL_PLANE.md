# MARSEL ROAPP — Unified Integration Control Plane

## Purpose

This document defines the single integration architecture for MARSEL ROAPP.

- **MARSEL** = business contour: customers, jewelry, repairs, production, inventory, materials, finance, sales and marketing.
- **ROAPP** = technical contour: API, data, integrations, automation, MCP, webhooks and CI/CD.
- `atalanrafael-jpg/Ro-app` / `main` = canonical source and production control plane.

## Architecture

```text
                    MARSEL ROAPP CORE
                           |
             +-------------+-------------+
             |                           |
       RO App Public API v2          RO App MCP
             |                           |
             +-------------+-------------+
                           |
                 Integration Control Plane
                           |
      +----------+---------+---------+----------+
      |          |         |         |          |
   Catalog    Inventory  Orders   Webhooks   Analytics
      |          |         |         |          |
   Website   Marketplace  Social   Finance    AI/Agents
```

## Canonical rules

1. No parallel live MARSEL/ROAPP control planes.
2. No direct production writes from external systems without an approved synchronization contract.
3. Public API v2 is the target API for new integrations. The deprecated API must not be introduced into active source/configuration.
4. MCP is an AI/development integration layer; it does not replace production authorization or synchronization controls.
5. Webhooks are event inputs; handlers must be idempotent and auditable.
6. Inventory, orders and catalog synchronization must have explicit ownership and conflict rules before production writes.
7. Missing evidence produces `REVIEW_REQUIRED`, never `PASS`.
8. Production WRITE remains disabled until backup/restore, reconciliation, dry-run, idempotency and rollback evidence exists.

## Integration domains

| Domain | Canonical responsibility | Production state |
|---|---|---|
| Catalog | Products, services, bundles, categories, prices | API v2 contract required |
| Inventory | Stock and warehouse state | READ-ONLY until write gate |
| Orders | Orders, items, status and lifecycle | API v2 contract required |
| Invoices | Invoice lifecycle and items | API v2 contract required |
| Webhooks | Sales, bookings, invoices and other events | Idempotent handlers required |
| Website/e-commerce | Leads, catalog, orders | Connector contract required |
| Marketplace | Listings, stock, orders | Connector contract required |
| Social Commerce | Product/content/sales entry points | Connector contract required |
| AI/MCP | Documentation, analysis, development assistance | Authorization gate required |
| CI/CD | Tests, security, API-v2 guard, production gates | Required |
| Analytics | Sales, margin, inventory and operational metrics | Read-only source preferred |

## Synchronization contract

Every external connector must define:

- source of truth per entity;
- field mapping;
- create/update/delete semantics;
- event ordering;
- idempotency key;
- retry/backoff policy;
- duplicate handling;
- conflict resolution;
- audit trail;
- rollback procedure;
- dry-run mode;
- production approval gate.

## RO App capabilities used by this architecture

RO App documents Public API capabilities for third-party integrations, including website lead/work-order creation and synchronization of stock/product prices. RO App also documents Public API v2 catalog, invoice, order, employee and webhook capabilities. These capabilities must still be validated against the exact live account and endpoint contract before production activation.

## Current verified boundary

The repository contains the API-v2 fail-closed guard merged into `main`. This proves the repository-level control exists; it does **not** prove that live RO App MCP authorization, production backup/restore, warehouse completeness or production synchronization has been completed.

## Implementation order

1. API v2 canonical registry and client contract.
2. Webhook ingress with idempotency and audit storage.
3. Catalog synchronization in dry-run/read-only mode.
4. Inventory synchronization in dry-run/read-only mode.
5. Order/invoice synchronization in dry-run mode.
6. Website/marketplace/social connectors.
7. Analytics and reconciliation.
8. Production write gate only after direct evidence for backup, restore, reconciliation, rollback and post-write verification.

## Evidence standard

A CI success is repository evidence only. Live integration status requires fresh evidence from the actual RO App account/environment. No live authorization, production mutation, or successful synchronization may be reported without that evidence.
