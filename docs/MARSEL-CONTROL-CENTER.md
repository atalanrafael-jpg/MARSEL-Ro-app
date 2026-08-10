# MARSEL Control Center

## Purpose
Create one control plane for Wix, Ro App, OpenAI and GitHub without making AI the source of truth for accounting or inventory.

## Operating loop
OBSERVE -> VALIDATE -> RECONCILE -> DETECT ANOMALIES -> PRIORITIZE -> PROPOSE -> APPROVE/REJECT -> APPLY -> VERIFY -> AUDIT

## Autonomy policy
### Autonomous
- Read-only audits.
- Data-quality checks.
- Duplicate detection.
- Reconciliation reports.
- Content drafts.
- Non-destructive recommendations.

### Approval required
- Price/cost changes.
- Stock changes.
- Accounting/financial records.
- Customer deletion.
- Order deletion/cancellation with financial impact.
- Bulk writes.

### Prohibited by default
- Unreviewed destructive operations.
- AI-generated financial values becoming authoritative.
- Silent conflict resolution.

## Core components
- `app/sync_ledger.py`: auditable operation records and deterministic payload hashes.
- `app/anomaly_engine.py`: deterministic anomaly flags for missing required fields, negative values and unusually large values.
- Ro App client: read-only API access with throttling/retry controls.
- GitHub Actions: scheduled/triggered audit evidence.

## Next deployment gates
1. Persist the ledger in production storage.
2. Add current Wix schema mapping.
3. Generate a complete permitted Ro App backup and perform a restore test.
4. Add deterministic external IDs and idempotency keys to mutation adapters.
5. Add dry-run reconciliation.
6. Add reversible test writes and post-write GET verification.
7. Enable production WRITE only after all evidence is attached to the audit trail.
