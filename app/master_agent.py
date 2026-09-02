"""MARSEL ROAPP Master Agent control-plane runtime.

The runtime is intentionally dependency-free and fail-closed. It models and
validates the control pipeline but never performs production mutations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Mapping


class Mode(str, Enum):
    READ_ONLY = "READ_ONLY"
    DRY_RUN = "DRY_RUN"
    PROPOSE = "PROPOSE"
    WRITE = "WRITE"


class Status(str, Enum):
    READY = "READY"
    BLOCKED = "BLOCKED"
    DONE = "DONE"
    NOT_VERIFIED = "NOT_VERIFIED"


PIPELINE = (
    "REQUEST",
    "VALIDATE",
    "READ",
    "ANALYZE",
    "BACKUP_RESTORE_CHECK",
    "DRY_RUN",
    "SAFETY_GATE",
    "WRITE",
    "VERIFY",
    "LOG",
    "CHECKPOINT",
)


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    kind: str
    verified: bool
    source: str
    details: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentRequest:
    request_id: str
    action: str
    mode: Mode = Mode.READ_ONLY
    production: bool = False
    destructive: bool = False


@dataclass(frozen=True)
class AgentState:
    request: AgentRequest
    status: Status
    current_step: str
    reason: str | None = None
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Checkpoint:
    request_id: str
    status: Status
    current_step: str
    reason: str | None
    evidence_ids: tuple[str, ...]
    state_hash: str


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def state_hash(state: AgentState) -> str:
    payload = {
        "request": {
            "request_id": state.request.request_id,
            "action": state.request.action,
            "mode": state.request.mode.value,
            "production": state.request.production,
            "destructive": state.request.destructive,
        },
        "status": state.status.value,
        "current_step": state.current_step,
        "reason": state.reason,
        "evidence_ids": list(state.evidence_ids),
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def make_checkpoint(state: AgentState) -> Checkpoint:
    return Checkpoint(
        request_id=state.request.request_id,
        status=state.status,
        current_step=state.current_step,
        reason=state.reason,
        evidence_ids=state.evidence_ids,
        state_hash=state_hash(state),
    )


def _blocked(request: AgentRequest, step: str, reason: str, evidence: list[Evidence]) -> AgentState:
    return AgentState(
        request=request,
        status=Status.BLOCKED,
        current_step=step,
        reason=reason,
        evidence_ids=tuple(e.evidence_id for e in evidence),
    )


def execute(request: AgentRequest, evidence: list[Evidence] | None = None) -> tuple[AgentState, Checkpoint]:
    """Validate and advance a request through the safe control boundary.

    This function never executes WRITE. A WRITE request is stopped at the
    safety gate unless the caller explicitly supplies the required evidence;
    even then, the runtime returns BLOCKED because production mutation is not
    implemented in this stage.
    """
    evidence = list(evidence or [])
    if not request.request_id.strip():
        state = _blocked(request, "VALIDATE", "request_id_missing", evidence)
        return state, make_checkpoint(state)
    if not request.action.strip():
        state = _blocked(request, "VALIDATE", "action_missing", evidence)
        return state, make_checkpoint(state)
    if request.mode == Mode.WRITE or request.production:
        state = _blocked(request, "SAFETY_GATE", "production_write_not_implemented", evidence)
        return state, make_checkpoint(state)
    if request.destructive:
        state = _blocked(request, "SAFETY_GATE", "destructive_action_requires_explicit_gate", evidence)
        return state, make_checkpoint(state)
    if any(not e.verified for e in evidence):
        state = _blocked(request, "ANALYZE", "unverified_evidence_present", evidence)
        return state, make_checkpoint(state)

    state = AgentState(
        request=request,
        status=Status.DONE,
        current_step="CHECKPOINT",
        reason=None,
        evidence_ids=tuple(e.evidence_id for e in evidence),
    )
    return state, make_checkpoint(state)


def checkpoint_dict(checkpoint: Checkpoint) -> dict[str, Any]:
    """Return deterministic, audit-friendly checkpoint data."""
    return {
        "request_id": checkpoint.request_id,
        "status": checkpoint.status.value,
        "current_step": checkpoint.current_step,
        "reason": checkpoint.reason,
        "evidence_ids": list(checkpoint.evidence_ids),
        "state_hash": checkpoint.state_hash,
    }
