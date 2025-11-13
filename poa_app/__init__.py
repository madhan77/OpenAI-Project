"""Product Owner Assist Agent package."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

from .agent import POAssistAgent
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
    *_LAZY_EXPORTS,
]


def __getattr__(name: str) -> Any:  # pragma: no cover - thin import proxy
    if name in _LAZY_EXPORTS:
        module = import_module(".preview", __name__)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:  # pragma: no cover - convenience for introspection
    return sorted(list(globals().keys()) + list(_LAZY_EXPORTS))
