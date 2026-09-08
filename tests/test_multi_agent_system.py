import threading

import pytest

from agent_runtime.multi_agent import (
    AgentResult,
    AgentTask,
    MultiAgentCoordinator,
    Risk,
    TaskState,
)
from agent_runtime.github_bridge import ChangeSet, GatedGitHubBridge


def test_default_agents_cover_required_specialties():
    coordinator = MultiAgentCoordinator()
    assert {"architect", "security", "data_integrity", "integration", "tester", "verifier", "documenter", "github"} <= set(coordinator.agents)


def test_dispatch_runs_specialists_and_completion_requires_evidence():
    coordinator = MultiAgentCoordinator()
    task = AgentTask("T-1", "audit integration boundary")
    handlers = {
        name: (lambda task, name=name: AgentResult(name, task.task_id, "PASS", evidence_reference="evidence/T-1.json"))
        for name in coordinator.agents
    }
    results = coordinator.dispatch(task, handlers)
    coordinator.verify_and_complete(task, results)
    assert task.state == TaskState.DONE
    assert task.verification_result == "PASS"
    assert task.evidence_reference == "evidence/T-1.json"


def test_dispatch_executes_independent_handlers_concurrently():
    coordinator = MultiAgentCoordinator(max_workers=2)
    task = AgentTask("T-PAR", "parallel audit")
    barrier = threading.Barrier(2)

    def handler(agent_id):
        def run(current):
            barrier.wait(timeout=1)
            return AgentResult(agent_id, current.task_id, "PASS", evidence_reference="evidence/T-PAR.json")

        return run

    results = coordinator.dispatch(task, {"architect": handler("architect"), "security": handler("security")})
    assert [result.agent_id for result in results] == ["architect", "security"]


def test_failed_agent_blocks_completion():
    coordinator = MultiAgentCoordinator()
    task = AgentTask("T-2", "test")
    task.state = TaskState.RUNNING
    coordinator.verify_and_complete(task, [AgentResult("tester", task.task_id, "FAIL")])
    assert task.state == TaskState.BLOCKED


def test_completion_requires_running_state():
    coordinator = MultiAgentCoordinator()
    task = AgentTask("T-STATE", "test")
    result = AgentResult("tester", task.task_id, "PASS", evidence_reference="evidence/T-STATE.json")
    coordinator.verify_and_complete(task, [result])
    assert task.state == TaskState.BLOCKED


def test_result_identity_mismatch_blocks_task():
    coordinator = MultiAgentCoordinator()
    task = AgentTask("T-ID", "test")
    with pytest.raises(ValueError):
        coordinator.dispatch(task, {"tester": lambda current: AgentResult("security", current.task_id, "PASS")})
    assert task.state == TaskState.BLOCKED


def test_critical_task_is_blocked():
    coordinator = MultiAgentCoordinator()
    task = AgentTask("T-3", "production mutation", risk=Risk.CRITICAL)
    result = coordinator.dispatch(task, {})
    assert task.state == TaskState.BLOCKED
    assert result[0].status == "BLOCKED"


def test_production_write_is_never_authorized():
    assert MultiAgentCoordinator.production_write_allowed() is False


def test_github_bridge_requires_explicit_publish_gate():
    publisher = object()
    bridge = GatedGitHubBridge(publisher, allow_publish=False)
    changes = ChangeSet("T-4", "feat/example", "fix: example", ("x.py",), "evidence/T-4.json")
    with pytest.raises(PermissionError):
        bridge.publish(changes)
