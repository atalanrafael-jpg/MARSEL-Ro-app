from dataclasses import dataclass, field
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
        if status == TaskStatus.DONE and not task.evidence:
            raise ValueError("DONE requires evidence")
        task.status = status
    def add_evidence(self, task: Task, evidence: dict[str, Any]) -> None:
        required = {"requested_action", "actual_action", "result"}
        if not required.issubset(evidence):
            raise ValueError("Incomplete evidence")
        task.evidence.append(evidence)
