"""Task automation helpers for the Enterprise Sales Agent."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Dict

from ..integrations.crm import CRMClient


class TaskAutomationService:
    """Creates and lists follow-up tasks."""

    def __init__(self, crm: CRMClient) -> None:
        self._crm = crm

    def create_follow_up(
        self,
        *,
        account_name: str,
        description: str,
        owner: str,
        due_in_days: int = 2,
    ) -> Dict:
        account = self._crm.find_account_by_name(account_name)
        if not account:
            raise ValueError(f"Unknown account: {account_name}")

        task = self._crm.add_task(
            description=description,
            due_date=date.today() + timedelta(days=due_in_days),
            owner=owner,
            related_account_id=account.id,
        )
        return {
            "id": task.id,
            "description": task.description,
            "due_date": task.due_date.isoformat(),
            "owner": task.owner,
            "related_account": account.name,
        }

    def upcoming_tasks(self, account_name: str) -> Dict:
        account = self._crm.find_account_by_name(account_name)
        if not account:
            raise ValueError(f"Unknown account: {account_name}")

        tasks = self._crm.list_tasks(account.id)
        return {
            "account": account.name,
            "tasks": [
                {
                    "id": task.id,
                    "description": task.description,
                    "due_date": task.due_date.isoformat(),
                    "owner": task.owner,
                }
                for task in tasks
            ],
        }

