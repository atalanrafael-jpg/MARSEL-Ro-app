# MARSEL ROAPP — Owner Control Center

## Purpose

The Owner Control Center is a deterministic, read-only aggregation layer for operational evidence. It gives the owner one structured snapshot of project state without authorizing production writes.

## Contract

`OBSERVE → VALIDATE → CLASSIFY → ASSESS_IMPACT → ASSESS_RISK → RECOMMEND → APPROVAL_GATE → ACTION → VERIFY → DOCUMENT`

This implementation stops before production action unless a separately verified and explicitly approved write path exists. The current module itself never performs external calls or writes.

## Status model

- `VERIFIED`
- `PARTIAL`
- `FAILED`
- `BLOCKED`
- `NOT VERIFIED`
- `PROPOSED`

Every item carries an evidence class, a factual message, and a next step. Invalid statuses are rejected rather than silently normalized.

## Safety invariants

- `mode = READ_ONLY`
- `production_write_authorized = false`
- `ro_app_data_mutated = false`
- No automatic deletion
- No automatic production changes
- No claim of verification without supplied evidence

## Current scope

Implemented:

- deterministic control-item model;
- status aggregation;
- fail-closed validation;
- explicit read-only invariants;
- unit coverage for the safety contract.

Not yet implemented by this module:

- live ROAPP/API collection;
- alert delivery;
- web UI;
- automatic remediation;
- production write authorization.

Those require separate verified integrations and safety gates.
