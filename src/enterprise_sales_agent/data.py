"""Sample data models and mock dataset loader for the Enterprise Sales Agent."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from importlib import resources
from typing import Dict, List, Optional, Tuple

_DATASET_RESOURCE = "mock_dataset.json"


@dataclass
class Stakeholder:
    """Represents an account stakeholder."""

    name: str
    title: str
    email: str
    relationship_status: str


@dataclass
class Opportunity:
    """Represents a pipeline opportunity."""

    id: str
    name: str
    stage: str
    amount: float
    close_date: date
    health_score: int
    next_steps: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)


@dataclass
class Account:
    """Represents an enterprise account."""

    id: str
    name: str
    industry: str
    annual_revenue: float
    employee_count: int
    headquarters: str
    recent_news: List[str]
    stakeholders: List[Stakeholder]
    opportunities: List[Opportunity]


@dataclass
class Meeting:
    """Represents a scheduled meeting related to an account."""

    id: str
    account_id: str
    datetime: datetime
    attendees: List[str]
    objectives: List[str]
    opportunity_id: Optional[str] = None


@dataclass
class Task:
    """Represents a follow-up task suggested by the agent."""

    id: str
    description: str
    due_date: date
    owner: str
    related_account_id: Optional[str] = None
    related_opportunity_id: Optional[str] = None


def _load_mock_dataset() -> Tuple[Dict[str, Account], Dict[str, List[Meeting]], Dict[str, List[Task]]]:
    """Load the curated mock dataset shipped with the package."""

    with resources.open_text("enterprise_sales_agent.resources", _DATASET_RESOURCE) as fh:
        raw = json.load(fh)

    accounts: Dict[str, Account] = {}
    for account_data in raw["accounts"]:
        stakeholders = [Stakeholder(**stakeholder) for stakeholder in account_data.get("stakeholders", [])]
        opportunities = [
            Opportunity(
                id=opportunity["id"],
                name=opportunity["name"],
                stage=opportunity["stage"],
                amount=float(opportunity["amount"]),
                close_date=date.fromisoformat(opportunity["close_date"]),
                health_score=int(opportunity["health_score"]),
                next_steps=list(opportunity.get("next_steps", [])),
                risks=list(opportunity.get("risks", [])),
            )
            for opportunity in account_data.get("opportunities", [])
        ]

        account = Account(
            id=account_data["id"],
            name=account_data["name"],
            industry=account_data["industry"],
            annual_revenue=float(account_data["annual_revenue"]),
            employee_count=int(account_data["employee_count"]),
            headquarters=account_data["headquarters"],
            recent_news=list(account_data.get("recent_news", [])),
            stakeholders=stakeholders,
            opportunities=opportunities,
        )
        accounts[account.id] = account

    meetings: Dict[str, List[Meeting]] = {}
    for account_id, meeting_list in raw.get("meetings", {}).items():
        meetings[account_id] = [
            Meeting(
                id=meeting["id"],
                account_id=meeting["account_id"],
                datetime=datetime.fromisoformat(meeting["datetime"]),
                attendees=list(meeting.get("attendees", [])),
                objectives=list(meeting.get("objectives", [])),
                opportunity_id=meeting.get("opportunity_id"),
            )
            for meeting in meeting_list
        ]

    tasks: Dict[str, List[Task]] = {}
    for account_id, task_list in raw.get("tasks", {}).items():
        tasks[account_id] = [
            Task(
                id=task["id"],
                description=task["description"],
                due_date=date.fromisoformat(task["due_date"]),
                owner=task["owner"],
                related_account_id=task.get("related_account_id"),
                related_opportunity_id=task.get("related_opportunity_id"),
            )
            for task in task_list
        ]

    return accounts, meetings, tasks


ACCOUNTS, MEETINGS, TASKS = _load_mock_dataset()
