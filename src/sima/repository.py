"""In-memory repositories for Single Issue Management App entities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional

from .models import Issue, IssueStatus


@dataclass(slots=True)
class IssueQuery:
    severity: Optional[str] = None
    status: Optional[str] = None
    customer: Optional[str] = None
    tag: Optional[str] = None


class IssueRepository:
    """A simple repository that stores issues in memory."""

    def __init__(self) -> None:
        self._issues: Dict[str, Issue] = {}

    def add(self, issue: Issue) -> Issue:
        self._issues[issue.id] = issue
        return issue

    def get(self, issue_id: str) -> Optional[Issue]:
        return self._issues.get(issue_id)

    def update(self, issue: Issue) -> Issue:
        self._issues[issue.id] = issue
        return issue

    def all(self) -> Iterable[Issue]:
        return self._issues.values()

    def filter(self, query: IssueQuery) -> List[Issue]:
        results = list(self._issues.values())
        if query.severity:
            results = [i for i in results if i.severity.value == query.severity]
        if query.status:
            results = [i for i in results if i.status.value == query.status]
        if query.customer:
            results = [i for i in results if i.customer == query.customer]
        if query.tag:
            results = [i for i in results if query.tag in i.tags]
        return sorted(results, key=lambda i: i.created_at, reverse=True)

    def detect_duplicate(self, title: str, impacted_assets: List[str], window: timedelta) -> Optional[Issue]:
        cutoff = datetime.utcnow() - window
        impacted_set = {asset.lower() for asset in impacted_assets}
        for issue in self._issues.values():
            if issue.created_at < cutoff:
                continue
            if issue.status in {IssueStatus.RESOLVED, IssueStatus.CLOSED}:
                continue
            if issue.title.strip().lower() != title.strip().lower():
                continue
            if impacted_set and impacted_set.intersection(asset.lower() for asset in issue.impacted_assets):
                return issue
        return None
