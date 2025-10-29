const activities = [];
const sleepSessions = [];
const nutritionEntries = [];
const hydrationLogs = [];
const heartRateSamples = [];
const mindfulnessSessions = [];
const dailyCheckIns = [];
const goals = [];

let wellnessSummary = {
  date: new Date(),
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
};

const cloneWithDate = (record) => ({
  ...record,
  date: record.date ? new Date(record.date) : record.date,
  recordedAt: record.recordedAt ? new Date(record.recordedAt) : record.recordedAt,
  startTime: record.startTime ? new Date(record.startTime) : record.startTime,
  endTime: record.endTime ? new Date(record.endTime) : record.endTime,
  startedAt: record.startedAt ? new Date(record.startedAt) : record.startedAt,
  createdAt: record.createdAt ? new Date(record.createdAt) : record.createdAt,
  updatedAt: record.updatedAt ? new Date(record.updatedAt) : record.updatedAt,
  stages: record.stages ? { ...record.stages } : record.stages,
});

export const activityStore = {
  addActivity(activity) {
    activities.push(activity);
  },
  getActivities() {
    return activities.map((activity) => cloneWithDate(activity));
  },
};

export const sleepStore = {
  addSession(session) {
    sleepSessions.push(session);
  },
  getSessions() {
    return sleepSessions.map((session) => cloneWithDate(session));
  },
};

export const nutritionStore = {
  addEntry(entry) {
    nutritionEntries.push(entry);
  },
  getEntries() {
    return nutritionEntries.map((entry) => cloneWithDate(entry));
  },
};

export const hydrationStore = {
  addLog(log) {
    hydrationLogs.push(log);
  },
  getLogs() {
    return hydrationLogs.map((log) => cloneWithDate(log));
  },
};

export const heartRateStore = {
  addSample(sample) {
    heartRateSamples.push(sample);
  },
  getSamples() {
    return heartRateSamples.map((sample) => cloneWithDate(sample));
  },
};

export const mindfulnessStore = {
  addSession(session) {
    mindfulnessSessions.push(session);
  },
  getSessions() {
    return mindfulnessSessions.map((session) => cloneWithDate(session));
  },
};

export const checkInStore = {
  addCheckIn(checkIn) {
    dailyCheckIns.push(checkIn);
  },
  getCheckIns() {
    return dailyCheckIns.map((checkIn) => cloneWithDate(checkIn));
  },
};

export const goalStore = {
  upsertGoal(goal) {
    const index = goals.findIndex(
      (existing) => existing.type === goal.type && existing.period === goal.period
    );

    if (index >= 0) {
      const existing = goals[index];
      const updatedGoal = {
        ...existing,
        ...goal,
        id: existing.id,
        createdAt: existing.createdAt,
      };
      goals[index] = updatedGoal;
      return cloneWithDate(updatedGoal);
    }

    goals.push(goal);
    return cloneWithDate(goal);
  },
  getGoals() {
    return goals.map((goal) => cloneWithDate(goal));
  },
};

export const summaryStore = {
  getSummary() {
    return {
      ...wellnessSummary,
      date: new Date(wellnessSummary.date),
    };
  },
  updateSummary(update) {
    wellnessSummary = {
      ...wellnessSummary,
      ...update,
      date: update.date ? new Date(update.date) : wellnessSummary.date,
    };
    return this.getSummary();
  },
  updateFromActivity(activity) {
    const steps = typeof activity.steps === 'number' ? activity.steps : 0;
    const caloriesBurned =
      typeof activity.caloriesBurned === 'number' ? activity.caloriesBurned : 0;

    wellnessSummary = {
      ...wellnessSummary,
      steps: (wellnessSummary.steps || 0) + steps,
      caloriesBurned: (wellnessSummary.caloriesBurned || 0) + caloriesBurned,
    };
  },
  updateFromSleep(durationMinutes) {
    if (typeof durationMinutes !== 'number' || Number.isNaN(durationMinutes)) {
      return;
    }

    const hoursSlept = durationMinutes / 60;
    wellnessSummary = {
      ...wellnessSummary,
      sleepHours: (wellnessSummary.sleepHours || 0) + hoursSlept,
    };
  },
  updateFromNutrition(entry) {
    const calories = typeof entry.calories === 'number' ? entry.calories : 0;
    const protein = typeof entry.proteinGrams === 'number' ? entry.proteinGrams : 0;
    const carbs = typeof entry.carbsGrams === 'number' ? entry.carbsGrams : 0;
    const fat = typeof entry.fatGrams === 'number' ? entry.fatGrams : 0;

    wellnessSummary = {
      ...wellnessSummary,
      caloriesIntake: (wellnessSummary.caloriesIntake || 0) + calories,
      proteinGrams: (wellnessSummary.proteinGrams || 0) + protein,
      carbsGrams: (wellnessSummary.carbsGrams || 0) + carbs,
      fatGrams: (wellnessSummary.fatGrams || 0) + fat,
    };
  },
  updateFromHydration(log) {
    const amount = typeof log.amountOz === 'number' ? log.amountOz : 0;
    wellnessSummary = {
      ...wellnessSummary,
      hydrationOz: (wellnessSummary.hydrationOz || 0) + amount,
    };
  },
  updateFromHeartRate(sample) {
    if (typeof sample.bpm !== 'number' || Number.isNaN(sample.bpm)) {
      return;
    }

    if (sample.context === 'resting') {
      const current = wellnessSummary.restingHeartRate;
      if (typeof current !== 'number' || current === 0) {
        wellnessSummary = { ...wellnessSummary, restingHeartRate: sample.bpm };
      } else {
        const averaged = Math.round((current + sample.bpm) / 2);
        wellnessSummary = { ...wellnessSummary, restingHeartRate: averaged };
      }
    }
  },
  updateFromCheckIn(checkIn) {
    const mood =
      typeof checkIn.moodScore === 'number' && !Number.isNaN(checkIn.moodScore)
        ? checkIn.moodScore
        : null;
    const stress =
      typeof checkIn.stressLevel === 'number' && !Number.isNaN(checkIn.stressLevel)
        ? checkIn.stressLevel
        : null;
    const energy =
      typeof checkIn.energyLevel === 'number' && !Number.isNaN(checkIn.energyLevel)
        ? checkIn.energyLevel
        : null;

    wellnessSummary = {
      ...wellnessSummary,
      moodScore: mood ?? wellnessSummary.moodScore,
      stressLevel: stress ?? wellnessSummary.stressLevel,
      energyLevel: energy ?? wellnessSummary.energyLevel,
    };
  },
};
