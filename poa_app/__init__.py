"""Product Owner Assist Agent package."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

from .agent import POAssistAgent
from .ingestion import ParsedIdea, parse_meeting_notes, parse_product_idea
from .integrations import (
    DocumentationPublisher,
    IntegrationHub,
    IntegrationResult,
    JiraConnector,
    SlackConnector,
)
from .models import (
    AcceptanceCriterion,
    BacklogItem,
    BacklogItemMetrics,
    MeetingAnalysis,
    MeetingRecord,
    MeetingTranscript,
    PrioritizedBacklogItem,
    ProductIdea,
    SprintCapacity,
    SprintPlan,
    UserStory,
)
from .repository import BacklogRepository, MeetingLog
from .roadmap import RoadmapEntry, RoadmapTimeline, build_roadmap

if TYPE_CHECKING:  # pragma: no cover - imported for static analysis only
    from .preview import PreviewSnapshot, build_preview, demo_preview

_LAZY_EXPORTS = {"PreviewSnapshot", "build_preview", "demo_preview"}

__all__ = [
    "POAssistAgent",
    "AcceptanceCriterion",
    "BacklogItem",
    "BacklogItemMetrics",
    "MeetingAnalysis",
    "MeetingRecord",
    "MeetingTranscript",
    "PrioritizedBacklogItem",
    "ProductIdea",
    "SprintCapacity",
    "SprintPlan",
    "UserStory",
    "BacklogRepository",
    "MeetingLog",
    "ParsedIdea",
    "parse_product_idea",
    "parse_meeting_notes",
    "IntegrationHub",
    "IntegrationResult",
    "JiraConnector",
    "SlackConnector",
    "DocumentationPublisher",
    "RoadmapEntry",
    "RoadmapTimeline",
    "build_roadmap",
    *_LAZY_EXPORTS,
]


def __getattr__(name: str) -> Any:  # pragma: no cover - thin import proxy
    if name in _LAZY_EXPORTS:
        module = import_module(".preview", __name__)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:  # pragma: no cover - convenience for introspection
    return sorted(list(globals().keys()) + list(_LAZY_EXPORTS))
