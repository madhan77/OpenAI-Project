const DAY_IN_MS = 24 * 60 * 60 * 1000;

const startOfDay = (date) => {
  const normalized = new Date(date);
  normalized.setHours(0, 0, 0, 0);
  return normalized;
};

const formatKey = (date) => startOfDay(date).toISOString();

const initializeDay = (date) => ({
  date: startOfDay(date),
  steps: 0,
  caloriesIntake: 0,
  caloriesBurned: 0,
  sleepHours: 0,
  hydrationOz: 0,
  mindfulnessMinutes: 0,
  moodTotal: 0,
  stressTotal: 0,
  moodCount: 0,
  stressCount: 0,
  checkInsLogged: 0,
});

const mapToDays = ({ days, now }) => {
  const endDate = startOfDay(now);
  const startDate = new Date(endDate.getTime() - (days - 1) * DAY_IN_MS);
  const map = new Map();

  for (let i = 0; i < days; i += 1) {
    const current = new Date(startDate.getTime() + i * DAY_IN_MS);
    map.set(formatKey(current), initializeDay(current));
  }

  return { map, startDate, endDate };
};

const addActivityToDay = (day, activity) => {
  day.steps += typeof activity.steps === 'number' ? activity.steps : 0;
  day.caloriesBurned +=
    typeof activity.caloriesBurned === 'number' ? activity.caloriesBurned : 0;
};

const addSleepToDay = (day, session) => {
  if (typeof session.durationMinutes === 'number') {
    day.sleepHours += session.durationMinutes / 60;
  }
};

const addNutritionToDay = (day, entry) => {
  if (typeof entry.calories === 'number') {
    day.caloriesIntake += entry.calories;
  }
};

const addHydrationToDay = (day, log) => {
  if (typeof log.amountOz === 'number') {
    day.hydrationOz += log.amountOz;
  }
};

const addMindfulnessToDay = (day, session) => {
  if (typeof session.durationMinutes === 'number') {
    day.mindfulnessMinutes += session.durationMinutes;
  }
};

const addCheckInToDay = (day, checkIn) => {
  if (typeof checkIn.moodScore === 'number' && !Number.isNaN(checkIn.moodScore)) {
    day.moodTotal += checkIn.moodScore;
    day.moodCount += 1;
  }

  if (
    typeof checkIn.stressLevel === 'number' &&
    !Number.isNaN(checkIn.stressLevel)
  ) {
    day.stressTotal += checkIn.stressLevel;
    day.stressCount += 1;
  }

  day.checkInsLogged += 1;
};

const summarizeDay = (day) => ({
  date: day.date,
  steps: Math.round(day.steps),
  caloriesIntake: Math.round(day.caloriesIntake),
  caloriesBurned: Math.round(day.caloriesBurned),
  sleepHours: Number(day.sleepHours.toFixed(2)),
  hydrationOz: Number(day.hydrationOz.toFixed(2)),
  mindfulnessMinutes: Math.round(day.mindfulnessMinutes),
  averageMood: day.moodCount ? Number((day.moodTotal / day.moodCount).toFixed(2)) : null,
  averageStressLevel: day.stressCount
    ? Number((day.stressTotal / day.stressCount).toFixed(2))
    : null,
  checkInsLogged: day.checkInsLogged,
});

export function generateWeeklyProgress({
  days = 7,
  now,
  activities,
  sleepSessions,
  nutritionEntries,
  hydrationLogs,
  mindfulnessSessions,
  checkIns,
}) {
  const normalizedDays = Number.isFinite(days) ? Math.floor(days) : 7;
  const safeDays = Math.min(Math.max(normalizedDays, 1), 30);
  const window = mapToDays({ days: safeDays, now });
  const { map, startDate, endDate } = window;

  const addRecord = (recordDate, adder) => {
    if (!recordDate) return;
    const key = formatKey(recordDate);
    if (!map.has(key)) return;
    const day = map.get(key);
    adder(day);
  };

  activities.forEach((activity) => {
    addRecord(activity.recordedAt, (day) => addActivityToDay(day, activity));
  });

  sleepSessions.forEach((session) => {
    const reference = session.endTime ?? session.startTime;
    addRecord(reference, (day) => addSleepToDay(day, session));
  });

  nutritionEntries.forEach((entry) => {
    addRecord(entry.recordedAt, (day) => addNutritionToDay(day, entry));
  });

  hydrationLogs.forEach((log) => {
    addRecord(log.recordedAt, (day) => addHydrationToDay(day, log));
  });

  mindfulnessSessions.forEach((session) => {
    addRecord(session.startedAt, (day) => addMindfulnessToDay(day, session));
  });

  checkIns.forEach((checkIn) => {
    addRecord(checkIn.createdAt, (day) => addCheckInToDay(day, checkIn));
  });

  const daysList = Array.from(map.values()).sort((a, b) => a.date - b.date);

  return {
    startDate,
    endDate,
    days: daysList.map((day) => summarizeDay(day)),
  };
}
