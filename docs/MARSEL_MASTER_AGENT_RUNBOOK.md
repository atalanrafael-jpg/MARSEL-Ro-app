# MARSEL ROAPP MASTER AGENT — RUNBOOK

## Request handling

1. Normalize the request.
2. Classify scope: documentation, code, API, data, security, automation, or production.
3. Identify the canonical repository and current commit.
4. Check existing evidence before creating new work.
5. Execute read-only inspection first.
6. Record findings as `DONE`, `IN PROGRESS`, `BLOCKED`, or `NOT VERIFIED`.
7. For any mutation, require dry-run, rollback evidence and the applicable safety gate.
8. Verify the result independently.
9. Record the resulting checkpoint and next task.

## Stop conditions

Stop and report `BLOCKED` when:

- the requested API/entity/schema is not verified;
- credentials or authorization cannot be verified safely;
- a backup/restore requirement is unmet;
- a destructive operation is requested without an approved gate;
- source-of-truth conflicts cannot be resolved from current evidence;
- the requested action would modify production outside the approved gate.

## Evidence priority

1. Current direct execution evidence.
2. Current repository state / commit evidence.
3. Current CI/Actions evidence.
4. Current external API evidence.
5. Historical documentation.

Historical evidence is context only when a newer direct source exists.

## Completion rule

A task becomes `DONE` only when the required result is directly verifiable. Otherwise retain `IN PROGRESS`, `BLOCKED`, or `NOT VERIFIED`.

## Continuation rule

After each completed stage, select the next logical task from the canonical task registry. Do not create duplicate tasks when an existing task already covers the same objective.
