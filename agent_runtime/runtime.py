from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    IDLE = "IDLE"
    ASSIGNED = "ASSIGNED"
    ANALYZING = "ANALYZING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    DONE = "DONE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    RETRY = "RETRY"
    ROLLED_BACK = "ROLLED_BACK"


EVIDENCE_FIELDS = {
    "task_id", "agent_id", "timestamp", "requested_action", "actual_action",
    "tool_or_system", "result", "evidence_reference", "verifier", "verification_result",
}

ALLOWED_TRANSITIONS = {
    TaskStatus.IDLE: {TaskStatus.ASSIGNED, TaskStatus.BLOCKED, TaskStatus.FAILED},
    TaskStatus.ASSIGNED: {TaskStatus.ANALYZING, TaskStatus.BLOCKED, TaskStatus.FAILED},
    TaskStatus.ANALYZING: {TaskStatus.EXECUTING, TaskStatus.BLOCKED, TaskStatus.FAILED, TaskStatus.RETRY},
    TaskStatus.EXECUTING: {TaskStatus.VERIFYING, TaskStatus.BLOCKED, TaskStatus.FAILED, TaskStatus.RETRY, TaskStatus.ROLLED_BACK},
    TaskStatus.VERIFYING: {TaskStatus.DONE, TaskStatus.FAILED, TaskStatus.RETRY, TaskStatus.ROLLED_BACK},
    TaskStatus.DONE: set(),
    TaskStatus.BLOCKED: {TaskStatus.ASSIGNED, TaskStatus.FAILED},
    TaskStatus.FAILED: {TaskStatus.RETRY, TaskStatus.ROLLED_BACK},
    TaskStatus.RETRY: {TaskStatus.ASSIGNED, TaskStatus.ANALYZING, TaskStatus.EXECUTING, TaskStatus.FAILED},
    TaskStatus.ROLLED_BACK: {TaskStatus.FAILED, TaskStatus.ASSIGNED},
}


@dataclass
class Task:
    task_id: str
    project: str
    task_type: str
    risk_level: str = "LOW"
    status: TaskStatus = TaskStatus.IDLE
    evidence: list[dict[str, Any]] = field(default_factory=list)


class AgentRuntime:
    allowed_projects = {"CHATGPT_CORE", "RAFAEL_AI_OS", "MARSEL_ROAPP", "MARSEL_BUSINESS"}

    def route(self, task: Task) -> dict[str, str]:
        if task.project not in self.allowed_projects:
            task.status = TaskStatus.BLOCKED
            return {"status": task.status.value, "reason": "UNKNOWN_PROJECT"}
        return {"project": task.project, "task_type": task.task_type, "risk_level": task.risk_level}

    def transition(self, task: Task, status: TaskStatus) -> None:
        if status not in ALLOWED_TRANSITIONS[task.status]:
            raise ValueError(f"Invalid transition: {task.status.value} -> {status.value}")
        if status == TaskStatus.DONE:
            if not task.evidence:
                raise ValueError("DONE requires evidence")
            latest = task.evidence[-1]
            if latest.get("verification_result") != "PASS":
                raise ValueError("DONE requires verification_result=PASS")
            if not latest.get("evidence_reference"):
                raise ValueError("DONE requires evidence_reference")
        task.status = status

    def add_evidence(self, task: Task, evidence: dict[str, Any]) -> None:
        missing = EVIDENCE_FIELDS - evidence.keys()
        if missing:
            raise ValueError(f"Incomplete evidence: missing {sorted(missing)}")
        if evidence["task_id"] != task.task_id:
            raise ValueError("Evidence task_id does not match task")
        if not evidence["evidence_reference"]:
            raise ValueError("evidence_reference is required")
        if not evidence["verification_result"]:
            raise ValueError("verification_result is required")
        task.evidence.append(evidence)

    @staticmethod
    def make_timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()
