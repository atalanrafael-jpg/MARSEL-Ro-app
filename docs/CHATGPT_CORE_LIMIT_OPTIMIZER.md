# ChatGPT Core — Limit Optimizer

## Purpose

Optimize use of available ChatGPT capabilities without bypassing account, safety, rate, billing, or platform controls.

## Operating rule

`VERIFY CAPABILITY → ROUTE → EXECUTE → VERIFY RESULT`

If a limit or unavailable capability blocks the preferred route, use an available alternative only when it preserves the task requirements. Do not spoof plans, bypass access controls, exploit vulnerabilities, or treat an unavailable integration as connected.

## Routing

| Workload | Preferred route | Fallback |
|---|---|---|
| Normal reasoning | ChatGPT | split task into verified stages |
| Current information | Web / primary sources | user-provided sources |
| Large documents | File search / targeted extraction | chunk and summarize |
| Data processing | Data Analysis when available | external runtime/API |
| Image work | Image generation/editing | reduce iterations and batch changes |
| Repository work | GitHub/Codex when actually connected | prepare patch/instructions |
| Repetitive automation | external runtime / automation service | manual staged execution |
| Persistent knowledge | project files / approved knowledge store | compact verified state |

## Limit-saving controls

1. Reuse verified outputs instead of regenerating them.
2. Search/extract only the context required for the current task.
3. Batch compatible operations when the available tool supports batching.
4. Keep durable project state in files/repositories rather than repeating it in prompts.
5. Separate research, implementation, and verification so failed work is not repeated blindly.
6. Prefer deterministic scripts for repetitive transformations.
7. Record blocked operations explicitly instead of retrying indefinitely.

## Status model

- `VERIFIED` — supported by current tool output or authoritative source.
- `DONE` — executed and verified.
- `PREPARED` — ready, but not executed.
- `AVAILABLE` — capability exists, account/runtime state not confirmed.
- `NEEDS USER ACTION` — requires an account/UI action.
- `BLOCKED` — cannot proceed with current access/capability.
- `FAILED` — execution attempted and failed.

## Security boundary

The optimizer must never claim that a tariff or system limit has been removed unless the platform itself confirms the change. It may optimize routing, context, storage, batching, caching, external execution, and workflow design.

## Verification

Every material change requires evidence. Missing tool output is not evidence of success.

Error protocol: `STOP → CORRECT → REVERIFY`.
