import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const STORAGE_DIR = path.resolve(__dirname, '../../storage');
const STORE_FILE = path.join(STORAGE_DIR, 'store.json');

const createDefaultSummary = () => ({
  date: new Date().toISOString(),
  steps: 0,
  caloriesIntake: 0,
  caloriesBurned: 0,
  sleepHours: 0,
  hydrationOz: 0,
  restingHeartRate: 0,
  proteinGrams: 0,
  carbsGrams: 0,
  fatGrams: 0,
  moodScore: null,
  stressLevel: null,
  energyLevel: null,
});

const createDefaultState = () => ({
  activities: [],
  sleepSessions: [],
  nutritionEntries: [],
  hydrationLogs: [],
  heartRateSamples: [],
  mindfulnessSessions: [],
  dailyCheckIns: [],
  goals: [],
  wellnessSummary: createDefaultSummary(),
});

let state = null;

const ensureStorageDir = () => {
  if (!fs.existsSync(STORAGE_DIR)) {
    fs.mkdirSync(STORAGE_DIR, { recursive: true });
  }
};

const normalizeState = (rawState) => {
  const base = createDefaultState();
  const stateWithDefaults = {
    ...base,
    ...rawState,
    activities: Array.isArray(rawState?.activities) ? rawState.activities : [],
    sleepSessions: Array.isArray(rawState?.sleepSessions)
      ? rawState.sleepSessions
      : [],
    nutritionEntries: Array.isArray(rawState?.nutritionEntries)
      ? rawState.nutritionEntries
      : [],
    hydrationLogs: Array.isArray(rawState?.hydrationLogs)
      ? rawState.hydrationLogs
      : [],
    heartRateSamples: Array.isArray(rawState?.heartRateSamples)
      ? rawState.heartRateSamples
      : [],
    mindfulnessSessions: Array.isArray(rawState?.mindfulnessSessions)
      ? rawState.mindfulnessSessions
      : [],
    dailyCheckIns: Array.isArray(rawState?.dailyCheckIns)
      ? rawState.dailyCheckIns
      : [],
    goals: Array.isArray(rawState?.goals) ? rawState.goals : [],
    wellnessSummary: {
      ...base.wellnessSummary,
      ...(rawState?.wellnessSummary ?? {}),
    },
  };

  return stateWithDefaults;
};

const loadState = () => {
  ensureStorageDir();
  if (!fs.existsSync(STORE_FILE)) {
    const initial = createDefaultState();
    fs.writeFileSync(STORE_FILE, JSON.stringify(initial, null, 2));
    return initial;
  }

  try {
    const content = fs.readFileSync(STORE_FILE, 'utf-8');
    if (!content) {
      return createDefaultState();
    }
    const parsed = JSON.parse(content);
    return normalizeState(parsed);
  } catch (error) {
    console.error('Failed to read store, recreating a new one', error);
    const initial = createDefaultState();
    fs.writeFileSync(STORE_FILE, JSON.stringify(initial, null, 2));
    return initial;
  }
};

const saveState = (data) => {
  ensureStorageDir();
  const normalized = normalizeState(data);
  fs.writeFileSync(STORE_FILE, JSON.stringify(normalized, null, 2));
  state = normalized;
};

const getState = () => {
  if (!state) {
    state = loadState();
  }
  return state;
};

const sumBy = (items, selector) =>
  items.reduce((total, item) => total + (Number(selector(item)) || 0), 0);

const toNumberOrNull = (value) => {
  if (value === undefined || value === null) {
    return null;
  }
  const numeric = Number(value);
  return Number.isNaN(numeric) ? null : numeric;
};

const calculateWellnessSummary = (data) => {
  const activitySteps = sumBy(data.activities, (activity) => activity.steps);
  const caloriesBurned = sumBy(
    data.activities,
    (activity) => activity.caloriesBurned
  );
  const caloriesIntake = sumBy(
    data.nutritionEntries,
    (entry) => entry.calories
  );
  const proteinGrams = sumBy(data.nutritionEntries, (entry) => entry.proteinGrams);
  const carbsGrams = sumBy(data.nutritionEntries, (entry) => entry.carbsGrams);
  const fatGrams = sumBy(data.nutritionEntries, (entry) => entry.fatGrams);
  const hydrationOz = sumBy(data.hydrationLogs, (log) => log.amountOz);
  const sleepMinutes = sumBy(
    data.sleepSessions,
    (session) => session.durationMinutes
  );
  const sleepHours = sleepMinutes / 60;

  const restingSamples = data.heartRateSamples.filter((sample) => {
    if (!sample.context) {
      return false;
    }
    return sample.context.toLowerCase().includes('rest');
  });

  const restingHeartRate =
    restingSamples.length > 0
      ? Math.round(sumBy(restingSamples, (sample) => sample.bpm) /
          restingSamples.length)
      : 0;

  const lastCheckIn = [...data.dailyCheckIns]
    .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
    .at(-1);

  return {
    date: new Date().toISOString(),
    steps: Math.round(activitySteps),
    caloriesIntake: Math.round(caloriesIntake),
    caloriesBurned: Math.round(caloriesBurned),
    sleepHours: Number.isFinite(sleepHours)
      ? Math.round(sleepHours * 100) / 100
      : 0,
    hydrationOz: Math.round(hydrationOz * 100) / 100,
    restingHeartRate,
    proteinGrams: Math.round(proteinGrams * 100) / 100,
    carbsGrams: Math.round(carbsGrams * 100) / 100,
    fatGrams: Math.round(fatGrams * 100) / 100,
    moodScore: toNumberOrNull(lastCheckIn?.moodScore),
    stressLevel: toNumberOrNull(lastCheckIn?.stressLevel),
    energyLevel: toNumberOrNull(lastCheckIn?.energyLevel),
  };
};

