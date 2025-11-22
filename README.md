# Health Claims Processing Platform

This repository contains a reference implementation of a health claims processing platform that aligns with the product requirements document (PRD) and is ready for formal stakeholder review.

## Features
- Intake, validation, manual review, and auto-adjudication orchestrated by `ClaimsProcessingApp`.
- Modular validators and rules capturing eligibility, documentation, coding, duplicate detection, and policy heuristics.
- Manual review work queue, payment instruction and EOB generation, and multi-channel notifications.
- In-memory repositories and metrics collectors for deterministic tests with clear extension points.
- Web portal prototype secured by Firebase Authentication for claim reviewers.

## Getting Started (Workflow Engine)
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt  # if using additional deps
   ```
   *(The core app uses only the Python standard library and `pytest` for tests.)*
2. **Run the test suite**
   ```bash
   pytest
   ```
3. **Explore the workflow**
   - Use the fixtures in `tests/test_claims_processing_app.py` as examples for constructing claims.
   - Instantiate `claims_app.ClaimsProcessingApp` to submit and process claims end to end.

## Running the Claims Portal Prototype
1. **Configure Firebase**
   - Copy `portal/firebase-config.example.js` to `portal/firebase-config.js`.
   - Replace the placeholder values with the configuration from your Firebase project (Settings → General → Your apps).
   - Ensure the email/password sign-in method is enabled for your Firebase Authentication instance.
2. **Serve the portal locally**
   ```bash
   cd portal
   python -m http.server 5173
   ```
   Then open `http://localhost:5173` in your browser. Any static web server will work.
3. **Sign in and explore**
   - Authenticate with a user provisioned in your Firebase project.
   - Review the mock claim queue, detailed breakdowns, and summary metrics that mirror the backend workflow outputs.

## Portal Login Link
- **Local development:** [http://localhost:5173/](http://localhost:5173/) (after starting a static server in the `portal/` directory).
- **Firebase Hosting:** `https://<your-project-id>.web.app/` or `https://<your-project-id>.firebaseapp.com/` once you deploy the `/portal` folder to your Firebase project. Replace `<your-project-id>` with the identifier from your Firebase console.

## Field Service Prototype (Mock Data)
- **Purpose:** Demo experience for field service coordinators and technicians to explore appointments, checklist completion, materials, timelines, and customer handoff data.
- **Run locally:**
  ```bash
  cd field-service-prototype
  python -m http.server 4173
  ```
  Then open [http://localhost:4173](http://localhost:4173) in your browser.
- **Firebase Hosting:** Use the shared hosting configuration to deploy the static prototype with `firebase deploy --only hosting:fieldService` after mapping the `fieldService` target to your site ID. See [Firebase Hosting Deployment Guide](docs/firebase-hosting.md).

## Documentation
- [PRD](docs/claims-processing-prd.md)
- [Application Architecture](docs/claims-processing-app.md)
- [Firebase Hosting Deployment Guide](docs/firebase-hosting.md)

## Project Structure
```
claims_app/        # Application modules (workflow, models, validators, rules, etc.)
agents/            # Convenience exports for downstream integrations
docs/              # Product and technical documentation
portal/            # Firebase-authenticated reviewer portal with mock data
tests/             # Pytest coverage demonstrating key workflows
```

## Contributing
Contributions should preserve the modular architecture and include pytest coverage for new behaviour. Please update documentation when introducing new workflows or policy rules.
