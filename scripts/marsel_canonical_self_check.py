#!/usr/bin/env python3
"""Static self-check for the canonical MARSEL/Ro App structure."""
from __future__ import annotations
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "marsel-unified-control-plane.yml"
GENERIC_TEST = ROOT / ".github" / "workflows" / "test.yml"
API_REGISTRY = ROOT / "scripts" / "marsel_api_v2_canonical_registry_v1.py"
API_REGISTRY_DOC = ROOT / "docs" / "MARSEL-API-REGISTRY.md"

# These are the actual canonical implementations wired by the unified workflow.
CANONICAL_SCRIPTS = {
    "scripts/marsel_api_inventory_v20_32.py",
    "scripts/marsel_data_quality_v22_readonly.py",
    "scripts/marsel_entity_audit_v20_35.py",
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
LIVE_MARKERS = ("ROAPP_API_KEY", "api.roapp.io/v2", "MARSEL read-only orders audit")
STALE_API_REGISTRY_MARKERS = ("marsel-live-probe-v20-27.yml", "marsel-readonly-integrity-v21.yml")


def fail(message: str) -> None:
    raise SystemExit(f"CANONICAL_SELF_CHECK_FAIL: {message}")

if not WORKFLOW.exists(): fail("canonical workflow is missing")
if not GENERIC_TEST.exists(): fail("generic test workflow is missing")
if not API_REGISTRY.exists(): fail("canonical API registry script is missing")
if not API_REGISTRY_DOC.exists(): fail("canonical API registry documentation is missing")

workflow_text = WORKFLOW.read_text(encoding="utf-8")
test_text = GENERIC_TEST.read_text(encoding="utf-8")
registry_text = API_REGISTRY.read_text(encoding="utf-8")
registry_doc_text = API_REGISTRY_DOC.read_text(encoding="utf-8")

for rel in CANONICAL_SCRIPTS:
    if not (ROOT / rel).exists(): fail(f"canonical script missing: {rel}")
    if rel not in workflow_text: fail(f"canonical script is not wired into unified workflow: {rel}")

for name in FORBIDDEN_LIVE_WORKFLOW_NAMES:
    if (WORKFLOW.parent / name).exists(): fail(f"superseded MARSEL workflow still exists: {name}")

if any(marker in test_text for marker in LIVE_MARKERS): fail("generic test workflow contains a live Ro App audit")
if any(marker in registry_doc_text for marker in STALE_API_REGISTRY_MARKERS): fail("API registry documentation still advertises a removed workflow as active")
if "REGISTRY: tuple[Endpoint, ...] = ()" in registry_text: fail("canonical API registry is empty")
if "POST" in registry_text or "PATCH" in registry_text or "DELETE" in registry_text: fail("canonical READ-ONLY API registry contains a write method")
if re.search(r"api\.roapp\.io/v2/v2", workflow_text): fail("duplicated /v2/v2 API base detected in workflow")

print("CANONICAL_SELF_CHECK=PASS")
print("CANONICAL_LIVE_AUDIT=ONE")
print("GENERIC_TEST_LIVE_AUDIT=NONE")
print("API_REGISTRY=NON_EMPTY_READ_ONLY")
print("RO_APP_DATA_MUTATION=NOT_PERFORMED")
