# OpenAI-Project Call Center Platform

## Overview

This repository delivers a production-aligned call center platform implementing the capabilities defined in [`docs/call_center_prd.md`](docs/call_center_prd.md). It now includes:

- **FastAPI services** that expose authenticated REST APIs for agent management, interaction routing, dashboards, reporting exports, and webhook integrations.
- **Mock omnichannel integrations** that model voice, web chat, mobile messaging, Salesforce, and Zendesk workflows using in-memory data sets for deterministic local development.
- **Compliance and security controls** including Firebase-backed authentication, encrypted recording retention, transcript redaction, structured audit logging, and configurable retention policies.
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

2. Provide Firebase configuration for authentication by setting the variables defined in `call_center/config.py` (for example, `CALL_CENTER_FIREBASE_PROJECT_ID` and `CALL_CENTER_FIREBASE_EMULATOR_JWT_SECRET`). When targeting a live Firebase project, supply `CALL_CENTER_FIREBASE_SERVICE_ACCOUNT_CERT` with a PEM-encoded certificate so ID tokens can be verified. The mock integrations ship with canned data and require no additional credentials.

3. Launch the API and UI server:

   ```bash
   uvicorn call_center.api.server:app --reload
   ```

4. Create an administrator through the `/api/agents` endpoint, link the agent to a Firebase UID via `/api/agents/{id}/identity`, and start the Firebase Auth emulator (or configure your live Firebase project).

5. Visit `http://localhost:8000/login` to sign in with your Firebase credentials. Upon successful authentication you will be redirected to `http://localhost:8000/` with a bearer token attached to the request.

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

## Publishing Changes to GitHub

This sandbox environment does not have direct access to GitHub remotes. To publish
your local commits:

1. Add your GitHub repository as a remote:

   ```bash
   git remote add origin git@github.com:<your-account>/<your-repo>.git
   ```

   Replace `<your-account>/<your-repo>` with the actual path to your GitHub
   repository and ensure your SSH key is configured for pushes.

2. Confirm the remote is configured correctly:

   ```bash
   git remote -v
   ```

3. Push the current branch (named `work` in this environment) to GitHub:

   ```bash
   git push -u origin work
   ```

If you are operating inside a restricted environment where outbound network
access is blocked, copy the repository contents to your local machine and run
the commands above from there.
