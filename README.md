# OpenAI-Project

This repository contains planning artifacts and the first implementation steps for the Wellness Tracker Agent mobile application.

## Project Artifacts
- [Wellness Tracker Agent — Product Requirements Document](docs/wellness_tracker_agent_prd.md)

## Backend Service
The `backend` directory contains a Node.js + Express + Apollo Server project that exposes a starter GraphQL API for tracking activities, sleep, nutrition, hydration, heart rate, mindfulness sessions, daily check-ins, personalized insights, goals, and rolling wellness summaries. Data is stored in-memory for now, which keeps the service simple while the domain model and integrations are explored.

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
