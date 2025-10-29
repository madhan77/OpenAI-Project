const activities = [
  {
    id: 'activity-1',
    type: 'running',
    durationMinutes: 35,
    caloriesBurned: 420,
    steps: 6500,
    recordedAt: '2025-05-07T11:30:00.000Z'
  },
  {
    id: 'activity-2',
    type: 'walk',
    durationMinutes: 20,
    caloriesBurned: 120,
    steps: 2800,
    recordedAt: '2025-05-07T17:45:00.000Z'
  },
  {
    id: 'activity-3',
    type: 'cycling',
    durationMinutes: 45,
    caloriesBurned: 380,
    steps: 0,
    recordedAt: '2025-05-06T06:15:00.000Z'
  },
  {
    id: 'activity-4',
    type: 'strength',
    durationMinutes: 50,
    caloriesBurned: 320,
    steps: 1500,
    recordedAt: '2025-05-05T18:10:00.000Z'
  },
  {
    id: 'activity-5',
    type: 'walk',
    durationMinutes: 30,
    caloriesBurned: 160,
    steps: 3600,
    recordedAt: '2025-05-04T13:20:00.000Z'
  }
];

const sleepSessions = [
  {
    id: 'sleep-1',
    startTime: '2025-05-06T22:30:00.000Z',
    endTime: '2025-05-07T06:30:00.000Z',
    durationMinutes: 480,
    qualityScore: 82,
    stages: {
      rem: 23,
      deep: 21,
      light: 46,
      awake: 10
    },
    createdAt: '2025-05-07T06:35:00.000Z'
  },
  {
    id: 'sleep-2',
    startTime: '2025-05-05T22:45:00.000Z',
    endTime: '2025-05-06T06:15:00.000Z',
    durationMinutes: 450,
    qualityScore: 76,
    stages: {
      rem: 22,
      deep: 19,
      light: 47,
      awake: 12
    },
    createdAt: '2025-05-06T06:20:00.000Z'
  },
  {
    id: 'sleep-3',
    startTime: '2025-05-04T23:00:00.000Z',
    endTime: '2025-05-05T06:00:00.000Z',
    durationMinutes: 420,
    qualityScore: 70,
    stages: {
      rem: 21,
      deep: 18,
      light: 48,
      awake: 13
    },
    createdAt: '2025-05-05T06:05:00.000Z'
  }
];

const nutritionEntries = [
  {
    id: 'meal-1',
    name: 'Protein oatmeal',
    mealType: 'breakfast',
    calories: 420,
    proteinGrams: 32,
    carbsGrams: 48,
    fatGrams: 12,
    recordedAt: '2025-05-07T07:45:00.000Z'
  },
  {
    id: 'meal-2',
    name: 'Grilled chicken salad',
    mealType: 'lunch',
    calories: 560,
    proteinGrams: 46,
    carbsGrams: 42,
    fatGrams: 18,
    recordedAt: '2025-05-07T12:30:00.000Z'
  },
  {
    id: 'meal-3',
    name: 'Greek yogurt parfait',
    mealType: 'snack',
    calories: 220,
    proteinGrams: 18,
    carbsGrams: 28,
    fatGrams: 4,
    recordedAt: '2025-05-07T16:15:00.000Z'
  },
  {
    id: 'meal-4',
    name: 'Salmon with quinoa',
    mealType: 'dinner',
    calories: 640,
    proteinGrams: 44,
    carbsGrams: 52,
    fatGrams: 22,
    recordedAt: '2025-05-06T19:10:00.000Z'
  },
  {
    id: 'meal-5',
    name: 'Smoothie',
    mealType: 'snack',
    calories: 210,
    proteinGrams: 16,
    carbsGrams: 34,
    fatGrams: 3,
    recordedAt: '2025-05-05T09:30:00.000Z'
  }
];

