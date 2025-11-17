"""Utilities for producing shareable previews of the PO Assist workflows."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

from .agent import POAssistAgent
from .models import (
    MeetingTranscript,
    ProductIdea,
    MeetingRecord,
    PrioritizedBacklogItem,
    SprintCapacity,
    SprintPlan,
)
from .roadmap import RoadmapTimeline, build_roadmap


@dataclass(frozen=True)
class PreviewSnapshot:
    """Aggregated view of backlog, meetings, and sprint planning outputs."""

    prioritized_backlog: Sequence[PrioritizedBacklogItem]
    meetings: Sequence[MeetingRecord]
    sprint_plan: SprintPlan
    roadmap: RoadmapTimeline | None = None

    def as_markdown(self) -> str:
        """Return a lightweight markdown summary for quick stakeholder previews."""

        lines: list[str] = ["# PO Assist Preview", ""]

        lines.append("## Backlog Highlights")
        if not self.prioritized_backlog:
            lines.append("*No backlog items available. Capture ideas to populate the queue.*")
        else:
            for entry in self.prioritized_backlog:
                item = entry.item
                lines.append(
                    f"{entry.rank}. {item.identifier} – {item.title} "
                    f"(WSJF {entry.score:.2f}, {item.estimate_points} pts)"
                )

        lines.append("")
        lines.append("## Recent Meetings")
        if not self.meetings:
            lines.append("*No recorded meetings yet.*")
        else:
            for record in self.meetings:
                summary = record.analysis.summary.split(". ")[0].strip()
                lines.append(f"- **{record.identifier}** — {summary}")

        lines.append("")
        lines.append("## Sprint Plan Preview")
        plan = self.sprint_plan
        lines.append(
            f"Capacity: {plan.capacity} pts · Planned: {plan.total_points} pts"
        )
        if plan.committed_items:
            for entry in plan.committed_items:
                item = entry.item
                lines.append(
                    f"- {entry.rank}. {item.identifier} ({item.estimate_points} pts) — {item.title}"
                )
        else:
            lines.append("- No stories selected. Review backlog readiness.")

        if plan.notes:
            lines.append("")
            lines.append("### Planning Notes")
            for note in plan.notes:
                lines.append(f"- {note}")

        if self.roadmap:
            lines.append("")
            lines.append(self.roadmap.as_markdown())

        return "\n".join(lines)


def build_preview(
    agent: POAssistAgent,
    *,
    capacity: SprintCapacity | None = None,
    backlog_limit: int = 5,
    include_meetings: bool = True,
    roadmap_capacities: Sequence[Tuple[str, int]] | None = None,
) -> PreviewSnapshot:
    """Generate a snapshot using the agent's current repositories."""

    prioritized_all: Sequence[PrioritizedBacklogItem] = agent.prioritise_backlog_repository()
    prioritized: Sequence[PrioritizedBacklogItem]
    if backlog_limit > 0:
        prioritized = prioritized_all[:backlog_limit]
    else:
        prioritized = prioritized_all

    meetings: Sequence[MeetingRecord]
    if include_meetings:
        meetings = agent.recent_meetings(limit=backlog_limit)
    else:
        meetings = ()

    planning_capacity = capacity or SprintCapacity(available_points=20)
    plan = agent.recommend_sprint_plan(prioritized_all, planning_capacity)

    roadmap: RoadmapTimeline | None = None
    if roadmap_capacities:
        roadmap = build_roadmap(prioritized_all, roadmap_capacities)

    return PreviewSnapshot(
        prioritized_backlog=prioritized,
        meetings=meetings,
        sprint_plan=plan,
        roadmap=roadmap,
    )


def demo_preview(agent: POAssistAgent | None = None) -> PreviewSnapshot:
    """Create a seeded preview so stakeholders can try the workflow immediately."""

    working_agent = agent or POAssistAgent()

    ideas = (
        ("POA-201", "Persona insights dashboard", "Enable PO to compare persona coverage"),
        (
            "POA-202",
            "Risk alignment digest",
            "Summarise delivery risks for weekly stakeholder updates",
        ),
    )

    for identifier, title, description in ideas:
        item = working_agent.capture_idea(
            identifier,
            ProductIdea(
                title=title,
                persona="product owner",
                goal="share the latest delivery context",
                benefit="stakeholders remain aligned",
                description=description,
                tags=("insight", "communication"),
            ),
        )
        working_agent.update_item_status(item.identifier, "ready")

    working_agent.register_meeting(
        "weekly-sync",
        MeetingTranscript(
            attendees=("PO", "Eng Lead", "Design"),
            goals=("Confirm roadmap messaging",),
            discussion_points=(
                "Reviewed persona dashboard mockups",
                "Agreed to pilot weekly risk digest",
            ),
            decisions=("Launch pilot with beta customers",),
            open_questions=("Who owns reporting automation?",),
            risks=("Digest may surface stale Jira data",),
        ),
    )

    roadmap = build_roadmap(
        working_agent.prioritise_backlog_repository(),
        capacities=(
            ("Q1", 16),
            ("Q2", 20),
            ("Q3", 18),
        ),
    )

    return PreviewSnapshot(
        prioritized_backlog=working_agent.prioritise_backlog_repository(),
        meetings=working_agent.recent_meetings(limit=5),
        sprint_plan=working_agent.plan_next_sprint(
            SprintCapacity(available_points=16, focus_factor=0.75)
        ),
        roadmap=roadmap,
    )


if __name__ == "__main__":  # pragma: no cover - manual exploration helper
    preview = demo_preview()
    print(preview.as_markdown())


__all__ = ["PreviewSnapshot", "build_preview", "demo_preview"]
