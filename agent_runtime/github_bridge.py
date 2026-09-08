"""GitHub publication boundary for the multi-agent system.

This module intentionally does not contain credentials or direct production
mutation. A host integration supplies the actual GitHub implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ChangeSet:
    task_id: str
    branch: str
    commit_message: str
    changed_paths: tuple[str, ...]
    evidence_reference: str


class GitHubPublisher(Protocol):
    def create_branch(self, branch: str) -> None: ...
    def publish_changes(self, changes: ChangeSet) -> str: ...
    def open_pull_request(self, branch: str, title: str, body: str) -> str: ...


class GatedGitHubBridge:
    """Publish only to a feature branch and create a reviewable PR."""

    def __init__(self, publisher: GitHubPublisher, *, allow_publish: bool = False) -> None:
        self.publisher = publisher
        self.allow_publish = allow_publish

    def publish(self, changes: ChangeSet) -> str:
        if not self.allow_publish:
            raise PermissionError("GitHub publication is disabled")
        if not changes.branch or changes.branch in {"main", "master"}:
            raise PermissionError("agent changes must use a feature branch")
        if not changes.evidence_reference:
            raise PermissionError("evidence_reference is required")
        self.publisher.create_branch(changes.branch)
        return self.publisher.publish_changes(changes)

    def open_review(self, branch: str, title: str, body: str) -> str:
        if not self.allow_publish:
            raise PermissionError("GitHub publication is disabled")
        return self.publisher.open_pull_request(branch, title, body)
