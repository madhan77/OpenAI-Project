"""Roadmap utilities translating prioritized backlog into quarterly plans."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from .models import PrioritizedBacklogItem


@dataclass(frozen=True)
class RoadmapEntry:
    """Represents the items planned for a specific quarter."""

    quarter: str
    items: Sequence[PrioritizedBacklogItem]
    total_points: int


@dataclass(frozen=True)
class RoadmapTimeline:
    """Quarterly roadmap containing the scheduled backlog work."""

    entries: Sequence[RoadmapEntry]
    backlog: Sequence[PrioritizedBacklogItem]

    def as_markdown(self) -> str:
        lines: List[str] = ["## Roadmap Overview", ""]
        for entry in self.entries:
            lines.append(f"### {entry.quarter} — {entry.total_points} pts")
            if entry.items:
                for prioritized in entry.items:
                    item = prioritized.item
                    lines.append(
                        f"- {item.identifier} ({item.estimate_points} pts) — {item.title}"
                    )
            else:
                lines.append("- No committed work; review backlog priorities.")
            lines.append("")

        if self.backlog:
            lines.append("### Backlog Awaiting Scheduling")
            for entry in self.backlog:
                item = entry.item
                lines.append(
                    f"- {item.identifier} ({item.estimate_points} pts) — {item.title}"
                )
        else:
            lines.append("All prioritised items are scheduled in the roadmap.")

        return "\n".join(lines).rstrip()


def build_roadmap(
    prioritized_items: Iterable[PrioritizedBacklogItem],
    capacities: Sequence[Tuple[str, int]],
) -> RoadmapTimeline:
    """Distribute prioritized items across quarters based on capacity."""

    remaining: List[PrioritizedBacklogItem] = list(prioritized_items)
    scheduled: List[RoadmapEntry] = []
    index = 0

    for quarter, capacity in capacities:
        points = 0
        selected: List[PrioritizedBacklogItem] = []

        while index < len(remaining):
            candidate = remaining[index]
            estimate = candidate.item.estimate_points
            if points + estimate > capacity:
                break
            selected.append(candidate)
            points += estimate
            index += 1

        scheduled.append(
            RoadmapEntry(quarter=quarter, items=tuple(selected), total_points=points)
        )

    backlog = tuple(remaining[index:])

    return RoadmapTimeline(entries=tuple(scheduled), backlog=backlog)


__all__ = ["RoadmapEntry", "RoadmapTimeline", "build_roadmap"]
