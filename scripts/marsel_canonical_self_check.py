#!/usr/bin/env python3
"""Fail-closed static check for the single MARSEL ROAPP control plane."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "marsel-unified-control-plane.yml"
GENERIC_TEST = ROOT / ".github" / "workflows" / "test.yml"
API_REGISTRY = ROOT / "scripts" / "marsel_api_v2_canonical_registry_v1.py"
API_REGISTRY_DOC = ROOT / "docs" / "MARSEL-API-REGISTRY.md"
TASK_REGISTRY = ROOT / "docs" / "MARSEL_ROAPP_TASK_REGISTRY.md"
ARCH = ROOT / "MARSEL_ROAPP_UNIFIED_SYSTEM.md"

CANONICAL_SCRIPTS = {
    "scripts/marsel_api_inventory_v20_32.py",
    "scripts/marsel_data_quality_v22_readonly.py",
    "scripts/marsel_entity_audit_v20_35.py",
    "scripts/marsel_product_code_collision_audit_v22_1.py",
    "scripts/marsel_warehouse_contract_v20_36.py",
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
FORBIDDEN_WRITE_METHODS = ("POST", "PUT", "PATCH", "DELETE")


def fail(message: str) -> None:
    raise SystemExit(f"CANONICAL_SELF_CHECK_FAIL: {message}")


def main() -> int:
    required = [WORKFLOW, GENERIC_TEST, API_REGISTRY, API_REGISTRY_DOC, TASK_REGISTRY, ARCH]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        fail("missing canonical files: " + ", ".join(missing))

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    test_text = GENERIC_TEST.read_text(encoding="utf-8")
    registry_text = API_REGISTRY.read_text(encoding="utf-8")
    registry_doc_text = API_REGISTRY_DOC.read_text(encoding="utf-8")
    task_text = TASK_REGISTRY.read_text(encoding="utf-8")
    arch_text = ARCH.read_text(encoding="utf-8")

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
    if any(marker in registry_doc_text for marker in STALE_API_REGISTRY_MARKERS):
        fail("API registry documentation still advertises a removed workflow as active")
    if "REGISTRY: tuple[Endpoint, ...] = ()" in registry_text:
        fail("canonical API registry is empty")
    if any(method in registry_text for method in FORBIDDEN_WRITE_METHODS):
        fail("canonical READ-ONLY API registry contains a write method")
    if "/v2/v2" in workflow_text:
        fail("duplicated /v2/v2 API base detected in workflow")

    # The unified workflow must stay structurally READ-ONLY. These are evidence fields,
    # not mutation commands, and must remain zero/false in the produced artifacts.
    for marker in ("write_requests_made", "ro_app_data_mutated", "readonly"):
        if marker not in workflow_text:
            fail(f"workflow safety marker missing: {marker}")
    if "Production mutations remain disabled" not in arch_text and "Production WRITE remains disabled" not in arch_text:
        fail("architecture does not explicitly keep production WRITE disabled")
    if "`WRITE=0`" not in task_text:
        fail("production WRITE gate is missing from task registry")

    print("CANONICAL_SELF_CHECK=PASS")
    print("SYSTEM=MARSEL_ROAPP")
    print("CANONICAL_LIVE_AUDIT=ONE")
    print("GENERIC_TEST_LIVE_AUDIT=NONE")
    print("API_REGISTRY=NON_EMPTY_READ_ONLY")
    print("PRODUCTION_WRITE=DISABLED")
    print("RO_APP_DATA_MUTATION=NOT_PERFORMED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
