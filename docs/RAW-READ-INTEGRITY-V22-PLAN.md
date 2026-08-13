# MARSEL V22 — Safe Raw-Read Integrity Gate

## Purpose

Provide a read-only evidence layer for relationship, duplicate, orphan, costing and stock analysis.

## Safety

- Only documented GET endpoints may be used.
- No identifiers may be guessed.
- No POST, PUT, PATCH or DELETE requests are permitted by the audit runtime.
- Raw responses are controlled CI artifacts only.
- The report must not be described as a database backup unless completeness is independently established.

## Exit criteria

A check may report PASS only when retained evidence supports it. Missing evidence is `NOT_ESTABLISHED`. Production writes remain locked until API write contracts, backup, dry-run and change approval are independently verified.

## CI

The audit should run on pull requests and pushes affecting the audit code. Manual dispatch is optional; GitHub documents that `workflow_dispatch` requires the workflow file to exist on the default branch.
