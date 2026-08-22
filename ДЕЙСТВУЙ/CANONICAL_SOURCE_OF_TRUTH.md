# CANONICAL SOURCE OF TRUTH

## Scope
This document defines the authority hierarchy for the MARSEL / RO App unified project.

## Authority
1. Current HEAD of `act/marsel-unified-system-2026-08-22`.
2. Current files and tests in that HEAD.
3. CI evidence tied to that exact HEAD.
4. Fresh read-only live RO App evidence.
5. Current official RO App documentation.
6. Historical branches, commits, old CI runs and legacy documents — history only.

## Legacy policy
The existing `*_MASTER.md` and `*_CURRENT_STATE.md` files outside `ДЕЙСТВУЙ/` are not independent sources of truth. They must be classified before reuse: `KEEP`, `MERGE`, `ARCHIVE`, `REMOVE`, or `VERIFY`.

No historical content is promoted into the current system merely because it exists in the repository.

## Unified MARSEL domains
- `JEWELRY` — jewelry manufacture/repair.
- `WATCH` — watch repair/service.
- `EYEWEAR` — eyewear repair/service.

All domains share the same customer, service-order, object, diagnosis, estimate, work, materials/parts, quality-control, delivery, payment and warranty flow.

## Safety
Live RO App remains read-only unless a separate explicit write authorization and verified API contract exist.

## Completion rule
`PASS` requires current evidence. Old PASS, assumptions, code existence or documentation alone never establish PASS.
