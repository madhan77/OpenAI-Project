"""High level orchestration for the project management tool."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
from typing import Callable, Dict, Iterable, List, Optional
from uuid import uuid4

from .models import Priority, Project, Task, TaskStatus
from .repositories import InMemoryProjectRepository, ProjectNotFoundError, TaskNotFoundError


IdGenerator = Callable[[], str]


def default_id() -> str:
    return uuid4().hex


class ProjectManagementService:
    """Coordinates project and task operations with progress analytics."""

    def __init__(
        self,
        repository: Optional[InMemoryProjectRepository] = None,
        project_id_generator: IdGenerator = default_id,
        task_id_generator: IdGenerator = default_id,
    ) -> None:
        self.repository = repository or InMemoryProjectRepository()
        self._project_id_generator = project_id_generator
        self._task_id_generator = task_id_generator

    # Project APIs
    def create_project(
        self,
        name: str,
        description: str,
        owner: str,
        start_date: date,
        due_date: Optional[date] = None,
    ) -> Project:
        project = Project(
            id=self._project_id_generator(),
            name=name,
            description=description,
            owner=owner,
            start_date=start_date,
            due_date=due_date,
        )
        self.repository.add_project(project)
        return project

    def get_project(self, project_id: str) -> Project:
        return self.repository.get_project(project_id)

    def list_projects(self) -> Iterable[Project]:
        return self.repository.list_projects()

    # Task APIs
    def add_task(
        self,
        project_id: str,
        title: str,
        description: str,
        *,
        assignee: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        status: TaskStatus = TaskStatus.TODO,
        due_date: Optional[date] = None,
        dependencies: Optional[Iterable[str]] = None,
    ) -> Task:
        self._ensure_project_exists(project_id)
        task = Task(
            id=self._task_id_generator(),
            project_id=project_id,
            title=title,
            description=description,
            assignee=assignee,
            priority=priority,
            status=status,
            due_date=due_date,
        )
        if dependencies:
            task.set_dependencies(dependencies)
        self.repository.add_task(task)
        return task

    def assign_task(self, task_id: str, assignee: Optional[str]) -> Task:
        task = self.repository.get_task(task_id)
        task.assign(assignee)
        return self.repository.update_task(task)

    def update_task_status(self, task_id: str, status: TaskStatus) -> Task:
        task = self.repository.get_task(task_id)
        task.update_status(status)
        return self.repository.update_task(task)

    def set_task_dependencies(self, task_id: str, dependency_ids: Iterable[str]) -> Task:
        task = self.repository.get_task(task_id)
        task.set_dependencies(dependency_ids)
        return self.repository.update_task(task)

    def get_task(self, task_id: str) -> Task:
        return self.repository.get_task(task_id)

    def list_tasks_for_project(self, project_id: str) -> Iterable[Task]:
        return self.repository.list_tasks_for_project(project_id)

    # Insights
    def project_progress(self, project_id: str) -> float:
        project = self.repository.get_project(project_id)
        return project.progress()

    def overdue_tasks(self, project_id: str, today: Optional[date] = None) -> List[Task]:
        project = self.repository.get_project(project_id)
        return project.overdue_tasks(today)

    def project_summary(self, project_id: str) -> Dict[str, object]:
        project = self.repository.get_project(project_id)
        total_tasks = len(project.tasks)
        completed = len(project.completed_tasks)
        statuses: Dict[TaskStatus, int] = {status: 0 for status in TaskStatus}
        for task in project.tasks:
            statuses[task.status] += 1
        return {
            "project": asdict(project),
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "progress_percent": round(project.progress() * 100, 2),
            "status_breakdown": {status.value: count for status, count in statuses.items()},
            "overdue_tasks": [task.id for task in project.overdue_tasks()],
        }

    def _ensure_project_exists(self, project_id: str) -> None:
        try:
            self.repository.get_project(project_id)
        except ProjectNotFoundError as exc:
            raise ProjectNotFoundError(f"Project '{project_id}' does not exist") from exc


__all__ = [
    "ProjectManagementService",
    "ProjectNotFoundError",
    "TaskNotFoundError",
]
