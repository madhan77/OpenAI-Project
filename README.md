# Enterprise Sales Agent

This repository contains a reference implementation of the **Enterprise Sales Agent**
described in the accompanying product requirements document. The application bundles
core workflows sales teams need to accelerate enterprise deals: account briefings,
meeting preparation, pipeline analysis, and follow-up task automation.

The project ships with:

- A curated mock dataset representing enterprise accounts, opportunities,
  stakeholders, meetings, and follow-up tasks.
- Service modules that orchestrate briefing, meeting support, pipeline management,
  and task automation workflows.
- A simple rule-based conversation engine that routes natural language prompts to the
  correct workflow.
- A command line interface for exploring the agent end-to-end.
- Automated unit tests covering the primary user journeys.

## Mock Data and Offline-Friendly Setup

All business logic runs entirely against the mock dataset stored in
`src/enterprise_sales_agent/resources/mock_dataset.json`. The data mirrors the types of
records described in the PRD while remaining safe for demos and local development. You
can edit the JSON file or load alternative fixtures to model your own accounts without
touching any production systems.

## Getting Started

The project targets Python 3.10+. Create and activate a virtual environment, install
the package in editable mode, and run the test suite:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m unittest discover
```

To explore the agent via the CLI:

```bash
# Anonymous prototyping using the built-in mock dataset
python scripts/enterprise_sales_agent_cli.py briefing "Acme Industries"
python scripts/enterprise_sales_agent_cli.py meeting "Globex Corporation"
python scripts/enterprise_sales_agent_cli.py pipeline "Acme Industries"
python scripts/enterprise_sales_agent_cli.py task "Acme Industries" "Jordan Blake" "Send ROI benchmarks"
python scripts/enterprise_sales_agent_cli.py chat "Prepare meeting for Globex Corporation"

# Authenticated usage with Firebase (see below for configuration details)
python scripts/enterprise_sales_agent_cli.py \
  --firebase-token "<ID_TOKEN>" \
  --firebase-credentials path/to/service-account.json \
  --firebase-project your-project-id \
  briefing "Acme Industries"
```

## Firebase Authentication

For teams that want to gate access to the CLI or future web surfaces, the package now
includes a lightweight Firebase Authentication integration. Provide a Firebase ID token
alongside your service account credentials and project ID, and the CLI will verify the
token before running any workflows.

Environment variables offer an alternative to passing command-line flags:

```bash
export FIREBASE_CREDENTIALS=path/to/service-account.json
export FIREBASE_PROJECT_ID=your-project-id
python scripts/enterprise_sales_agent_cli.py --firebase-token "<ID_TOKEN>" briefing "Acme Industries"
```

When experimenting with the Firebase emulator, supply `--use-firebase-emulator` (or set
`FIREBASE_AUTH_EMULATOR_HOST`) and omit the service account file. The CLI will announce
the authenticated user for easier debugging.

## Project Structure

```
├── docs/
│   └── enterprise-sales-agent-prd.md
├── scripts/
│   └── enterprise_sales_agent_cli.py
├── src/
│   └── enterprise_sales_agent/
│       ├── app.py
│       ├── auth/
│       │   ├── __init__.py
│       │   └── firebase.py
│       ├── data.py
│       ├── integrations/
│       │   ├── crm.py
│       │   └── knowledge_base.py
│       ├── resources/
│       │   ├── __init__.py
│       │   └── mock_dataset.json
│       └── services/
│           ├── account_briefing.py
│           ├── conversation.py
│           ├── meeting_support.py
│           ├── pipeline_management.py
│           └── task_automation.py
└── tests/
    └── test_agent.py
```

## Extending the Agent

The implementation uses modular services to make it easy to plug in real integrations
as they become available. Each service accepts dependency instances in its constructor
so developers can swap in production connectors for CRM, knowledge bases, call
intelligence, or analytics without rewriting business logic. The mock data provides a
safe sandbox for iterating on prompts, workflows, and user experience before wiring
up live systems.

