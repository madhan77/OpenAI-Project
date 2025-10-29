# OpenAI-Project

This repository contains planning artifacts and the first implementation steps for the Wellness Tracker Agent mobile application.

## Project Artifacts
- [Wellness Tracker Agent — Product Requirements Document](docs/wellness_tracker_agent_prd.md)

## Backend Service
The `backend` directory contains a Node.js + Express + Apollo Server project that exposes a starter GraphQL API for tracking activities, sleep, nutrition, hydration, heart rate, mindfulness sessions, daily check-ins, personalized insights, goals, and rolling wellness summaries. Wellness data is now persisted to disk using a lightweight JSON document store so records survive service restarts while deeper infrastructure work (PostgreSQL, Redis, etc.) is planned.

### Getting Started
1. Install dependencies:
   ```bash
   cd backend
   npm install
   ```
2. Configure environment variables:
   ```bash
   cp .env.example .env
   # adjust values as needed
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Access the health check at `http://localhost:4000/health` and the GraphQL Playground at `http://localhost:4000/graphql`.

### Data Persistence

- Logged activity, recovery, and wellness data is written to `backend/storage/store.json`. The file is automatically created the first time the service receives a mutation.
- The storage directory already ignores `store.json` in git so you can safely reset the datastore by deleting the file.
- Because the service aggregates the complete dataset after each write, manual edits to `store.json` should maintain the expected property shapes (ISO date strings, numeric metrics) to avoid inconsistent summaries.

### GraphQL Overview

The schema focuses on early wellness tracking primitives that map to the product requirements document. Queries provide read access to activities, sleep sessions, nutrition entries, hydration logs, heart rate samples, mindfulness sessions, daily check-ins, goals, daily insights, and aggregated wellness and weekly progress reports. Mutations allow creating new logs, recording check-ins, and upserting goals while keeping the summary metrics synchronized.

Example query fetching the latest metrics:

```graphql
query WellnessDashboard {
  wellnessSummary {
    date
    steps
    caloriesIntake
    caloriesBurned
    sleepHours
    hydrationOz
    restingHeartRate
    proteinGrams
    carbsGrams
    fatGrams
    moodScore
    stressLevel
    energyLevel
  }
  activities {
    id
    type
    durationMinutes
    caloriesBurned
    steps
    recordedAt
  }
  sleepSessions {
    id
    durationMinutes
    qualityScore
  }
  nutritionEntries {
    id
    mealType
    calories
  }
  hydrationLogs {
    id
    amountOz
  }
  heartRateSamples {
    id
    bpm
    context
  }
  mindfulnessSessions {
    id
    type
    durationMinutes
  }
  goals {
    id
    type
    targetValue
    unit
    period
  }
  dailyCheckIns {
    id
    moodScore
    stressLevel
    energyLevel
    createdAt
  }
  dailyInsights {
    id
    category
    message
    severity
  }
  weeklyProgress(days: 7) {
    startDate
    endDate
    days {
      date
      steps
      caloriesIntake
      caloriesBurned
      sleepHours
      hydrationOz
      mindfulnessMinutes
      averageMood
      averageStressLevel
      checkInsLogged
    }
  }
}
```

## Frontend Web Client

The `frontend` directory houses a Vite + React + TypeScript single-page application that visualizes the API. It connects to the GraphQL backend using Apollo Client and includes an initial dashboard experience with daily summary cards, AI-powered insights, and a weekly progress grid.

### Getting Started

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Configure environment variables (optional):
   ```bash
   cp .env.example .env
   # set VITE_GRAPHQL_URL if the backend is not running on http://localhost:4000/graphql
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open the app at the URL shown in the terminal (default `http://localhost:5173`).

### Key Files

- `src/services/apolloClient.ts` configures Apollo Client and targets the backend GraphQL endpoint.
- `src/pages/DashboardPage.tsx` issues the wellness dashboard query and orchestrates the page layout.
- `src/components/` contains modular UI building blocks such as the app shell, summary cards, insights panel, and weekly progress grid.
- `src/styles/global.css` defines the global design foundation shared across components.

The frontend is intentionally lightweight to accelerate iteration; future milestones will introduce routing, authentication, richer analytics visualizations, and mobile responsiveness enhancements aligned with the product requirements.
