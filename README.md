# OpenAI-Project
OpenAI Project

## Call Center Agent Application

This repository contains a simplified in-memory implementation of the Call Center
Agent application described in [`docs/call_center_prd.md`](docs/call_center_prd.md).
It focuses on the MVP capabilities outlined in the PRD, including skills-based
routing, wrap-up enforcement, supervisor tooling, and quality controls.

### Features

- Register agents with roles, skills, and presence states.
- Configure queues with priorities, business rules, and wait time thresholds.
- Receive and route voice/chat interactions using multiple routing strategies.
- Transfer interactions between agents or queues, enforcing wrap-up codes before
  agents return to an available status.
- Support concurrent chat handling (up to two simultaneous chats per agent by
  default) while preserving wrap-up compliance gates.
- Generate supervisor dashboard snapshots and queue breach alerts.
- Schedule supervisor reports and manage recording redactions for QA workflows.

### Quick Start

Create a virtual environment with Python 3.10+ and install the package in
editable mode if desired:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Run the demo script to see a minimal workflow:

```bash
python -m call_center.demo
```

### Testing

Execute the automated test suite with `pytest`:

```bash
pytest
```
