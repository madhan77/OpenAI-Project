"""Sprint planning recommendations."""
from __future__ import annotations

from typing import Iterable, List

from .models import (
    PrioritizedBacklogItem,
    SprintCapacity,
    SprintPlan,
)


def suggest_sprint_plan(
    prioritized_items: Iterable[PrioritizedBacklogItem],
    capacity: SprintCapacity,
) -> SprintPlan:
    """Select the highest-ranked work within the team's effective capacity."""

    effective_capacity = capacity.effective_capacity()
    selected: List[PrioritizedBacklogItem] = []
    point_total = 0

    for item in prioritized_items:
        points = item.item.estimate_points
        if point_total + points > effective_capacity:
            continue

        selected.append(item)
        point_total += points

    notes: List[str] = []
    if point_total < effective_capacity:
        notes.append(
            "Available capacity remains; consider bringing in stretch items or bug fixes."
        )
    if point_total == 0:
        notes.append("No work selected. Review estimates or focus factor inputs.")

    return SprintPlan(
        committed_items=selected,
        total_points=point_total,
        capacity=effective_capacity,
        notes=notes,
    )


__all__ = ["suggest_sprint_plan"]
