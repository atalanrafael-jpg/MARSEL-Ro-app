# MARSEL / ROAPP Product Roadmap Kanban

Updated: 2026-08-16

## 🔴 AT RISK
- [ ] Complete API/entity coverage and safety gates (#30)
  - Resolve 7 unverified API entities
  - Prove backup/restore readiness
  - Review 11 product-code collision groups without automatic deletion
  - Verify Gmail OAuth with a live read test
  - Verify official RO App MCP authorization
  - Keep production writes disabled until all applicable safety gates pass
- [ ] Production go-live (#19) — blocked until safety gates pass

## 🟡 UP NEXT
1. Run canonical READ-ONLY API inventory.
2. Run data-quality audit.
3. Run entity audit for the 7 unresolved entities.
4. Run product-code collision review.
5. Evaluate unified safety/quality gates.
6. Publish evidence artifact and update roadmap.

## 🟢 VERIFIED BASELINE
- Live RO App GET/read-only access is working.
- Production writes remain disabled.
- Unified Control Plane workflow exists and runs on pushes to `main`.

## 🚫 SAFETY RULE
No production WRITE operations or automatic deletion are permitted by this roadmap.