const withState = (mutator, { recalc = true } = {}) => {
  const data = getState();
  const result = mutator(data);
  if (recalc) {
    data.wellnessSummary = calculateWellnessSummary(data);
  }
  saveState(data);
  return result;
};

const toDate = (value) => {
  if (!value) {
    return value;
  }
  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? value : date;
};

const cloneWithDates = (record) => ({
  ...record,
  date: record?.date ? toDate(record.date) : record?.date,
  recordedAt: record?.recordedAt ? toDate(record.recordedAt) : record?.recordedAt,
  startTime: record?.startTime ? toDate(record.startTime) : record?.startTime,
  endTime: record?.endTime ? toDate(record.endTime) : record?.endTime,
  startedAt: record?.startedAt ? toDate(record.startedAt) : record?.startedAt,
  createdAt: record?.createdAt ? toDate(record.createdAt) : record?.createdAt,
  updatedAt: record?.updatedAt ? toDate(record.updatedAt) : record?.updatedAt,
});

const serialiseDates = (record, fields) => {
  const serialised = { ...record };
  fields.forEach((field) => {
    if (serialised[field] instanceof Date) {
      serialised[field] = serialised[field].toISOString();
    }
  });
  return serialised;
};

export const activityStore = {
  addActivity(activity) {
    const stored = serialiseDates(activity, ['recordedAt']);
    withState((data) => {
      data.activities.push(stored);
    });
    return cloneWithDates(stored);
  },
  getActivities() {
    return getState().activities.map((activity) => cloneWithDates(activity));
  },
};

export const sleepStore = {
  addSession(session) {
    const stored = serialiseDates(session, ['startTime', 'endTime', 'createdAt']);
    withState((data) => {
      data.sleepSessions.push(stored);
    });
    return cloneWithDates(stored);
  },
  getSessions() {
    return getState().sleepSessions.map((session) => cloneWithDates(session));
  },
};

export const nutritionStore = {
  addEntry(entry) {
    const stored = serialiseDates(entry, ['recordedAt']);
    withState((data) => {
      data.nutritionEntries.push(stored);
    });
    return cloneWithDates(stored);
  },
  getEntries() {
    return getState().nutritionEntries.map((entry) => cloneWithDates(entry));
  },
};

export const hydrationStore = {
  addLog(log) {
    const stored = serialiseDates(log, ['recordedAt']);
    withState((data) => {
      data.hydrationLogs.push(stored);
    });
    return cloneWithDates(stored);
  },
  getLogs() {
    return getState().hydrationLogs.map((log) => cloneWithDates(log));
  },
};

export const heartRateStore = {
  addSample(sample) {
    const stored = serialiseDates(sample, ['recordedAt']);
    withState((data) => {
      data.heartRateSamples.push(stored);
    });
    return cloneWithDates(stored);
  },
  getSamples() {
    return getState().heartRateSamples.map((sample) => cloneWithDates(sample));
  },
};

export const mindfulnessStore = {
  addSession(session) {
    const stored = serialiseDates(session, ['startedAt']);
    withState((data) => {
      data.mindfulnessSessions.push(stored);
    });
    return cloneWithDates(stored);
  },
  getSessions() {
    return getState().mindfulnessSessions.map((session) => cloneWithDates(session));
  },
};

export const checkInStore = {
  addCheckIn(checkIn) {
    const stored = serialiseDates(checkIn, ['createdAt']);
    withState((data) => {
      data.dailyCheckIns.push(stored);
    });
    return cloneWithDates(stored);
  },
  getCheckIns() {
    return getState().dailyCheckIns.map((checkIn) => cloneWithDates(checkIn));
  },
};

export const goalStore = {
  upsertGoal(goal) {
    const stored = serialiseDates(goal, ['createdAt', 'updatedAt']);
    const result = withState((data) => {
      const index = data.goals.findIndex(
        (existing) => existing.type === stored.type && existing.period === stored.period
      );

      if (index >= 0) {
        const existing = data.goals[index];
        const merged = {
          ...existing,
          ...stored,
          id: existing.id,
          createdAt: existing.createdAt,
        };
        data.goals[index] = merged;
        return merged;
      } else {
        data.goals.push(stored);
        return stored;
      }
    });
    return cloneWithDates(result);
  },
  getGoals() {
    return getState().goals.map((goal) => cloneWithDates(goal));
  },
};

export const summaryStore = {
  getSummary() {
    return cloneWithDates(getState().wellnessSummary);
  },
  updateSummary(update) {
    const serialised = serialiseDates(update, ['date']);
    withState((data) => {
      data.wellnessSummary = {
        ...data.wellnessSummary,
        ...serialised,
        date: serialised.date || data.wellnessSummary.date,
      };
    }, { recalc: false });
    return this.getSummary();
  },
};

