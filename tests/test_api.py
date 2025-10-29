from __future__ import annotations

from dataclasses import replace
import pathlib
import sys

import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from sima.models import (
    EscalationRequest,
    IssueDraft,
    IssueStatus,
    IssueUpdate,
    PostMortemDraft,
    Severity,
    TaskDraft,
    TaskStatus,
    TaskUpdate,
    TimelineAudience,
    TimelineEventDraft,
)
from sima.repository import IssueQuery
from sima.services import (
    DuplicateIssueError,
    IssueService,
    IssueServiceError,
    TaskNotFoundError,
)


@pytest.fixture()
def service() -> IssueService:
    return IssueService()


def _default_draft() -> IssueDraft:
    return IssueDraft(
        title="Critical outage",
        description="Primary database cluster unreachable impacting customers.",
        severity=Severity.CRITICAL,
        impact_summary="All users unable to login",
        customer="Acme Corp",
        category="infrastructure",
        impacted_assets=["db-cluster-1"],
        sla_minutes=120,
        owner="alice",
        tags=["database", "sev1"],
    )


def test_create_and_get_issue(service: IssueService) -> None:
    issue = service.create_issue(_default_draft())
    assert issue.title == "Critical outage"
    fetched = service.get_issue(issue.id)
    assert fetched.id == issue.id
    assert fetched.status == IssueStatus.NEW


def test_duplicate_detection(service: IssueService) -> None:
    service.create_issue(_default_draft())
    with pytest.raises(DuplicateIssueError):
        service.create_issue(_default_draft())


def test_task_lifecycle(service: IssueService) -> None:
    issue = service.create_issue(_default_draft())
    task = service.add_task(
        issue.id,
        TaskDraft(title="Diagnose database", description="Identify root cause", owner="bob"),
    )
    assert task.title == "Diagnose database"
    updated_task = service.update_task(
        issue.id,
        task.id,
        TaskUpdate(status=TaskStatus.IN_PROGRESS, owner="carol"),
    )
    assert updated_task.status == TaskStatus.IN_PROGRESS
    assert updated_task.owner == "carol"


def test_timeline_and_escalation(service: IssueService) -> None:
    issue = service.create_issue(_default_draft())
    event = service.add_timeline_event(
        issue.id,
        TimelineEventDraft(
            message="Customer notified of investigation",
            author="alice",
            audience=TimelineAudience.CUSTOMER,
        ),
    )
    assert event.audience == TimelineAudience.CUSTOMER

    escalated = service.escalate_issue(
        issue.id,
        EscalationRequest(reason="SLA risk", approver="ExecOnCall"),
    )
    assert escalated.escalated_at is not None
    assert any("Escalation approved" in e.message for e in escalated.timeline)


def test_postmortem_and_analytics(service: IssueService) -> None:
    issue = service.create_issue(_default_draft())
    postmortem = service.attach_postmortem(
        issue.id,
        author="dana",
        draft=PostMortemDraft(
            root_cause="Configuration drift",
            remediation="Reapply baseline",
            preventive_actions=["Automate config checks"],
        ),
    )
    assert postmortem.author == "dana"

    # Force SLA breach by manipulating stored issue
    stored = service.repository.get(issue.id)
    assert stored is not None
    service.repository.update(replace(stored, due_at=stored.created_at))

    analytics = service.analytics_snapshot()
    assert analytics["total_issues"] == 1
    assert analytics["sla_breaches"] == 1
    assert analytics["severity_breakdown"]["critical"] == 1


def test_issue_update_flow(service: IssueService) -> None:
    issue = service.create_issue(_default_draft())
    updated = service.update_issue(
        issue.id,
        IssueUpdate(status=IssueStatus.IN_PROGRESS, owner="frank"),
    )
    assert updated.status == IssueStatus.IN_PROGRESS
    assert updated.owner == "frank"

    resolved = service.update_issue(issue.id, IssueUpdate(status=IssueStatus.RESOLVED))
    assert resolved.status == IssueStatus.RESOLVED
    assert resolved.resolved_at is not None


def test_filtering_and_errors(service: IssueService) -> None:
    issue = service.create_issue(_default_draft())
    second = service.create_issue(
        IssueDraft(
            title="Minor latency",
            description="Some customers reporting slower responses",
            severity=Severity.MEDIUM,
            impact_summary="Partial impact",
            customer="Beta Corp",
            category="application",
            sla_minutes=240,
        )
    )
    service.update_issue(second.id, IssueUpdate(status=IssueStatus.TRIAGE))

    issues = service.list_issues(IssueQuery(severity="critical"))
    assert len(issues) == 1 and issues[0].id == issue.id

    triage = service.list_issues(IssueQuery(status=IssueStatus.TRIAGE.value))
    assert len(triage) == 1 and triage[0].id == second.id

    with pytest.raises(TaskNotFoundError):
        service.update_task(issue.id, "missing", TaskUpdate(status=TaskStatus.BLOCKED))

    with pytest.raises(IssueServiceError):
        service.get_issue("missing")
