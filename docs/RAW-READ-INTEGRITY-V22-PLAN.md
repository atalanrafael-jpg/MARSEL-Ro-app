# MARSEL V22 — Safe Raw-Read Integrity Gate

## Purpose

Add a read-only evidence layer for relationship, duplicate, orphan, costing and stock analysis.

## Safety

- Only documented GET endpoints may be used.
- No identifiers may be guessed.
- No POST, PUT, PATCH or DELETE requests are permitted.
- Raw responses must be retained only as controlled CI artifacts.
- The report must explicitly state that it is not a database backup unless completeness is independently established.

## Required evidence

1. Endpoint and HTTP status.
2. Raw JSON response or a controlled redacted equivalent.
3. Stable identifier extraction.
4. Duplicate identifier detection.
5. Candidate foreign-key fields.
6. Cross-collection orphan detection only when both source and target identifiers are actually present in evidence.
7. Separate costing and stock checks; absence of required fields must be reported as `NOT_ESTABLISHED`, never inferred as zero or consistent.

## Exit criteria

The V22 audit may report PASS only for checks supported by retained evidence. Missing evidence remains `NOT_ESTABLISHED`. Production writes remain locked until API write contracts, backup, dry-run and change approval are independently verified.
