"""Prioritisation heuristics for backlog management."""
from __future__ import annotations

from typing import Iterable, List

from .models import BacklogItem, PrioritizedBacklogItem


def prioritize_backlog(items: Iterable[BacklogItem]) -> List[PrioritizedBacklogItem]:
    """Return items ordered by WSJF score."""

    scored: List[PrioritizedBacklogItem] = []
    for item in items:
        score = item.metrics.weighted_shortest_job_first()

        if item.metrics.dependencies:
            score -= 0.1 * len(item.metrics.dependencies)

        if item.status not in {"proposed", "ready"}:
            score -= 1

        scored.append(PrioritizedBacklogItem(item=item, score=score, rank=0))

    scored.sort(key=lambda entry: entry.score, reverse=True)

    for idx, entry in enumerate(scored, start=1):
        scored[idx - 1] = PrioritizedBacklogItem(
            item=entry.item,
            score=entry.score,
            rank=idx,
        )

    return scored


__all__ = ["prioritize_backlog"]
