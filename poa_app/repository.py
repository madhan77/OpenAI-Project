"""In-memory storage for the PO Assist Agent prototype."""
from __future__ import annotations

from dataclasses import replace
from typing import Dict, Iterable, List, Sequence

from .models import BacklogItem, MeetingRecord


class BacklogRepository:
    """Track backlog items for the agent prototype."""

    def __init__(self) -> None:
        self._items: Dict[str, BacklogItem] = {}

    def upsert(self, item: BacklogItem) -> BacklogItem:
        self._items[item.identifier] = item
        return item

    def get(self, identifier: str) -> BacklogItem:
        try:
            return self._items[identifier]
        except KeyError as exc:  # pragma: no cover - defensive path
            raise KeyError(f"Unknown backlog item '{identifier}'") from exc

    def list(self, *, status: str | None = None) -> List[BacklogItem]:
        items: Iterable[BacklogItem] = self._items.values()
        if status is not None:
            items = [item for item in items if item.status == status]
        return sorted(items, key=lambda item: item.identifier)

    def update_status(self, identifier: str, status: str) -> BacklogItem:
        item = self.get(identifier)
        updated = replace(item, status=status)
        self._items[identifier] = updated
        return updated


class MeetingLog:
    """Persist meeting artefacts and enable quick look-ups."""

    def __init__(self) -> None:
        self._records: List[MeetingRecord] = []

    def record(self, record: MeetingRecord) -> None:
        self._records.append(record)

    def latest(self, limit: int = 5) -> Sequence[MeetingRecord]:
        if limit <= 0:
            return []
        return list(self._records[-limit:])

    def all(self) -> Sequence[MeetingRecord]:
        return list(self._records)


__all__ = ["BacklogRepository", "MeetingLog"]

