#!/usr/bin/env python3
"""MARSEL final repository verification.

Deterministic repository-level verifier. It never mutates RO App and never
manufactures external evidence. It checks that the release control plane is
internally consistent and emits a machine-readable result.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    ".github/workflows/mcp-production.yml",
    ".github/workflows/marsel-production-gate.yml",
    ".github/workflows/marsel-release-readiness.yml",
    "scripts/marsel_canonical_self_check.py",
    "scripts/marsel_production_gate_v1.py",
    "scripts/marsel_release_readiness_v1.py",
    "docs/MARSEL-PRODUCTION-GO-LIVE-GATES.md",
    "docs/MARSEL_ROAPP_TASK_REGISTRY.md",
    "SECURITY.md",
    "Dockerfile",
)
# Detect unfinished implementation markers without self-matching this verifier
# or known negative-marker assertions in the test suite.
# Exclude exception class names (e.g. NotImplementedError) from this marker list
# to avoid false positives where the exception name appears in otherwise-complete code.
UNFINISHED_MARKER = re.compile(r"(?i)\b(TODO|FIXME|XXX|HACK)\b")
MARKER_SCAN_EXCLUSIONS = {
    "scripts/marsel_final_verification.py",
    "tests/test_codex_plugin.py",
}


def git_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, check=True
    )
    return [line for line in result.stdout.splitlines() if line]


def main() -> int:
    failures: list[str] = []
    files = git_files()

    for path in REQUIRED:
        if not (ROOT / path).is_file():
            failures.append(f"missing_required_file:{path}")

    for path in files:
        if path in MARKER_SCAN_EXCLUSIONS or path.startswith(".git/"):
            continue
        p = ROOT / path
        if not p.is_file() or p.stat().st_size > 2_000_000:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if UNFINISHED_MARKER.search(text):
            failures.append(f"unfinished_marker:{path}")

    gate = ROOT / "scripts/marsel_production_gate_v1.py"
    if gate.exists():
        text = gate.read_text(encoding="utf-8")
        if "PRODUCTION_WRITE_AUTHORIZED=false" not in text:
            failures.append("write_gate_missing_fail_closed_output")
        if "write_approval_is_not_authorized_by_automated_gate" not in text:
            failures.append("write_gate_missing_authorization_block")

    workflow = ROOT / ".github/workflows/mcp-production.yml"
    if workflow.exists():
        text = workflow.read_text(encoding="utf-8")
        for marker in ("pytest", "pip-audit", "timeout-minutes:"):
            if marker not in text:
                failures.append(f"production_workflow_missing:{marker}")

    result = {
        "repository": "atalanrafael-jpg/MARSEL-Ro-app",
        "result": "PASS" if not failures else "FAIL",
        "repository_controls": "PASS" if not failures else "FAIL",
        "production_write_authorized": False,
        "external_evidence": "MUST_BE_VERIFIED_SEPARATELY",
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
