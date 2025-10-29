# OpenAI-Project Call Center Platform

## Overview

This repository delivers a production-aligned call center platform implementing the capabilities defined in [`docs/call_center_prd.md`](docs/call_center_prd.md). It now includes:

- **FastAPI services** that expose authenticated REST APIs for agent management, interaction routing, dashboards, reporting exports, and webhook integrations.
- **Omnichannel integrations** with Twilio Voice, hosted web chat, mobile messaging, Salesforce, and Zendesk via dedicated gateway classes in `call_center/integrations`.
- **Compliance and security controls** including OAuth2/SAML-friendly token issuance, encrypted recording retention, transcript redaction, structured audit logging, and configurable retention policies.
- **Persistent storage** built on SQLAlchemy with async SQLite for quick starts and compatibility with PostgreSQL in production deployments.
- **Responsive supervisor and agent desktop UI** served through FastAPI with accessible styling, queue visualizations, and live interaction status.
- **Observability hooks** covering Prometheus metrics, structured JSON logging, and environment-driven configuration management.

## Getting Started

1. Create and activate a Python 3.11+ virtual environment, then install the project with development extras:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```

2. Populate credentials for external providers via environment variables or a `.env` file using the prefixes defined in `call_center/config.py` (for example, `CALL_CENTER_TWILIO_ACCOUNT_SID`, `CALL_CENTER_SALESFORCE_CLIENT_ID`).

3. Launch the API and UI server:

   ```bash
   uvicorn call_center.api.server:app --reload
   ```

4. Create an administrator through the `/api/agents` endpoint, set a password using `/api/agents/{id}/password`, request an OAuth token from `/api/auth/token`, and then open `http://localhost:8000/` to access the supervisor console.

## Metrics and Observability

- Prometheus metrics are exposed at `/metrics` when `CALL_CENTER_PROMETHEUS_ENABLED=true` (default).
- Structured logs are emitted in JSON via `structlog` and can be forwarded to your observability stack.
- Audit entries are available through the `AuditLogger` utility for compliance reviews.

## Additional Tooling

- The in-memory CLI demo remains available for quick experimentation:

  ```bash
  python -m call_center.demo
  ```

- Automated tests validate routing, integrations, and compliance behaviors:

  ```bash
  pytest
  ```

Refer to the PRD for the full scope and to `docs/` for supplemental documentation.
