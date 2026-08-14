# MARSEL Automation Health Registry

## Purpose
Single human-readable registry for autonomous RO APP checks. It records the expected gates and the evidence required to mark them VERIFIED.

## Scheduled gates
| Gate | Schedule (UTC) | Mode | Evidence |
|---|---|---|---|
| Live API Probe | 06:00, 18:00 | READ ONLY | JSON + SHA-256 |
| Data Quality | 06:15, 18:15 | READ ONLY | JSON report |
| Integrity Consolidation | 06:30, 18:30 | READ ONLY | JSON + SHA-256 |

## Status rules
- VERIFIED: the scheduled run completed successfully and its safety/data invariants passed.
- FAILED: the run failed or an invariant failed.
- BLOCKED: the workflow could not execute because required configuration/access was unavailable.
- UNKNOWN: no run evidence has yet been retrieved.

## Safety invariants
- GET-only policy.
- `write_requests_made == 0`.
- `ro_app_data_mutated == false`.
- API key supplied only through GitHub Actions secrets.
- Evidence artifact exists and is non-empty.

## Important limitation
This registry is configuration-level documentation. It is not a claim that a scheduled run succeeded. A run must be checked in GitHub Actions before marking VERIFIED.

## Next automation layer
1. Collect the latest run result for each gate.
2. Record PASS/FAIL/BLOCKED with timestamp and run URL.
3. Preserve artifact/evidence identifiers.
4. Open a diagnostic issue on failure without changing RO APP data.
5. Keep all remediation READ ONLY until a separately authorized write workflow exists.
