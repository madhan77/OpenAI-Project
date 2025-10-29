# Enterprise Sales Agent

This repository contains a reference implementation of the **Enterprise Sales Agent**
described in the accompanying product requirements document. The application bundles
core workflows sales teams need to accelerate enterprise deals: account briefings,
meeting preparation, pipeline analysis, and follow-up task automation.

The project ships with:

- An in-memory dataset representing enterprise accounts, opportunities, stakeholders,
  and meetings.
- Service modules that orchestrate briefing, meeting support, pipeline management,
  and task automation workflows.
- A simple rule-based conversation engine that routes natural language prompts to the
  correct workflow.
- A command line interface for exploring the agent end-to-end.
- Automated unit tests covering the primary user journeys.

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
python scripts/enterprise_sales_agent_cli.py briefing "Acme Industries"
python scripts/enterprise_sales_agent_cli.py meeting "Globex Corporation"
python scripts/enterprise_sales_agent_cli.py pipeline "Acme Industries"
python scripts/enterprise_sales_agent_cli.py task "Acme Industries" "Jordan Blake" "Send ROI benchmarks"
python scripts/enterprise_sales_agent_cli.py chat "Prepare meeting for Globex Corporation"
```

## Project Structure

```
├── docs/
│   └── enterprise-sales-agent-prd.md
├── scripts/
│   └── enterprise_sales_agent_cli.py
├── src/
│   └── enterprise_sales_agent/
│       ├── app.py
│       ├── data.py
│       ├── integrations/
│       │   ├── crm.py
│       │   └── knowledge_base.py
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

