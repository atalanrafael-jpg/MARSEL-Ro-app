# Permission Matrix

## Default
READ: allowed when required.
WRITE: denied by default.
DELETE: denied by default.
PRODUCTION: explicit approval required.
SECRETS: never exposed in task context.

## Risk gates
LOW: single verification.
MEDIUM: evidence + verification.
HIGH: independent verification.
CRITICAL: human approval + independent verification.