"""Utilities for turning product ideas into structured backlog artefacts."""
from __future__ import annotations

from typing import List

from .models import AcceptanceCriterion, ProductIdea, UserStory


def _generate_acceptance_criteria(idea: ProductIdea) -> List[AcceptanceCriterion]:
    criteria: List[AcceptanceCriterion] = [
        AcceptanceCriterion(
            statement=(
                f"User can achieve the goal '{idea.goal}' without manual assistance "
                "within the primary workflow."
            )
        ),
        AcceptanceCriterion(
            statement=(
                "Success metrics are captured so product owners can measure the "
                f"benefit '{idea.benefit}'."
            )
        ),
    ]

    for constraint in idea.constraints:
        criteria.append(
            AcceptanceCriterion(
                statement=f"Implementation respects constraint: {constraint}."
            )
        )

    if idea.description:
        criteria.append(
            AcceptanceCriterion(
                statement=(
                    "Edge cases from the description are documented with supporting "
                    "examples."
                )
            )
        )

    return criteria


def _generate_definition_of_done(idea: ProductIdea) -> List[str]:
    dod = [
        "User documentation updated with new workflow steps.",
        "Stakeholder demo conducted and feedback captured.",
        "Tracking dashboards updated to include the new capability.",
    ]

    if idea.constraints:
        dod.append("Risk review completed for highlighted constraints.")

    return dod


def generate_user_story(idea: ProductIdea) -> UserStory:
    """Produce a user story from a product idea."""

    narrative = (
        f"As a {idea.persona}, I want {idea.goal} so that {idea.benefit}."
    )

    if idea.description:
        narrative += f" {idea.description.strip()}"

    acceptance_criteria = _generate_acceptance_criteria(idea)
    definition_of_done = _generate_definition_of_done(idea)

    return UserStory(
        title=idea.title,
        narrative=narrative,
        acceptance_criteria=acceptance_criteria,
        definition_of_done=definition_of_done,
    )


__all__ = ["generate_user_story"]
