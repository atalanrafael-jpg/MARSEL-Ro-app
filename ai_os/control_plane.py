"""Deterministic MARSEL ROAPP Master Agent control-plane core.

This module is deliberately side-effect free: it performs no network calls,
secret handling, production writes, or deletions. Execution adapters must sit
behind explicit safety gates and provide direct evidence before completion.
"""
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any


class State(str, Enum):
    INBOX = "INBOX"
    VALIDATE = "VALIDATE"
    READ = "READ"
    ANALYZE = "ANALYZE"
    BACKUP_RESTORE_CHECK = "BACKUP_RESTORE_CHECK"
    DRY_RUN = "DRY_RUN"
    SAFETY_GATE = "SAFETY_GATE"
    WRITE = "WRITE"
    VERIFY = "VERIFY"
    LOG = "LOG"
    CHECKPOINT = "CHECKPOINT"
    NEXT = "NEXT"
    BLOCKED = "BLOCKED"
    DONE = "DONE"


class Permission(str, Enum):
    READ_ONLY = "read_only"
    WRITE = "write"


CANONICAL_PIPELINE = (
    State.INBOX,
    State.VALIDATE,
    State.READ,
    State.ANALYZE,
    State.BACKUP_RESTORE_CHECK,
    State.DRY_RUN,
    State.SAFETY_GATE,
    State.WRITE,
    State.VERIFY,
    State.LOG,
    State.CHECKPOINT,
    State.NEXT,
)

# WRITE is reachable only after SAFETY_GATE. A task that starts read-only is
# never silently promoted to WRITE; callers must explicitly change permission.
ALLOWED = {
    State.INBOX: {State.VALIDATE, State.BLOCKED},
    State.VALIDATE: {State.READ, State.BLOCKED},
    State.READ: {State.ANALYZE, State.BLOCKED},
    State.ANALYZE: {State.BACKUP_RESTORE_CHECK, State.BLOCKED},
    State.BACKUP_RESTORE_CHECK: {State.DRY_RUN, State.BLOCKED},
    State.DRY_RUN: {State.SAFETY_GATE, State.BLOCKED},
    State.SAFETY_GATE: {State.WRITE, State.VERIFY, State.BLOCKED},
    State.WRITE: {State.VERIFY, State.BLOCKED},
    State.VERIFY: {State.LOG, State.ANALYZE, State.BLOCKED},
    State.LOG: {State.CHECKPOINT, State.BLOCKED},
    State.CHECKPOINT: {State.NEXT, State.BLOCKED},
    State.NEXT: {State.DONE, State.VALIDATE, State.BLOCKED},
    State.BLOCKED: {State.VALIDATE, State.READ},
    State.DONE: set(),
}


REQUEST_KINDS = {
    "web": "web",
    "app": "app",
    "api": "api",
    "integration": "integration",
    "automation": "automation",
    "ai": "ai",
    "data": "data",
    "database": "database",
    "ci": "ci",
    "infrastructure": "infrastructure",
    "backup": "backup",
    "restore": "restore",
    "security": "security",
    "audit": "audit",
    "unknown": "unknown",
}


def classify_request(kind: str) -> str:
    """Normalize a request category without guessing an unknown category."""
    normalized = str(kind).strip().lower()
    return REQUEST_KINDS.get(normalized, "unknown")


def route_language(kind: str) -> str:
    mapping = {
        "web": "typescript",
        "app": "typescript",
        "api": "typescript",
        "integration": "typescript",
        "automation": "python",
        "ai": "python",
        "data": "python",
        "database": "sql",
        "ci": "shell",
        "infrastructure": "shell",
        "backup": "python",
        "restore": "python",
        "security": "python",
        "audit": "python",
    }
    return mapping.get(classify_request(kind), "python")


@dataclass
class Task:
    task_id: str
    objective: str
    state: State = State.INBOX
    permission: Permission = Permission.READ_ONLY
    evidence: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def transition(self, target: State) -> None:
        if target not in ALLOWED[self.state]:
            raise ValueError(f"Invalid transition: {self.state} -> {target}")
        if target == State.WRITE and self.permission is not Permission.WRITE:
            raise ValueError("WRITE requires explicit write permission")
        if target == State.DONE and not self.evidence:
            raise ValueError("DONE requires evidence")
        self.state = target

    def add_evidence(self, reference: str) -> None:
        reference = str(reference).strip()
        if not reference:
            raise ValueError("Evidence reference cannot be empty")
        self.evidence.append(reference)

    def grant_write(self, *, safety_gate_passed: bool) -> None:
        """Explicitly opt a task into WRITE; never inferred from state."""
        if not safety_gate_passed:
            raise ValueError("WRITE permission requires a passed safety gate")
        if self.state is not State.SAFETY_GATE:
            raise ValueError("WRITE permission can only be granted at SAFETY_GATE")
        self.permission = Permission.WRITE

    def fail_verification(self, reason: str) -> None:
        reason = str(reason).strip()
        if not reason:
            raise ValueError("Verification failure reason cannot be empty")
        self.metadata["verification_failure"] = reason
        self.transition(State.ANALYZE)

    def checkpoint(self) -> str:
        """Return a deterministic checkpoint digest for the current task state."""
        payload = {
            "task_id": self.task_id,
            "objective": self.objective,
            "state": self.state.value,
            "permission": self.permission.value,
            "evidence": list(self.evidence),
            "metadata": self.metadata,
        }
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
