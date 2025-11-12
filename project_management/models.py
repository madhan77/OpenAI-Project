"""Domain models for the project management tool."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Iterable, List, Optional, Set


class TaskStatus(str, Enum):
    """Enumerates the lifecycle states for a task."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    DONE = "done"


class Priority(str, Enum):
    """Represents relative ordering for work."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class Task:
    """Work item that belongs to a project."""

    id: str
    project_id: str
    title: str
    description: str
    assignee: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    due_date: Optional[date] = None
    dependencies: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def update_status(self, status: TaskStatus) -> None:
        self.status = status
        self.updated_at = datetime.utcnow()

    def assign(self, assignee: Optional[str]) -> None:
        self.assignee = assignee
        self.updated_at = datetime.utcnow()

    def set_dependencies(self, dependency_ids: Iterable[str]) -> None:
        self.dependencies = set(dependency_ids)
        self.updated_at = datetime.utcnow()


@dataclass(slots=True)
class Project:
    """Represents a project comprised of tasks."""

    id: str
    name: str
    description: str
    owner: str
    start_date: date
    due_date: Optional[date] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    @property
    def completed_tasks(self) -> List[Task]:
        return [task for task in self.tasks if task.status == TaskStatus.DONE]

    @property
    def active_tasks(self) -> List[Task]:
        return [task for task in self.tasks if task.status != TaskStatus.DONE]

    def progress(self) -> float:
        if not self.tasks:
            return 0.0
        return len(self.completed_tasks) / len(self.tasks)

    def overdue_tasks(self, today: Optional[date] = None) -> List[Task]:
        today = today or date.today()
        return [
            task
            for task in self.tasks
            if task.due_date and task.due_date < today and task.status != TaskStatus.DONE
        ]
