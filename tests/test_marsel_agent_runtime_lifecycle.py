import pytest

from agent_runtime import AgentRuntime, Task, TaskStatus


def make_task():
    return Task(task_id="t-1", project="MARSEL_ROAPP", task_type="audit")


def make_evidence(verification_result="PASS"):
    return {
        "task_id": "t-1",
        "agent_id": "agent-1",
        "timestamp": AgentRuntime.make_timestamp(),
        "requested_action": "audit",
        "actual_action": "read-only audit",
        "tool_or_system": "GitHub",
        "result": "ok",
        "evidence_reference": "run://test-1",
        "verifier": "test-suite",
        "verification_result": verification_result,
    }


def test_only_marsel_roapp_project_is_routable():
    assert AgentRuntime().route(make_task())["project"] == "MARSEL_ROAPP"
    unknown = Task(task_id="t-2", project="OTHER_PROJECT", task_type="audit")
    assert AgentRuntime().route(unknown)["status"] == "BLOCKED"


def test_done_requires_verifying_state():
    task = make_task()
    runtime = AgentRuntime()
    runtime.add_evidence(task, make_evidence())
    with pytest.raises(ValueError, match="Invalid transition"):
        runtime.transition(task, TaskStatus.DONE)


def test_done_requires_pass_and_evidence_reference():
    task = make_task()
    runtime = AgentRuntime()
    for status in (TaskStatus.ASSIGNED, TaskStatus.ANALYZING, TaskStatus.EXECUTING, TaskStatus.VERIFYING):
        runtime.transition(task, status)
    runtime.add_evidence(task, make_evidence("FAIL"))
    with pytest.raises(ValueError, match="verification_result=PASS"):
        runtime.transition(task, TaskStatus.DONE)


def test_valid_verifying_to_done():
    task = make_task()
    runtime = AgentRuntime()
    for status in (TaskStatus.ASSIGNED, TaskStatus.ANALYZING, TaskStatus.EXECUTING, TaskStatus.VERIFYING):
        runtime.transition(task, status)
    runtime.add_evidence(task, make_evidence())
    runtime.transition(task, TaskStatus.DONE)
    assert task.status is TaskStatus.DONE


def test_evidence_task_id_must_match():
    task = make_task()
    evidence = make_evidence()
    evidence["task_id"] = "other"
    with pytest.raises(ValueError, match="does not match"):
        AgentRuntime().add_evidence(task, evidence)
