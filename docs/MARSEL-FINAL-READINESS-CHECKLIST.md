# MARSEL — Final Readiness Checklist

## Confirmed
- [x] RO App API live read-only access from GitHub Actions.
- [x] Automated Python tests pass in the latest verified run.
- [x] Orders audit passes.
- [x] Order schema audit passes.
- [x] Master audit passes.
- [x] API inventory passes.
- [x] Audit artifacts are published with SHA-256 evidence.
- [x] Production mutation remains disabled.
- [x] API client now enforces the configured 3 requests/second ceiling.

## Required before production WRITE
- [ ] Full permitted entity inventory at current API state.
- [ ] Full backup/export of every writable entity supported by the API.
- [ ] Restore procedure tested on a non-production copy or equivalent safe environment.
- [ ] Wix↔Ro App stable-ID mapping validated against live schemas.
- [ ] Dry-run reconciliation produces zero unexpected destructive operations.
- [ ] Idempotency verified for every write endpoint.
- [ ] Small controlled write test and read-back verification.
- [ ] Rollback procedure validated for each mutation class.
- [ ] Alerts/monitoring enabled for failed syncs and data drift.

## Recommended improvements
1. Keep separate READ, PROPOSE and APPLY credentials/policies.
2. Add a dead-letter queue for failed sync events.
3. Add correlation IDs and immutable audit logs for every mutation.
4. Add contract tests against recorded API fixtures so CI does not depend only on live API behavior.
5. Add schema-drift detection for RO App and Wix payloads.
6. Add reconciliation dashboards: products, services, orders, customers, stock and financial totals.
7. Add anomaly thresholds before any automated action.
8. Require human approval for financial, stock, customer and destructive changes.
9. Add secret rotation and environment separation for staging/production.
10. Keep AI in advisory/transformational roles; authoritative financial and inventory values must come from source systems.
