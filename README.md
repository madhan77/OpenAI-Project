# OpenAI-Project

This repository contains the Single Issue Management domain services (Python) and an accompanying web front end implemented with Vite + React.

## Front-end prototype

The prototype dashboard renders mock operational data so that the UI can be developed without depending on the production API. Authentication is handled through your Firebase project.

### Prerequisites

- Node.js 18+
- npm 9+
- A Firebase project with Google sign-in enabled

### Setup

1. Follow the [Firebase setup guide](docs/firebase-setup.md) if you need to provision a new Firebase project. This repository is
   preconfigured with credentials for `open-ai-project-723a7`.

2. Copy the example environment file (already populated with the provided Firebase credentials) to `.env.local`:

   ```bash
   cp frontend/.env.example frontend/.env.local
   ```

   The copied file contains:

   ```env
   VITE_FIREBASE_API_KEY="AIzaSyB-bo4wgmeLm0Wg1eTiiFe69l6fuXRGCns"
   VITE_FIREBASE_AUTH_DOMAIN="open-ai-project-723a7.firebaseapp.com"
   VITE_FIREBASE_PROJECT_ID="open-ai-project-723a7"
   VITE_FIREBASE_APP_ID="project-299553862015"
   ```

   Adjust these values only if you intend to connect a different Firebase project.

3. Install dependencies and start the development server:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. Visit the printed URL (default [`http://localhost:5173`](http://localhost:5173)) to use the dashboard with mock incident data.

### Login link

- Once the dev server is running, share [`http://localhost:5173/login`](http://localhost:5173/login) with stakeholders who need direct access to the Firebase login screen.
- The unauthenticated view now includes a "Copy link" action so you can quickly distribute the login URL without leaving the app.

The dashboard currently reads from static mock data located in `frontend/src/data/mockData.ts`. Replace this module with live API calls once the backend endpoints are ready.

## Python services

The in-memory domain services powering issue lifecycle logic remain available in `src/sima`. Run the test suite with:

```bash
pytest
```
