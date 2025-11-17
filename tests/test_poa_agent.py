from __future__ import annotations

import pytest

from poa_app import (
    BacklogItem,
    BacklogItemMetrics,
    BacklogRepository,
    DocumentationPublisher,
    IntegrationHub,
    JiraConnector,
    JiraIssuePayload,
    MeetingLog,
    MeetingTranscript,
    POAssistAgent,
    ParsedIdea,
    ProductIdea,
    SlackConnector,
    RoadmapTimeline,
    SprintCapacity,
    SprintPlan,
    build_preview,
    build_roadmap,
    parse_meeting_notes,
    parse_product_idea,
)
from poa_app.evaluation import evaluate_product_idea


def _sample_backlog_item(identifier: str = "POA-SLACK") -> BacklogItem:
    return BacklogItem(
        identifier=identifier,
        title="Slack validation story",
        metrics=BacklogItemMetrics(
            business_value=6,
            time_criticality=5,
            risk_reduction=4,
            effort=2,
        ),
        estimate_points=3,
        status="ready",
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


def test_parse_product_idea_from_text() -> None:
    text = (
        "Title: Unified sprint board\n"
        "As a scrum master, I want to visualise cross-team work so that dependencies are clear.\n"
        "Constraints: Integrate Jira; Must support PI Planning\n"
        "Tags: visibility, #planning\n"
        "Impact: 9\n"
        "Effort: 5\n"
    )

    parsed: ParsedIdea = parse_product_idea(text)

    assert parsed.idea.persona == "scrum master"
    assert "Integrate Jira" in parsed.idea.constraints[0]
    assert parsed.idea.tags == ("visibility", "planning")
    assert parsed.idea.impact == 9
    assert parsed.notes


def test_parse_meeting_notes_creates_transcript() -> None:
    notes = (
        "Attendees: PO, Eng Lead\n"
        "Goals: Align roadmap\n"
        "Discussion: Reviewed dashboard; Highlighted reporting gaps\n"
        "Decisions: Proceed with MVP\n"
        "Questions: Who owns QA?\n"
        "Risks: Data freshness\n"
    )

    transcript = parse_meeting_notes(notes)

    assert "PO" in transcript.attendees
    assert "Reviewed dashboard" in transcript.discussion_points[0]
    assert transcript.open_questions == ("Who owns QA?",)


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
    integrations = IntegrationHub(documentation=DocumentationPublisher())
    agent = POAssistAgent(backlog_repository=backlog, meeting_log=meetings, integrations=integrations)

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

    results = agent.sync_backlog_item(item.identifier)
    assert any(result.destination == "jira" for result in results)
    assert all(result.status == "success" for result in results)


def test_log_meeting_notes_and_broadcast() -> None:
    integrations = IntegrationHub()
    agent = POAssistAgent(integrations=integrations)

    notes = (
        "Attendees: PO, Eng Lead\n"
        "Discussion: Prioritisation workflow; Preview mock\n"
        "Decisions: Roll preview to pilot team\n"
    )

    record = agent.log_meeting_notes("sync-002", notes)
    assert record.analysis.action_items

    sync_results = agent.broadcast_meeting("sync-002")
    assert any(result.destination == "slack" for result in sync_results)
    assert all(result.status == "success" for result in sync_results)


def test_build_roadmap_distributes_work() -> None:
    agent = POAssistAgent()

    for index in range(1, 6):
        idea = ProductIdea(
            title=f"Capability {index}",
            persona="product owner",
            goal="ship incremental value",
            benefit="stakeholders stay aligned",
            description="Short enhancement",
        )
        item = agent.capture_idea(f"POA-{index}", idea)
        agent.update_item_status(item.identifier, "ready")

    prioritized = agent.prioritise_backlog_repository()
    roadmap: RoadmapTimeline = build_roadmap(
        prioritized,
        capacities=(
            ("Q1", 3),
            ("Q2", 3),
        ),
    )

    assert roadmap.entries[0].items
    assert roadmap.backlog


def test_preview_snapshot_provides_markdown_summary_with_roadmap() -> None:
    backlog = BacklogRepository()
    meetings = MeetingLog()
    agent = POAssistAgent(backlog_repository=backlog, meeting_log=meetings)

    idea = ProductIdea(
        title="Team health dashboard",
        persona="product owner",
        goal="spot blockers quickly",
        benefit="the team can address risks before sprint review",
        description="Aggregates cycle time, WIP, and blockers into a single view.",
        tags=("insight", "operations"),
    )

    item = agent.capture_idea("POA-301", idea)
    agent.update_item_status(item.identifier, "ready")

    agent.register_meeting(
        "retro-sync",
        MeetingTranscript(
            attendees=("PO", "Scrum Master"),
            goals=("Surface sprint health actions",),
            discussion_points=("Team agreed to focus on WIP limits",),
            decisions=("Pilot dashboard widget next sprint",),
        ),
    )

    preview = build_preview(
        agent,
        capacity=SprintCapacity(available_points=12),
        roadmap_capacities=(("Q1", 10),),
    )
    summary = preview.as_markdown()

    assert "PO Assist Preview" in summary
    assert "POA-301" in summary
    assert "retro-sync" in summary
    assert "Capacity" in summary
    assert "Roadmap Overview" in summary


def test_ingest_raw_idea_returns_parsed_metadata() -> None:
    agent = POAssistAgent()
    item, parsed = agent.ingest_raw_idea(
        "POA-999",
        "As a product owner, I want to highlight risks so that we can course correct early.",
    )

    assert item.identifier == "POA-999"
    assert parsed.notes


def test_slack_connector_records_messages_without_webhook() -> None:
    connector = SlackConnector(channel="#product-demo")
    item = _sample_backlog_item("POA-777")

    result = connector.post_story_sync(item)

    assert result.status == "success"
    assert connector.messages[-1].channel == "#product-demo"
    assert connector.messages[-1].context["type"] == "story"
    assert "Stored locally" in result.message


def test_slack_connector_surfaces_transport_errors() -> None:
    def failing_transport(payload: dict[str, str]) -> None:
        raise RuntimeError("network down")

    connector = SlackConnector(transport=failing_transport)

    plan = SprintPlan(committed_items=(), total_points=8, capacity=10)
    result = connector.post_sprint_plan(plan)

    assert result.status == "failed"
    assert "network down" in result.message


def test_jira_connector_builds_issue_payload_and_stores_locally() -> None:
    connector = JiraConnector(project_key="POA")
    item = _sample_backlog_item("POA-888")

    result = connector.push_story(item)

    assert result.status == "success"
    assert connector.issue_payloads[-1].issue_key == "POA-888"
    assert isinstance(connector.issue_payloads[-1], JiraIssuePayload)
    assert "Stored locally" in result.message


def test_jira_connector_reports_transport_errors() -> None:
    def failing_transport(payload: dict[str, object]) -> None:
        raise RuntimeError(f"Failed for {payload['issue_key']}")

    connector = JiraConnector(transport=failing_transport)
    item = _sample_backlog_item("POA-889")

    result = connector.push_story(item)

    assert result.status == "failed"
    assert "Failed for POA-889" in result.message
