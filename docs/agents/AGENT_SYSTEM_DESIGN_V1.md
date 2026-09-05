# Agent System Design v1

## Status
DRAFT SPECIFICATION

## Purpose
Controlled multi-agent architecture for CHATGPT CORE.

## Principles
1. Verify capability before action.
2. Separate projects and domains.
3. Least privilege.
4. Evidence is required for DONE.
5. Independent verification for high-risk actions.
6. STOP -> CORRECT -> REVERIFY on failure.

## Architecture
USER -> MASTER ORCHESTRATOR -> ROUTERS -> AGENT REGISTRY -> EXECUTION -> EVIDENCE -> VERIFICATION.

## Routers
- Project Router
- Task Router
- Risk Router

## Lifecycle
IDLE -> ASSIGNED -> ANALYZING -> EXECUTING -> VERIFYING -> DONE

Alternative states: BLOCKED, FAILED, RETRY, ROLLED_BACK.

## Completion
DONE is allowed only after evidence and verification.