const hydrationLogs = [
  {
    id: 'hydration-1',
    amountOz: 16,
    source: 'water bottle',
    recordedAt: '2025-05-07T08:15:00.000Z'
  },
  {
    id: 'hydration-2',
    amountOz: 20,
    source: 'water bottle',
    recordedAt: '2025-05-07T11:50:00.000Z'
  },
  {
    id: 'hydration-3',
    amountOz: 16,
    source: 'herbal tea',
    recordedAt: '2025-05-07T15:30:00.000Z'
  },
  {
    id: 'hydration-4',
    amountOz: 18,
    source: 'water bottle',
    recordedAt: '2025-05-06T10:05:00.000Z'
  },
  {
    id: 'hydration-5',
    amountOz: 16,
    source: 'sparkling water',
    recordedAt: '2025-05-05T13:20:00.000Z'
  },
  {
    id: 'hydration-6',
    amountOz: 12,
    source: 'coffee',
    recordedAt: '2025-05-04T09:05:00.000Z'
  }
];

const heartRateSamples = [
  {
    id: 'hr-1',
    bpm: 62,
    recordedAt: '2025-05-07T06:45:00.000Z',
    context: 'resting'
  },
  {
    id: 'hr-2',
    bpm: 138,
    recordedAt: '2025-05-07T11:30:00.000Z',
    context: 'running workout'
  },
  {
    id: 'hr-3',
    bpm: 118,
    recordedAt: '2025-05-06T06:25:00.000Z',
    context: 'post-ride recovery'
  },
  {
    id: 'hr-4',
    bpm: 60,
    recordedAt: '2025-05-05T07:00:00.000Z',
    context: 'resting'
  }
];

const mindfulnessSessions = [
  {
    id: 'mindfulness-1',
    type: 'guided-breathing',
    durationMinutes: 10,
    startedAt: '2025-05-07T07:15:00.000Z',
    moodAfter: 'calm',
    notes: 'Focused breathing before starting work.'
  },
  {
    id: 'mindfulness-2',
    type: 'meditation',
    durationMinutes: 12,
    startedAt: '2025-05-06T20:45:00.000Z',
    moodAfter: 'relaxed',
    notes: 'Evening wind-down routine.'
  },
  {
    id: 'mindfulness-3',
    type: 'body-scan',
    durationMinutes: 8,
    startedAt: '2025-05-05T07:05:00.000Z',
    moodAfter: 'centered',
    notes: 'Quick reset before commute.'
  }
];

const dailyCheckIns = [
  {
    id: 'checkin-1',
    moodScore: 4,
    stressLevel: 2,
    energyLevel: 4,
    notes: 'Great run this morning, feeling focused.',
    createdAt: '2025-05-07T08:00:00.000Z'
  },
  {
    id: 'checkin-2',
    moodScore: 3,
    stressLevel: 3,
    energyLevel: 3,
    notes: 'Busy workday but manageable.',
    createdAt: '2025-05-06T18:10:00.000Z'
  },
  {
    id: 'checkin-3',
    moodScore: 3,
    stressLevel: 4,
    energyLevel: 2,
    notes: 'Need to plan meals earlier to reduce stress.',
    createdAt: '2025-05-05T20:30:00.000Z'
  }
];

const goals = [
  {
    id: 'goal-steps',
    type: 'steps',
    targetValue: 10000,
    unit: 'steps',
    period: 'daily',
    currentValue: 8600,
    description: 'Stay above 10k steps to support cardio fitness.',
    createdAt: '2025-05-01T08:00:00.000Z',
    updatedAt: '2025-05-07T08:00:00.000Z'
  },
  {
    id: 'goal-sleep',
    type: 'sleep',
    targetValue: 7.5,
    unit: 'hours',
    period: 'daily',
    currentValue: 7.5,
    description: 'Average at least 7.5 hours of sleep per night.',
    createdAt: '2025-05-01T08:10:00.000Z',
    updatedAt: '2025-05-07T08:10:00.000Z'
  },
  {
    id: 'goal-hydration',
    type: 'hydration',
    targetValue: 80,
    unit: 'oz',
    period: 'daily',
    currentValue: 68,
    description: 'Maintain 80 oz hydration goal.',
    createdAt: '2025-05-01T08:15:00.000Z',
    updatedAt: '2025-05-07T08:15:00.000Z'
  }
];

const mockData = {
  activities,
  sleepSessions,
  nutritionEntries,
  hydrationLogs,
  heartRateSamples,
  mindfulnessSessions,
  dailyCheckIns,
  goals
};

export default mockData;
