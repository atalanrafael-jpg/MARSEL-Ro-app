import pytest
from agent_runtime.runtime import AgentRuntime, Task, TaskStatus

def test_known_project_routes():
    task = Task("1", "CHATGPT_CORE", "audit")
    assert AgentRuntime().route(task)["project"] == "CHATGPT_CORE"

def test_unknown_project_blocks():
    task = Task("1", "UNKNOWN", "audit")
    result = AgentRuntime().route(task)
    assert result["status"] == "BLOCKED"

def test_done_requires_evidence():
    task = Task("1", "CHATGPT_CORE", "audit")
    with pytest.raises(ValueError):
        AgentRuntime().transition(task, TaskStatus.DONE)

def test_done_with_evidence():
    runtime = AgentRuntime()
    task = Task("1", "CHATGPT_CORE", "audit")
    runtime.add_evidence(task, {"requested_action":"audit","actual_action":"audit","result":"PASS"})
    runtime.transition(task, TaskStatus.DONE)
    assert task.status == TaskStatus.DONE
