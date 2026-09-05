# MARSEL ROAPP — Core AI Hardware Verification Gate

Status: **BLOCKED — FRESH APPLE SILICON EVIDENCE REQUIRED**

## Scope

This document defines the minimum evidence required before the optional Core AI integration in PR #112 can be considered hardware-verified.

The repository smoke test validates conversion only. It deliberately does not claim on-device execution.

## Required environment

- Physical Apple Silicon Mac (`arm64`), not an emulated/non-Apple environment.
- macOS version recorded exactly.
- Python version recorded exactly; Python >=3.11.
- Exact versions from `requirements-coreai.txt` recorded.
- Clean virtual environment.

## Required checks

Run, in order:

```bash
uname -m
sw_vers
python --version
python -m pip freeze
python scripts/marsel_coreai_torch_smoke.py
```

Then perform a separate runtime validation using the Core AI runtime available on the host. Record:

1. successful model conversion;
2. generated Core AI program/model artifact, if the runtime flow produces one;
3. successful model loading;
4. successful inference with deterministic test input;
5. output shape/type and a stable checksum or equivalent deterministic evidence;
6. whether execution used CPU, GPU, and/or Neural Engine where the runtime exposes that information;
7. elapsed runtime and peak memory when measurable.

## Safety constraints

- Use only a tiny local test model for the first hardware gate.
- Do not call RO App production APIs.
- Do not write production data.
- Do not introduce Core AI packages into production server dependencies.
- Do not call `program.optimize()` as part of this gate unless a separate review explicitly approves it.
- Do not claim MARSEL model compatibility from the tiny smoke model alone.

## Evidence record

A verification record must contain:

- date/time;
- host model/chip;
- macOS version;
- Python version;
- package versions;
- exact Git commit SHA;
- exact command output or attached CI/local log;
- runtime result;
- pass/fail decision;
- verifier identity.

## Gate decision

**PASS** only when all required runtime checks succeed and fresh evidence is attached to the project/PR.

**HOLD** when hardware is unavailable, conversion succeeds but runtime execution is not tested, or evidence is incomplete.

Successful GitHub Actions CI alone does not satisfy this gate because the integration is explicitly Apple Silicon-specific.

## Current decision

As of PR #112 head `a72d237a57fe5f48fca209880fc39421e7bc8ec9`, the gate remains **HOLD** until fresh physical Apple Silicon runtime evidence is produced.
