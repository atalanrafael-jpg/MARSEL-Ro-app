from pathlib import Path

from agents.marsel_control_agent import _is_protected_path, _is_sensitive_path, _repo_relative_path


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
    relative, error = _repo_relative_path("agents/marsel_control_agent.py")
    assert error is None
    assert not _is_sensitive_path(relative)
    assert not _is_protected_path(relative)
