# MARSEL — Repair Status Matrix V1

Status: DESIGN / NOT LIVE IN RO APP

## Canonical lifecycle
| Code | Russian status | Entry condition | Exit condition |
|---|---|---|---|
| received | Принят | Item accepted and condition recorded | Diagnosis started |
| diagnostics | Диагностика | Item received | Diagnosis recorded |
| awaiting_customer_approval | Ожидает согласования | Scope/price requires customer decision | Approved or cancelled |
| approved | Согласован | Customer approved scope/price | Work started |
| in_repair | В ремонте | Operation started | Work complete or blocked |
| quality_check | Контроль качества | Repair operations complete | Pass → ready; fail → rework |
| rework | Доработка | QC failed | Recheck |
| ready | Готов к выдаче | QC passed and financial/material reconciliation complete | Delivered |
| delivered | Выдан | Delivery evidence recorded | Terminal |
| cancelled | Отменён | Explicit cancellation reason | Terminal |

## Transition rules
- No silent status changes.
- No `received → delivered` normal transition.
- Price/scope increase requires `awaiting_customer_approval`.
- Failed QC requires `rework`.
- `ready` requires unresolved-critical-items count = 0.
- `delivered` requires delivery evidence.

## Required audit event
Each transition should record previous status, new status, actor, timestamp, reason when applicable and source/channel where supported.

## Repair-type preservation
Jewelry, watch and eyewear orders share this lifecycle but retain type-specific diagnosis, operations, materials, measurements and evidence.

## Ro App mapping rule
These codes are MARSEL canonical values. They must be mapped to actual Ro App status IDs only after live schema verification. Do not create or assume Ro App status IDs from this document.

## Safety
Design only. No production writes authorized.
