# MARSEL Production Go-Live Gates

Status: CONTROLLED / NO PRODUCTION WRITE ENABLED

## Mandatory gates
- [x] Read-only API connectivity verified in CI.
- [x] Automated tests pass in the latest verified run.
- [x] Read-only inventory and data-quality audits exist.
- [x] Rate-limit retry/throttling controls exist.
- [x] Secrets are supplied through environment/CI secrets.
- [ ] Complete permitted backup/export of all writable Ro App entities.
- [ ] Restore test from that backup.
- [ ] Live Wix ↔ Ro App schema mapping using current API responses.
- [ ] Reconciliation report with zero unexplained critical conflicts.
- [ ] Dry-run of every planned mutation.
- [ ] Idempotency keys / deterministic external IDs for every mutation path.
- [ ] Explicit rollback strategy for every mutation type.
- [ ] Test write in an isolated/test record or otherwise reversible scope.
- [ ] Post-write GET verification.
- [ ] Production write permission granted explicitly.

## Recommended enhancements
1. Separate service credentials for READ, PROPOSE and APPLY.
2. Add a persistent synchronization ledger with source_id, target_id, operation, correlation_id and result.
3. Add dead-letter handling for failed records.
4. Add schema-drift detection and alerting.
5. Add reconciliation metrics and scheduled reports.
6. Add branch protection and mandatory CI before production changes.
7. Keep financial, inventory and accounting fields outside autonomous AI writes.
8. Add anomaly thresholds for unusually large price, stock, cost or order changes.

## Go-live rule
A production write must not be enabled merely because API connectivity works. All mandatory gates above must pass, with evidence stored as CI artifacts or auditable records.
