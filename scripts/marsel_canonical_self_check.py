#!/usr/bin/env python3
"""Fail-closed static check for the single MARSEL ROAPP control plane."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REPOSITORY = "atalanrafael-jpg/MARSEL-Ro-app"
EXPECTED_BRANCH = "main-MARSEL-ROAPP"
WORKFLOW = ROOT / ".github" / "workflows" / "marsel-unified-control-plane.yml"
GOVERNANCE = ROOT / "docs" / "MARSEL_ROAPP_CANONICAL_GOVERNANCE.md"
CANONICAL = ROOT / "01_MASTER" / "MARSEL_ROAPP_CANONICAL.md"
CURRENT = ROOT / "01_MASTER" / "MARSEL_ROAPP_CURRENT_STATE.md"
REGISTRY = ROOT / "01_MASTER" / "MARSEL_ROAPP_MASTER_REGISTRY.md"
ARCHIVE = ROOT / "06_ARCHIVE"
AGENTS = ROOT / "AGENTS.md"
CANONICAL_DIRS = ("01_MASTER", "02_MARSEL", "03_ROAPP", "04_DEVELOPMENT", "05_CONTROL", "06_ARCHIVE")
FORBIDDEN_ROOT_MASTERS = (
    "01_MARSEL_MASTER.md",
    "02_ROAPP_TECHNICAL_MASTER.md",
    "03_MARSEL_DATA_MASTER.md",
    "04_MARSEL_LEGAL_FINANCE_MASTER.md",
    "MARSEL_ROAPP_MASTER_CORE.md",
)


def fail(message: str) -> None:
    raise SystemExit(f"CANONICAL_SELF_CHECK_FAIL: {message}")


def main() -> int:
    runtime_repository = os.getenv("GITHUB_REPOSITORY")
    runtime_ref_name = os.getenv("GITHUB_REF_NAME")
    if runtime_repository and runtime_repository != EXPECTED_REPOSITORY:
        fail(f"unexpected repository: {runtime_repository}")
    if runtime_ref_name and runtime_ref_name != EXPECTED_BRANCH:
        fail(f"unexpected canonical branch: {runtime_ref_name}; expected {EXPECTED_BRANCH}")

    for rel in CANONICAL_DIRS:
        if not (ROOT / rel).is_dir():
            fail(f"canonical directory missing: {rel}")
    for path in (WORKFLOW, GOVERNANCE, CANONICAL, CURRENT, REGISTRY, AGENTS):
        if not path.exists():
            fail(f"required canonical file missing: {path.relative_to(ROOT)}")
    for name in FORBIDDEN_ROOT_MASTERS:
        if (ROOT / name).exists():
            fail(f"superseded root master still exists: {name}")
    if (ROOT / "старые данные").exists():
        fail("legacy `старые данные/` tree still exists; migrated history must live under 06_ARCHIVE")

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    governance_text = GOVERNANCE.read_text(encoding="utf-8")
    canonical_text = CANONICAL.read_text(encoding="utf-8")
    current_text = CURRENT.read_text(encoding="utf-8")
    registry_text = REGISTRY.read_text(encoding="utf-8")
    agents_text = AGENTS.read_text(encoding="utf-8")

    corpus = "\n".join((workflow_text, governance_text, canonical_text, current_text, registry_text, agents_text))
    for label, marker in {
        "repository": EXPECTED_REPOSITORY,
        "branch": EXPECTED_BRANCH,
        "workflow": "marsel-unified-control-plane.yml",
        "readonly": "contents: read",
        "production_write": "Production WRITE remains disabled",
    }.items():
        if marker not in corpus:
            fail(f"required marker missing: {label} -> {marker}")

    if "main` is the only canonical integration branch" in governance_text:
        fail("governance still names `main` as canonical")
    if "Canonical branch: `main`" in governance_text:
        fail("governance contains stale canonical branch")
    if "Canonical branch: `main`" in agents_text:
        fail("agent instructions contain stale canonical branch")
    if "main` does not currently exist" not in canonical_text:
        fail("canonical document does not explicitly fence off nonexistent main")
    if "FULL CLEANUP IN PROGRESS" in current_text:
        fail("current-state document still reports cleanup as incomplete")
    archive_paths = "\n".join(p.as_posix() for p in ARCHIVE.rglob("*"))
    if "legacy-root" not in archive_paths:
        fail("legacy root archive is missing")
    if "legacy-old-data" not in archive_paths:
        fail("migrated old-data archive is missing")
    if "main-MARSEL-ROAPP" not in workflow_text:
        fail("unified workflow is not wired to canonical branch")
    if "PRODUCTION_WRITE" not in workflow_text:
        fail("workflow lacks production-write safety marker")

    # Historical snapshots may retain obsolete branch wording for traceability.
    # The active source-of-truth set is the files checked above; historical material
    # must be moved under 06_ARCHIVE before it can become authoritative again.

    print("CANONICAL_SELF_CHECK=PASS")
    print("SYSTEM=MARSEL_ROAPP")
    print(f"CANONICAL_REPOSITORY={EXPECTED_REPOSITORY}")
    print(f"CANONICAL_BRANCH={EXPECTED_BRANCH}")
    print("CANONICAL_STRUCTURE=01_MASTER..06_ARCHIVE")
    print("LEGACY_TREE=MIGRATED")
    print("ROOT_MASTER_DUPLICATES=REMOVED")
    print("PRODUCTION_WRITE=DISABLED")
    print("RO_APP_DATA_MUTATION=NOT_PERFORMED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
