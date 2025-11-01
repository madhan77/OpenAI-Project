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
   - Copy `portal/.env.example` to `portal/.env.local` (or `.env`) so the local dev server can expose the Firebase credentials at runtime. The example file already contains the Firebase project shared for review:
     ```bash
     VITE_FIREBASE_API_KEY="AIzaSyB-bo4wgmeLm0Wg1eTiiFe69l6fuXRGCns"
     VITE_FIREBASE_AUTH_DOMAIN="open-ai-project-723a7.firebaseapp.com"
     VITE_FIREBASE_PROJECT_ID="open-ai-project-723a7"
     VITE_FIREBASE_APP_ID="project-299553862015"
     ```
   - The Node-based dev server reads these `.env` files automatically and serves a `firebase-env.js` helper. For static hosting without a build step, you can still copy `portal/firebase-config.example.json` to `portal/firebase-config.json` and reuse the same values or create `portal/firebase-config.local.js` that sets `window.FIREBASE_CONFIG = { ... }`.
   - If you skip the environment files entirely, the portal falls back to the shared Firebase credentials embedded in `portal/firebase-env.js`, so reviewers can sign in immediately after starting the server.
   - Ensure the email/password sign-in method is enabled for your Firebase Authentication instance.
2. **Serve the portal locally**
   ```bash
   cd portal
   npm start
   ```
   The lightweight dev server will read your `.env` file and host the portal at `http://localhost:5173`. (You can still use any static web server if you prefer; just ensure Firebase credentials are provided via JSON or a custom script.)
3. **Sign in and explore**
   - Authenticate with a user provisioned in your Firebase project.
   - Review the mock claim queue, detailed breakdowns, and summary metrics that mirror the backend workflow outputs.

## Portal Login Link
- **Local development:** [http://localhost:5173/](http://localhost:5173/) (after starting a static server in the `portal/` directory).
- **Firebase Hosting:** `https://<your-project-id>.web.app/` or `https://<your-project-id>.firebaseapp.com/` once you deploy the `/portal` folder to your Firebase project. Replace `<your-project-id>` with the identifier from your Firebase console.

## Documentation
- [PRD](docs/claims-processing-prd.md)
- [Application Architecture](docs/claims-processing-app.md)

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
