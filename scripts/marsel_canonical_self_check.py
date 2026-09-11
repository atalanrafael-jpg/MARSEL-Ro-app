#!/usr/bin/env python3
"""Fail-closed static check for the single canonical MARSEL ROAPP system."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REPOSITORY = "atalanrafael-jpg/MARSEL-Ro-app"
EXPECTED_BRANCH = "main"
WORKFLOW = ROOT / ".github" / "workflows" / "marsel-unified-control-plane.yml"
PRODUCTION_GATE = ROOT / ".github" / "workflows" / "marsel-production-gate.yml"
GENERIC_TEST = ROOT / ".github" / "workflows" / "test.yml"
WORKFLOW_REGISTRY = ROOT / "05_CONTROL" / "ACTIVE-WORKFLOW-REGISTRY.md"
SCRIPT_REGISTRY = ROOT / "05_CONTROL" / "ACTIVE-SCRIPT-REGISTRY.md"
CANONICAL = ROOT / "01_MASTER" / "MARSEL_ROAPP_CANONICAL.md"
MASTER_REGISTRY = ROOT / "01_MASTER" / "MARSEL_ROAPP_MASTER_REGISTRY.md"
CURRENT_STATE = ROOT / "01_MASTER" / "MARSEL_ROAPP_CURRENT_STATE.md"
TASK_REGISTRY = ROOT / "01_MASTER" / "MARSEL_ROAPP_TASK_REGISTER.md"
DECISION_LOG = ROOT / "01_MASTER" / "MARSEL_ROAPP_DECISION_LOG.md"
API_REGISTRY = ROOT / "scripts" / "marsel_api_v2_canonical_registry_v1.py"
API_REGISTRY_DOC = ROOT / "docs" / "MARSEL-API-REGISTRY.md"
EVIDENCE_BUILDER = ROOT / "scripts" / "marsel_evidence_builder_v1.py"
CANONICAL_SCRIPTS = {
    "scripts/marsel_api_inventory_v20_32.py",
    "scripts/marsel_data_quality_v22_readonly.py",
    "scripts/marsel_entity_audit_v20_35.py",
    "scripts/marsel_product_code_collision_audit_v22_3.py",
    "scripts/marsel_warehouse_contract_v20_48.py",
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
    "marsel-location-by-id-v20-49.yml",
    "marsel-warehouse-contract-v20-48.yml",
}
LIVE_MARKERS = ("ROAPP_API_KEY", "api.roapp.io/v2", "MARSEL read-only orders audit")
STALE_API_REGISTRY_MARKERS = ("marsel-live-probe-v20-27.yml", "marsel-readonly-integrity-v21.yml")
FORBIDDEN_WRITE_METHODS = ("POST", "PUT", "PATCH", "DELETE")


def fail(message: str) -> None:
    raise SystemExit(f"CANONICAL_SELF_CHECK_FAIL: {message}")


def main() -> int:
    runtime_repository = os.getenv("GITHUB_REPOSITORY")
    runtime_ref_name = os.getenv("GITHUB_REF_NAME")
    if runtime_repository and runtime_repository != EXPECTED_REPOSITORY:
        fail(f"unexpected canonical repository: {runtime_repository}; expected {EXPECTED_REPOSITORY}")

    required = [
        WORKFLOW, PRODUCTION_GATE, GENERIC_TEST, WORKFLOW_REGISTRY, SCRIPT_REGISTRY,
        CANONICAL, MASTER_REGISTRY, CURRENT_STATE, TASK_REGISTRY, DECISION_LOG,
        API_REGISTRY, API_REGISTRY_DOC, EVIDENCE_BUILDER,
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        fail("missing canonical files: " + ", ".join(missing))

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    production_gate_text = PRODUCTION_GATE.read_text(encoding="utf-8")
    test_text = GENERIC_TEST.read_text(encoding="utf-8")
    workflow_registry_text = WORKFLOW_REGISTRY.read_text(encoding="utf-8")
    script_registry_text = SCRIPT_REGISTRY.read_text(encoding="utf-8")
    canonical_text = CANONICAL.read_text(encoding="utf-8")
    master_registry_text = MASTER_REGISTRY.read_text(encoding="utf-8")
    current_state_text = CURRENT_STATE.read_text(encoding="utf-8")
    task_text = TASK_REGISTRY.read_text(encoding="utf-8")
    decision_text = DECISION_LOG.read_text(encoding="utf-8")
    registry_text = API_REGISTRY.read_text(encoding="utf-8")
    registry_doc_text = API_REGISTRY_DOC.read_text(encoding="utf-8")
    evidence_builder_text = EVIDENCE_BUILDER.read_text(encoding="utf-8")

    if (ROOT / "старые данные").exists():
        fail("obsolete legacy data directory still exists")
    for marker in ("One system: MARSEL ROAPP", "Canonical branch: `main`", "Production WRITE remains disabled"):
        if marker not in canonical_text:
            fail(f"canonical system marker missing: {marker}")
    for marker in ("Project control", "Business", "Technical", "Development", "Control", "History"):
        if marker not in master_registry_text:
            fail(f"master registry marker missing: {marker}")
    if "CANONICAL CLEANUP IN PROGRESS" not in current_state_text:
        fail("current state does not identify canonical cleanup")
    if "2026-09-11" not in decision_text:
        fail("decision log is missing current consolidation decision")

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
    for marker in ("write_requests_made", "ro_app_data_mutated", "readonly"):
        if marker not in workflow_text:
            fail(f"workflow safety marker missing: {marker}")
    if "MARSEL_WRITE_APPROVED" not in production_gate_text or '"false"' not in production_gate_text:
        fail("production gate does not explicitly default MARSEL_WRITE_APPROVED to false")
    if "contents: read" not in workflow_text:
        fail("unified workflow is missing least-privilege contents: read permission")
    if "github.event_name != 'pull_request'" not in workflow_text:
        fail("live secret/audit boundary for pull_request events is missing")
    if "marsel-unified-control-plane.yml" not in workflow_registry_text:
        fail("workflow registry does not name the canonical control plane")
    if "scripts/marsel_api_inventory_v20_32.py" not in script_registry_text:
        fail("script registry does not name the canonical inventory entrypoint")
    for marker in ("ROAPP remains READ-ONLY", "Production WRITE remains disabled"):
        if marker not in canonical_text:
            fail(f"canonical safety marker missing: {marker}")
    if "`WRITE=0`" not in task_text and "Production WRITE" not in task_text:
        fail("production WRITE gate is missing from task register")
    for marker in ("NEVER fabricates production evidence", '"fabricated_evidence": False', '"production_write": False'):
        if marker not in evidence_builder_text:
            fail(f"evidence builder safety marker missing: {marker}")
    if runtime_ref_name == EXPECTED_BRANCH and "Canonical branch: `main`" not in canonical_text:
        fail("main branch is missing the canonical branch declaration")

    print("CANONICAL_SELF_CHECK=PASS")
    print("SYSTEM=MARSEL_ROAPP")
    print(f"CANONICAL_REPOSITORY={EXPECTED_REPOSITORY}")
    print("CANONICAL_BRANCH=main")
    print("CANONICAL_LIVE_AUDIT=ONE")
    print("GENERIC_TEST_LIVE_AUDIT=NONE")
    print("MASTER_CORE=CANONICAL_AND_VERIFIED")
    print("API_REGISTRY=NON_EMPTY_READ_ONLY")
    print("WORKFLOW_REGISTRY=CANONICAL_PRESENT")
    print("CANONICAL_GOVERNANCE=PRESENT")
    print("EVIDENCE_BUILDER=FAIL_CLOSED")
    print("PRODUCTION_WRITE=DISABLED")
    print("RO_APP_DATA_MUTATION=NOT_PERFORMED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
