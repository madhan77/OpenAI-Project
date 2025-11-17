# PO Assist Agent Prototype

This document captures the evolving prototype for the Product Owner Assist Agent (POA) based on the approved PRD. The goal of the
prototype is to demonstrate end-to-end automation for the highest priority workflows: idea capture, backlog readiness, meeting
documentation, sprint planning recommendations, and roadmap visualisation with lightweight integrations.

## Architecture

The prototype is implemented as a Python package `poa_app` that exposes a facade `POAssistAgent`. The agent stitches together specialised
modules so that downstream surfaces (CLI, chat UI, integrations) only need to interact with a single object.

```
POAssistAgent
├── ingestion.py         # Natural-language parsing for ideas and meeting notes
├── evaluation.py        # Heuristics that turn product ideas into backlog items
├── generators.py        # Structured user story templates with acceptance criteria
├── meetings.py          # Meeting summarisation and action item extraction
├── prioritizer.py       # WSJF-style ranking with dependency & status awareness
├── sprint_planning.py   # Capacity-aware sprint planning suggestions
├── roadmap.py           # Quarterly roadmap distribution utilities
├── integrations.py      # Simulated connectors for Jira, Slack, and documentation
├── repository.py        # In-memory backlog + meeting storage for rapid iteration
└── preview.py           # Markdown preview snapshots for stakeholders
```

## Capabilities

| Capability | Description | Prototype Output |
|------------|-------------|------------------|
| Idea Capture | `POAssistAgent.capture_idea()` evaluates a `ProductIdea`, generates a user story, and stores a backlog item with WSJF metrics. | `BacklogItem` with attached `UserStory`, ready for refinement. |
| Natural Language Ingestion | `POAssistAgent.ingest_raw_idea()` and `log_meeting_notes()` convert free-form notes into structured artefacts. | Parsed `ProductIdea` metadata and `MeetingTranscript` with provenance notes. |
| Backlog Prioritisation | `POAssistAgent.prioritise_backlog_repository()` or `prioritise_backlog()` ranks items using WSJF, dependency penalties, and status checks. | Ordered `PrioritizedBacklogItem` list for planning. |
| Meeting Analysis | `POAssistAgent.register_meeting()` persists `MeetingRecord`s with summaries, action items, risks, and clarity gaps. | `MeetingRecord` accessible via `recent_meetings()`. |
| Sprint Planning | `POAssistAgent.plan_next_sprint()` composes prioritisation with capacity-aware selection. | `SprintPlan` containing committed items, total points, and planning notes. |
| Roadmap Visualisation | `POAssistAgent.build_roadmap()` organises prioritised work into quarterly buckets based on capacity. | `RoadmapTimeline` with markdown rendering support. |
| Integrations | `POAssistAgent.sync_backlog_item()`/`broadcast_meeting()`/`announce_sprint_plan()` push artefacts to Jira, Slack, and documentation connectors. | `IntegrationResult` records for auditability. |
| Preview Snapshots | `build_preview()` aggregates backlog, meetings, sprint plan, and roadmap into a single markdown digest. | Shareable markdown summary. |

## Usage Walkthrough

```python
from poa_app import (
    POAssistAgent,
    ProductIdea,
    SprintCapacity,
    build_preview,
)

agent = POAssistAgent()

# Capture a product idea and produce a backlog entry
idea = ProductIdea(
    title="Roadmap heatmap",
    persona="product owner",
    goal="visualise delivery confidence",
    benefit="I can communicate risk earlier",
    description="Interactive roadmap view with risk overlays and velocity insights.",
    tags=("analytics", "risk"),
)

item = agent.capture_idea("POA-101", idea)
agent.update_item_status(item.identifier, "ready")

# Draft a sprint plan using current capacity
capacity = SprintCapacity(available_points=18, focus_factor=0.75)
plan = agent.plan_next_sprint(capacity)

for entry in plan.committed_items:
    print(entry.rank, entry.item.identifier, entry.item.title)
```

### Natural Language Ingestion

```python
from poa_app import parse_product_idea

description = """
Title: Persona insights dashboard
As a product owner, I want to review persona coverage so that gaps are visible.
Constraints: Connect to Jira, Share summaries to Slack
Tags: insights, alignment
Impact: 8
"""

parsed = parse_product_idea(description)
print(parsed.idea.goal)  # => review persona coverage
```

### Roadmap and Previewing the Workflow

```python
from poa_app import build_preview

preview = build_preview(
    agent,
    capacity=SprintCapacity(available_points=20),
    roadmap_capacities=(("Q1", 20), ("Q2", 18)),
)
print(preview.as_markdown())
```

For a ready-to-run demo seeded with sample data use:

```bash
python -m poa_app.preview
```

## Integrations

The `IntegrationHub` bundles lightweight connectors that simulate syncing artefacts to Jira, Slack, and Notion/Confluence-style documentation. Each sync method returns `IntegrationResult` records so downstream services can audit behaviour or surface notifications.

```python
from poa_app import IntegrationHub

hub = IntegrationHub()
results = hub.sync_story(item)
for result in results:
    print(result.destination, result.status)
```

### Configuring Slack Delivery

The Slack connector now supports real webhook delivery. Provide a webhook URL via the `POA_SLACK_WEBHOOK_URL` environment variable or pass it directly to `SlackConnector` along with an optional custom channel. When no webhook is provided, the connector records structured payloads locally so you can inspect the generated messages.

```python
import os
from poa_app import IntegrationHub, SlackConnector

os.environ["POA_SLACK_WEBHOOK_URL"] = "https://hooks.slack.com/services/T000/B000/SECRET"
hub = IntegrationHub(slack=SlackConnector(channel="#delivery-alerts"))
hub.announce_sprint_plan(plan)
```

### Configuring Jira Delivery

`JiraConnector` mirrors the Slack configurability so local development is never blocked. You can:

- Supply `POA_JIRA_BASE_URL` (e.g., `https://example.atlassian.net`) to activate REST delivery.
- Inject a `transport` callable that receives the serialised `JiraIssuePayload` for custom posting or contract tests.
- Rely on the default in-memory mode where payloads are stored and `IntegrationResult` indicates "Stored locally" for deterministic tests.

```python
from poa_app import IntegrationHub, JiraConnector

hub = IntegrationHub(jira=JiraConnector(project_key="POA"))
results = hub.sync_story(item)
for result in results:
    print(result.destination, result.message)
```

## Next Steps

- Wire the repositories to persistent storage (PostgreSQL or Airtable) so the agent can run in a multi-user environment.
- Extend the meeting analysis module to propose follow-up backlog entries automatically.
- Provide API/CLI layers that expose the facade within Slack or Jira automation scripts.
- Integrate velocity history and dependency graphs for more accurate sprint forecasting.
- Replace simulated integrations with production-grade API clients.

