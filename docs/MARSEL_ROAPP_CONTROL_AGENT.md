# MARSEL ROAPP Control Agent

## Purpose

The Control Agent is the engineering operator for MARSEL ROAPP. It is designed to inspect the current repository, diagnose issues, implement safe improvements, run verification, document evidence, and identify the next highest-value task.

## Operating loop

`OBSERVE → MEASURE → FIND → FIX → TEST → VERIFY → DOCUMENT → MONITOR`

## Capabilities

- repository and file inspection;
- deterministic verification through allow-listed checks;
- safe file creation and correction when the explicit local write gate is enabled;
- regression-oriented testing;
- evidence-first reporting;
- duplicate/conflict avoidance;
- security and production-gate enforcement;
- preparation for later MCP/API/tool integrations.

## Safety model

- `MARSEL_AGENT_ALLOW_WRITE=0` by default;
- production WRITE is permanently disabled;
- `.github/workflows/`, `Dockerfile`, and `requirements.lock` are protected from agent writes;
- credentials are never printed, stored, or guessed;
- missing evidence is reported as `NOT_VERIFIED` rather than `PASS`;
- irreversible or high-risk operations require human approval.

## Local usage

Install project dependencies, provide `OPENAI_API_KEY` through the environment, then run:

```bash
python -m agents.marsel_control_agent
```

A task can be supplied with `MARSEL_AGENT_TASK`. Repository modification requires an explicit `MARSEL_AGENT_ALLOW_WRITE=1` environment variable.

## Future extensions

The next safe extensions are dedicated tools for GitHub PR inspection, CI evidence collection, RO App read-only API verification, backup/restore evidence, MCP health checks, and structured task/checkpoint state. Each extension should retain the same production safety gate.
