# OpenAI-Project

This repository contains the Single Issue Management domain services (Python) and an accompanying web front end implemented with Vite + React.

## Front-end prototype

The prototype dashboard renders mock operational data so that the UI can be developed without depending on the production API. Authentication is handled through your Firebase project.

### Prerequisites

- Node.js 18+
- npm 9+
- A Firebase project with Google sign-in enabled

### Setup

1. Copy the Firebase web credentials for your project and add them to `frontend/.env.local`:

   ```env
   VITE_FIREBASE_API_KEY=your-api-key
   VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project-id
   VITE_FIREBASE_APP_ID=your-app-id
   ```

2. Install dependencies and start the development server:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Visit the printed URL (default `http://localhost:5173`) to use the dashboard with mock incident data.

The dashboard currently reads from static mock data located in `frontend/src/data/mockData.ts`. Replace this module with live API calls once the backend endpoints are ready.

## Python services

The in-memory domain services powering issue lifecycle logic remain available in `src/sima`. Run the test suite with:

```bash
pytest
```
