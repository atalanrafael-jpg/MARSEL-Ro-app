---
title: MARSEL ROAPP
category:
  uri: documentation
excerpt: Canonical documentation entry point for the unified MARSEL ROAPP system.
hidden: false
---

# MARSEL ROAPP

**Ювелирная студия MARSEL** uses MARSEL ROAPP as one unified system: MARSEL is the business contour and ROAPP is the technical contour.

## Canonical repository

- GitHub: `atalanrafael-jpg/MARSEL-Ro-app`
- Canonical branch: `main`

## Operating model

`OBSERVE → MEASURE → FIND → FIX → TEST → VERIFY → DOCUMENT → MONITOR`

For RO App live work:

`INVENTORY → DATA QUALITY → ENTITY AUDIT → COLLISION REVIEW → WAREHOUSE CONTRACT → SAFETY GATE → EVIDENCE`

## Production safety

RO App live auditing is read-only by default. Production WRITE requires fresh evidence for backup/export, restore integrity, schema reconciliation, full read-only inventory, duplicate/orphan/reference analysis, dry-run, idempotency, rollback, controlled write, and post-write verification.

## Documentation source of truth

Repository documentation is the source-controlled content. ReadMe is the published documentation surface. Changes are validated in GitHub Actions and are published only from `main` when the `README_API_KEY` repository secret is configured.

## Evidence rule

`DONE` / `PASS` requires current direct evidence. `PLANNED`, `CODED`, `NOT_TESTED`, `ASSUMED`, `OLD_PASS`, and `UNVERIFIED` are not `PASS`.
