"""Heuristics for turning product ideas into backlog-ready items."""
from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .generators import generate_user_story
from .models import BacklogItem, BacklogItemMetrics, ProductIdea, UserStory


def _clamp(value: int, minimum: int = 1, maximum: int = 10) -> int:
    return max(minimum, min(maximum, value))


def _score_from_keywords(text: str, keywords: Iterable[str], high: int, default: int) -> int:
    lowered = text.lower()
    if any(keyword in lowered for keyword in keywords):
        return high
    return default


def _derive_business_value(idea: ProductIdea) -> int:
    if idea.impact is not None:
        return _clamp(idea.impact)

    combined = " ".join((idea.title, idea.goal, idea.benefit, idea.description))
    return _score_from_keywords(
        combined,
        keywords=("automation", "insight", "executive", "visibility"),
        high=8,
        default=6,
    )


def _derive_time_criticality(idea: ProductIdea) -> int:
    if idea.urgency is not None:
        return _clamp(idea.urgency)

    combined = " ".join(tuple(idea.constraints) + tuple(idea.tags))
    default = 5
    if not combined:
        combined = idea.description

    return _score_from_keywords(
        combined,
        keywords=("regulation", "compliance", "deadline", "commitment"),
        high=9,
        default=default,
    )


def _derive_risk_reduction(idea: ProductIdea) -> int:
    if idea.risk_mitigation is not None:
        return _clamp(idea.risk_mitigation)

    combined = " ".join((idea.description, " ".join(idea.constraints)))
    return _score_from_keywords(
        combined,
        keywords=("risk", "security", "accessibility", "resilience", "encryption", "compliance"),
        high=7,
        default=4,
    )


def _derive_effort(idea: ProductIdea) -> int:
    if idea.estimated_effort is not None:
        return max(1, idea.estimated_effort)

    description_length = len(idea.description.split())
    if description_length < 40:
        return 3
    if description_length < 120:
        return 5
    return 8


def _derive_story_points(idea: ProductIdea) -> int:
    effort = _derive_effort(idea)
    if effort <= 3:
        return 3
    if effort <= 5:
        return 5
    if effort <= 8:
        return 8
    return 13


def evaluate_product_idea(identifier: str, idea: ProductIdea) -> BacklogItem:
    """Create a backlog item and supporting story from a product idea."""

    story: UserStory = generate_user_story(idea)

    metrics = BacklogItemMetrics(
        business_value=_derive_business_value(idea),
        time_criticality=_derive_time_criticality(idea),
        risk_reduction=_derive_risk_reduction(idea),
        effort=_derive_effort(idea),
        dependencies=tuple(idea.constraints),
    )

    estimate = _derive_story_points(idea)

    return BacklogItem(
        identifier=identifier,
        title=idea.title,
        metrics=metrics,
        estimate_points=estimate,
        story=story,
    )


def update_backlog_item_story(item: BacklogItem, story: UserStory) -> BacklogItem:
    """Attach a refined story to an existing backlog item."""

    return replace(item, story=story)


__all__ = [
    "evaluate_product_idea",
    "update_backlog_item_story",
]

