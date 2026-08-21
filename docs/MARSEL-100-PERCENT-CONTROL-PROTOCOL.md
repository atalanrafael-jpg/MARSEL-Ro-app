# MARSEL — 100% CONTROL PROTOCOL

## Purpose
This document is the operational instruction for future agents, developers and operators working on the MARSEL/ROAPP project.

## Non-negotiable rules
1. `main` is canonical unless a documented release branch is explicitly designated.
2. MARSEL + ROAPP are treated as one system.
3. Existing canonical implementation wins over another versioned implementation.
4. Never infer completion from a commit alone.
5. Never infer API capability from a URL, documentation title or naming convention.
6. Live operations are READ-ONLY by default.
7. Never discover API identifiers by writing to production.
8. Secrets never enter source, docs, logs, test output or artifacts.
9. Every production write requires explicit safety gates.
10. Every change requires post-change verification.

## Required task lifecycle

### Phase 0 — Context
- recover the latest confirmed checkpoint;
- identify current HEAD;
- identify active workflows;
- identify open PRs/issues relevant to the task;
- read canonical project controls.

### Phase 1 — Inventory
- enumerate relevant files;
- map imports and runtime dependencies;
- map workflow references;
- map tests to active modules;
- distinguish active code from historical/archive code.

### Phase 2 — Design
Produce a minimal canonical change. Do not create a new version merely because an old version exists.

### Phase 3 — Static verification
Check imports, syntax, path references, configuration, secret exposure and test discovery.

### Phase 4 — Runtime verification
Run the relevant test suite. For CI, require an actual GitHub Actions result. `statuses: []` is not PASS.

### Phase 5 — Evidence
Every test workflow must preserve machine-readable and human-readable evidence on both success and failure. Evidence must not contain credentials or personal data.

### Phase 6 — Data safety
For ROAPP: READ-ONLY inventory → contract verification → dry-run → reconciliation → idempotency → controlled write → post-write verification → rollback verification.

### Phase 7 — Reconciliation
Compare expected architecture, active registry, workflow registry, implementation, tests and documentation. Record every unresolved gap.

### Phase 8 — Release gate
A release is READY only if:
- CI is PASS;
- required artifacts exist;
- no unresolved blocking test failures exist;
- active dependency graph is consistent;
- security checks pass;
- live API claims are evidence-backed;
- data mutation status is explicitly known;
- documentation matches implementation.

## Evidence states
Use only these states:
- `PASS` — directly verified.
- `FAIL` — directly verified failure.
- `REVIEW_REQUIRED` — evidence insufficient or contradictory.
- `NOT_RUN` — no execution performed.
- `BLOCKED` — execution prevented by a prerequisite.

Never convert `REVIEW_REQUIRED`, `NOT_RUN` or `BLOCKED` into PASS.

## Architecture
```text
MARSEL BUSINESS
├── Customers
├── Orders
├── Master Catalog
├── Manufacturing
├── Jewelry Repair
├── Watch Repair
├── Materials & Stones
├── Warehouse
├── Sales & Payments
├── E-commerce / Marketplace
├── Marketing
└── Analytics

TECHNICAL CONTROL PLANE
├── API inventory
├── Data quality
├── Reference integrity
├── Product-code collision audit
├── Warehouse contract
├── MCP/security controls
├── CI/CD
├── Evidence artifacts
└── Release gates
```

## Business operating principle
Every business process must have: owner, input, state transition, output, accounting effect, quality control, audit trail and recovery path.

## Automation principle
Automate observation first, then recommendations, then reversible low-risk operations. High-impact mutations remain gated until evidence proves correctness.

## Final acceptance
The project is never described as "100% complete" merely because the repository contains documentation. 100% means all defined gates have a current evidence record and no known blocking gap remains. If a gate has not been verified, report it explicitly.
