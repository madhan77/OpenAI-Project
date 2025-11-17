"""Core data models for the Product Owner Assist Agent."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass(frozen=True)
class AcceptanceCriterion:
    """Single acceptance criterion statement."""

    statement: str


@dataclass(frozen=True)
class ProductIdea:
    """Input description that the agent can expand into a user story."""

    title: str
    persona: str
    goal: str
    benefit: str
    description: str = ""
    constraints: Sequence[str] = field(default_factory=tuple)
    tags: Sequence[str] = field(default_factory=tuple)
    impact: int | None = None
    urgency: int | None = None
    risk_mitigation: int | None = None
    estimated_effort: int | None = None


@dataclass(frozen=True)
class UserStory:
    """Structured user story output for engineering teams."""

    title: str
    narrative: str
    acceptance_criteria: Sequence[AcceptanceCriterion]
    definition_of_done: Sequence[str]


@dataclass(frozen=True)
class BacklogItemMetrics:
    """Scoring inputs for backlog prioritisation."""

    business_value: int
    time_criticality: int
    risk_reduction: int
    effort: int
    dependencies: Sequence[str] = field(default_factory=tuple)

    def weighted_shortest_job_first(self) -> float:
        """Return a WSJF-style score."""

        numerator = self.business_value + self.time_criticality + self.risk_reduction
        denominator = max(self.effort, 1)
        return numerator / denominator


@dataclass(frozen=True)
class BacklogItem:
    """Backlog item enriched with sizing information."""

    identifier: str
    title: str
    metrics: BacklogItemMetrics
    estimate_points: int
    story: "UserStory | None" = None
    status: str = "proposed"


@dataclass(frozen=True)
class PrioritizedBacklogItem:
    """Backlog item together with its prioritisation score."""

    item: BacklogItem
    score: float
    rank: int


@dataclass(frozen=True)
class MeetingTranscript:
    """Structured representation of a meeting or discovery session."""

    attendees: Sequence[str]
    goals: Sequence[str]
    discussion_points: Sequence[str]
    decisions: Sequence[str] = field(default_factory=tuple)
    open_questions: Sequence[str] = field(default_factory=tuple)
    risks: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class MeetingAnalysis:
    """Output extracted from a meeting transcript."""

    summary: str
    action_items: Sequence[str]
    clarity_gaps: Sequence[str]
    risks: Sequence[str]


@dataclass(frozen=True)
class MeetingRecord:
    """Stored meeting artefact combining transcript and analysis."""

    identifier: str
    transcript: MeetingTranscript
    analysis: MeetingAnalysis


@dataclass(frozen=True)
class SprintCapacity:
    """Team capacity inputs used to produce sprint planning suggestions."""

    available_points: int
    focus_factor: float = 0.8

    def effective_capacity(self) -> int:
        """Return the usable capacity after applying the focus factor."""

        capacity = int(self.available_points * self.focus_factor)
        return max(capacity, 0)


@dataclass(frozen=True)
class SprintPlan:
    """Sprint plan recommendation."""

    committed_items: Sequence[PrioritizedBacklogItem]
    total_points: int
    capacity: int
    notes: Sequence[str] = field(default_factory=tuple)


__all__ = [
    "AcceptanceCriterion",
    "ProductIdea",
    "UserStory",
    "BacklogItemMetrics",
    "BacklogItem",
    "PrioritizedBacklogItem",
    "MeetingTranscript",
    "MeetingAnalysis",
    "MeetingRecord",
    "SprintCapacity",
    "SprintPlan",
]
