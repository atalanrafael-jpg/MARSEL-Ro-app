from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "control_agent" / "marsel_control_agent.py"
SPEC = spec_from_file_location("marsel_control_agent_under_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

AgentStage = MODULE.AgentStage
AgentState = MODULE.AgentState
_is_protected_path = MODULE._is_protected_path
_is_sensitive_path = MODULE._is_sensitive_path
_repo_relative_path = MODULE._repo_relative_path
next_stage = MODULE.next_stage


def test_repo_relative_path_rejects_escape():
    relative, error = _repo_relative_path("../../outside")
    assert relative is None
    assert error == "BLOCKED: path escapes repository"


def test_protected_policy_uses_normalized_relative_path():
    relative, error = _repo_relative_path("./.github/workflows/ci.yml")
    assert error is None
    assert _is_protected_path(relative)


def test_protected_policy_covers_protected_files():
    assert _is_protected_path(Path("Dockerfile"))
    assert _is_protected_path(Path("requirements.lock"))


def test_sensitive_policy_blocks_secret_paths():
    assert _is_sensitive_path(Path(".env"))
    assert _is_sensitive_path(Path("config/credentials/prod.json"))
    assert _is_sensitive_path(Path("certs/service.key"))


def test_normal_source_path_is_not_sensitive_or_protected():
    relative, error = _repo_relative_path("control_agent/marsel_control_agent.py")
    assert error is None
    assert not _is_sensitive_path(relative)
    assert not _is_protected_path(relative)


def test_agent_state_defaults_to_read_only_and_serializes():
    state = AgentState(request_id="req-1")
    assert state.stage is AgentStage.REQUEST
    assert state.read_only is True
    assert state.production_write_enabled is False
    assert state.checkpoint() == {
        "stage": "REQUEST",
        "request_id": "req-1",
        "read_only": True,
        "production_write_enabled": False,
        "evidence": [],
        "blockers": [],
    }


def test_agent_state_can_advance_forward():
    state = AgentState(request_id="req-2")
    state = next_stage(state, AgentStage.VALIDATE)
    state = next_stage(state, AgentStage.READ)
    assert state.stage is AgentStage.READ
    assert state.read_only is True


def test_agent_state_rejects_backward_transition():
    state = AgentState(stage=AgentStage.ANALYZE)
    with pytest.raises(ValueError, match="cannot move backwards"):
        next_stage(state, AgentStage.READ)


def test_agent_state_fail_closes_write():
    state = AgentState(stage=AgentStage.SAFETY_GATE, request_id="req-3")
    with pytest.raises(PermissionError, match="production WRITE is fail-closed"):
        next_stage(state, AgentStage.WRITE)
