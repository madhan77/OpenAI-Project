"""Core orchestration logic for the Enterprise Sales Agent."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from .integrations.crm import CRMClient
from .integrations.knowledge_base import KnowledgeBaseClient
from .services.account_briefing import AccountBriefingService
from .services.conversation import ConversationEngine
from .services.meeting_support import MeetingSupportService
from .services.pipeline_management import PipelineManagementService
from .services.task_automation import TaskAutomationService


class EnterpriseSalesAgent:
    """High-level facade for the Enterprise Sales Agent application."""

    def __init__(self) -> None:
        self._crm = CRMClient()
        self._knowledge_base = KnowledgeBaseClient()

        self._account_briefing = AccountBriefingService(self._crm, self._knowledge_base)
        self._meeting_support = MeetingSupportService(self._crm, self._knowledge_base)
        self._pipeline_management = PipelineManagementService(self._crm)
        self._task_automation = TaskAutomationService(self._crm)
        self._conversation = ConversationEngine(self)

    # Public API ---------------------------------------------------------

    def account_briefing(self, account_name: str) -> Optional[Dict]:
        return self._account_briefing.build_briefing(account_name)

    def prepare_meeting(
        self,
        *,
        account_name: str,
        meeting_datetime: Optional[datetime] = None,
    ) -> Optional[Dict]:
        return self._meeting_support.prepare_meeting(
            account_name=account_name,
            meeting_datetime=meeting_datetime,
        )

    def summarize_meeting(self, account_name: str) -> Optional[str]:
        return self._meeting_support.summarize_meeting_notes(account_name)

    def pipeline_health(self, account_name: str) -> Dict:
        return self._pipeline_management.pipeline_health(account_name)

    def organization_forecast(self) -> Dict:
        return self._pipeline_management.org_wide_forecast()

    def create_follow_up_task(
        self,
        *,
        account_name: str,
        description: str,
        owner: str,
        due_in_days: int = 2,
    ) -> Dict:
        return self._task_automation.create_follow_up(
            account_name=account_name,
            description=description,
            owner=owner,
            due_in_days=due_in_days,
        )

    def list_tasks(self, account_name: str) -> Dict:
        return self._task_automation.upcoming_tasks(account_name)

    def converse(self, message: str) -> Dict:
        return self._conversation.respond(message)

