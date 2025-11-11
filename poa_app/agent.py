"""Facade for orchestrating core Product Owner Assist behaviours."""
from __future__ import annotations

from typing import Iterable, Sequence

from .generators import generate_user_story
from .meetings import analyze_meeting
from .models import (
    BacklogItem,
    MeetingAnalysis,
    MeetingTranscript,
    PrioritizedBacklogItem,
    ProductIdea,
    SprintCapacity,
    SprintPlan,
    UserStory,
)
from .prioritizer import prioritize_backlog
from .sprint_planning import suggest_sprint_plan


class POAssistAgent:
    """High-level facade aligning with the PRD capabilities."""

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

    def recommend_sprint_plan(
        self,
        prioritized_items: Sequence[PrioritizedBacklogItem],
        capacity: SprintCapacity,
    ) -> SprintPlan:
        """Recommend the sprint scope given capacity constraints."""

        return suggest_sprint_plan(prioritized_items, capacity)


__all__ = ["POAssistAgent"]
