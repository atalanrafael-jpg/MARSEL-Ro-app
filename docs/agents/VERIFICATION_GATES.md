# Verification Gates

LOW: evidence + self-check.
MEDIUM: evidence + independent verification.
HIGH: independent verification + regression check.
CRITICAL: independent verification + regression check + explicit human approval.

Failure path:
STOP -> CLASSIFY -> CORRECT -> REVERIFY.

Terminal states:
DONE, BLOCKED, FAILED, ROLLED_BACK.