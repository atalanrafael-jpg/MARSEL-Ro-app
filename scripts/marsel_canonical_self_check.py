#!/usr/bin/env python3
"""Static self-check for the canonical MARSEL/Ro App structure.

This check does not call Ro App. It prevents the repository from silently
reintroducing duplicate live-audit pipelines or stale workflow references.
"""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "marsel-unified-control-plane.yml"
GENERIC_TEST = ROOT / ".github" / "workflows" / "test.yml"

CANONICAL_SCRIPTS = {
    "scripts/marsel_api_inventory_v20_31.py",
    "scripts/marsel_data_quality_v22_readonly.py",
    "scripts/marsel_entity_audit_v20_32.py",
    "scripts/marsel_product_code_collision_audit_v22_1.py",
}
FORBIDDEN_LIVE_WORKFLOW_NAMES = {
    "marsel-inventory-v20-12.yml",
    "marsel-live-probe-v20-27.yml",
    "marsel-master-directories-v1.yml",
    "marsel-orders-backup-v20-20.yml",
    "marsel-product-code-collision-v22-1.yml",
    "marsel-readonly-integrity-v21.yml",
    "marsel-v21-5-quality-gate.yml",
    "marsel-v21-6-naming-quality-gate.yml",
}
LIVE_MARKERS = (
    "ROAPP_API_KEY",
    "api.roapp.io/v2",
    "MARSEL read-only orders audit",
)


def fail(message: str) -> None:
    raise SystemExit(f"CANONICAL_SELF_CHECK_FAIL: {message}")


if not WORKFLOW.exists():
    fail("canonical workflow is missing")
if not GENERIC_TEST.exists():
    fail("generic test workflow is missing")

workflow_text = WORKFLOW.read_text(encoding="utf-8")
test_text = GENERIC_TEST.read_text(encoding="utf-8")

for rel in CANONICAL_SCRIPTS:
    if not (ROOT / rel).exists():
        fail(f"canonical script missing: {rel}")
    if rel not in workflow_text:
        fail(f"canonical script is not wired into unified workflow: {rel}")

for name in FORBIDDEN_LIVE_WORKFLOW_NAMES:
    if (WORKFLOW.parent / name).exists():
        fail(f"superseded MARSEL workflow still exists: {name}")

if any(marker in test_text for marker in LIVE_MARKERS):
    fail("generic test workflow contains a live Ro App audit")

# Prevent the common URL-normalization regression that produced /v2/v2/... .
if re.search(r"api\.roapp\.io/v2/v2", workflow_text):
    fail("duplicated /v2/v2 API base detected in workflow")

print("CANONICAL_SELF_CHECK=PASS")
print("CANONICAL_LIVE_AUDIT=ONE")
print("GENERIC_TEST_LIVE_AUDIT=NONE")
print("RO_APP_DATA_MUTATION=NOT_PERFORMED")
