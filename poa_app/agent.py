"""Facade for orchestrating core Product Owner Assist behaviours."""
from __future__ import annotations

from typing import Iterable, Sequence

from .evaluation import evaluate_product_idea
from .generators import generate_user_story
from .meetings import analyze_meeting
from .models import (
    BacklogItem,
    MeetingAnalysis,
    MeetingRecord,
    MeetingTranscript,
    PrioritizedBacklogItem,
    ProductIdea,
    SprintCapacity,
    SprintPlan,
    UserStory,
)
from .prioritizer import prioritize_backlog
from .repository import BacklogRepository, MeetingLog
from .sprint_planning import suggest_sprint_plan


class POAssistAgent:
    """High-level facade aligning with the PRD capabilities."""

    def __init__(
        self,
        *,
        backlog_repository: BacklogRepository | None = None,
        meeting_log: MeetingLog | None = None,
    ) -> None:
        self._backlog = backlog_repository or BacklogRepository()
        self._meetings = meeting_log or MeetingLog()

    def create_user_story(self, idea: ProductIdea) -> UserStory:
        """Convert an idea into a story template."""

        return generate_user_story(idea)

    def prioritise_backlog(
        self, backlog: Iterable[BacklogItem]
    ) -> Sequence[PrioritizedBacklogItem]:
        """Return backlog items ordered by score."""

        return prioritize_backlog(backlog)

    def analyse_meeting(self, transcript: MeetingTranscript) -> MeetingAnalysis:
        """Summarise a meeting and extract actionable tasks."""

        return analyze_meeting(transcript)

    def register_meeting(
        self, identifier: str, transcript: MeetingTranscript
    ) -> MeetingRecord:
        """Persist a meeting and return the structured artefact."""

        analysis = self.analyse_meeting(transcript)
        record = MeetingRecord(identifier=identifier, transcript=transcript, analysis=analysis)
        self._meetings.record(record)
        return record

    def recent_meetings(self, limit: int = 5) -> Sequence[MeetingRecord]:
        """Return the latest recorded meetings for quick recall."""

        return self._meetings.latest(limit)

    def recommend_sprint_plan(
        self,
        prioritized_items: Sequence[PrioritizedBacklogItem],
        capacity: SprintCapacity,
    ) -> SprintPlan:
        """Recommend the sprint scope given capacity constraints."""

        return suggest_sprint_plan(prioritized_items, capacity)

    def capture_idea(self, identifier: str, idea: ProductIdea) -> BacklogItem:
        """Evaluate an idea and store it in the backlog repository."""

        item = evaluate_product_idea(identifier, idea)
        self._backlog.upsert(item)
        return item

    def backlog_items(self, *, status: str | None = None) -> Sequence[BacklogItem]:
        """Return backlog entries tracked by the agent."""

        return self._backlog.list(status=status)

    def update_item_status(self, identifier: str, status: str) -> BacklogItem:
        """Set a new workflow status for a backlog item."""

        return self._backlog.update_status(identifier, status)

    def prioritise_backlog_repository(self) -> Sequence[PrioritizedBacklogItem]:
        """Prioritise the tracked backlog using the stored repository."""

        return prioritize_backlog(self._backlog.list(status="ready") or self._backlog.list())

    def plan_next_sprint(self, capacity: SprintCapacity) -> SprintPlan:
        """End-to-end helper prioritising the backlog and drafting a sprint plan."""

        prioritized = self.prioritise_backlog_repository()
        return self.recommend_sprint_plan(prioritized, capacity)


__all__ = ["POAssistAgent"]
