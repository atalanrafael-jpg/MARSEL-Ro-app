import pytest

from agent_runtime import AgentRuntime, Task, TaskStatus


def task():
    return Task(task_id="t-1", project="MARSEL_ROAPP", task_type="audit")


def evidence(verification_result="PASS"):
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


def test_known_project_routes():
    t = task()
    assert AgentRuntime().route(t)["project"] == "MARSEL_ROAPP"


def test_unknown_project_blocks():
    t = Task(task_id="t-1", project="UNKNOWN", task_type="audit")
    assert AgentRuntime().route(t)["status"] == "BLOCKED"


def test_done_requires_verifying_state():
    t = task()
    runtime = AgentRuntime()
    runtime.add_evidence(t, evidence())
    with pytest.raises(ValueError, match="Invalid transition"):
        runtime.transition(t, TaskStatus.DONE)


def test_done_requires_pass_verification():
    t = task()
    runtime = AgentRuntime()
    runtime.transition(t, TaskStatus.ASSIGNED)
    runtime.transition(t, TaskStatus.ANALYZING)
    runtime.transition(t, TaskStatus.EXECUTING)
    runtime.transition(t, TaskStatus.VERIFYING)
    runtime.add_evidence(t, evidence("FAIL"))
    with pytest.raises(ValueError, match="verification_result=PASS"):
        runtime.transition(t, TaskStatus.DONE)


def test_valid_verifying_to_done():
    t = task()
    runtime = AgentRuntime()
    for status in (TaskStatus.ASSIGNED, TaskStatus.ANALYZING, TaskStatus.EXECUTING, TaskStatus.VERIFYING):
        runtime.transition(t, status)
    runtime.add_evidence(t, evidence())
    runtime.transition(t, TaskStatus.DONE)
    assert t.status is TaskStatus.DONE


def test_evidence_requires_full_schema():
    t = task()
    with pytest.raises(ValueError, match="Incomplete evidence"):
        AgentRuntime().add_evidence(t, {"task_id": "t-1", "result": "ok"})


def test_evidence_task_id_must_match():
    t = task()
    item = evidence()
    item["task_id"] = "other"
    with pytest.raises(ValueError, match="does not match"):
        AgentRuntime().add_evidence(t, item)
