"""Core domain models for the Single Issue Management App."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional
from uuid import uuid4


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueStatus(Enum):
    NEW = "new"
    TRIAGE = "triage"
    IN_PROGRESS = "in_progress"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"


class TimelineAudience(Enum):
    INTERNAL = "internal"
    CUSTOMER = "customer"
    SYSTEM = "system"


@dataclass(slots=True)
class IssueDraft:
    title: str
    description: str
    severity: Severity
    impact_summary: str
    customer: str
    category: str
    impacted_assets: List[str] = field(default_factory=list)
    sla_minutes: int = 60
    owner: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.title or len(self.title) < 3:
            raise ValueError("title must be at least 3 characters long")
        if not self.description or len(self.description) < 10:
            raise ValueError("description must be at least 10 characters long")
        if not (0 < self.sla_minutes <= 7 * 24 * 60):
            raise ValueError("sla_minutes must be between 1 minute and 7 days")
        if len(self.attachments) > 5:
            raise ValueError("a maximum of five attachment references is supported")


@dataclass(slots=True)
class IssueUpdate:
    status: Optional[IssueStatus] = None
    severity: Optional[Severity] = None
    owner: Optional[str] = None
    tags: Optional[List[str]] = None
    impact_summary: Optional[str] = None


@dataclass(slots=True)
class TaskDraft:
    title: str
    description: Optional[str] = None
    owner: Optional[str] = None
    due_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if not self.title or len(self.title) < 3:
            raise ValueError("task title must be at least 3 characters long")


@dataclass(slots=True)
class TaskUpdate:
    title: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    due_at: Optional[datetime] = None
    status: Optional[TaskStatus] = None


@dataclass(slots=True)
class TimelineEventDraft:
    message: str
    author: str
    audience: TimelineAudience = TimelineAudience.INTERNAL

    def __post_init__(self) -> None:
        if not self.message or len(self.message) < 3:
            raise ValueError("timeline message must be at least 3 characters long")
        if not self.author or len(self.author) < 2:
            raise ValueError("author must be at least 2 characters long")


@dataclass(slots=True)
class EscalationRequest:
    reason: str
    approver: str

    def __post_init__(self) -> None:
        if len(self.reason) < 5:
            raise ValueError("reason must be at least 5 characters long")
        if len(self.approver) < 2:
            raise ValueError("approver must be at least 2 characters long")


@dataclass(slots=True)
class PostMortemDraft:
    root_cause: str
    remediation: str
    preventive_actions: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.root_cause) < 5:
            raise ValueError("root cause must be at least 5 characters long")
        if len(self.remediation) < 5:
            raise ValueError("remediation must be at least 5 characters long")


@dataclass(slots=True)
class TimelineEvent:
    id: str
    message: str
    author: str
    audience: TimelineAudience
    created_at: datetime

    @classmethod
    def from_draft(cls, draft: TimelineEventDraft) -> "TimelineEvent":
        return cls(
            id=str(uuid4()),
            message=draft.message,
            author=draft.author,
            audience=draft.audience,
            created_at=datetime.utcnow(),
        )


@dataclass(slots=True)
class Task:
    id: str
    title: str
    description: Optional[str]
    owner: Optional[str]
    due_at: Optional[datetime]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    @classmethod
    def from_draft(cls, draft: TaskDraft) -> "Task":
        now = datetime.utcnow()
        return cls(
            id=str(uuid4()),
            title=draft.title,
            description=draft.description,
            owner=draft.owner,
            due_at=draft.due_at,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

    def apply_update(self, update: TaskUpdate) -> "Task":
        new_status = update.status or self.status
        completed_at = self.completed_at
        if new_status == TaskStatus.COMPLETED and self.status != TaskStatus.COMPLETED:
            completed_at = datetime.utcnow()
        elif new_status != TaskStatus.COMPLETED:
            completed_at = None
        return replace(
            self,
            title=update.title or self.title,
            description=update.description if update.description is not None else self.description,
            owner=update.owner if update.owner is not None else self.owner,
            due_at=update.due_at if update.due_at is not None else self.due_at,
            status=new_status,
            updated_at=datetime.utcnow(),
            completed_at=completed_at,
        )


@dataclass(slots=True)
class PostMortem:
    created_at: datetime
    author: str
    root_cause: str
    remediation: str
    preventive_actions: List[str]

    @classmethod
    def from_draft(cls, author: str, draft: PostMortemDraft) -> "PostMortem":
        return cls(
            created_at=datetime.utcnow(),
            author=author,
            root_cause=draft.root_cause,
            remediation=draft.remediation,
            preventive_actions=list(draft.preventive_actions),
        )


@dataclass(slots=True)
class Issue:
    id: str
    title: str
    description: str
    severity: Severity
    impact_summary: str
    customer: str
    category: str
    impacted_assets: List[str]
    sla_minutes: int
    owner: Optional[str]
    status: IssueStatus
    tags: List[str]
    attachments: List[str]
    created_at: datetime
    updated_at: datetime
    due_at: datetime
    escalated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    timeline: List[TimelineEvent] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    postmortem: Optional[PostMortem] = None

    @classmethod
    def from_draft(cls, draft: IssueDraft) -> "Issue":
        now = datetime.utcnow()
        return cls(
            id=str(uuid4()),
            title=draft.title,
            description=draft.description,
            severity=draft.severity,
            impact_summary=draft.impact_summary,
            customer=draft.customer,
            category=draft.category,
            impacted_assets=list(draft.impacted_assets),
            sla_minutes=draft.sla_minutes,
            owner=draft.owner,
            status=IssueStatus.NEW,
            tags=list(draft.tags),
            attachments=list(draft.attachments),
            created_at=now,
            updated_at=now,
            due_at=now + timedelta(minutes=draft.sla_minutes),
        )

    def with_updates(self, update: IssueUpdate) -> "Issue":
        new_status = update.status or self.status
        resolved_at = self.resolved_at
        if new_status in {IssueStatus.RESOLVED, IssueStatus.CLOSED} and self.resolved_at is None:
            resolved_at = datetime.utcnow()
        elif new_status not in {IssueStatus.RESOLVED, IssueStatus.CLOSED}:
            resolved_at = None
        return replace(
            self,
            status=new_status,
            severity=update.severity or self.severity,
            owner=update.owner if update.owner is not None else self.owner,
            tags=list(update.tags) if update.tags is not None else self.tags,
            impact_summary=update.impact_summary if update.impact_summary is not None else self.impact_summary,
            resolved_at=resolved_at,
            updated_at=datetime.utcnow(),
        )

    def add_task(self, task: Task) -> "Issue":
        return replace(self, tasks=[*self.tasks, task], updated_at=datetime.utcnow())

    def add_timeline_event(self, event: TimelineEvent) -> "Issue":
        return replace(self, timeline=[*self.timeline, event], updated_at=datetime.utcnow())

    def update_task(self, task_id: str, update: TaskUpdate) -> "Issue":
        updated_tasks: List[Task] = []
        found = False
        for task in self.tasks:
            if task.id == task_id:
                updated_tasks.append(task.apply_update(update))
                found = True
            else:
                updated_tasks.append(task)
        if not found:
            raise KeyError(task_id)
        return replace(self, tasks=updated_tasks, updated_at=datetime.utcnow())

    def mark_escalated(self) -> "Issue":
        if self.escalated_at:
            return self
        return replace(self, escalated_at=datetime.utcnow(), updated_at=datetime.utcnow())

    def attach_postmortem(self, postmortem: PostMortem) -> "Issue":
        return replace(self, postmortem=postmortem, updated_at=datetime.utcnow())

    def sla_breached(self, reference: Optional[datetime] = None) -> bool:
        reference = reference or datetime.utcnow()
        if self.status in {IssueStatus.RESOLVED, IssueStatus.CLOSED}:
            if not self.resolved_at:
                return False
            return self.resolved_at > self.due_at
        return reference > self.due_at


@dataclass(slots=True)
class IssueView:
    id: str
    title: str
    description: str
    severity: str
    impact_summary: str
    customer: str
    category: str
    impacted_assets: List[str]
    sla_minutes: int
    owner: Optional[str]
    status: str
    tags: List[str]
    attachments: List[str]
    created_at: datetime
    updated_at: datetime
    due_at: datetime
    escalated_at: Optional[datetime]
    resolved_at: Optional[datetime]
    timeline: List[TimelineEvent]
    tasks: List[Task]
    postmortem: Optional[PostMortem]
    sla_breached: bool

    @classmethod
    def from_issue(cls, issue: Issue) -> "IssueView":
        return cls(
            id=issue.id,
            title=issue.title,
            description=issue.description,
            severity=issue.severity.value,
            impact_summary=issue.impact_summary,
            customer=issue.customer,
            category=issue.category,
            impacted_assets=list(issue.impacted_assets),
            sla_minutes=issue.sla_minutes,
            owner=issue.owner,
            status=issue.status.value,
            tags=list(issue.tags),
            attachments=list(issue.attachments),
            created_at=issue.created_at,
            updated_at=issue.updated_at,
            due_at=issue.due_at,
            escalated_at=issue.escalated_at,
            resolved_at=issue.resolved_at,
            timeline=list(issue.timeline),
            tasks=list(issue.tasks),
            postmortem=issue.postmortem,
            sla_breached=issue.sla_breached(),
        )
