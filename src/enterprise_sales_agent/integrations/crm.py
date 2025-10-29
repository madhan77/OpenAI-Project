"""Mock CRM integration for the Enterprise Sales Agent application."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Iterable, List, Optional

from .. import data


class CRMClient:
    """Lightweight CRM client backed by the in-memory sample dataset."""

    def __init__(self) -> None:
        self._accounts = data.ACCOUNTS
        self._meetings = data.MEETINGS
        self._tasks = data.TASKS

    # Account operations -------------------------------------------------

    def list_accounts(self) -> Iterable[data.Account]:
        return self._accounts.values()

    def get_account(self, account_id: str) -> Optional[data.Account]:
        return self._accounts.get(account_id)

    def find_account_by_name(self, account_name: str) -> Optional[data.Account]:
        normalized = account_name.strip().lower()
        for account in self._accounts.values():
            if account.name.lower() == normalized:
                return account
        return None

    # Meeting operations -------------------------------------------------

    def get_meetings(self, account_id: str) -> List[data.Meeting]:
        return list(self._meetings.get(account_id, []))

    # Task operations ----------------------------------------------------

    def list_tasks(self, account_id: Optional[str] = None) -> List[data.Task]:
        if account_id:
            return list(self._tasks.get(account_id, []))
        tasks: List[data.Task] = []
        for account_tasks in self._tasks.values():
            tasks.extend(account_tasks)
        return tasks

    def add_task(
        self,
        *,
        description: str,
        due_date,
        owner: str,
        related_account_id: Optional[str] = None,
        related_opportunity_id: Optional[str] = None,
    ) -> data.Task:
        """Create a new task in the mock CRM."""

        task_id = f"TSK-{len(self._tasks) + sum(len(v) for v in self._tasks.values()) + 3001}"
        task = data.Task(
            id=task_id,
            description=description,
            due_date=due_date,
            owner=owner,
            related_account_id=related_account_id,
            related_opportunity_id=related_opportunity_id,
        )
        if related_account_id:
            self._tasks.setdefault(related_account_id, []).append(task)
        else:
            self._tasks.setdefault("general", []).append(task)
        return task

    # Serialization helpers ---------------------------------------------

    @staticmethod
    def serialize_account(account: data.Account) -> Dict:
        return {
            **asdict(account),
            "stakeholders": [asdict(stakeholder) for stakeholder in account.stakeholders],
            "opportunities": [
                {
                    **asdict(opportunity),
                    "close_date": opportunity.close_date.isoformat(),
                }
                for opportunity in account.opportunities
            ],
        }

