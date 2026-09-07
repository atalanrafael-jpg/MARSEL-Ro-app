"""Safe multi-agent orchestration for MARSEL ROAPP.

The runtime coordinates specialist agents but keeps production mutation disabled by
construction. Agents return plans/results; a separate GitHub bridge may publish
approved branch changes and PR metadata.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable


class Risk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TaskState(str, Enum):
    PLANNED = "PLANNED"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    VERIFIED = "VERIFIED"
    DONE = "DONE"


@dataclass(frozen=True)
class AgentSpec:
    agent_id: str
    domain: str
    permissions: frozenset[str] = frozenset({"read", "plan", "test", "document"})


@dataclass
class AgentTask:
    task_id: str
    objective: str
    risk: Risk = Risk.MEDIUM
    state: TaskState = TaskState.PLANNED
    evidence_reference: str | None = None
    verification_result: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentResult:
    agent_id: str
    task_id: str
    status: str
    findings: tuple[str, ...] = ()
    proposed_changes: tuple[str, ...] = ()
    evidence_reference: str | None = None


class MultiAgentCoordinator:
    """Run independent specialists, then gate aggregation and completion."""

    DEFAULT_AGENTS = (
        AgentSpec("architect", "architecture"),
        AgentSpec("security", "security"),
        AgentSpec("data_integrity", "data-integrity"),
        AgentSpec("integration", "integrations"),
        AgentSpec("tester", "testing"),
        AgentSpec("verifier", "verification"),
        AgentSpec("documenter", "documentation"),
        AgentSpec("github", "change-management", frozenset({"read", "plan", "publish_branch", "open_pr"})),
    )

    def __init__(self, agents: Iterable[AgentSpec] | None = None) -> None:
        self.agents = {a.agent_id: a for a in (agents or self.DEFAULT_AGENTS)}

    def dispatch(
        self,
        task: AgentTask,
        handlers: dict[str, Callable[[AgentTask], AgentResult]],
    ) -> list[AgentResult]:
        if task.state != TaskState.PLANNED:
            raise ValueError("task must start in PLANNED state")
        if task.risk == Risk.CRITICAL:
            task.state = TaskState.BLOCKED
            return [AgentResult("coordinator", task.task_id, "BLOCKED", ("critical risk requires explicit external authorization",))]
        task.state = TaskState.RUNNING
        results: list[AgentResult] = []
        for agent_id, handler in handlers.items():
            if agent_id not in self.agents:
                raise KeyError(f"unknown agent: {agent_id}")
            results.append(handler(task))
        return results

    @staticmethod
    def verify_and_complete(task: AgentTask, results: Iterable[AgentResult]) -> AgentTask:
        results = list(results)
        if not results or any(r.status != "PASS" for r in results):
            task.state = TaskState.BLOCKED
            return task
        evidence = next((r.evidence_reference for r in results if r.evidence_reference), None)
        if not evidence:
            task.state = TaskState.BLOCKED
            return task
        task.evidence_reference = evidence
        task.verification_result = "PASS"
        task.state = TaskState.VERIFIED
        task.state = TaskState.DONE
        return task

    @staticmethod
    def production_write_allowed() -> bool:
        """Hard safety invariant: orchestration never authorizes production WRITE."""
        return False
