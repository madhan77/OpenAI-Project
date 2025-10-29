from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Deque, Dict, Iterable, List, Optional

from .models import Claim, ClaimStatus, ClaimEvent, build_timeline_event


class ClaimRepository:
    """Abstract repository contract."""

    def save(self, claim: Claim) -> None:
        raise NotImplementedError

    def get(self, claim_id: str) -> Optional[Claim]:
        raise NotImplementedError

    def update_status(self, claim_id: str, status: ClaimStatus) -> None:
        raise NotImplementedError

    def record_event(self, claim_id: str, event: ClaimEvent) -> None:
        raise NotImplementedError

    def events(self, claim_id: str) -> Iterable[ClaimEvent]:
        raise NotImplementedError


class InMemoryClaimRepository(ClaimRepository):
    """In-memory implementation suitable for tests and demos."""

    def __init__(self) -> None:
        self._claims: Dict[str, Claim] = {}
        self._events: Dict[str, List[ClaimEvent]] = {}
        self._status: Dict[str, ClaimStatus] = {}

    def save(self, claim: Claim) -> None:
        self._claims[claim.claim_id] = claim
        self._status[claim.claim_id] = ClaimStatus.RECEIVED
        self._events.setdefault(claim.claim_id, []).append(
            build_timeline_event(ClaimStatus.RECEIVED, "Claim received by intake service.")
        )

    def get(self, claim_id: str) -> Optional[Claim]:
        return self._claims.get(claim_id)

    def update_status(self, claim_id: str, status: ClaimStatus) -> None:
        if claim_id not in self._claims:
            raise KeyError(f"Claim {claim_id} not found")
        self._status[claim_id] = status
        self._events[claim_id].append(build_timeline_event(status, f"Status transitioned to {status.name}"))

    def record_event(self, claim_id: str, event: ClaimEvent) -> None:
        self._events.setdefault(claim_id, []).append(event)

    def events(self, claim_id: str) -> Iterable[ClaimEvent]:
        return tuple(self._events.get(claim_id, ()))

    def status(self, claim_id: str) -> Optional[ClaimStatus]:
        return self._status.get(claim_id)


@dataclass(slots=True)
class ManualReviewItem:
    claim_id: str
    reason_codes: List[str]
    assigned_to: Optional[str] = None
    priority: str = "standard"
    created_at: datetime = datetime.utcnow()


class ManualReviewQueue:
    """Queue for manual review tasks."""

    def __init__(self) -> None:
        self._queue: Deque[ManualReviewItem] = deque()

    def enqueue(self, item: ManualReviewItem) -> None:
        if item.priority == "urgent":
            self._queue.appendleft(item)
        else:
            self._queue.append(item)

    def dequeue(self) -> Optional[ManualReviewItem]:
        if not self._queue:
            return None
        return self._queue.popleft()

    def list_items(self) -> List[ManualReviewItem]:
        return list(self._queue)


class ProcessedClaimTracker:
    """Tracks recent claims for duplicate detection."""

    def __init__(self) -> None:
        self._history: Dict[str, datetime] = {}

    def record(self, claim: Claim) -> None:
        self._history[claim.claim_id] = claim.submitted_at

    def seen_recently(self, claim: Claim, within: timedelta) -> bool:
        last = self._history.get(claim.claim_id)
        if not last:
            return False
        delta = abs(claim.submitted_at - last)
        return delta <= within


__all__ = [
    "ClaimRepository",
    "InMemoryClaimRepository",
    "ManualReviewItem",
    "ManualReviewQueue",
    "ProcessedClaimTracker",
]
