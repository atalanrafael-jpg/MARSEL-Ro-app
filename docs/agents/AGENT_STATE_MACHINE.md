# Agent State Machine

IDLE -> ASSIGNED -> ANALYZING -> EXECUTING -> VERIFYING -> DONE

Alternative transitions:
ANALYZING -> BLOCKED
EXECUTING -> FAILED
FAILED -> RETRY
FAILED -> ROLLED_BACK
VERIFYING -> EXECUTING when correction is required.

No transition to DONE bypasses VERIFYING.