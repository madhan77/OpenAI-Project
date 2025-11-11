from __future__ import annotations

import pytest

from poa_app import (
    BacklogItem,
    BacklogItemMetrics,
    MeetingTranscript,
    POAssistAgent,
    ProductIdea,
    SprintCapacity,
)


def test_generate_user_story_structure() -> None:
    agent = POAssistAgent()
    idea = ProductIdea(
        title="Prioritised backlog view",
        persona="product owner",
        goal="to quickly gauge backlog health",
        benefit="I can keep stakeholders aligned",
        description="Includes filters for teams and target release.",
        constraints=("Follow accessibility AA standards",),
    )

    story = agent.create_user_story(idea)

    assert story.title == idea.title
    assert story.narrative.startswith("As a product owner")
    assert any(
        "benefit" in criterion.statement.lower()
        for criterion in story.acceptance_criteria
    )
    assert "Risk review" in story.definition_of_done[-1]


def test_prioritise_backlog_orders_by_score() -> None:
    agent = POAssistAgent()
    items = [
        BacklogItem(
            identifier="STORY-1",
            title="Automation",
            metrics=BacklogItemMetrics(
                business_value=10,
                time_criticality=5,
                risk_reduction=3,
                effort=5,
            ),
            estimate_points=5,
        ),
        BacklogItem(
            identifier="STORY-2",
            title="Dashboard",
            metrics=BacklogItemMetrics(
                business_value=8,
                time_criticality=8,
                risk_reduction=5,
                effort=3,
            ),
            estimate_points=8,
        ),
    ]

    prioritized = agent.prioritise_backlog(items)

    assert prioritized[0].item.identifier == "STORY-2"
    assert prioritized[0].score > prioritized[1].score


def test_meeting_analysis_returns_tasks() -> None:
    agent = POAssistAgent()
    transcript = MeetingTranscript(
        attendees=("PO", "Design", "Engineering"),
        goals=("Finalize MVP scope",),
        discussion_points=("Agreed on dashboard layout", "Need analytics event list"),
        decisions=("Ship dashboard without export",),
        open_questions=("Who owns telemetry schema?",),
        risks=("External API quota may cap usage",),
    )

    analysis = agent.analyse_meeting(transcript)

    assert "Ship dashboard without export" in " ".join(analysis.action_items)
    assert any("Unresolved question" in gap for gap in analysis.clarity_gaps)
    assert "quota" in " ".join(analysis.risks)


def test_recommend_sprint_plan_respects_capacity() -> None:
    agent = POAssistAgent()
    items = agent.prioritise_backlog(
        [
            BacklogItem(
                identifier="STORY-1",
                title="Automation",
                metrics=BacklogItemMetrics(
                    business_value=10,
                    time_criticality=5,
                    risk_reduction=3,
                    effort=5,
                ),
                estimate_points=3,
            ),
            BacklogItem(
                identifier="STORY-2",
                title="Dashboard",
                metrics=BacklogItemMetrics(
                    business_value=8,
                    time_criticality=8,
                    risk_reduction=5,
                    effort=3,
                ),
                estimate_points=5,
            ),
        ]
    )

    capacity = SprintCapacity(available_points=10, focus_factor=0.7)

    plan = agent.recommend_sprint_plan(items, capacity)

    assert plan.total_points <= plan.capacity
    assert plan.total_points == sum(
        entry.item.estimate_points for entry in plan.committed_items
    )
    assert plan.capacity == pytest.approx(7, abs=1)
    assert any("Available capacity" in note for note in plan.notes)
