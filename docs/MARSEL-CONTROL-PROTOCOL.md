# MARSEL CONTROL PROTOCOL

## Purpose
Single operational protocol for MARSEL / RO App / GitHub / AI integrations. The protocol is designed to prevent stale assumptions, unsafe writes, duplicated work, and unverified completion.

## Mandatory cycle
1. IDENTIFY — define the exact task, target system, scope, and success criteria.
2. CONTEXT — retrieve the latest project state, recent commits/runs, relevant files, prior decisions, and current conversation context.
3. SOURCE — verify current vendor/API documentation before relying on an endpoint, permission, product capability, or integration behavior.
4. INVENTORY — inspect the live system in read-only mode whenever possible.
5. COMPARE — reconcile documentation, repository code, CI evidence, live API evidence, and prior records.
6. CLASSIFY — label each finding VERIFIED, NOT_VERIFIED, ERROR, BLOCKED, or REVIEW_REQUIRED.
7. PLAN — choose the smallest safe change that solves the verified problem.
8. EXECUTE — make changes on an isolated branch first unless a direct production action is explicitly safe and required.
9. SELF-CHECK — inspect the resulting diff/output and run relevant tests/audits.
10. REGRESSION CHECK — confirm previously verified behavior remains intact.
11. EVIDENCE — record exact run IDs, commit SHAs, endpoint results, counts, and failure reasons.
12. UPDATE — update canonical project state only from verified evidence.
13. NEXT — proceed only after the current step passes verification.

## RO App safety gates
Default mode is READ_ONLY.

Production WRITE is prohibited until all applicable gates pass:
- current API access confirmed;
- endpoint contract verified from current RO App documentation;
- schema/payload verified;
- complete backup or explicitly bounded reversible snapshot available;
- restore procedure tested when required;
- dry-run completed;
- idempotency strategy defined;
- rollback strategy defined;
- write scope minimized;
- post-write read verification defined.

Never infer an endpoint, ID, payload, permission, or business rule from memory.

## Current evidence rules
- A GitHub secret existing is not proof of API validity.
- A successful CI run is not proof of data correctness.
- Historical 403 responses must not be treated as current blockers without a fresh live test.
- Documentation is not proof that a feature is enabled in the user's account.
- Code implementing OAuth/MCP is not proof that the account is actually authorized.
- Project requirements are not proof of current production configuration.

## Data quality
Potential duplicate product codes are review findings. Never delete or merge records automatically without verified identity, business intent, and rollback evidence.

## AI architecture
Prefer existing official capabilities over redundant custom agents:
- Codex for repository engineering, tests, CI/CD, and controlled code changes.
- RO App official API/MCP where available and actually authorized.
- Apps SDK/MCP for a ChatGPT-facing MARSEL application where account capabilities permit it.
- Agents SDK only where a custom autonomous backend agent is genuinely required.
- Supabase for durable state/audit data only when justified by the architecture.

Do not create a separate agent merely to duplicate an existing tool.

## Gmail
Gmail OAuth code in the repository is not proof of live authorization. Require a fresh authenticated read test before declaring Gmail connected.

## Canonical state
The canonical state must distinguish:
- BUSINESS_REQUIREMENT — desired business behavior;
- PRODUCTION_STATE — verified current state;
- CODE_STATE — repository implementation;
- API_STATE — verified live API behavior;
- CI_EVIDENCE — automated test/audit evidence;
- BLOCKER — currently verified blocker;
- HISTORICAL — superseded evidence.

## Completion rule
A task is DONE only when the requested outcome is verified by evidence. If verification is impossible, status must remain NOT_VERIFIED or BLOCKED; never mark it complete by inference.
