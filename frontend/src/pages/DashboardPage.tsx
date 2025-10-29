import { gql, useQuery } from '@apollo/client';
import { useMemo } from 'react';
import { SummaryCard } from '../components/SummaryCard.tsx';
import { InsightsPanel } from '../components/InsightsPanel.tsx';
import { ProgressTrend } from '../components/ProgressTrend.tsx';
import './DashboardPage.css';

const DASHBOARD_QUERY = gql`
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
      mindfulnessMinutes
      moodScore
      stressLevel
      energyLevel
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
        caloriesBurned
        sleepHours
        hydrationOz
        mindfulnessMinutes
        averageMood
        averageStressLevel
      }
    }
  }
`;

export function DashboardPage() {
  const { data, loading, error } = useQuery(DASHBOARD_QUERY, {
    fetchPolicy: 'cache-and-network'
  });

  const summary = data?.wellnessSummary;
  const macros = useMemo(() => {
    if (!summary) return { protein: 0, carbs: 0, fat: 0 };
    return {
      protein: summary.proteinGrams ?? 0,
      carbs: summary.carbsGrams ?? 0,
      fat: summary.fatGrams ?? 0
    };
  }, [summary]);

  return (
    <div className="dashboard-page">
      <div className="dashboard-page__header">
        <div>
          <h2>Today&apos;s wellness snapshot</h2>
          <p>Track activity, recovery, and mindfulness to stay on top of your goals.</p>
        </div>
        {summary && (
          <span className="dashboard-page__date">
            Updated {new Date(summary.date).toLocaleString()}
          </span>
        )}
      </div>

      {loading && <p className="dashboard-page__state">Loading latest data…</p>}
      {error && <p className="dashboard-page__state dashboard-page__state--error">{error.message}</p>}

      {summary && (
        <section className="dashboard-page__cards" aria-label="Daily wellness metrics">
          <SummaryCard title="Steps" value={summary.steps.toLocaleString()} helper="Goal: 10k" accent="blue" />
          <SummaryCard
            title="Active calories"
            value={`${Math.round(summary.caloriesBurned)} kcal`}
            helper={`Intake ${Math.round(summary.caloriesIntake)} kcal`}
            accent="orange"
          />
          <SummaryCard title="Sleep" value={`${summary.sleepHours.toFixed(1)} hrs`} helper="Past 24h" accent="purple" />
          <SummaryCard
            title="Hydration"
            value={`${summary.hydrationOz.toFixed(0)} oz`}
            helper="Water intake"
            accent="green"
          />
          <SummaryCard
            title="Resting HR"
            value={`${summary.restingHeartRate ?? '—'} bpm`}
            helper="Rolling average"
            accent="blue"
          />
          <SummaryCard
            title="Mindfulness"
            value={`${summary.mindfulnessMinutes ?? 0} min`}
            helper="Guided sessions"
            accent="purple"
          />
          <SummaryCard
            title="Mood"
            value={`${summary.moodScore?.toFixed(1) ?? '—'} / 5`}
            helper={`Energy ${summary.energyLevel?.toFixed(1) ?? '—'}`}
            accent="green"
          />
          <SummaryCard
            title="Macros"
            value={`${macros.protein}P • ${macros.carbs}C • ${macros.fat}F`}
            helper="grams"
            accent="orange"
          />
        </section>
      )}

      {data?.dailyInsights && data.dailyInsights.length > 0 && (
        <InsightsPanel
          title="Personalized insights"
          subtitle="Daily guidance generated from your recent activity"
          insights={data.dailyInsights}
        />
      )}

      {data?.weeklyProgress?.days && data.weeklyProgress.days.length > 0 && (
        <ProgressTrend days={data.weeklyProgress.days} />
      )}
    </div>
  );
}
