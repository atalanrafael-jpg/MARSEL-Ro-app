from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "control_agent" / "marsel_control_agent.py"
SPEC = spec_from_file_location("marsel_control_agent_under_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
try:
    SPEC.loader.exec_module(MODULE)
finally:
    sys.modules.pop(SPEC.name, None)

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