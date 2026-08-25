# MARSEL MASTER BOOTSTRAP

Date: 2026-08-24

## Purpose

Establish a fresh canonical control point for MARSEL / ROAPP without changing RO App production data.

## Canonical system

- Business contour: MARSEL
- Technology contour: ROAPP
- Canonical repository: `atalanrafael-jpg/Ro-app`
- Canonical branch: `main`
- Canonical live audit workflow: `.github/workflows/marsel-unified-control-plane.yml`
- Historical implementations: `старые данные/`

## Verified from current main

- Repository is active, public, not archived.
- `main` is the default branch.
- The unified system document explicitly defines MARSEL + ROAPP as one system.
- The canonical control plane is READ-ONLY and blocks production WRITE.
- The current workflow performs API inventory, data quality, entity audit, product-code review, warehouse contract audit, safety gate and evidence generation.
- Production WRITE is disabled until backup/export, restore integrity, reconciliation, full READ-ONLY inventory, duplicate/orphan/reference analysis, dry-run, idempotency, rollback and post-write verification are directly evidenced.

## Current open gates

1. Fresh live READ-ONLY evidence for the documented warehouse list contract (#42).
2. Complete current API/entity coverage and verified parameterized GET probes (#30, #25).
3. Full backup/export evidence and verified restore/integrity test (#19, #30).
4. Classification of 11 product-code duplicate groups (#35); no automatic deletion/merge.
5. User-authorized Gmail OAuth READ-ONLY verification (#27).
6. Official RO App MCP authorization verification (#30).
7. Security remediation/evidence for the historical credential-exposure issue (#23).

## Safety decision

`PRODUCTION_WRITE = BLOCKED`

No production mutation, mass synchronization, deletion, merge, reconciliation write, or irreversible data operation is authorized by this bootstrap.

## Control rule

Fresh evidence from the current `main` must replace historical assumptions. A successful CI run alone is not proof of production synchronization. Missing or incomplete evidence is `REVIEW_REQUIRED`, not `PASS`.

## Next execution order

`FRESH CONTROL-PLANE RUN → EVIDENCE REVIEW → CLOSE VERIFIED GATES → BACKUP/RESTORE PROOF → DATA RECONCILIATION → DRY-RUN → IDEMPOTENCY/ROLLBACK → SAFETY GATE → ONLY THEN CONSIDER CONTROLLED WRITE`

## Bootstrap execution marker

A documentation-only marker update on 2026-08-24 is intentionally used to trigger the canonical `main` control-plane workflow. It does not authorize or perform any RO App production write.

## Status

`PARTIAL / REVIEW_REQUIRED`

This document is a control-point record, not a claim that production readiness has been achieved.
