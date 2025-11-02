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
   - Ensure the email/password sign-in method is enabled for your Firebase Authentication instance. Enable Google as a federated provider if you want to use the new one-click Gmail option described below.
2. **Serve the portal locally**
   - Open a terminal at the repository root (or a new window if you want to keep other processes running) and change into the portal directory:
     ```bash
     cd portal
     ```
   - Run the dev server from inside that directory:
     ```bash
     npm start
     ```
   The lightweight dev server will read your `.env` file, host the portal at `http://localhost:5173`, and automatically open the login page in your default browser. (Set `AUTO_OPEN=false` in the same shell if you prefer to launch the browser yourself.) You can still use any static web server if you prefer; just ensure Firebase credentials are provided via JSON or a custom script.
   - Want the login link echoed back in your terminal? Run `npm run login-url` from the same directory at any time to print both the local and Firebase-hosted URLs detected from your environment settings.
   - **Common typo:** If your terminal reports `zsh: command not found: nmp`, double-check the command spelling—the Node package manager is `npm`, not `nmp`.
3. **Sign in and explore**
   - Authenticate with a user provisioned in your Firebase project.
   - Need to create a reviewer account? Click **Create one** beneath the form to switch to sign-up mode, enter the new credentials (with password confirmation), and the portal will provision the Firebase user for you.
   - Prefer a faster sign-in? Click **Sign in with Google** to launch the OAuth flow for any Google account registered with your Firebase project.
   - Alternatively, click **Use Demo Mode** to explore the portal with mock data and no authentication (ideal when credentials are unavailable during review).
   - Review the mock claim queue, detailed breakdowns, and summary metrics that mirror the backend workflow outputs.

## Portal Login URLs
- **Local development:** [http://localhost:5173/](http://localhost:5173/) (after starting `npm start` inside the `portal/` directory).
- **Firebase Hosting:** `https://<your-project-id>.web.app/` or `https://<your-project-id>.firebaseapp.com/` once you deploy the `/portal` folder to your Firebase project. Replace `<your-project-id>` with the identifier from your Firebase console.
- **Command-line reminder:** `cd portal && npm run login-url` prints both links using the Firebase project ID discovered from your environment.

## Deploying the Portal to Firebase Hosting
If you open the hosted URL before deploying, Firebase will display a **Site Not Found** banner. Deploying the portal bundle resolves this:

1. **Install the Firebase CLI** (if you do not already have it):
   ```bash
   npm install -g firebase-tools
   ```
2. **Authenticate with Firebase** (only required the first time):
   ```bash
   firebase login
   ```
3. **Review the project configuration:**
   - The provided `.firebaserc` file defaults to the shared `open-ai-project-723a7` project ID. Update it if you plan to deploy elsewhere.
   - `firebase.json` points hosting to the `portal/` directory and rewrites requests to `index.html` for the single-page app.
4. **Deploy the reviewer portal:**
   ```bash
   cd portal
   npm run deploy
   ```
   If you have not installed the Firebase CLI yet, run `npm install -g firebase-tools` first (or install it locally inside the `portal/` folder). The helper script wraps the Firebase CLI, automatically targeting the project ID from `.firebaserc`, your environment variables, or the shared `open-ai-project-723a7` fallback. When the command finishes you should be able to load `https://<project-id>.web.app/` without seeing the Site Not Found message.

Need to verify the links after deploying? Run `npm --prefix portal run login-url` to print the local and hosted URLs again. The deploy script also echoes the expected hosted URL on success so you can click it immediately.

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
