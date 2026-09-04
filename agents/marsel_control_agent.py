"""MARSEL ROAPP Control Agent.

A guarded, repository-first agent for inspect -> diagnose -> change -> test -> verify.
Production writes remain disabled by default and require explicit approval.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional

from agents import Agent, Runner, function_tool

ROOT = Path(__file__).resolve().parents[1]
WRITE_ENABLED = os.getenv("MARSEL_AGENT_ALLOW_WRITE", "0") == "1"
PRODUCTION_WRITE_ENABLED = False


@function_tool
def inspect_file(path: str) -> str:
    """Read a text file inside the repository; paths may not escape the repo."""
    target = (ROOT / path).resolve()
    if ROOT not in target.parents and target != ROOT:
        return "BLOCKED: path escapes repository"
    if not target.is_file():
        return f"NOT_FOUND: {path}"
    return target.read_text(encoding="utf-8")[:30000]


@function_tool
def run_check(command: str) -> str:
    """Run an allow-listed repository verification command."""
    allowed = {
        "pytest": ["pytest", "-q"],
        "canonical-self-check": ["python", "scripts/marsel_canonical_self_check.py"],
        "git-status": ["git", "status", "--short"],
        "git-diff": ["git", "diff", "--check"],
    }
    if command not in allowed:
        return "BLOCKED: command is not allow-listed"
    result = subprocess.run(allowed[command], cwd=ROOT, text=True, capture_output=True, timeout=300)
    return f"exit={result.returncode}\nSTDOUT:\n{result.stdout[-12000:]}\nSTDERR:\n{result.stderr[-12000:]}"


@function_tool
def write_file(path: str, content: str) -> str:
    """Write a repository file only when the explicit local write gate is enabled."""
    if not WRITE_ENABLED:
        return "BLOCKED: MARSEL_AGENT_ALLOW_WRITE is not enabled"
    target = (ROOT / path).resolve()
    if ROOT not in target.parents:
        return "BLOCKED: path escapes repository"
    if path.startswith(".github/workflows/") or path in {"Dockerfile", "requirements.lock"}:
        return "BLOCKED: protected infrastructure requires manual review"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"UPDATED: {path}"


AGENT_INSTRUCTIONS = """You are the MARSEL ROAPP Control Agent.

Mission: maximize useful autonomous engineering support for MARSEL ROAPP: inspect, analyze,
diagnose, correct, create, improve, test, verify, document, monitor, and automate.

Operating loop:
OBSERVE -> MEASURE -> FIND -> FIX -> TEST -> VERIFY -> DOCUMENT -> MONITOR.

Rules:
1. Source-first and no-guess. Inspect current repository state before proposing or changing code.
2. Preserve the canonical project: MARSEL ROAPP; MARSEL is business contour, ROAPP technical contour.
3. Prefer the smallest safe change. Never create duplicate implementations, workflows, tasks, or documents.
4. Production WRITE is permanently blocked in this agent. Never enable or simulate a production write.
5. Repository writes are blocked unless MARSEL_AGENT_ALLOW_WRITE=1 is explicitly present.
6. Even with write enabled, protected infrastructure (.github/workflows, Dockerfile, requirements.lock) requires manual review.
7. After every change, run available verification and report exact evidence and remaining NOT_VERIFIED items.
8. Never invent credentials, API responses, IDs, reviewers, approvals, or deployment success.
9. Treat CI success as evidence for CI only; do not claim live integration success without direct evidence.
10. For risky or irreversible actions, stop at a plan and require human approval.

Use tools deliberately. Return a concise action log: findings, changes, tests, verification, blockers, next task.
"""

agent = Agent(
    name="MARSEL ROAPP Control Agent",
    instructions=AGENT_INSTRUCTIONS,
    tools=[inspect_file, run_check, write_file],
)


def run(prompt: str) -> str:
    """Run the control agent against the current repository workspace."""
    result = Runner.run_sync(agent, prompt)
    return result.final_output


if __name__ == "__main__":
    task = os.getenv("MARSEL_AGENT_TASK", "Audit the repository and identify the highest-priority safe improvement.")
    print(run(task))
