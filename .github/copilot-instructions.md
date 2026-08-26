# MARSEL ROAPP — VS Code Agent Instructions

## Project identity
- Canonical project name: MARSEL ROAPP.
- Business contour: MARSEL.
- Technical contour: ROAPP.
- Canonical repository: `atalanrafael-jpg/Ro-app`.

## Safety
- Treat live ROAPP operations as READ-ONLY unless direct production evidence explicitly authorizes a controlled write.
- Never invent identifiers, evidence, API responses, credentials, or successful production state.
- Never place secrets in source, prompts, logs, commits, artifacts, or screenshots.
- Never create synthetic PASS evidence to satisfy a gate.

## Automation loop
1. Inspect the relevant code and workflow.
2. Make the smallest canonical change.
3. Run the canonical local checks.
4. Capture/inspect evidence.
5. Run CI and review the result.
6. Only then report completion.

## Canonical local verification
Run:
```bash
python -m compileall -q scripts
python scripts/marsel_canonical_self_check.py
python scripts/marsel_release_readiness_v1.py
MARSEL_WRITE_APPROVED=true python scripts/marsel_production_gate_v1.py
```
The final command is expected to fail closed; a successful exit is a test failure.

## Evidence policy
The production gate requires real, fresh evidence. If evidence is missing, stale, malformed, or incomplete, preserve the failure/review state and fix the producer/transport path rather than weakening the gate.

## VS Code tools
- Use code/search/editor tools for repository work.
- Use terminal for the canonical checks above.
- Use browser tools only for UI verification.
- Use MCP only after its server, authentication, and permissions are explicitly configured and verified.
- Keep the active tool set minimal and task-specific.
