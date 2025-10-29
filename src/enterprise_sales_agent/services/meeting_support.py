"""Meeting support workflows."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Dict, List, Optional

from ..integrations.crm import CRMClient
from ..integrations.knowledge_base import KnowledgeBaseClient


class MeetingSupportService:
    """Creates agendas, notes, and follow-up actions for meetings."""

    def __init__(self, crm: CRMClient, knowledge_base: KnowledgeBaseClient) -> None:
        self._crm = crm
        self._knowledge_base = knowledge_base

    def prepare_meeting(
        self,
        *,
        account_name: str,
        meeting_datetime: Optional[datetime] = None,
        focus_topics: Optional[List[str]] = None,
    ) -> Optional[Dict]:
        account = self._crm.find_account_by_name(account_name)
        if not account:
            return None

        opportunity = max(account.opportunities, key=lambda opp: opp.amount)
        agenda = self._build_agenda(account, opportunity, focus_topics)
        objection_handlers = self._knowledge_base.suggest_objection_handlers("pricing")

        return {
            "account": self._crm.serialize_account(account),
            "opportunity": asdict(opportunity),
            "meeting_datetime": (meeting_datetime or datetime.utcnow()).isoformat(),
            "agenda": agenda,
            "call_objectives": [
                "Validate stakeholder priorities",
                "Align on success criteria and next steps",
            ],
            "objection_handlers": objection_handlers,
            "recommended_collateral": self._recommended_collateral(account.industry),
            "post_meeting_tasks": [
                "Send summary email with agreed actions",
                "Log meeting notes and update CRM fields",
            ],
        }

    def summarize_meeting_notes(self, account_name: str) -> Optional[str]:
        account = self._crm.find_account_by_name(account_name)
        if not account:
            return None
        return (
            f"Meeting summary for {account.name}: \n"
            "- Confirmed interest in accelerated deployment.\n"
            "- Stakeholders requested ROI benchmarks and implementation timeline.\n"
            "- Follow-ups: share security documents, schedule executive sponsor call."
        )

    def _build_agenda(
        self,
        account,
        opportunity,
        focus_topics: Optional[List[str]],
    ) -> List[str]:
        agenda = [
            "Introductions and meeting goals",
            "Review current challenges and impact",
            "Demonstrate solution capabilities",
            "Discuss implementation plan",
            "Agree on next steps",
        ]
        if focus_topics:
            agenda.extend(focus_topics)
        if opportunity.stage.lower() in {"proposal/price quote", "negotiation/review"}:
            agenda.insert(3, "Review commercial terms")
        return agenda

    def _recommended_collateral(self, industry: str) -> List[str]:
        collateral = [
            "Executive summary deck",
            "ROI case study",
            "Security and compliance overview",
        ]
        if industry.lower() == "manufacturing":
            collateral.append("Predictive maintenance customer story")
        elif industry.lower() == "technology":
            collateral.append("AI governance whitepaper")
        return collateral

