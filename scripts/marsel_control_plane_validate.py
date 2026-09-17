#!/usr/bin/env python3
"""Fail-closed validation for the MARSEL ROAPP canonical control plane.

This validator is repository-local and performs no network calls and no writes
against RO App production data. It checks the canonical structure, required
control documents, and the production-write safety invariant.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "01_MASTER",
    "02_MARSEL",
    "03_ROAPP",
    "04_DEVELOPMENT",
    "05_CONTROL",
    "06_ARCHIVE",
    "docs/PROJECT_MASTER_CONTROL.md",
    ".github/workflows/marsel-unified-control-plane.yml",
)


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        raise SystemExit(f"CONTROL_PLANE_INVALID missing={missing}")

    control = (ROOT / "docs/PROJECT_MASTER_CONTROL.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/marsel-unified-control-plane.yml").read_text(
        encoding="utf-8"
    )

    required_markers = (
        "Canonical branch: `main`",
        "Production WRITE: DISABLED",
        "Current integration mode: READ-ONLY.",
        "Never expose or commit `ROAPP_API_KEY`.",
    )
    missing_markers = [m for m in required_markers if m not in control]
    if missing_markers:
        raise SystemExit(f"CONTROL_PLANE_INVALID control_markers={missing_markers}")

    workflow_markers = (
        "branches: [main]",
        "permissions:\n  contents: read",
        "PRODUCTION_WRITE=DISABLED",
        "ROAPP_API_KEY: ${{ secrets.ROAPP_API_KEY }}",
    )
    missing_workflow_markers = [m for m in workflow_markers if m not in workflow]
    if missing_workflow_markers:
        raise SystemExit(
            f"CONTROL_PLANE_INVALID workflow_markers={missing_workflow_markers}"
        )

    print("CONTROL_PLANE_RESULT=PASS")
    print("CANONICAL_BRANCH=main")
    print("PRODUCTION_WRITE=DISABLED")
    print("LIVE_MUTATIONS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
