"""Facade for orchestrating core Product Owner Assist behaviours."""
from __future__ import annotations

from typing import Iterable, Sequence

from .evaluation import evaluate_product_idea
from .generators import generate_user_story
from .ingestion import ParsedIdea, parse_meeting_notes, parse_product_idea
from .integrations import IntegrationHub, IntegrationResult
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
from .roadmap import RoadmapTimeline, build_roadmap
from .sprint_planning import suggest_sprint_plan


class POAssistAgent:
    """High-level facade aligning with the PRD capabilities."""

    def __init__(
        self,
        *,
        backlog_repository: BacklogRepository | None = None,
        meeting_log: MeetingLog | None = None,
        integrations: IntegrationHub | None = None,
    ) -> None:
        self._backlog = backlog_repository or BacklogRepository()
        self._meetings = meeting_log or MeetingLog()
        self._integrations = integrations or IntegrationHub()

    # Idea capture -----------------------------------------------------------------
    def create_user_story(self, idea: ProductIdea) -> UserStory:
        """Convert an idea into a story template."""

        return generate_user_story(idea)

    def ingest_raw_idea(self, identifier: str, description: str) -> tuple[BacklogItem, ParsedIdea]:
        """Parse a natural-language idea and store it in the backlog."""

        parsed = parse_product_idea(description)
        item = self.capture_idea(identifier, parsed.idea)
        return item, parsed

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

    def prioritise_backlog(self, backlog: Iterable[BacklogItem]) -> Sequence[PrioritizedBacklogItem]:
        """Return backlog items ordered by score."""

        return prioritize_backlog(backlog)

    def prioritise_backlog_repository(self) -> Sequence[PrioritizedBacklogItem]:
        """Prioritise the tracked backlog using the stored repository."""

        ready = self._backlog.list(status="ready")
        items = ready or self._backlog.list()
        return prioritize_backlog(items)

    # Meeting insights --------------------------------------------------------------
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

    def log_meeting_notes(self, identifier: str, notes: str) -> MeetingRecord:
        """Parse raw notes into a transcript before registering the meeting."""

        transcript = parse_meeting_notes(notes)
        return self.register_meeting(identifier, transcript)

    def recent_meetings(self, limit: int = 5) -> Sequence[MeetingRecord]:
        """Return the latest recorded meetings for quick recall."""

        return self._meetings.latest(limit)

    # Planning ---------------------------------------------------------------------
    def recommend_sprint_plan(
        self,
        prioritized_items: Sequence[PrioritizedBacklogItem],
        capacity: SprintCapacity,
    ) -> SprintPlan:
        """Recommend the sprint scope given capacity constraints."""

        return suggest_sprint_plan(prioritized_items, capacity)

    def plan_next_sprint(self, capacity: SprintCapacity) -> SprintPlan:
        """End-to-end helper prioritising the backlog and drafting a sprint plan."""

        prioritized = self.prioritise_backlog_repository()
        return self.recommend_sprint_plan(prioritized, capacity)

    def build_roadmap(self, capacities: Sequence[tuple[str, int]]) -> RoadmapTimeline:
        """Create a quarterly roadmap for upcoming prioritized work."""

        prioritized = self.prioritise_backlog_repository()
        return build_roadmap(prioritized, capacities)

    # Integrations -----------------------------------------------------------------
    def sync_backlog_item(self, identifier: str, *, notify: bool = True) -> Sequence[IntegrationResult]:
        """Push a backlog item to connected integrations."""

        item = self._backlog.get(identifier)
        return self._integrations.sync_story(item, notify=notify)

    def broadcast_meeting(self, identifier: str) -> Sequence[IntegrationResult]:
        """Share a meeting summary with documentation and messaging surfaces."""

        record = next((record for record in self._meetings.all() if record.identifier == identifier), None)
        if record is None:  # pragma: no cover - defensive path
            raise KeyError(f"Unknown meeting '{identifier}'")
        return self._integrations.broadcast_meeting(identifier, record.analysis)

    def announce_sprint_plan(self, plan: SprintPlan | None = None) -> Sequence[IntegrationResult]:
        """Publish the latest sprint plan to stakeholders."""

        working_plan = plan or self.plan_next_sprint(SprintCapacity(available_points=20))
        return self._integrations.announce_sprint_plan(working_plan)


__all__ = ["POAssistAgent"]
