from __future__ import annotations

import pytest

from poa_app import (
    BacklogItem,
    BacklogItemMetrics,
    BacklogRepository,
    MeetingLog,
    MeetingTranscript,
    POAssistAgent,
    ProductIdea,
    SprintCapacity,
)
from poa_app.evaluation import evaluate_product_idea


def test_generate_user_story_structure() -> None:
    agent = POAssistAgent()
    idea = ProductIdea(
        title="Prioritised backlog view",
        persona="product owner",
        goal="to quickly gauge backlog health",
        benefit="I can keep stakeholders aligned",
        description="Includes filters for teams and target release.",
        constraints=("Follow accessibility AA standards",),
        tags=("analytics", "insight"),
    )

    story = agent.create_user_story(idea)

    assert story.title == idea.title
    assert story.narrative.startswith("As a product owner")
    assert any(
        "benefit" in criterion.statement.lower()
        for criterion in story.acceptance_criteria
    )
    assert "Risk review" in story.definition_of_done[-1]


def test_evaluate_product_idea_applies_keyword_heuristics() -> None:
    idea = ProductIdea(
        title="Compliance evidence uploader",
        persona="compliance manager",
        goal="attach audit reports",
        benefit="our regulators receive timely evidence",
        description="Workflow must highlight overdue submissions and require encryption.",
        constraints=("Regulation ABC-123",),
    )

    backlog_item = evaluate_product_idea("POA-55", idea)

    assert backlog_item.metrics.time_criticality >= 8
    assert backlog_item.metrics.risk_reduction >= 6
    assert backlog_item.story is not None


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
            status="ready",
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
            status="ready",
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


def test_capture_idea_and_plan_sprint_flow() -> None:
    backlog = BacklogRepository()
    meetings = MeetingLog()
    agent = POAssistAgent(backlog_repository=backlog, meeting_log=meetings)

    idea = ProductIdea(
        title="Roadmap heatmap",
        persona="product owner",
        goal="visualize delivery confidence",
        benefit="I can communicate risk earlier",
        description=(
            "Interactive roadmap view highlighting risky initiatives with capacity "
            "signals pulled from Jira velocity reports."
        ),
        tags=("analytics", "risk"),
    )

    item = agent.capture_idea("POA-101", idea)
    agent.update_item_status(item.identifier, "ready")

    transcript = MeetingTranscript(
        attendees=("PO", "Engineering Manager"),
        goals=("Clarify roadmap risk communication",),
        discussion_points=(
            "Need to align on definition of red/yellow/green",
            "Design to explore hover states",
        ),
        decisions=("Prototype heatmap in Figma",),
        open_questions=("Can analytics ingest data nightly?",),
        risks=("Velocity source may lag by 2 sprints",),
    )
    record = agent.register_meeting("roadmap-sync-1", transcript)

    assert record.analysis.action_items
    assert agent.recent_meetings()[-1].identifier == "roadmap-sync-1"

    capacity = SprintCapacity(available_points=18, focus_factor=0.75)
    plan = agent.plan_next_sprint(capacity)

    assert plan.total_points <= plan.capacity
    assert any(entry.item.identifier == item.identifier for entry in plan.committed_items)
    assert plan.capacity == pytest.approx(13, abs=1)
