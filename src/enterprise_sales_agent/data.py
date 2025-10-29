"""Sample data models used by the Enterprise Sales Agent.

The project does not integrate with real third-party systems, so a curated
set of representative enterprise sales data is provided to let developers run
and test the application locally. The data is intentionally small but covers
key artifacts referenced throughout the PRD, such as accounts, opportunities,
meetings, and historical performance indicators.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional


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


# Sample dataset -----------------------------------------------------------

STAKEHOLDERS: Dict[str, List[Stakeholder]] = {
    "acme-industries": [
        Stakeholder(
            name="Lena Howard",
            title="VP of Operations",
            email="lena.howard@acmeindustries.com",
            relationship_status="Champion",
        ),
        Stakeholder(
            name="Raj Patel",
            title="CIO",
            email="raj.patel@acmeindustries.com",
            relationship_status="Supporter",
        ),
        Stakeholder(
            name="Simone Yang",
            title="Procurement Director",
            email="simone.yang@acmeindustries.com",
            relationship_status="Neutral",
        ),
    ],
    "globex": [
        Stakeholder(
            name="Amanda Clarke",
            title="Chief Revenue Officer",
            email="amanda.clarke@globex.com",
            relationship_status="Champion",
        ),
        Stakeholder(
            name="Eduardo Silva",
            title="VP Finance",
            email="eduardo.silva@globex.com",
            relationship_status="Skeptic",
        ),
    ],
}

OPPORTUNITIES: Dict[str, List[Opportunity]] = {
    "acme-industries": [
        Opportunity(
            id="OPP-1001",
            name="Enterprise Analytics Platform",
            stage="Proposal/Price Quote",
            amount=450000.0,
            close_date=date(2024, 6, 20),
            health_score=72,
            next_steps=[
                "Follow up on security questionnaire",
                "Coordinate reference call with manufacturing customer",
            ],
            risks=[
                "Budget review pushed to next quarter",
                "Need executive sponsor sign-off",
            ],
        ),
        Opportunity(
            id="OPP-1002",
            name="Field Service Optimization",
            stage="Value Proposition",
            amount=220000.0,
            close_date=date(2024, 7, 15),
            health_score=58,
            next_steps=["Schedule discovery with operations team"],
            risks=["Competing pilot with incumbent vendor"],
        ),
    ],
    "globex": [
        Opportunity(
            id="OPP-2001",
            name="AI-Powered Forecasting",
            stage="Negotiation/Review",
            amount=780000.0,
            close_date=date(2024, 5, 30),
            health_score=81,
            next_steps=[
                "Finalize redlines with legal",
                "Share updated implementation timeline",
            ],
            risks=["Need CFO approval for pre-pay discount"],
        ),
    ],
}

ACCOUNTS: Dict[str, Account] = {
    "acme-industries": Account(
        id="acme-industries",
        name="Acme Industries",
        industry="Manufacturing",
        annual_revenue=1.8e9,
        employee_count=5400,
        headquarters="Chicago, IL",
        recent_news=[
            "Announced expansion of smart factory initiative",
            "Selected as finalist for Industry Innovation Award",
        ],
        stakeholders=STAKEHOLDERS["acme-industries"],
        opportunities=OPPORTUNITIES["acme-industries"],
    ),
    "globex": Account(
        id="globex",
        name="Globex Corporation",
        industry="Technology",
        annual_revenue=3.2e9,
        employee_count=7200,
        headquarters="Austin, TX",
        recent_news=[
            "Completed acquisition of data security startup SecureIQ",
            "Named a leader in Gartner Magic Quadrant for Cloud Platforms",
        ],
        stakeholders=STAKEHOLDERS["globex"],
        opportunities=OPPORTUNITIES["globex"],
    ),
}

MEETINGS: Dict[str, List[Meeting]] = {
    "acme-industries": [
        Meeting(
            id="MTG-9001",
            account_id="acme-industries",
            datetime=datetime(2024, 5, 6, 15, 0),
            attendees=[
                "Jordan Blake (Account Executive)",
                "Lena Howard",
                "Raj Patel",
            ],
            objectives=[
                "Review security questionnaire responses",
                "Align on next steps for proof-of-concept",
            ],
            opportunity_id="OPP-1001",
        ),
    ],
    "globex": [
        Meeting(
            id="MTG-9002",
            account_id="globex",
            datetime=datetime(2024, 5, 8, 11, 0),
            attendees=[
                "Taylor Reed (Account Executive)",
                "Amanda Clarke",
                "Eduardo Silva",
            ],
            objectives=[
                "Walk through updated ROI analysis",
                "Confirm legal redline timeline",
            ],
            opportunity_id="OPP-2001",
        ),
    ],
}

TASKS: Dict[str, List[Task]] = {
    "acme-industries": [
        Task(
            id="TSK-3001",
            description="Send security questionnaire follow-up email",
            due_date=date(2024, 5, 3),
            owner="Jordan Blake",
            related_account_id="acme-industries",
            related_opportunity_id="OPP-1001",
        ),
    ],
    "globex": [
        Task(
            id="TSK-3002",
            description="Share implementation plan with Globex legal team",
            due_date=date(2024, 5, 2),
            owner="Taylor Reed",
            related_account_id="globex",
            related_opportunity_id="OPP-2001",
        ),
    ],
}

