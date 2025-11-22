# Firebase Hosting Deployment Guide

This project includes two static experiences you can deploy to Firebase Hosting:

- `portal/` — the claims reviewer portal secured by Firebase Authentication.
- `field-service-prototype/` — the mock field service experience with demo data.

## Prerequisites
- Install the Firebase CLI: `npm install -g firebase-tools`.
- Confirm you have access to the target Firebase project and hosting site IDs.

## One-Time Setup
1. Authenticate and select the project:
   ```bash
   firebase login
   firebase use open-ai-project-723a7
   ```
2. Map hosting targets to your site IDs (run once per machine):
   ```bash
   firebase target:apply hosting portal open-ai-project-723a7
   firebase target:apply hosting fieldService open-ai-project-723a7
   ```
   - If you prefer a separate hosting site, replace the IDs above with your preferred site IDs.
3. `.firebaserc` is preconfigured with the provided project and hosting targets (portal/fieldService) mapped to `open-ai-project-723a7`. Adjust the mapping if you plan to use different site IDs.

## Deploy
To deploy both experiences:
```bash
firebase deploy --only hosting:portal,hosting:fieldService
```

To deploy just the field service prototype:
```bash
firebase deploy --only hosting:fieldService
```

## Preview with Hosting Emulator
```bash
firebase emulators:start --only hosting
```
Open the URLs printed by the CLI to verify the pages locally using the Firebase Hosting emulator.

## Notes
- Both hosting targets serve from their respective directories and rewrite all routes to `index.html` for SPA-style navigation.
- The repo remains static; no build step is required for either experience.
