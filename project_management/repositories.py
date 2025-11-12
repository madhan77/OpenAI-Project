"""Repositories for persisting project management data."""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, Iterable, Optional

from .models import Project, Task


class ProjectNotFoundError(KeyError):
    """Raised when a project lookup fails."""


class TaskNotFoundError(KeyError):
    """Raised when a task lookup fails."""


class InMemoryProjectRepository:
    """Simple repository storing projects and tasks in memory."""

    def __init__(self) -> None:
        self._projects: Dict[str, Project] = {}
        self._tasks: Dict[str, Task] = {}

    # Project operations
    def add_project(self, project: Project) -> None:
        self._projects[project.id] = project

    def get_project(self, project_id: str) -> Project:
        try:
            return self._projects[project_id]
        except KeyError as exc:
            raise ProjectNotFoundError(project_id) from exc

    def list_projects(self) -> Iterable[Project]:
        return self._projects.values()

    # Task operations
    def add_task(self, task: Task) -> None:
        self._tasks[task.id] = task
        project = self.get_project(task.project_id)
        project.add_task(task)

    def get_task(self, task_id: str) -> Task:
        try:
            return self._tasks[task_id]
        except KeyError as exc:
            raise TaskNotFoundError(task_id) from exc

    def update_task(self, task: Task) -> Task:
        if task.id not in self._tasks:
            raise TaskNotFoundError(task.id)
        self._tasks[task.id] = task
        project = self.get_project(task.project_id)
        project.tasks = [existing if existing.id != task.id else task for existing in project.tasks]
        return task

    def replace_task(self, task_id: str, **changes) -> Task:
        task = self.get_task(task_id)
        updated = replace(task, **changes)
        return self.update_task(updated)

    def list_tasks_for_project(self, project_id: str) -> Iterable[Task]:
        project = self.get_project(project_id)
        return project.tasks

    def find_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)
