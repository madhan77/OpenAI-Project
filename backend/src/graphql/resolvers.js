import { GraphQLScalarType, Kind } from 'graphql';
import { v4 as uuid } from 'uuid';
import {
  activityStore,
  summaryStore,
  sleepStore,
  nutritionStore,
  hydrationStore,
  heartRateStore,
  mindfulnessStore,
  goalStore,
  checkInStore,
} from '../data/memoryStore.js';
import { generateDailyInsights } from '../services/insights.js';
import { generateWeeklyProgress } from '../services/reports.js';

const DateTimeScalar = new GraphQLScalarType({
  name: 'DateTime',
  description: 'ISO-8601 compliant DateTime type',
  serialize(value) {
    if (value instanceof Date) {
      return value.toISOString();
    }
    return new Date(value).toISOString();
  },
  parseValue(value) {
    return new Date(value);
  },
  parseLiteral(ast) {
    if (ast.kind === Kind.STRING) {
      return new Date(ast.value);
    }
    return null;
  },
});

const ensureDate = (value, fieldName) => {
  const parsed = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    throw new Error(`${fieldName} must be a valid DateTime value`);
  }
  return parsed;
};

const calculateDurationMinutes = (start, end) => {
  const durationMs = end.getTime() - start.getTime();
  if (durationMs <= 0) {
    throw new Error('endTime must be after startTime');
  }
  return Math.round(durationMs / 60000);
};

export const resolvers = {
  DateTime: DateTimeScalar,
  Query: {
    healthStatus: () => ({
      status: 'ok',
      timestamp: new Date(),
    }),
    activities: () => activityStore.getActivities(),
    sleepSessions: () => sleepStore.getSessions(),
    nutritionEntries: () => nutritionStore.getEntries(),
    hydrationLogs: () => hydrationStore.getLogs(),
    heartRateSamples: () => heartRateStore.getSamples(),
    mindfulnessSessions: () => mindfulnessStore.getSessions(),
    goals: () => goalStore.getGoals(),
    wellnessSummary: () => summaryStore.getSummary(),
    dailyCheckIns: () => checkInStore.getCheckIns(),
    dailyInsights: () =>
      generateDailyInsights({
        summary: summaryStore.getSummary(),
        activities: activityStore.getActivities(),
        sleepSessions: sleepStore.getSessions(),
        nutritionEntries: nutritionStore.getEntries(),
        hydrationLogs: hydrationStore.getLogs(),
        heartRateSamples: heartRateStore.getSamples(),
        goals: goalStore.getGoals(),
        mindfulnessSessions: mindfulnessStore.getSessions(),
        dailyCheckIns: checkInStore.getCheckIns(),
      }),
    weeklyProgress: (_, { days = 7 }) =>
      generateWeeklyProgress({
        days,
        now: new Date(),
        activities: activityStore.getActivities(),
        sleepSessions: sleepStore.getSessions(),
        nutritionEntries: nutritionStore.getEntries(),
        hydrationLogs: hydrationStore.getLogs(),
        mindfulnessSessions: mindfulnessStore.getSessions(),
        checkIns: checkInStore.getCheckIns(),
      }),
  },
  Mutation: {
    addActivity: (_, { input }) => {
      const activity = {
        id: uuid(),
        ...input,
        recordedAt: input.recordedAt ? ensureDate(input.recordedAt, 'recordedAt') : new Date(),
      };
      activityStore.addActivity(activity);
      summaryStore.updateFromActivity(activity);
      return activity;
    },
    logSleepSession: (_, { input }) => {
      const startTime = ensureDate(input.startTime, 'startTime');
      const endTime = ensureDate(input.endTime, 'endTime');
      const durationMinutes = calculateDurationMinutes(startTime, endTime);
      const session = {
        id: uuid(),
        startTime,
        endTime,
        durationMinutes,
        qualityScore: input.qualityScore ?? null,
        stages: input.stages ? { ...input.stages } : null,
        createdAt: new Date(),
      };
      sleepStore.addSession(session);
      summaryStore.updateFromSleep(durationMinutes);
      return session;
    },
    logNutritionEntry: (_, { input }) => {
      const entry = {
        id: uuid(),
        name: input.name ?? null,
        mealType: input.mealType,
        calories: input.calories,
        proteinGrams: input.proteinGrams ?? null,
        carbsGrams: input.carbsGrams ?? null,
        fatGrams: input.fatGrams ?? null,
        recordedAt: input.recordedAt ? ensureDate(input.recordedAt, 'recordedAt') : new Date(),
      };
      nutritionStore.addEntry(entry);
      summaryStore.updateFromNutrition(entry);
      return entry;
    },
    logHydration: (_, { input }) => {
      const log = {
        id: uuid(),
        amountOz: input.amountOz,
        source: input.source ?? null,
        recordedAt: input.recordedAt ? ensureDate(input.recordedAt, 'recordedAt') : new Date(),
      };
      hydrationStore.addLog(log);
      summaryStore.updateFromHydration(log);
      return log;
    },
    logHeartRate: (_, { input }) => {
      if (input.bpm <= 0) {
        throw new Error('Heart rate must be a positive value');
      }

      const sample = {
        id: uuid(),
        bpm: input.bpm,
        recordedAt: input.recordedAt ? ensureDate(input.recordedAt, 'recordedAt') : new Date(),
        context: input.context ?? null,
      };
      heartRateStore.addSample(sample);
      summaryStore.updateFromHeartRate(sample);
      return sample;
    },
    logMindfulnessSession: (_, { input }) => {
      if (input.durationMinutes <= 0) {
        throw new Error('Mindfulness session duration must be positive');
      }

      const session = {
        id: uuid(),
        type: input.type,
        durationMinutes: input.durationMinutes,
        startedAt: input.startedAt ? ensureDate(input.startedAt, 'startedAt') : new Date(),
        moodAfter: input.moodAfter ?? null,
        notes: input.notes ?? null,
      };
      mindfulnessStore.addSession(session);
      return session;
    },
    logDailyCheckIn: (_, { input }) => {
      const validateScore = (value, field) => {
        if (value === undefined || value === null) {
          return null;
        }

        if (typeof value !== 'number' || Number.isNaN(value)) {
          throw new Error(`${field} must be a numeric value between 1 and 5`);
        }

        if (value < 1 || value > 5) {
          throw new Error(`${field} must be between 1 and 5`);
        }

        return value;
      };

      const checkIn = {
        id: uuid(),
        moodScore: validateScore(input.moodScore, 'moodScore'),
        stressLevel: validateScore(input.stressLevel, 'stressLevel'),
        energyLevel: validateScore(input.energyLevel, 'energyLevel'),
        notes: input.notes ?? null,
        createdAt: input.createdAt ? ensureDate(input.createdAt, 'createdAt') : new Date(),
      };

      checkInStore.addCheckIn(checkIn);
      summaryStore.updateFromCheckIn(checkIn);
      return checkIn;
    },
    setGoal: (_, { input }) => {
      const now = new Date();
      const goal = {
        id: uuid(),
        type: input.type,
        targetValue: input.targetValue,
        unit: input.unit,
        period: input.period,
        currentValue: input.currentValue ?? null,
        description: input.description ?? null,
        createdAt: now,
        updatedAt: now,
      };
      return goalStore.upsertGoal(goal);
    },
    updateDailySummary: (_, { input }) => {
      return summaryStore.updateSummary(input);
    },
  },
};
