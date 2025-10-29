import { v4 as uuid } from 'uuid';

const withinHours = (date, hours) => {
  if (!date) return false;
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  return diffMs <= hours * 3600000;
};

const normalize = (value, fallback = 0) =>
  typeof value === 'number' && !Number.isNaN(value) ? value : fallback;

const hasRecentMindfulness = (sessions) =>
  sessions.some((session) => withinHours(session.startedAt, 24));

const lastCheckIn = (checkIns) =>
  checkIns
    .slice()
    .sort((a, b) => b.createdAt - a.createdAt)[0];

export function generateDailyInsights({
  summary,
  activities,
  sleepSessions,
  nutritionEntries,
  hydrationLogs,
  heartRateSamples,
  goals,
  mindfulnessSessions,
  dailyCheckIns,
}) {
  const insights = [];
  const now = new Date();
  const addInsight = (category, message, severity = 'info') => {
    insights.push({
      id: uuid(),
      category,
      message,
      severity,
      createdAt: now,
    });
  };

  const stepsGoal = goals.find((goal) => goal.type === 'steps');
  const steps = normalize(summary.steps);
  if (stepsGoal && steps < stepsGoal.targetValue) {
    const remaining = Math.max(stepsGoal.targetValue - steps, 0);
    addInsight(
      'activity',
      `Take a quick walk — you're ${remaining} steps away from your daily goal of ${stepsGoal.targetValue}.`,
      remaining > 1000 ? 'warning' : 'info'
    );
  }

  const hydration = normalize(summary.hydrationOz);
  if (hydration < 64) {
    addInsight(
      'hydration',
      `Hydration check: you've logged ${hydration} oz today. Aim for at least 64 oz to stay refreshed.`,
      'warning'
    );
  }

  const sleepHours = normalize(summary.sleepHours);
  if (sleepHours > 0 && sleepHours < 7) {
    addInsight(
      'sleep',
      `Sleep recovery is important — consider adding a short wind-down routine to boost your ${sleepHours.toFixed(
        1
      )}-hour night.`,
      'warning'
    );
  }

  const caloriesIn = normalize(summary.caloriesIntake);
  const caloriesOut = normalize(summary.caloriesBurned);
  if (caloriesOut && caloriesIn && caloriesIn - caloriesOut > 400) {
    addInsight(
      'nutrition',
      `Your calorie intake exceeds burn by ${Math.round(
        caloriesIn - caloriesOut
      )} kcal. A lighter dinner or extra movement can help balance things out.`,
      'info'
    );
  }

  const restingSample = heartRateSamples
    .filter((sample) => sample.context === 'resting')
    .sort((a, b) => b.recordedAt - a.recordedAt)[0];
  if (restingSample && restingSample.bpm > 85) {
    addInsight(
      'heartRate',
      `Resting heart rate is elevated at ${restingSample.bpm} bpm. Try a breathing exercise or light stretch to wind down.`,
      'warning'
    );
  }

  if (!hasRecentMindfulness(mindfulnessSessions)) {
    addInsight(
      'mindfulness',
      'Schedule a 5-minute breathing break — consistent mindfulness helps reduce daily stress.',
      'info'
    );
  }

  const latestCheckIn = lastCheckIn(dailyCheckIns);
  if (!latestCheckIn || !withinHours(latestCheckIn.createdAt, 36)) {
    addInsight(
      'checkIn',
      'Log a quick daily check-in to keep your wellness trends up to date.',
      'info'
    );
  }

  if (latestCheckIn) {
    if (typeof latestCheckIn.stressLevel === 'number' && latestCheckIn.stressLevel >= 4) {
      addInsight(
        'stress',
        'Your recent check-in shows elevated stress. Try a guided breathing exercise or short walk to reset.',
        'warning'
      );
    }

    if (typeof latestCheckIn.moodScore === 'number' && latestCheckIn.moodScore <= 2) {
      addInsight(
        'mood',
        'Mood has been low recently. Consider reaching out to a friend or scheduling a relaxing activity today.',
        'info'
      );
    }
  }

  const lastActivity = activities.sort((a, b) => b.recordedAt - a.recordedAt)[0];
  if (!lastActivity || !withinHours(lastActivity.recordedAt, 6)) {
    addInsight(
      'activity',
      'It has been over 6 hours since your last logged activity. Consider a quick stretch or walk.',
      'info'
    );
  }

  const sleepQuality = sleepSessions
    .filter((session) => typeof session.qualityScore === 'number')
    .slice(-3)
    .map((session) => session.qualityScore);
  if (sleepQuality.length === 3) {
    const avgQuality = sleepQuality.reduce((total, score) => total + score, 0) / sleepQuality.length;
    if (avgQuality < 70) {
      addInsight(
        'sleep',
        `Average sleep quality over last 3 nights is ${Math.round(avgQuality)}. Try limiting screen time before bed for deeper rest.`,
        'info'
      );
    }
  }

  if (!insights.length) {
    addInsight('overview', 'Great job! Your logs look balanced today. Keep up the momentum.', 'success');
  }

  return insights;
}
