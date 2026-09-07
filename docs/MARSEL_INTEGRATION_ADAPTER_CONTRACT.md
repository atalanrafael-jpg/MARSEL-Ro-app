# MARSEL ROAPP — Integration Adapter Contract

**Status:** v1.0 — READ/sandbox baseline

## Adapter boundary

Website, marketplaces, payments and social-commerce channels integrate through MARSEL ROAPP. They must not directly mutate the RO App operational system.

Each adapter implements a provider-specific contract behind a common boundary.

## Required capabilities

- `read()` — retrieve provider state
- `normalize()` — convert provider payload to canonical representation
- `validate()` — enforce contract and required fields
- `map_identity()` — map canonical and external IDs
- `reconcile()` — compare provider and operational state
- `write()` — provider mutation, disabled unless its explicit gate is passed

## Provider controls

Each adapter must declare:

- provider name/version
- supported entities
- READ capability
- WRITE capability
- sandbox availability
- rate limits
- retry policy
- idempotency support
- reconciliation strategy
- audit event type
- credential reference name (never the secret value)

## Standard lifecycle

`READ → NORMALIZE → VALIDATE → MAP → IDEMPOTENCY CHECK → WRITE (gated) → RECONCILE → AUDIT`

## Safety

Default state is READ-only. Provider credentials must be stored outside source control. No adapter may silently fall back from failed reconciliation to destructive correction.

## Initial adapter roadmap

1. RO App — operational connector; verify live contract first.
2. Website — catalog/order projection.
3. Marketplace — listing, stock and order synchronization.
4. Payment — payment status and webhook reconciliation.
5. Social commerce — lead/order attribution and channel reconciliation.

Implementation must begin with READ/sandbox probes and contract tests. Production WRITE remains blocked until the global production gate and provider-specific gate both pass.
