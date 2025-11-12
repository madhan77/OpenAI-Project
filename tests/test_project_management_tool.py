"""Tests for the project management toolkit."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Iterator

import pytest

from project_management import (
    InMemoryProjectRepository,
    Priority,
    ProjectManagementService,
    TaskStatus,
)


def sequence_ids(prefix: str) -> Iterator[str]:
    counter = 0
    while True:
        counter += 1
        yield f"{prefix}-{counter}"


def make_generators(prefix: str):
    ids = sequence_ids(prefix)

    def generator() -> str:
        return next(ids)

    return generator


def test_project_lifecycle():
    project_id_gen = make_generators("proj")
    task_id_gen = make_generators("task")
    service = ProjectManagementService(
        InMemoryProjectRepository(),
        project_id_generator=project_id_gen,
        task_id_generator=task_id_gen,
    )

    project = service.create_project(
        name="Claims Portal Overhaul",
        description="Rebuild reviewer experience to align with new workflows",
        owner="nina",
        start_date=date(2024, 5, 1),
        due_date=date(2024, 8, 30),
    )
    assert project.id == "proj-1"

    backlog = service.add_task(
        project.id,
        title="Define user journey",
        description="Document reviewer scenarios and QA flows",
        assignee="alex",
        due_date=date(2024, 5, 15),
        priority=Priority.HIGH,
    )
    implementation = service.add_task(
        project.id,
        title="Build UI components",
        description="Implement dashboard, claim detail, and notifications",
        assignee="casey",
        status=TaskStatus.IN_PROGRESS,
        due_date=date(2024, 6, 30),
        dependencies=[backlog.id],
    )

    assert backlog.id == "task-1"
    assert implementation.dependencies == {"task-1"}

    service.update_task_status(backlog.id, TaskStatus.DONE)
    progress = service.project_progress(project.id)
    assert pytest.approx(progress, rel=1e-3) == 0.5

    overdue = service.overdue_tasks(project.id, today=date(2024, 6, 1))
    assert overdue == []

    service.update_task_status(implementation.id, TaskStatus.REVIEW)
    summary = service.project_summary(project.id)
    assert summary["total_tasks"] == 2
    assert summary["completed_tasks"] == 1
    assert summary["status_breakdown"][TaskStatus.REVIEW.value] == 1


def test_overdue_detection_and_assignment():
    project_id_gen = make_generators("proj")
    task_id_gen = make_generators("task")
    service = ProjectManagementService(
        project_id_generator=project_id_gen,
        task_id_generator=task_id_gen,
    )

    project = service.create_project(
        "Launch automation",
        "Operationalize nightly adjudication",
        owner="taylor",
        start_date=date(2024, 1, 2),
    )

    stale = service.add_task(
        project.id,
        title="Configure scheduler",
        description="Set up cronjobs and alerting",
        due_date=date.today() - timedelta(days=3),
    )

    service.assign_task(stale.id, "jamal")
    overdue = service.overdue_tasks(project.id)
    assert overdue[0].assignee == "jamal"
    assert service.project_progress(project.id) == 0

    service.update_task_status(stale.id, TaskStatus.DONE)
    assert service.project_progress(project.id) == 1
