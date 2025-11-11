# PO Assist Agent Prototype

This document captures the initial prototype for the Product Owner Assist Agent (POA) based on the approved PRD. The goal of the prototype is to demonstrate end-to-end automation for the highest priority workflows: idea capture, backlog readiness, meeting documentation, and sprint planning recommendations.

## Architecture

The prototype is implemented as a Python package `poa_app` that exposes a facade `POAssistAgent`. The agent stitches together specialised modules so that downstream surfaces (CLI, chat UI, integrations) only need to interact with a single object.

```
POAssistAgent
├── evaluation.py        # Heuristics that turn product ideas into backlog items
├── generators.py        # Structured user story templates with acceptance criteria
├── meetings.py          # Meeting summarisation and action item extraction
├── prioritizer.py       # WSJF-style ranking with dependency & status awareness
├── repository.py        # In-memory backlog + meeting storage for rapid iteration
└── sprint_planning.py   # Capacity-aware sprint planning suggestions
```

## Capabilities

| Capability | Description | Prototype Output |
|------------|-------------|------------------|
| Idea Capture | `POAssistAgent.capture_idea()` evaluates a `ProductIdea`, generates a user story, and stores a backlog item with WSJF metrics. | `BacklogItem` with attached `UserStory`, ready for refinement. |
| Backlog Prioritisation | `POAssistAgent.prioritise_backlog_repository()` or `prioritise_backlog()` ranks items using WSJF, dependency penalties, and status checks. | Ordered `PrioritizedBacklogItem` list for planning. |
| Meeting Analysis | `POAssistAgent.register_meeting()` persists `MeetingRecord`s with summaries, action items, risks, and clarity gaps. | `MeetingRecord` accessible via `recent_meetings()`. |
| Sprint Planning | `POAssistAgent.plan_next_sprint()` composes prioritisation with capacity-aware selection. | `SprintPlan` containing committed items, total points, and planning notes. |

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

### Previewing the Workflow

To generate a shareable snapshot of the current backlog, recent meetings, and sprint plan, call the preview helper:

```python
from poa_app import build_preview, POAssistAgent

agent = POAssistAgent()
# populate the agent using capture_idea / register_meeting...

preview = build_preview(agent)
print(preview.as_markdown())
```

For a ready-to-run demo seeded with sample data use:

```bash
python -m poa_app.preview
```

## Next Steps

- Wire the repositories to persistent storage (PostgreSQL or Airtable) so the agent can run in a multi-user environment.
- Extend the meeting analysis module to propose follow-up backlog entries automatically.
- Provide API/CLI layers that expose the facade within Slack or Jira automation scripts.
- Integrate velocity history and dependency graphs for more accurate sprint forecasting.

