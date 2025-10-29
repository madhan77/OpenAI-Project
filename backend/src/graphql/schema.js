import { gql } from 'apollo-server-express';

export const typeDefs = gql`
  scalar DateTime

  type Query {
    healthStatus: HealthStatus!
    activities: [Activity!]!
    sleepSessions: [SleepSession!]!
    nutritionEntries: [NutritionEntry!]!
    hydrationLogs: [HydrationLog!]!
    heartRateSamples: [HeartRateSample!]!
    mindfulnessSessions: [MindfulnessSession!]!
    goals: [Goal!]!
    wellnessSummary: WellnessSummary!
    dailyCheckIns: [DailyCheckIn!]!
    dailyInsights: [Insight!]!
    weeklyProgress(days: Int = 7): WeeklyProgress!
  }

  type Mutation {
    addActivity(input: ActivityInput!): Activity!
    logSleepSession(input: SleepSessionInput!): SleepSession!
    logNutritionEntry(input: NutritionEntryInput!): NutritionEntry!
    logHydration(input: HydrationInput!): HydrationLog!
    logHeartRate(input: HeartRateInput!): HeartRateSample!
    logMindfulnessSession(input: MindfulnessSessionInput!): MindfulnessSession!
    logDailyCheckIn(input: DailyCheckInInput!): DailyCheckIn!
    setGoal(input: GoalInput!): Goal!
    updateDailySummary(input: DailySummaryInput!): WellnessSummary!
  }

  type HealthStatus {
    status: String!
    timestamp: DateTime!
  }

  type Activity {
    id: ID!
    type: String!
    durationMinutes: Int!
    caloriesBurned: Int!
    steps: Int
    recordedAt: DateTime!
  }

  input ActivityInput {
    type: String!
    durationMinutes: Int!
    caloriesBurned: Int!
    steps: Int
    recordedAt: DateTime
  }

  input DailySummaryInput {
    date: DateTime!
    steps: Int
    caloriesIntake: Int
    caloriesBurned: Int
    sleepHours: Float
    hydrationOz: Float
    restingHeartRate: Int
    proteinGrams: Float
    carbsGrams: Float
    fatGrams: Float
    moodScore: Float
    stressLevel: Float
    energyLevel: Float
  }

  type WellnessSummary {
    date: DateTime!
    steps: Int
    caloriesIntake: Int
    caloriesBurned: Int
    sleepHours: Float
    hydrationOz: Float
    restingHeartRate: Int
    proteinGrams: Float
    carbsGrams: Float
    fatGrams: Float
    moodScore: Float
    stressLevel: Float
    energyLevel: Float
  }

  type SleepSession {
    id: ID!
    startTime: DateTime!
    endTime: DateTime!
    durationMinutes: Int!
    qualityScore: Int
    stages: SleepStageBreakdown
    createdAt: DateTime!
  }

  input SleepSessionInput {
    startTime: DateTime!
    endTime: DateTime!
    qualityScore: Int
    stages: SleepStageInput
  }

  type SleepStageBreakdown {
    rem: Float
    deep: Float
    light: Float
    awake: Float
  }

  input SleepStageInput {
    rem: Float
    deep: Float
    light: Float
    awake: Float
  }

  type NutritionEntry {
    id: ID!
    name: String
    mealType: String!
    calories: Int!
    proteinGrams: Float
    carbsGrams: Float
    fatGrams: Float
    recordedAt: DateTime!
  }

  input NutritionEntryInput {
    name: String
    mealType: String!
    calories: Int!
    proteinGrams: Float
    carbsGrams: Float
    fatGrams: Float
    recordedAt: DateTime
  }

  type HydrationLog {
    id: ID!
    amountOz: Float!
    source: String
    recordedAt: DateTime!
  }

  input HydrationInput {
    amountOz: Float!
    source: String
    recordedAt: DateTime
  }

  type HeartRateSample {
    id: ID!
    bpm: Int!
    recordedAt: DateTime!
    context: String
  }

  input HeartRateInput {
    bpm: Int!
    recordedAt: DateTime
    context: String
  }

  type MindfulnessSession {
    id: ID!
    type: String!
    durationMinutes: Int!
    startedAt: DateTime!
    moodAfter: String
    notes: String
  }

  input MindfulnessSessionInput {
    type: String!
    durationMinutes: Int!
    startedAt: DateTime
    moodAfter: String
    notes: String
  }

  type DailyCheckIn {
    id: ID!
    moodScore: Float
    stressLevel: Float
    energyLevel: Float
    notes: String
    createdAt: DateTime!
  }

  input DailyCheckInInput {
    moodScore: Float
    stressLevel: Float
    energyLevel: Float
    notes: String
    createdAt: DateTime
  }

  type WeeklyProgress {
    startDate: DateTime!
    endDate: DateTime!
    days: [DailyProgress!]!
  }

  type DailyProgress {
    date: DateTime!
    steps: Int
    caloriesIntake: Int
    caloriesBurned: Int
    sleepHours: Float
    hydrationOz: Float
    mindfulnessMinutes: Int
    averageMood: Float
    averageStressLevel: Float
    checkInsLogged: Int!
  }

  type Insight {
    id: ID!
    category: String!
    message: String!
    severity: String!
    createdAt: DateTime!
  }

  type Goal {
    id: ID!
    type: String!
    targetValue: Float!
    unit: String!
    period: String!
    currentValue: Float
    description: String
    createdAt: DateTime!
    updatedAt: DateTime!
  }

  input GoalInput {
    type: String!
    targetValue: Float!
    unit: String!
    period: String!
    currentValue: Float
    description: String
  }
`;
