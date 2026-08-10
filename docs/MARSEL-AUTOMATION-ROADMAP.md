# MARSEL Automation Roadmap

## Objective
Maximize useful automation while preserving financial, inventory and operational integrity.

## Layer 1 — Observe
- Scheduled Ro App read-only API inventory.
- Scheduled data-quality audit.
- Wix catalog/forms/order monitoring.
- SHA-256 integrity artifacts.

## Layer 2 — Understand
- Normalize records by stable external IDs.
- Detect duplicates and missing required fields.
- Produce Wix↔Ro App reconciliation reports.
- Classify anomalies by severity.

## Layer 3 — Decide
- AI-assisted summaries and prioritization.
- Margin/product/service analysis.
- SEO/content recommendations.
- Customer and order triage.
- Never treat generated AI values as authoritative accounting data.

## Layer 4 — Act safely
- Dry-run diffs first.
- Idempotent writes only.
- No deletes by default.
- Small controlled writes.
- Verify every mutation.
- Automatic rollback procedure where the API supports it.

## Layer 5 — Continuous improvement
- Measure sync failures and data drift.
- Re-run audits after changes.
- Open GitHub issues for unresolved defects.
- Promote changes only after CI safety gates pass.

## Priority backlog
1. Confirm live RO App API credentials and documented writable endpoints in deployment runtime.
2. Generate a complete permitted backup/export.
3. Build Wix↔Ro App field mapping from actual schemas.
4. Implement dry-run reconciliation.
5. Add controlled write adapter.
6. Add scheduled reconciliation and alerts.
7. Add analytics/AI decision layer.
