"""Account briefing service."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Optional

from ..integrations.crm import CRMClient
from ..integrations.knowledge_base import KnowledgeBaseClient


class AccountBriefingService:
    """Generates consolidated account briefings for sellers."""

    def __init__(self, crm: CRMClient, knowledge_base: KnowledgeBaseClient) -> None:
        self._crm = crm
        self._knowledge_base = knowledge_base

    def build_briefing(self, account_name: str) -> Optional[Dict]:
        account = self._crm.find_account_by_name(account_name)
        if not account:
            return None

        playbook_steps = self._knowledge_base.get_playbook_steps(account.industry)
        meetings = self._crm.get_meetings(account.id)
        tasks = self._crm.list_tasks(account.id)

        return {
            "account": self._crm.serialize_account(account),
            "meetings": [
                {
                    **asdict(meeting),
                    "datetime": meeting.datetime.isoformat(),
                }
                for meeting in meetings
            ],
            "open_tasks": [
                {
                    **asdict(task),
                    "due_date": task.due_date.isoformat(),
                }
                for task in tasks
            ],
            "industry_playbook": playbook_steps,
        }

