# MARSEL ROAPP Control Agent

## Purpose

The Control Agent is the engineering operator for MARSEL ROAPP. It inspects the repository, diagnoses issues, implements safe improvements, runs verification, documents evidence, and identifies the next highest-value task.

## Operating loop

`OBSERVE → MEASURE → FIND → FIX → TEST → VERIFY → DOCUMENT → MONITOR`

## Capabilities

- repository and file inspection;
- deterministic verification through allow-listed checks;
- guarded repository modification when the explicit local write gate is enabled;
- regression-oriented testing;
- evidence-first reporting;
- duplicate/conflict avoidance;
- security and production-gate enforcement.

## Safety model

- `MARSEL_AGENT_ALLOW_WRITE=0` by default;
- production WRITE is permanently disabled;
- `.github/workflows/`, `Dockerfile`, and `requirements.lock` are protected;
- credentials are never printed, stored, or guessed;
- missing evidence is `NOT_VERIFIED`, never `PASS`;
- irreversible or high-risk operations require human approval.

## Local usage

Install project dependencies and provide `OPENAI_API_KEY` through the environment, then run:

```bash
python -m agents.marsel_control_agent
```

A task can be supplied with `MARSEL_AGENT_TASK`. Repository modification requires an explicit `MARSEL_AGENT_ALLOW_WRITE=1` environment variable.

## Verification boundary

CI and repository checks prove repository/CI behavior only. They do not prove live RO App authorization, production backup/restore, Gmail OAuth, MCP authorization, or production readiness without direct evidence.
