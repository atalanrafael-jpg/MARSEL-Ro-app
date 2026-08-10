# MARSEL Synchronization Contract

## Source of truth
- Product/catalog publication: Wix.
- Operational orders, workshop services, materials and accounting records: Ro App.
- AI-generated text is never authoritative for financial or operational fields.

## Identity
Records must be matched using stable external IDs, not names alone.

## Conflict policy
- Never silently overwrite conflicting records.
- Financial quantities, prices, costs and stock require explicit source-of-truth rules.
- Deletions are disabled by default.
- Every write must be idempotent and auditable.

## Required audit fields
- source_system
- source_id
- target_id
- operation
- timestamp
- result
- request/correlation ID

## Rollout
DRY RUN -> TEST WRITE -> VERIFY -> ENABLE SCHEDULED SYNC.
