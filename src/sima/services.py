"""Domain services for orchestrating Single Issue Management workflows."""
from __future__ import annotations

from datetime import timedelta
from typing import Dict, List

from .models import (
    EscalationRequest,
    Issue,
    IssueDraft,
    IssueStatus,
    IssueUpdate,
    IssueView,
    PostMortem,
    PostMortemDraft,
    Severity,
    Task,
    TaskDraft,
    TaskUpdate,
    TimelineAudience,
    TimelineEvent,
    TimelineEventDraft,
)
from .repository import IssueQuery, IssueRepository


class IssueService:
    """High-level operations for managing issues and related artifacts."""

    DUPLICATE_DETECTION_WINDOW = timedelta(hours=12)

    def __init__(self, repository: IssueRepository | None = None) -> None:
        self.repository = repository or IssueRepository()

    def create_issue(self, draft: IssueDraft) -> Issue:
        duplicate = self.repository.detect_duplicate(
            title=draft.title,
            impacted_assets=draft.impacted_assets,
            window=self.DUPLICATE_DETECTION_WINDOW,
        )
        if duplicate:
            raise DuplicateIssueError(duplicate.id)
        issue = Issue.from_draft(draft)
        self.repository.add(issue)
        return issue

    def list_issues(self, query: IssueQuery) -> List[IssueView]:
        return [IssueView.from_issue(issue) for issue in self.repository.filter(query)]

    def get_issue(self, issue_id: str) -> Issue:
        issue = self.repository.get(issue_id)
        if not issue:
            raise IssueNotFoundError(issue_id)
        return issue

    def update_issue(self, issue_id: str, update: IssueUpdate) -> Issue:
        issue = self.get_issue(issue_id)
        updated = issue.with_updates(update)
        self.repository.update(updated)
        return updated

    def add_task(self, issue_id: str, draft: TaskDraft) -> Task:
        issue = self.get_issue(issue_id)
        task = Task.from_draft(draft)
        updated = issue.add_task(task)
        self.repository.update(updated)
        return task

    def update_task(self, issue_id: str, task_id: str, update: TaskUpdate) -> Task:
        issue = self.get_issue(issue_id)
        try:
            updated_issue = issue.update_task(task_id, update)
        except KeyError as exc:  # pragma: no cover - defensive
            raise TaskNotFoundError(task_id) from exc
        self.repository.update(updated_issue)
        for task in updated_issue.tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(task_id)  # pragma: no cover - should not happen

    def add_timeline_event(self, issue_id: str, draft: TimelineEventDraft) -> TimelineEvent:
        issue = self.get_issue(issue_id)
        event = TimelineEvent.from_draft(draft)
        updated = issue.add_timeline_event(event)
        self.repository.update(updated)
        return event

    def escalate_issue(self, issue_id: str, request: EscalationRequest) -> Issue:
        issue = self.get_issue(issue_id)
        if issue.escalated_at:
            return issue
        escalation_event = TimelineEvent.from_draft(
            TimelineEventDraft(
                message=f"Escalation approved by {request.approver}: {request.reason}",
                author="system",
                audience=TimelineAudience.INTERNAL,
            )
        )
        updated = issue.mark_escalated().add_timeline_event(escalation_event)
        self.repository.update(updated)
        return updated

    def attach_postmortem(self, issue_id: str, author: str, draft: PostMortemDraft) -> PostMortem:
        issue = self.get_issue(issue_id)
        postmortem = PostMortem.from_draft(author, draft)
        updated = issue.attach_postmortem(postmortem)
        self.repository.update(updated)
        return postmortem

    def analytics_snapshot(self) -> Dict[str, object]:
        issues = list(self.repository.all())
        totals: Dict[str, int] = {status.value: 0 for status in IssueStatus}
        severity_totals: Dict[str, int] = {severity.value: 0 for severity in Severity}
        breached = 0
        for issue in issues:
            totals[issue.status.value] += 1
            severity_totals[issue.severity.value] += 1
            if issue.sla_breached():
                breached += 1
        return {
            "total_issues": len(issues),
            "status_breakdown": totals,
            "severity_breakdown": severity_totals,
            "sla_breaches": breached,
        }


class IssueServiceError(RuntimeError):
    """Base error for service-level issues."""


class IssueNotFoundError(IssueServiceError):
    def __init__(self, issue_id: str) -> None:
        super().__init__(f"Issue {issue_id} was not found")
        self.issue_id = issue_id


class DuplicateIssueError(IssueServiceError):
    def __init__(self, duplicate_issue_id: str) -> None:
        super().__init__("Duplicate issue detected")
        self.duplicate_issue_id = duplicate_issue_id


class TaskNotFoundError(IssueServiceError):
    def __init__(self, task_id: str) -> None:
        super().__init__(f"Task {task_id} was not found")
        self.task_id = task_id
